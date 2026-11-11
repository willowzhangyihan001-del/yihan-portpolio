from pathlib import Path
import json
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8765/'
OUT = Path(__file__).resolve().parent
SIZES = [(320,568),(390,844),(768,1024),(844,390),(1024,768),(1366,768),(1920,1080),(2560,1440)]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
    page = browser.new_page(reduced_motion='reduce')
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(BASE, wait_until='networkidle')
    assert page.locator('.avatar, body > header').count() == 0
    assert page.locator('.theme').get_attribute('aria-pressed') == 'false'
    page.locator('.theme').click()
    assert page.locator('.theme').get_attribute('aria-pressed') == 'true'
    page.locator('.theme').click()

    home_results = []
    for width,height in SIZES:
        page.set_viewport_size({'width':width,'height':height})
        page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
        page.wait_for_timeout(80)
        result = page.evaluate('''() => {
            const rect = s => document.querySelector(s).getBoundingClientRect().toJSON();
            const work = rect('#work');
            return {width:innerWidth,docWidth:document.documentElement.scrollWidth,
              hero:rect('#home'),title:rect('#home h1'),art:rect('.hero-artwork-wrap'),
              links:[...document.querySelectorAll('.hero-stage > a')].map(e=>e.getBoundingClientRect().toJSON()),
              work,photos:[...document.querySelectorAll('.hanging-photo')].map(e=>e.getBoundingClientRect().toJSON()),
              aboutOverflow:[...document.querySelectorAll('#about *')].filter(e=>{const r=e.getBoundingClientRect();return r.width && (r.left < -1 || r.right > innerWidth+1)}).map(e=>e.className)};
        }''')
        assert result['docWidth'] <= width, result
        assert result['title']['left'] >= 0 and result['title']['right'] <= width, result
        assert result['art']['bottom'] < result['hero']['bottom']-30, result
        assert not result['aboutOverflow'], result
        for box in result['links']:
            assert box['left']>=-1 and box['right']<=width+1, (width,box)
            assert box['top']>=result['title']['bottom'] and box['bottom']<result['hero']['bottom']-25, (width,box)
        for box in result['photos']:
            assert box['left']>=-1 and box['right']<=width+1, (width,box)
            assert box['top']>=result['work']['top'] and box['bottom']<=result['work']['bottom'], (width,box,result['work'])
        if width in [320,390,768,1366,2560]:
            page.screenshot(path=str(OUT/f'responsive-home-{width}.png'))
        if width in [390,768,1366]:
            for img in page.locator('#work img').all():
                img.scroll_into_view_if_needed()
                img.evaluate('(e)=>e.decode()')
            page.locator('#work').screenshot(path=str(OUT/f'responsive-work-{width}.png'))
            page.locator('#about').screenshot(path=str(OUT/f'responsive-about-{width}.png'))
        page.locator('#contact').evaluate('(e)=>e.scrollIntoView({behavior:"instant"})')
        contact = page.locator('#contact').bounding_box()
        for selector in ['.contact-name','.contact-message','.contact-artwork','.contact-footer']:
            box = page.locator(selector).bounding_box()
            assert box['x']>=-1 and box['x']+box['width']<=width+1,(width,selector,box)
            assert box['y']>=contact['y'] and box['y']+box['height']<=contact['y']+contact['height']+1,(width,selector,box,contact)
        theme=page.locator('.theme').bounding_box()
        back=page.locator('.contact-top').bounding_box()
        assert back['x']+back['width']<theme['x'] or back['y']+back['height']<theme['y'],(width,theme,back)
        home_results.append(result)
        print(f'PASS home {width}x{height}: no removed UI, overflow, cropped cards, or footer collisions')

    for project in range(1,5):
        page.goto(f'{BASE}project-{project}.html',wait_until='networkidle')
        boards=page.locator('.project-board')
        assert boards.count()==6
        for board in boards.all():
            board.scroll_into_view_if_needed()
            board.locator('img').evaluate('(e)=>e.decode()')
        for width,height in SIZES:
            page.set_viewport_size({'width':width,'height':height})
            page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
            page.wait_for_timeout(50)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), (project,width)
            header=page.locator('.project-header').bounding_box()
            previous=None
            for i,board in enumerate(boards.all()):
                box=board.bounding_box()
                image=board.locator('img')
                natural=image.evaluate('(e)=>({w:e.naturalWidth,h:e.naturalHeight})')
                assert abs(box['width']/box['height']-natural['w']/natural['h'])<.003,(project,width,i,box,natural)
                assert box['x']>=11 and box['x']+box['width']<=width-11,(project,width,box)
                assert box['width']<=1800.1,(project,width,box)
                if previous:assert box['y']-previous['y']-previous['height']>=19.9
                else:assert box['y']>=header['height']+19.9
                assert board.get_attribute('href')==image.get_attribute('src')
                previous=box
            if width in [390,1366,2560]:
                page.screenshot(path=str(OUT/f'responsive-project-{project}-{width}.png'))
        page.evaluate('window.scrollTo(0,document.documentElement.scrollHeight)')
        page.wait_for_timeout(100)
        assert page.locator('.reading-progress').get_attribute('aria-valuenow')=='100'
        page.evaluate('window.scrollTo(0,0)')
        page.wait_for_timeout(100)
        assert page.locator('.reading-progress').get_attribute('aria-valuenow')=='0'
        with page.expect_popup() as popup_info:
            boards.first.click()
        popup=popup_info.value
        popup.wait_for_load_state()
        assert popup.url.endswith(boards.first.get_attribute('href'))
        popup.close()
        page.locator('.home-link').click()
        page.wait_for_url('**/index.html#work')
        print(f'PASS project {project}: six original board ratios at eight sizes, size cap, full-size view, progress and Home link')

    # Check entrance behavior in a short landscape viewport, where the old
    # intersection threshold could never be reached by the two-row gallery.
    page.emulate_media(reduced_motion='no-preference')
    page.set_viewport_size({'width':812,'height':320})
    page.goto(BASE,wait_until='networkidle')
    page.locator('#work').evaluate('(e)=>e.scrollIntoView({behavior:"instant"})')
    page.wait_for_timeout(3300)
    assert page.locator('.card-mount').evaluate_all('es=>es.every(e=>getComputedStyle(e).opacity==="1")')
    assert page.locator('.hanging-card').evaluate_all('es=>es.every(e=>getComputedStyle(e).visibility==="visible")')
    assert errors==[],errors
    (OUT/'responsive-layout-results.json').write_text(json.dumps({'home':home_results,'errors':errors},indent=2),encoding='utf-8')
    print('PASS: short landscape entrance and no browser errors')
    browser.close()
