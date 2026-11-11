from pathlib import Path
import json
import sys
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
BASE = 'http://127.0.0.1:8765/'
PROJECT = int(sys.argv[1]) if len(sys.argv) > 1 else 1
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
    page = browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
    errors=[]
    page.on('pageerror',lambda error: errors.append(str(error)))
    page.goto(BASE,wait_until='networkidle')
    page.screenshot(path=str(ROOT / f'qa/project{PROJECT}-home.png'))
    page.locator('.deck-card').nth(PROJECT-1).click()
    page.wait_for_url(f'**/project-{PROJECT}.html')
    assert page.locator('header').count()==1
    assert page.locator('nav,footer,button,select,dialog').count()==0
    assert page.locator('.home-link').get_attribute('href')=='index.html#work'
    assert page.locator('main').inner_text().strip()==''
    imgs=page.locator('main>img')
    assert imgs.count()==6
    for i,img in enumerate(imgs.all()):
        img.scroll_into_view_if_needed()
        img.evaluate('(img)=>img.decode()')
        expected=[2888,1032] if PROJECT==1 and i==1 else [2880,1024]
        assert img.evaluate('(img)=>[img.naturalWidth,img.naturalHeight]')==expected
    for width in [1920,1440,768,390,320]:
        page.set_viewport_size({'width':width,'height':900})
        page.evaluate('window.scrollTo(0,0)')
        assert page.evaluate('document.documentElement.scrollWidth===document.documentElement.clientWidth')
        rects=[img.bounding_box() for img in imgs.all()]
        assert rects[0]['y'] >= page.locator('header').bounding_box()['height']+24
        for i,r in enumerate(rects):
            assert r['x']>=12 and r['width']<page.evaluate('document.documentElement.clientWidth')
            if i: assert r['y']-rects[i-1]['y']-rects[i-1]['height']>=23.9
        if width==1440: page.screenshot(path=str(ROOT/f'qa/project{PROJECT}-dark-scroll.png'))
    page.set_viewport_size({'width':1440,'height':900})
    page.evaluate('window.scrollTo(0,0)')
    page.wait_for_timeout(100)
    assert page.locator('.reading-progress').get_attribute('aria-valuenow')=='0'
    page.evaluate('window.scrollTo(0,document.documentElement.scrollHeight)')
    page.wait_for_timeout(100)
    assert page.locator('.reading-progress').get_attribute('aria-valuenow')=='100'
    assert page.locator('header').bounding_box()['y']==0
    assert page.locator('.ambient-background').evaluate('(el)=>getComputedStyle(el,"::before").animationName')=='none'
    page.emulate_media(reduced_motion='no-preference')
    assert page.locator('.ambient-background').evaluate('(el)=>getComputedStyle(el,"::before").animationName')=='ambient-drift'
    page.locator('.home-link').click()
    page.wait_for_url('**/index.html#work')
    assert not errors,errors
    print('Verified: original images, responsive spacing, fixed Home bar, 0-100% reading progress, animated background and reduced-motion support.')
    browser.close()
