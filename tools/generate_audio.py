"""Generate only missing MP3 files from lesson manifests; requires network.

Synthetic speech: Microsoft Edge TTS via edge-tts. No secrets required.
Delete a specific MP3 before regenerating a changed utterance.
"""
import asyncio
import json
from pathlib import Path
import edge_tts

ROOT = Path(__file__).resolve().parents[1]

async def main():
    gate = asyncio.Semaphore(3)
    async def generate(folder, item):
        target = folder / item['file']
        if target.exists() and target.stat().st_size > 1000:
            return
        async with gate:
            for attempt in range(3):
                try:
                    await edge_tts.Communicate(item['text'], item['voice'], rate='-10%').save(str(target))
                    print(f"Created {target.relative_to(ROOT)}", flush=True)
                    return
                except Exception:
                    target.unlink(missing_ok=True)
                    if attempt == 2:
                        raise
                    await asyncio.sleep(2)
    jobs = []
    for manifest in sorted(ROOT.glob('lessons/*/audio/manifest.json')):
        data = json.loads(manifest.read_text(encoding='utf-8'))
        jobs.extend(generate(manifest.parent, item) for item in data['clips'])
    if not jobs:
        raise SystemExit('No manifests. Run build_lessons.py --prepare first.')
    await asyncio.gather(*jobs)

if __name__ == '__main__':
    asyncio.run(main())
