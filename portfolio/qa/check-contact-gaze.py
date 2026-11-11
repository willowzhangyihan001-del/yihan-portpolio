from pathlib import Path
import math
from playwright.sync_api import sync_playwright

BASE='http://127.0.0.1:8765/'
OUT=Path(__file__).resolve().parent

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(BASE+'#contact',wait_until='networkidle')
    page.wait_for_selector('.contact-artwork.gaze-ready')
    page.wait_for_timeout(400)
    assert page.locator('.contact-pupil').count()==4
    assert page.locator('.contact-bubble').inner_text()=='Shall we talk?'
    assert page.locator('.contact-bubble').evaluate('(e)=>getComputedStyle(e).visibility')=='visible'
    assert page.locator('.contact-cat-canvas>img').evaluate('(e)=>getComputedStyle(e).opacity')=='0'
    assert page.locator('.contact-gaze').evaluate('(e)=>getComputedStyle(e).opacity')=='1'

    def gaze():
        return page.locator('.contact-gaze').evaluate('''svg=>{
            const bubble=document.querySelector('.contact-bubble').getBoundingClientRect();
            const target=new DOMPoint(bubble.x+bubble.width/2,bubble.y+bubble.height/2).matrixTransform(svg.getScreenCTM().inverse());
            return [...svg.querySelectorAll('.contact-pupil')].map(e=>{
                const matrix=e.transform.baseVal.consolidate().matrix;
                return {x:matrix.e,y:matrix.f,dx:target.x-e.cx.baseVal.value,dy:target.y-e.cy.baseVal.value};
            });
        }''')

    art=page.locator('.contact-cat-canvas').bounding_box()
    samples=[]
    for label,px,py in [('left',.08,.65),('right',.95,.65),('up',.6,.04),('down',.6,.97)]:
        page.mouse.move(art['x']+art['width']*px,art['y']+art['height']*py)
        page.wait_for_timeout(650)
        assert page.locator('#contact').evaluate('(e)=>getComputedStyle(e).cursor')=='none'
        samples.append(gaze())
        for item,(rx,ry) in zip(samples[-1],[(11,8),(11,8),(7,5),(4.5,4)]):
            assert (item['x']/rx)**2+(item['y']/ry)**2<=1.002,item
            assert item['x']*item['dx']>=-.01 and item['y']*item['dy']>=-.01,item
        page.screenshot(path=str(OUT/f'contact-gaze-{label}.png'))
    assert samples[0][0]['x']<samples[1][0]['x']
    page.mouse.move(500,400)
    page.wait_for_timeout(650)
    assert page.locator('#contact').evaluate('(e)=>getComputedStyle(e).cursor')=='none'
    assert gaze()[0]['x']<0
    print('PASS: all four pupils track the visible bubble in four directions, bounded to their original faces')

    page.locator('.contact-email').hover()
    page.wait_for_timeout(800)
    assert not page.locator('#contact').evaluate('(e)=>e.classList.contains("has-bubble-cursor")')
    assert page.locator('.contact-email').evaluate('(e)=>getComputedStyle(e).cursor')=='pointer'
    page.locator('.theme').click()
    page.wait_for_timeout(1000)
    assert page.locator('.contact-cat-drawing').evaluate('(e)=>getComputedStyle(e).filter')=='invert(1)'
    page.screenshot(path=str(OUT/'contact-gaze-dark.png'))
    page.locator('.theme').click()
    page.locator('.contact-top').click()
    page.wait_for_function('scrollY<2')
    assert page.locator('.contact-bubble').evaluate('(e)=>getComputedStyle(e).visibility')=='hidden'
    assert page.locator('#contact').evaluate('(e)=>getComputedStyle(e).cursor')!='none'
    print('PASS: normal cursor on links and outside contact, dark mode, Back to top')

    page.emulate_media(reduced_motion='reduce')
    for width,height in [(320,568),(390,844),(768,1024),(844,390),(1920,1080),(2560,1440)]:
        page.set_viewport_size({'width':width,'height':height})
        page.locator('#contact').evaluate('(e)=>e.scrollIntoView({behavior:"instant"})')
        page.mouse.move(2,2)
        page.wait_for_timeout(100)
        bubble=page.locator('.contact-bubble').bounding_box()
        assert bubble['x']>=0 and bubble['y']>=0 and bubble['x']+bubble['width']<=width and bubble['y']+bubble['height']<=height,(width,bubble)
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        contact=page.locator('#contact').bounding_box()
        for selector in ['.contact-name','.contact-message','.contact-artwork','.contact-footer']:
            box=page.locator(selector).bounding_box()
            assert box['x']>=-1 and box['x']+box['width']<=width+1,(width,selector,box)
            assert box['y']>=contact['y'] and box['y']+box['height']<=contact['y']+contact['height']+1,(width,selector,box,contact)
        if width in [320,390,1920]:page.screenshot(path=str(OUT/f'contact-gaze-{width}.png'))
        before=page.locator('.contact-bubble').get_attribute('style')
        page.wait_for_timeout(100)
        assert before==page.locator('.contact-bubble').get_attribute('style')
    print('PASS: 320-2560px and short landscape; reduced motion stops idle drift')

    mobile=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
    mobile_page=mobile.new_page()
    mobile_page.goto(BASE+'#contact',wait_until='networkidle')
    mobile_page.wait_for_selector('.gaze-ready')
    mobile_page.wait_for_timeout(200)
    assert mobile_page.locator('.contact-bubble').evaluate('(e)=>getComputedStyle(e).visibility')=='visible'
    assert not mobile_page.locator('#contact').evaluate('(e)=>e.classList.contains("has-bubble-cursor")')
    mobile_page.screenshot(path=str(OUT/'contact-gaze-touch.png'))
    mobile_page.locator('.theme').tap()
    assert mobile_page.locator('.theme').get_attribute('aria-pressed')=='true'
    print('PASS: mobile floating bubble, original touch scrolling and theme control')
    assert not errors,errors
    browser.close()
