"""Validate content packaging, audio decoding and optionally real browser behavior.

python tools/verify.py --browser
Browser check uses an installed Chrome/Edge with Playwright, including offline file://.
Does not assess human pronunciation quality.
"""
import argparse
import base64
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from urllib.parse import unquote, urlsplit
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]

def structural():
    pages=[ROOT/'index.html',*sorted(ROOT.glob('lessons/*/index.html'))]
    assert len(pages)==3, 'Expected catalog and two lessons'
    audio_count=0
    for page in pages:
        soup=BeautifulSoup(page.read_text(encoding='utf-8'),'html.parser')
        assert soup.html.get('lang')=='ru'
        assert soup.find('meta',attrs={'name':'viewport'})
        assert soup.find('h1')
        ids=[n['id'] for n in soup.select('[id]')]
        assert len(ids)==len(set(ids)),f'Duplicate id in {page}'
        for link in soup.select('[href]'):
            url=link['href']
            parsed=urlsplit(url)
            if parsed.scheme or parsed.netloc:
                continue
            if not parsed.path:
                assert parsed.fragment in ids,(page,url)
            else:
                target=(page.parent/unquote(parsed.path)).resolve()
                assert target.exists(),(page,url)
        for node in soup.select('[src]'):
            assert node['src'].startswith('data:'),f'External dependency: {page}'
        if page.parent==ROOT:
            continue
        for name in ['README.md','speaking.md','cards.tsv','audio/manifest.json']:
            assert (page.parent/name).exists(),name
        manifest=json.loads((page.parent/'audio/manifest.json').read_text(encoding='utf-8'))
        audio=soup.select('audio source')
        assert len(audio)==len(manifest['clips']),f'Audio count: {page}'
        files={}
        for item in manifest['clips']:
            path=page.parent/'audio'/item['file']
            assert path.stat().st_size>1000,path
            result=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f','null','-'],capture_output=True)
            assert result.returncode==0,result.stderr.decode(errors='replace')
            files[path.read_bytes()]=item
        for source in audio:
            data=base64.b64decode(source['src'].split(',',1)[1],validate=True)
            assert data in files,'Embedded audio differs from MP3 source'
            item=files[data]
            clip=source.find_parent('div',class_='clip')
            if item['id'].startswith('dict-'):
                details=clip.find_next_sibling('details')
                assert details and item['text'] in details.get_text(),item
            else:
                assert item['text'] in clip.get_text(),item
        card_ids={line.split('\t')[3] for line in (page.parent/'cards.tsv').read_text(encoding='utf-8').splitlines()[1:]}
        assert card_ids <= {x['id'] for x in manifest['clips']}
        assert soup.select('svg[role="img"] title')
        audio_count+=len(audio)
        print(f'Validated {page.relative_to(ROOT)}: {len(audio)} embedded clips')
    print(f'PASS: {len(pages)} HTML files; {audio_count} MP3 decodes; links and manifests consistent.')

def browser():
    from playwright.sync_api import sync_playwright
    candidates=[Path('C:/Program Files/Google/Chrome/Application/chrome.exe'),Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')]
    executable=next((str(x) for x in candidates if x.exists()),None)
    artifacts=ROOT/'artifacts'
    artifacts.mkdir(exist_ok=True)
    with sync_playwright() as p:
        args={'headless':True,'args':['--autoplay-policy=no-user-gesture-required']}
        if executable:
            args['executable_path']=executable
        b=p.chromium.launch(**args)
        context=b.new_context(offline=True)
        page=context.new_page()
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        requests=[]
        page.on('request',lambda r:requests.append(r.url) if r.url.startswith(('http://','https://')) else None)
        for file in [ROOT/'index.html',*sorted(ROOT.glob('lessons/*/index.html'))]:
            page.goto(file.as_uri())
            for width in [360,390,430,1280]:
                page.set_viewport_size({'width':width,'height':844})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),f'Overflow: {file} {width}'
                if width==390:
                    page.screenshot(path=str(artifacts/f'{file.parent.name if file.parent!=ROOT else "catalog"}-mobile.png'),full_page=True)
            if file.parent==ROOT:
                continue
            # Expand full alphabet reference for metadata checks too.
            if page.locator('#alphabet details').count():
                page.locator('#alphabet summary').click()
                assert page.locator('#alphabet details').get_attribute('open') is not None
            page.locator('audio').evaluate_all('(xs)=>xs.forEach(a=>a.load())')
            page.wait_for_function('Array.from(document.querySelectorAll("audio")).every(a=>a.readyState>=1 && Number.isFinite(a.duration) && a.duration>0)',timeout=30000)
            page.select_option('#speed','0.8')
            assert page.locator('audio').evaluate_all('(xs)=>xs.every(a=>a.playbackRate===0.8)')
            first=page.locator('audio').first
            first.evaluate('(a)=>a.play()')
            first.evaluate('(a)=>new Promise((resolve,reject)=>{if(a.currentTime>0)return resolve();a.addEventListener("timeupdate",()=>{if(a.currentTime>0)resolve()},{once:true});setTimeout(()=>reject(new Error("Audio clock did not advance")),10000)})')
            assert first.evaluate('(a)=>!a.paused && a.currentTime>0')
            page.locator('audio').nth(1).evaluate('(a)=>a.play()')
            assert first.evaluate('(a)=>a.paused'), 'Other audio should pause'
            page.locator('audio').nth(1).evaluate('(a)=>a.pause()')
            page.locator('[data-copy]').click()
            page.wait_for_function('document.querySelector("[data-copy]").textContent!=="Скопировать инструкцию тренеру"')
            assert page.locator('[data-copy]').inner_text() in ['Скопировано','Выделите и скопируйте текст ниже']
            assert page.locator('#coach').inner_text().startswith('Ты — мой голосовой тренер')
            for details in page.locator('#practice details').all():
                assert details.get_attribute('open') is None,'Answers should initially be hidden'
            page.locator('#practice summary').first.click()
            assert page.locator('#practice details').first.get_attribute('open') is not None
            print(f'Browser PASS: {file.parent.name}; 4 widths, offline audio, rate, copy fallback, answers')
        # Single-file publication simulation: no adjacent assets, and no JavaScript.
        with tempfile.TemporaryDirectory(prefix='turkish-standalone-') as temp:
            isolated=Path(temp)/'lesson.html'
            shutil.copyfile(ROOT/'lessons/01-sounds-and-hello/index.html',isolated)
            nojs=b.new_context(offline=True,java_script_enabled=False,viewport={'width':390,'height':844})
            static=nojs.new_page()
            static.goto(isolated.as_uri())
            static.locator('#practice summary').first.click()
            assert static.locator('#practice details').first.get_attribute('open') is not None
            assert static.locator('audio source').count()==18
            nojs.close()
        assert not errors,errors
        assert not requests,requests
        b.close()
    print('PASS: isolated file/no-JS content; no page errors or HTTP dependencies.')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--browser',action='store_true')
    args=parser.parse_args()
    structural()
    if args.browser: browser()
