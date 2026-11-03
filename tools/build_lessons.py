"""Source of the two initial lessons. Build standalone HTML with embedded audio/SVG.

--prepare writes manifests, cards and supporting Markdown before audio generation.
Normal build requires all MP3s. Python standard library only.
"""
import argparse
import base64
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LESSONS = ROOT / 'lessons'
FEMALE = 'tr-TR-EmelNeural'
MALE = 'tr-TR-AhmetNeural'

AUDIO = {
 '01-sounds-and-hello': [
  ('alphabet-1', 'araba. balık. cam. çay. deniz. ev. fil. göz.', FEMALE),
  ('alphabet-2', 'dağ. hava. ılık. iki. jilet. kedi. limon.', FEMALE),
  ('alphabet-3', 'masa. nar. okul. ön. para. renk. su.', MALE),
  ('alphabet-4', 'şeker. top. un. üç. vapur. yol. zaman.', MALE),
  ('vowels', 'a. e. ı. i. o. ö. u. ü.', FEMALE),
  ('contrast-i', 'ılık. ilik.', FEMALE),
  ('contrast-o', 'on. ön.', MALE),
  ('contrast-u', 'un. ün.', FEMALE),
  ('hello', 'Merhaba.', FEMALE),
  ('name', 'Benim adım Deniz.', FEMALE),
  ('question-name', 'Senin adın ne?', MALE),
  ('pleased', 'Memnun oldum.', MALE),
  ('repeat', 'Tekrar eder misin?', FEMALE),
  ('slow', 'Yavaş, lütfen.', FEMALE),
  ('dialogue', 'Merhaba. Benim adım Deniz. Senin adın ne? Benim adım Ece. Memnun oldum.', MALE),
  ('dict-1', 'çay', MALE), ('dict-2', 'üç', FEMALE), ('dict-3', 'göz', MALE),
 ],
 '02-numbers-and-requests': [
  *[(f'n-{i}', word, FEMALE if i % 2 == 0 else MALE) for i,word in enumerate(['sıfır','bir','iki','üç','dört','beş','altı','yedi','sekiz','dokuz','on'])],
  ('numbers', 'sıfır. bir. iki. üç. dört. beş. altı. yedi. sekiz. dokuz. on.', MALE),
  ('request', 'Bir çay, lütfen.', FEMALE),
  ('question', 'Kaç çay?', MALE),
  ('thanks', 'Teşekkür ederim.', FEMALE),
  ('dialogue', 'Merhaba. Bir çay, lütfen. Kaç çay? Bir çay, lütfen. Teşekkür ederim.', MALE),
  ('dict-1', 'üç. bir. yedi.', MALE),
  ('dict-2', 'dört. sıfır. on.', FEMALE),
  ('dict-3', 'İki çay, lütfen.', MALE),
 ]
}

TITLES = {'01-sounds-and-hello':'Буквы, звуки и первое знакомство', '02-numbers-and-requests':'Числа 0–10 и вежливая просьба'}

CSS = '''
:root{color-scheme:light;--ink:#18332f;--muted:#465d58;--paper:#f7f5ee;--accent:#176252;--line:#cfdbd4;--warm:#f4e8ca}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:18px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}a{color:#155c50;text-underline-offset:4px}a:hover{text-decoration-thickness:3px}
main{max-width:780px;margin:auto;padding:24px 18px 64px}header{padding:18px 0 28px;border-bottom:2px solid var(--ink)}h1{font-size:clamp(2rem,7vw,3.2rem);line-height:1.12;letter-spacing:-.03em;margin:18px 0}h2{font-size:1.5rem;line-height:1.3;margin:0 0 18px}h3{font-size:1.13rem;margin:22px 0 10px}p{margin:10px 0 16px}section{padding:28px 0;border-bottom:1px solid var(--line)}.eyebrow{font-size:.8rem;font-weight:750;letter-spacing:.09em;text-transform:uppercase;color:var(--muted)}.tag{display:inline-block;background:var(--warm);padding:4px 10px;border-radius:6px;margin:4px 4px 4px 0;font-size:.9rem}.lead{font-size:1.15rem}.callout{border-left:4px solid var(--accent);padding:12px 16px;background:#e9f0e9;border-radius:0 8px 8px 0}.small{font-size:.9rem;color:var(--muted)}nav{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0}nav a{padding:10px 14px;border:1px solid var(--line);border-radius:8px;min-height:44px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,235px),1fr));gap:12px}.card{background:white;padding:18px;border:1px solid var(--line);border-radius:12px;min-width:0}.tr{font-size:1.35rem;font-weight:650}.clip{background:white;border:1px solid var(--line);border-radius:10px;margin:14px 0;padding:14px;min-width:0}.clip p{margin:0 0 8px}.clip audio{display:block;width:100%;min-width:0;max-width:100%;height:44px}button,select{font:inherit;padding:8px 12px;min-height:44px;border:1px solid #71887e;border-radius:6px;background:white;color:var(--ink);cursor:pointer}button:hover{background:#e6efe7}button:focus-visible,a:focus-visible,summary:focus-visible,select:focus-visible{outline:3px solid #a34c00;outline-offset:4px}label{display:block;margin:12px 0}details{margin:14px 0;border:1px solid var(--line);border-radius:8px;background:white;padding:0 14px}summary{cursor:pointer;padding:12px 0;min-height:48px;font-weight:650}details>div{padding:0 0 14px}table{border-collapse:collapse;width:100%;font-size:1rem}td,th{text-align:left;border-bottom:1px solid var(--line);padding:10px 6px;vertical-align:top}th{font-size:.86rem;color:var(--muted)}td small{display:block;color:var(--muted)}.letter{font-size:1.4rem;font-weight:700}ul,ol{padding-left:24px}li{margin:8px 0}.number{font-size:2.3rem;line-height:1.2;color:var(--accent)}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:16px/1.6 system-ui;background:#eef2eb;padding:16px;border-radius:8px}svg{width:100%;height:auto;display:block}figure{margin:18px 0}figcaption{font-size:.9rem;color:var(--muted)}.check{border-top:1px solid var(--line);padding:12px 0}.check input{width:22px;height:22px;vertical-align:middle;margin-right:10px;accent-color:var(--accent)}footer{padding-top:24px;font-size:.88rem;color:var(--muted)}.hidden-answer{font-weight:650} @media(max-width:420px){main{padding:18px 14px 48px}.card{padding:14px}td,th{padding:8px 4px;font-size:.92rem}}@media print{body{background:white}main{max-width:none}audio,button,nav,.settings{display:none}details{break-inside:avoid}details>div{display:block}section{break-inside:auto}}
'''

JS = '''
document.querySelectorAll('audio').forEach(a=>a.addEventListener('play',()=>{document.querySelectorAll('audio').forEach(b=>{if(b!==a)b.pause()})}));
document.getElementById('speed')?.addEventListener('change',e=>document.querySelectorAll('audio').forEach(a=>a.playbackRate=Number(e.target.value)));
document.querySelectorAll('[data-copy]').forEach(b=>b.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(document.getElementById(b.dataset.copy).textContent);b.textContent='Скопировано'}catch{b.textContent='Выделите и скопируйте текст ниже'}}));
'''

def tr(text): return f'<span lang="tr">{html.escape(text)}</span>'
def answer(content, title='Показать ответ и объяснение'):
    return f'<details><summary>{title}</summary><div>{content}</div></details>'
def section(id, title, content):
    return f'<section id="{id}"><h2>{title}</h2>{content}</section>'
def audio(slug, id, label, text=None):
    item = next(x for x in AUDIO[slug] if x[0]==id)
    source = LESSONS / slug / 'audio' / f'{id}.mp3'
    encoded = base64.b64encode(source.read_bytes()).decode('ascii')
    transcript = '' if text is False else f'<p class="tr" lang="tr">{html.escape(text if text is not None else item[1])}</p>'
    return f'<div class="clip"><p class="small">{html.escape(label)} · синтез речи</p><audio controls preload="none" aria-label="{html.escape(label)}"><source src="data:audio/mpeg;base64,{encoded}" type="audio/mpeg">Аудио не поддерживается браузером.</audio>{transcript if text is not False else ""}</div>'

def clip(slug, id, label, hide=False):
    # Hidden dictation transcript must remain available without JavaScript.
    item = next(x for x in AUDIO[slug] if x[0]==id)
    if not hide:
        return audio(slug,id,label)
    return audio(slug,id,label,False) + answer(f'<p lang="tr" class="tr">{html.escape(item[1])}</p>', 'Открыть расшифровку после ответа')

def scaffold(slug, number, intro, content):
    return f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#176252"><meta name="description" content="Турецкий с нуля: урок {number}, теория, практика, встроенное аудио и разговорный сценарий."><title>{number} · {TITLES[slug]}</title><style>{CSS}</style></head>
<body><main><a href="../../index.html">← Каталог курса</a><header><div class="eyebrow">Турецкий с нуля / Старт</div><h1>{TITLES[slug]}</h1><span class="tag">Урок {number}</span><span class="tag">До A1 · с нуля</span><span class="tag">30–40 минут · можно в 2 подхода</span><p class="lead">{intro}</p><nav aria-label="Разделы урока"><a href="#learn">Разобраться</a><a href="#listen">Послушать</a><a href="#practice">Потренироваться</a><a href="#speak">Поговорить</a><a href="#check">Проверить себя</a></nav></header>
<div class="settings"><label for="speed">Скорость аудио <select id="speed"><option value="1">Обычная учебная</option><option value="0.8">Медленнее · 0,8×</option><option value="1.1">Быстрее · 1,1×</option></select></label><p class="small">Записи уже немного замедлены при создании. Сначала обычная учебная скорость, замедление — при трудности, затем снова обычная. Без JavaScript можно пользоваться настройками плеера браузера.</p></div>
<div class="callout"><strong>Как работать со звуком.</strong> Нажмите ▶, посмотрите на турецкий текст и поймите смысл. Послушайте ещё раз, повторите. Потом закройте текст рукой и попробуйте услышать/сказать без чтения. Диктанты ниже имеют скрытую расшифровку.</div>
{content}
<footer><p>Версия 1.0 · 03.11.2026. Оригинальные учебные тексты и SVG-схемы. Озвучка: Microsoft Edge TTS, tr-TR-EmelNeural / tr-TR-AhmetNeural, синтетическая. Не проходила слуховую проверку носителем. Декодируемость проверяется отдельно; эти записи не являются экзаменационным эталоном живой речи.</p><p>Весь материал, аудио и схемы встроены: файл можно открыть без сети и отдельно публиковать. Ссылка на каталог работает в полном дереве курса; при публикации одного урока возвращайтесь через страницу, откуда его открыли. Чекбоксы — временные пометки, не журнал и не сохранённый результат.</p><p>Языковые ориентиры: <a href="https://tdk.gov.tr/icerik/yazim-kurallari/ses-harf-ve-alfabe/">TDK: алфавит</a>; <a href="https://yazim.tdk.gov.tr/content/02-sesler-ve-ses-uyumlari.html">TDK: звуки и гармония</a>. Методика: <a href="https://doi.org/10.1111/lang.12479">распределённая практика</a>, <a href="https://doi.org/10.1017/S0142716424000195">фонетический тренинг</a>. Внешние ссылки требуют интернета, выполнение урока — нет.</p></footer></main><script>{JS}</script></body></html>'''

SPEAK_1 = '''Ты — мой голосовой тренер турецкого. Я русскоязычный абсолютный новичок, урок 01. Проведи 8–10 минут знакомства, задавая по одной реплике и дожидаясь моего ответа. Не играй за меня.
Мой материал: Merhaba — здравствуйте/привет; Benim adım … — меня зовут …; Senin adın ne? — как тебя зовут?; Memnun oldum — приятно познакомиться; Tekrar eder misin? — повторишь?; Yavaş, lütfen — медленнее, пожалуйста. Обращение пока неформальное, на «ты».
Сначала скажи Merhaba, затем спроси Senin adın ne? Помоги, если не отвечаю. После этого поменяй роли: я сам приветствую и спрашиваю имя. Ты называешь вымышленное имя Deniz или Ece. Пусть я хотя бы раз попрошу повторить или замедлиться.
Подсказывай постепенно: смысл → начало фразы → образец → мой повтор. Исправляй не более 1–2 целевых ошибок. Фонетика: ı/i и ü, ç/ş — только если получаешь реальное аудио. Если доступна одна транскрипция, скажи «произношение не оценено».
В конце новый обмен без чтения. Цель: 4 самостоятельные реплики, ≤2 подсказок. Отчёт: самостоятельные ответы/всего, подсказки, одна трудность, что повторить завтра. Не объявляй урок пройденным без моих ответов.'''

SPEAK_2 = '''Ты — мой голосовой тренер турецкого. Урок 02, 8–12 минут: заказ чая. Я знаю Merhaba; Benim adım …; Senin adın ne?; Memnun oldum; Tekrar eder misin?; Yavaş, lütfen.
Новый материал: sıfır 0, bir 1, iki 2, üç 3, dört 4, beş 5, altı 6, yedi 7, sekiz 8, dokuz 9, on 10; çay — чай; Bir çay, lütfen — один чай, пожалуйста; Kaç çay? — сколько чаёв/чашек чая?; Teşekkür ederim — спасибо.
Одна реплика за раз, жди мой ответ. Сначала 4 числа вразброс: я называю цифру/пишу её. Затем я заказываю 1, 2 или 3 чая, ты переспрашиваешь Kaç çay?, я подтверждаю количество и благодарю. Не добавляй цену, деньги и другую грамматику. После трёх заказов меняем роли: я спрашиваю количество. Устрой один повод попросить повторить.
Если трудно, дай намёк, начало, затем образец; попроси повторить. Исправляй одну целевую ошибку, затем вернись к разговору. После числа существительное в единственном: iki çay, не iki çaylar.
Финал: новый заказ без шпаргалки. Цель: 3 заказа со сменой числа и один вопрос Kaç çay?, ≤2 подсказок. Произношение оценивай только по реальному аудио, не по транскрипции. Отчёт: независимые ответы/всего, подсказки, трудность, цель на завтра. Не выдавай результат заранее.'''

def speaking_block(script):
    return f'''<p>Откройте отдельного голосового агента и передайте инструкцию ниже. Сам HTML не слушает микрофон и не оценивает вашу речь. Если есть только текстовый чат, проговорите ответы вслух самостоятельно; оценку произношения оставьте непроверенной.</p><button type="button" data-copy="coach">Скопировать инструкцию тренеру</button><pre id="coach">{html.escape(script)}</pre><p class="small">Если кнопка не сработала, выделите текст и скопируйте вручную. На усталый день: два коротких обмена вместо полной сессии.</p>'''

def checks(items):
    return ''.join(f'<label class="check"><input type="checkbox">{item}</label>' for item in items)

def return_plan():
    return '''<p><strong>Сегодня:</strong> закройте страницу и вспомните 3 главные фразы. <strong>Завтра:</strong> сначала ответьте без повторного чтения, потом сверяйтесь. <strong>Через 3, 7, 14 и 30 дней:</strong> повторите короткую задачу с новым именем или числом.</p><p>Ответ не вспомнился — откройте образец, повторите правильно и вернитесь завтра. Запишите фактическую дату и результат в журнал репозитория или заметку телефона: минуты, правильные ответы/всего, подсказки, следующая дата. Страница сама прогресс не сохраняет.</p>'''

def lesson_one():
    s = '01-sounds-and-hello'
    body = section('start','Сегодня вы сможете', '''<ul><li>Отличать написание ı/i, ç/ş, ö/ü и начать слышать гласные.</li><li>Поздороваться, назвать имя и попросить повторить.</li><li>Написать 3 знакомых слова по короткому аудио.</li></ul><p>Ничего заранее знать не нужно. В первый подход (15–20 минут) — гласные и приветствие, во второй — практика и разговор. <strong>На 10 минут:</strong> Merhaba + Benim adım …, одна пара гласных и два обмена с агентом.</p>''')
    svg = '''<figure><svg viewBox="0 0 600 230" role="img" aria-labelledby="vowel-title vowel-desc"><title id="vowel-title">Две настройки губ для гласных</title><desc id="vowel-desc">Слева неокруглённые губы для и; справа округлённые губы для ю-подобного турецкого ü. Положение языка сохраняется как для и. Для ö начните с э и округлите губы.</desc><rect x="2" y="2" width="596" height="226" rx="20" fill="#e9f0e9"/><path d="M65 100 Q150 145 235 100 Q150 115 65 100" fill="#176252"/><ellipse cx="450" cy="105" rx="39" ry="49" fill="none" stroke="#176252" stroke-width="12"/><path d="M275 105 H350 l-15 -12 M350 105 l-15 12" fill="none" stroke="#18332f" stroke-width="5"/><text x="150" y="190" text-anchor="middle" font-size="24" fill="#18332f">i → ü</text><text x="450" y="190" text-anchor="middle" font-size="24" fill="#18332f">e → ö</text></svg><figcaption>Схема-подсказка: ü — язык примерно как для «и», губы округлены; ö — начните с «э» и округлите губы. Не добавляйте отдельный звук «й». Это не точная анатомическая схема.</figcaption></figure>'''
    body += section('learn','1. Буква → звук', '''<p>В турецком 29 букв. Пишем слева направо. Не нужно учить названия всех букв сегодня: важнее начать узнавать написание и звучание в словах. Звук — то, что слышим; буква — знак на письме. Название буквы c — ce, а её звук в слове похож на «дж».</p><div class="grid"><div class="card"><div class="tr" lang="tr">I ı ≠ İ i</div><p>Это две разные буквы. ı — неогублённый задний гласный, примерно «ы», но не точная копия русского звука. i близко к «и».</p></div><div class="card"><div class="tr" lang="tr">C c · Ç ç · Ş ş</div><p>c примерно «дж», ç — «ч», ş — «ш». Турецкое c не читается как русское «с».</p></div><div class="card"><div class="tr" lang="tr">Ö ö · Ü ü</div><p>Губы округлены. Не заменяйте ö на «о», ü на «у» и не читайте их как два звука.</p></div><div class="card"><div class="tr" lang="tr">Ğ ğ · H h · Y y</div><p>ğ не русское «г»; часто удлиняет или связывает соседние гласные. h — лёгкий выдох, мягче русского «х». y близко к «й».</p></div></div>''' + svg + '<p>Гласных восемь: '+tr('a e ı i o ö u ü')+'. Произносите каждую ясно; не превращайте безударное o автоматически в русское «а». Ударение разберём по словам: правило «всегда на последнем слоге» неверно.</p>' + clip(s,'vowels','Восемь гласных — слушайте, затем повторите'))
    rows = [
      ('A a','a','araba','машина'),('B b','be','balık','рыба'),('C c','ce','cam','стекло'),('Ç ç','çe','çay','чай'),('D d','de','deniz','море'),('E e','e','ev','дом'),('F f','fe','fil','слон'),('G g','ge','göz','глаз'),
      ('Ğ ğ','yumuşak ge','dağ','гора; отдельного «г» не добавляем'),('H h','he','hava','воздух; погода'),('I ı','ı','ılık','тёплый, не горячий'),('İ i','i','iki','два'),('J j','je','jilet','бритвенное лезвие; j примерно «ж»'),('K k','ke','kedi','кошка'),('L l','le','limon','лимон'),
      ('M m','me','masa','стол'),('N n','ne','nar','гранат'),('O o','o','okul','школа'),('Ö ö','ö','ön','передняя сторона; перед'),('P p','pe','para','деньги'),('R r','re','renk','цвет'),('S s','se','su','вода'),
      ('Ş ş','şe','şeker','сахар'),('T t','te','top','мяч'),('U u','u','un','мука'),('Ü ü','ü','üç','три'),('V v','ve','vapur','паром'),('Y y','ye','yol','дорога'),('Z z','ze','zaman','время')]
    groups = [(rows[:8],'alphabet-1','A–G'),(rows[8:15],'alphabet-2','Ğ–L'),(rows[15:22],'alphabet-3','M–S'),(rows[22:],'alphabet-4','Ş–Z')]
    table = '<p><strong>Справочник, а не список для заучивания.</strong> В аудио звучат слова-примеры по порядку строк, не названия букв. Названия букв даны для будущего чтения по буквам; q, w, x в современный турецкий алфавит не входят.</p>'
    for group, aud, title in groups:
        table += f'<h3>{title}</h3><table><thead><tr><th>Буква</th><th>Название</th><th>Пример / смысл</th></tr></thead><tbody>'
        table += ''.join(f'<tr><td class="letter" lang="tr">{letter}</td><td lang="tr">{name}</td><td><span lang="tr">{word}</span><small>{meaning}</small></td></tr>' for letter,name,word,meaning in group)
        table += '</tbody></table>' + clip(s,aud,f'Слова-примеры {title}')
    body += section('alphabet','2. Алфавит под рукой',answer(table,'Открыть все 29 букв и аудио-примеры'))
    body += section('listen','3. Услышать различие', '<p>Прослушайте каждую пару с текстом. Повторите два разных звука, затем закройте подпись рукой и попробуйте определить, какое слово звучит первым. Это знакомство с контрастом, а не независимый тест.</p>' + clip(s,'contrast-i','ı и i') + '<p class="small">ılık — тёплый; ilik — костный мозг. Эти слова нужны для звуков, заучивать их сегодня не нужно.</p>' + clip(s,'contrast-o','o и ö') + '<p class="small">on — десять; ön — передняя сторона.</p>' + clip(s,'contrast-u','u и ü') + '<p class="small">un — мука; ün — слава. Значения здесь только для осмысленного различения.</p>')
    phrases = [('hello','Merhaba.','Здравствуйте / привет. Подходит и для нейтрального приветствия.'),('name','Benim adım Deniz.','Меня зовут Дениз. Подставьте своё имя вместо Deniz.'),('question-name','Senin adın ne?','Как тебя зовут? Здесь обращение на «ты». Вежливое «Вы» будет позже.'),('pleased','Memnun oldum.','Приятно познакомиться.'),('repeat','Tekrar eder misin?','Повторишь? Пока учим целой фразой, без разбора окончаний.'),('slow','Yavaş, lütfen.','Медленнее, пожалуйста.')]
    text = '<p><strong>Активная порция — 6 выражений.</strong> Начните с первых двух; остальные добавьте во второй подход. `Benim adım …` — готовая конструкция: буквально «моё имя …». Сегодня не требуется выводить все окончания из правил.</p>'
    for id, phrase, meaning in phrases:
        text += clip(s,id,meaning)
    text += '<h3>Диалог-образец</h3><p>В записи один голос читает обе роли. Слушайте фразы по очереди, затем сыграйте роль B сами. Ece — вымышленное имя.</p>' + clip(s,'dialogue','Знакомство · один голос') + '<p><strong>A:</strong> '+tr('Merhaba. Benim adım Deniz. Senin adın ne?')+'<br><strong>B:</strong> '+tr('Benim adım Ece.')+'<br><strong>A:</strong> '+tr('Memnun oldum.')+'</p>'
    body += section('phrases','4. Первые фразы',text)
    body += section('practice','5. Попробуйте сами','''<h3>А. Сначала скажите, потом откройте</h3><ol><li>Поздоровайтесь.</li><li>Назовите своё имя.</li><li>Спросите имя собеседника на «ты».</li><li>Попросите повторить.</li><li>Попросите говорить медленнее.</li></ol>''' + answer('<ol><li>'+tr('Merhaba.')+'</li><li>'+tr('Benim adım …')+'</li><li>'+tr('Senin adın ne?')+'</li><li>'+tr('Tekrar eder misin?')+'</li><li>'+tr('Yavaş, lütfen.')+'</li></ol><p>Имя может быть любым вашим вариантом; многоточие не произносится.</p>') + '<h3>Б. Буквы без ловушек</h3><p>Запишите строчные буквы для I, İ, Ç, Ş, Ö, Ü. Затем объясните вслух, чем c отличается от ç.</p>' + answer('<p lang="tr">ı, i, ç, ş, ö, ü.</p><p>c примерно «дж», ç — «ч». Русские буквы здесь лишь приближение. Обычное английское приведение к нижнему регистру может испортить пару I/ı.</p>') + '<h3>В. Мини-диктант</h3><p>В словаре выше уже есть все три слова. Не открывая расшифровку, послушайте каждое до двух раз и запишите турецкими буквами. После проверки прочитайте своё написание вслух.</p>' + ''.join(clip(s,f'dict-{i}',f'Диктант {i}',True) for i in range(1,4)))
    body += section('speak','6. Поговорите с агентом',speaking_block(SPEAK_1))
    body += section('check','7. Проверка и следующий шаг','''<p>После паузы 2–5 минут без страницы: выполните 5 реплик из задания А, запишите 6 строчных букв из Б и 3 слова диктанта в новом порядке (попросите агента). Всего 14 коротких ответов. Цель — ≥12/14 без подсказки. При меньшем результате повторите трудную часть, а не весь урок подряд.</p>''' + checks(['Могу поздороваться и назвать имя без чтения.','Могу спросить имя и попросить повторить.','Получились 4 самостоятельные реплики с агентом, не больше 2 подсказок.','Проверил(а) результат через сутки; произношение пометил(а) отдельно.']) + '<p>Порог — рабочий критерий курса. Он не означает, что весь алфавит уже освоен. Если завтра трудно различать ı/i или ü/u, продолжайте знакомство и вернитесь к одной паре на 3 минуты.</p>' + return_plan() + '<p><strong>Дальше:</strong> урок 02 — числа 0–10 и заказ чая. Откройте его из каталога курса или папки следующего урока.</p>')
    return scaffold(s,'01','Сначала соединяем буквы со звуками, затем используем их в коротком знакомстве. Читать по-турецки идеально пока не требуется.',body)

def lesson_two():
    s = '02-numbers-and-requests'
    body = section('start','Сегодня вы сможете','''<ul><li>Узнать и назвать числа от 0 до 10.</li><li>Попросить 1–3 чая, уточнить количество и поблагодарить.</li><li>Записать простые числа на слух.</li></ul><p>Нужно после урока 01: Merhaba, lütfen, просьба повторить; знать, что ı и i различаются. Если не помните, начните с двух минут возврата. <strong>На 10 минут:</strong> только 0–3, один заказ и два обмена с агентом. Полный урок делите: сначала 0–5, затем 6–10 и разговор.</p><h3>Возврат без подсказки · 2 минуты</h3><p>Поздоровайтесь, назовите имя, попросите повторить. Напишите строчные I и İ.</p>''' + answer('<p>'+tr('Merhaba. Benim adım … Tekrar eder misin?')+'</p><p lang="tr">I → ı; İ → i.</p>'))
    nums = ['sıfır','bir','iki','üç','dört','beş','altı','yedi','sekiz','dokuz','on']
    body += section('learn','1. Числа: короткими группами','<p>Сегодня исключение из обычной порции слов: целый ряд из 11 чисел. Сначала 0–5, пауза, затем 6–10. Не добавляйте ещё десятки и цены. Цифра — символ, слово — его звучащее название.</p><div class="grid">' + ''.join(f'<div class="card"><div class="number">{i}</div><div class="tr" lang="tr">{word}</div>'+clip(s,f'n-{i}',f'Число {i}')+'</div>' for i,word in enumerate(nums)) + '</div><p class="callout"><strong>Звуки, которые уже встречались:</strong> в '+tr('sıfır')+' и '+tr('altı')+' — ı, не i; в '+tr('üç')+' — ü и ç; в '+tr('dört')+' — ö; в '+tr('beş')+' — ş. Сначала слушайте, затем повторяйте. Для '+tr('bir')+' используйте учебное полное произношение; разговорные сокращения пока не нужны.</p>')
    body += section('listen','2. От порядка к узнаванию',clip(s,'numbers','Ряд 0–10') + '<ol><li>Послушайте ряд и показывайте на цифры.</li><li>Назовите самостоятельно: 2, 5, 0, 8, 3. Проверьте по карточкам.</li><li>Закройте подписи и запишите слова для 1, 4, 6, 10.</li><li>Попросите агента назвать вразброс ещё 5 чисел; покажите или напишите цифру.</li></ol><p>Счёт по порядку легче узнавания числа в разговоре. Для перехода дальше нужны оба умения.</p>')
    svg = '''<figure><svg viewBox="0 0 600 210" role="img" aria-labelledby="tea-title tea-desc"><title id="tea-title">Один чай и два чая</title><desc id="tea-desc">Слева одна чашка с подписью bir çay. Справа две чашки с подписью iki çay. После числа слово çay не получает множественного окончания.</desc><rect x="2" y="2" width="596" height="206" rx="20" fill="#f4e8ca"/><g fill="#a44d21" stroke="#18332f" stroke-width="4"><path d="M100 50 H170 L160 125 H110 Z"/><path d="M360 50 H415 L408 125 H367 Z"/><path d="M450 50 H505 L498 125 H457 Z"/></g><g fill="none" stroke="#18332f" stroke-width="4"><path d="M170 65 Q205 68 168 95 M415 65 Q442 68 413 95 M505 65 Q535 68 503 95"/></g><g font-size="27" fill="#18332f" text-anchor="middle"><text x="135" y="178">bir çay</text><text x="435" y="178">iki çay</text></g></svg><figcaption>После числительного: iki çay — два чая. Здесь не добавляем -lar/-ler.</figcaption></figure>'''
    body += section('phrases','3. Один маленький заказ','<p>Новые слова: '+tr('çay')+' — чай, '+tr('kaç')+' — сколько. Вежливые выражения учим целиком. Новый активный материал помимо чисел — четыре опоры ниже; '+tr('lütfen')+' уже встречалось.</p>' + clip(s,'request','Один чай, пожалуйста.') + '<p>Замените только число: '+tr('İki çay, lütfen.')+' — два чая, пожалуйста; '+tr('Üç çay, lütfen.')+' — три чая, пожалуйста. Не добавляйте множественное окончание после числа.</p>' + svg + clip(s,'question','Сколько чаёв / чашек чая?') + clip(s,'thanks','Спасибо.') + '<p>'+tr('Teşekkür ederim')+' пока не разбираем на части. Не нужно быстро произносить: важно, чтобы собеседник понял.</p><h3>Образец обмена</h3><p>В записи один голос читает обе роли. В реальном разговоре повторный вопрос может понадобиться, если вас не расслышали.</p>' + clip(s,'dialogue','Заказ и уточнение · один голос') + '<p><strong>Клиент:</strong> '+tr('Merhaba. Bir çay, lütfen.')+'<br><strong>Сотрудник:</strong> '+tr('Kaç çay?')+'<br><strong>Клиент:</strong> '+tr('Bir çay, lütfen. Teşekkür ederim.')+'</p>')
    body += section('practice','4. Закройте образец и ответьте','''<h3>А. Ситуация → фраза вслух</h3><ol><li>Попросите два чая.</li><li>Уточните, сколько чашек чая нужно.</li><li>Поблагодарите.</li><li>Не расслышали: попросите повторить.</li></ol>''' + answer('<ol><li>'+tr('İki çay, lütfen.')+'</li><li>'+tr('Kaç çay?')+'</li><li>'+tr('Teşekkür ederim.')+'</li><li>'+tr('Tekrar eder misin?')+'</li></ol>') + '<h3>Б. Мини-диктант: сначала цифры</h3><p>Записи 1 и 2: запишите три цифры в услышанном порядке. После проверки напишите слова с турецкими буквами. Запись 3: запишите просьбу целиком и скажите, сколько чая заказано. Не смотрите в ряд чисел во время попытки.</p>' + clip(s,'dict-1','Диктант 1 · три числа',True) + answer('<p>Цифры: 3, 1, 7. '+tr('üç, bir, yedi')+'.</p>','Сверить цифры 1') + clip(s,'dict-2','Диктант 2 · три числа',True) + answer('<p>Цифры: 4, 0, 10. '+tr('dört, sıfır, on')+'.</p>','Сверить цифры 2') + clip(s,'dict-3','Диктант 3 · просьба',True) + answer('<p>'+tr('İki çay, lütfen.')+' — два чая, пожалуйста. Прописная İ сохраняет точку. Пунктуацию в этом задании отдельно не оцениваем.</p>','Сверить смысл 3') + '<h3>В. Исправьте одну ошибку</h3><p>'+tr('İki çaylar, lütfen.')+'</p>' + answer('<p>'+tr('İki çay, lütfen.')+' После числа в этом сочетании существительное в единственном числе.</p>'))
    body += section('speak','5. Поговорите с агентом',speaking_block(SPEAK_2))
    body += section('check','6. Проверка и повторение','<p>Без страницы: агент называет 5 случайных чисел (вы пишете цифры), вы называете 3 предложенные цифры, затем просите 2 чая и благодарите. Всего 10 ответов. Цель ≥8/10 без подсказки; отдельно выполните 3 заказа со сменой числа и один вопрос '+tr('Kaç çay?')+' с ≤2 подсказками.</p>' + checks(['Узнаю числа вразброс, а не только считаю от нуля.','Могу попросить 1–3 чая и уточнить количество.','После числа говорю çay без -lar.','Есть результат проверки через сутки и заметка о трудностях.']) + '<p>Если 6–10 путаются, оставьте их на завтра, а сегодня заказывайте 1–3. Это разделение нагрузки; полный урок пока остаётся незавершённым. Цель — доступные фразы в разговоре, не скорость декламации ряда.</p>' + return_plan() + '<p><strong>Следующий запланированный урок:</strong> числа 11–100, телефон и простая цена. Он ещё не создан; при заказе следующего урока передайте результат сегодняшней проверки.</p>')
    return scaffold(s,'02','Учимся слышать количество и использовать числа в коротком заказе. Новые окончания сегодня не нужны.',body)

def prepare():
    for slug,items in AUDIO.items():
        folder = LESSONS / slug
        (folder/'audio').mkdir(parents=True,exist_ok=True)
        manifest = {'engine':'Microsoft Edge TTS via edge-tts','generated_date':'2026-11-03','rate':'-10%','kind':'synthetic','native_listener_review':'not performed','clips':[{'id':id,'text':text,'voice':voice,'file':f'{id}.mp3'} for id,text,voice in items]}
        (folder/'audio'/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        script = SPEAK_1 if slug.startswith('01') else SPEAK_2
        (folder/'speaking.md').write_text('# Сценарий разговорного занятия\n\n'+script+'\n',encoding='utf-8')
        (folder/'README.md').write_text(f'# {TITLES[slug]}\n\nСтатус: материал подготовлен; учеником не пройден.\n\nОткройте `index.html` в браузере. Это самостоятельный файл со встроенными аудио и SVG. `speaking.md` — инструкция отдельному голосовому агенту, также есть целиком в HTML. `cards.tsv` — исходник карточек UTF-8, не автоматический планировщик.\n\nMP3 и точные тексты в `audio/manifest.json`; синтез Microsoft Edge TTS, дата 2026-11-03, слуховая проверка носителем не выполнялась. Для изменения контента правьте `tools/build_lessons.py` в корне, пересоздавайте изменённые MP3 через `tools/generate_audio.py`, затем собирайте HTML.\n',encoding='utf-8')
        cards = ([('Поздоровайтесь','Merhaba.','hello'),('Назовите имя (подставьте своё)','Benim adım …','name'),('Как тебя зовут?','Senin adın ne?','question-name'),('Приятно познакомиться','Memnun oldum.','pleased'),('Попросите повторить','Tekrar eder misin?','repeat'),('Медленнее, пожалуйста','Yavaş, lütfen.','slow')] if slug.startswith('01') else [(f'Назовите число {i}',word,f'n-{i}') for i,word in enumerate(['sıfır','bir','iki','üç','dört','beş','altı','yedi','sekiz','dokuz','on'])]+[('Один чай, пожалуйста','Bir çay, lütfen.','request'),('Сколько чаёв?','Kaç çay?','question'),('Спасибо','Teşekkür ederim.','thanks')])
        content='id\tprompt_ru\tanswer_tr\taudio_id\n'+''.join(f'{slug[:2]}-{i:02d}\t{prompt}\t{ans}\t{aud}\n' for i,(prompt,ans,aud) in enumerate(cards,1))
        (folder/'cards.tsv').write_text(content,encoding='utf-8')

def catalog():
    content = '''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Турецкий с нуля → A2</title><style>'''+CSS+'''</style></head><body><main><header><div class="eyebrow">Личный курс · версия 1.0</div><h1>Турецкий.<br>С первого звука.</h1><p class="lead">Понять, услышать, сказать и вспомнить завтра. Два первых урока на пути к повседневному общению.</p><span class="tag">С нуля → A2</span><span class="tag">Для телефона</span><span class="tag">Аудио без сети</span></header><section><h2>Начните с малого</h2><p>Откройте первый урок. Сегодня достаточно 10 минут: послушать одну пару звуков, поздороваться и назвать имя. Каждый урок содержит теорию, задания, ответы и сценарий для отдельного голосового агента.</p><div class="grid">'''
    for slug,title in TITLES.items():
        content += f'<a class="card" href="lessons/{slug}/index.html"><div class="eyebrow">Урок {slug[:2]}</div><h2>{title}</h2><p>30–40 минут, можно в несколько подходов →</p></a>'
    content += '''</div></section><section><h2>Как двигаться дальше</h2><p>Основной режим пока предложен: 30–45 минут 6 дней в неделю. Разговор входит в это время. Урок не равен одному дню: возвращайтесь к нему и проверяйте себя без текста.</p><p>Готовы первые два урока. Следующие создаются по дорожной карте с учётом ваших реальных результатов. Плановый бюджет 180–260 активных часов до A2 — рабочая гипотеза; скорость уточняем после первых 10 часов.</p><p>После занятия сохраните в заметке: дату, минуты, правильные ответы/всего, помощь и трудность. Страницы не сохраняют журнал автоматически.</p></section><section><h2>Документы репозитория</h2><ul><li><a href="README.md">Навигация и использование</a></li><li><a href="docs/STRATEGY.md">Стратегия</a></li><li><a href="docs/ROADMAP.md">Дорожная карта из 48 единиц</a></li><li><a href="docs/RESEARCH.md">Исследования и ограничения</a></li><li><a href="progress/LOG.md">Журнал прогресса</a></li></ul><p class="small">Документы — Markdown для репозитория и агентов; браузер может скачать их как текст. Вся необходимая ученику теория первых двух уроков находится в HTML.</p></section><footer>03.11.2026 · Пока только локальные материалы. Публикация отдельного урока — по вашему запросу. Озвучка синтетическая, не проверена носителем.</footer></main></body></html>'''
    (ROOT/'index.html').write_text(content,encoding='utf-8')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--prepare',action='store_true')
    args=parser.parse_args()
    prepare()
    if args.prepare:
        print('Manifests, cards and speaking instructions prepared.')
        return
    for slug,fn in zip(AUDIO,[lesson_one,lesson_two]):
        (LESSONS/slug/'index.html').write_text(fn(),encoding='utf-8')
        print(f'Built {slug}')
    catalog()

if __name__=='__main__': main()
