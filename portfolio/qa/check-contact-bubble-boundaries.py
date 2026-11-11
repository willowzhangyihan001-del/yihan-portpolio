from pathlib import Path
from playwright.sync_api import sync_playwright

OUT=Path(__file__).resolve().parent

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1:8765/#contact',wait_until='networkidle')
    page.wait_for_selector('.gaze-ready')
    page.wait_for_timeout(150)
    bubble=page.locator('.contact-bubble')
    assert bubble.inner_text()=='Shall we talk?'

    def assert_clear():
        frame=page.evaluate('''()=>{
            const content=document.querySelector('.contact-main').getBoundingClientRect();
            const heading=document.querySelector('.contact-topline').getBoundingClientRect();
            const footer=document.querySelector('.contact-footer').getBoundingClientRect();
            const theme=document.querySelector('.theme').getBoundingClientRect();
            const bubble=document.querySelector('.contact-bubble').getBoundingClientRect();
            return {bubble:bubble.toJSON(),left:content.left,right:content.right,
              top:Math.max(content.top,heading.bottom+12,8),
              bottom:Math.min(content.bottom,footer.top-12,theme.top-12,innerHeight-8)};
        }''')
        rect=frame['bubble']
        assert rect['left']>=frame['left'] and rect['right']<=frame['right'],frame
        assert rect['top']>=frame['top'] and rect['bottom']<=frame['bottom'],frame
        collisions=page.evaluate('''() => {
            const bubble=document.querySelector('.contact-bubble').getBoundingClientRect();
            const obstacles=[];
            for(const selector of ['.contact-kicker','.contact-name','.contact-note','.contact-footer>span']){
                const range=document.createRange();
                range.selectNodeContents(document.querySelector(selector));
                obstacles.push(...range.getClientRects());
            }
            for(const selector of ['.contact-email','.contact-top','.theme'])obstacles.push(document.querySelector(selector).getBoundingClientRect());
            return obstacles.filter(r=>Math.min(bubble.right,r.right)-Math.max(bubble.left,r.left)>.25 && Math.min(bubble.bottom,r.bottom)-Math.max(bubble.top,r.top)>.25).map(r=>r.toJSON());
        }''')
        assert not collisions,collisions

    # Crossing a title in a single pointer move must stop before its text.
    page.mouse.move(1320,245)
    page.wait_for_timeout(800)
    right=bubble.bounding_box()
    page.mouse.move(80,245)
    page.wait_for_timeout(1100)
    title=page.locator('.contact-name').evaluate('''e=>{const r=document.createRange();r.selectNodeContents(e);return r.getBoundingClientRect().toJSON()}''')
    stopped=bubble.bounding_box()
    assert stopped['x']>=title['right']+5,(stopped,title)
    assert_clear()
    page.screenshot(path=str(OUT/'contact-bubble-title-edge.png'))

    # Free space above, below and on either side of the cats remains reachable.
    for px,py in [(740,80),(1320,450),(1320,840),(650,840),(650,450),(120,450),(620,200)]:
        page.mouse.move(px,py,steps=12)
        page.wait_for_timeout(500)
        assert_clear()
    assert right['x']-stopped['x']>500
    print('PASS: wide travel, high-speed text collision and clear paths around the page')

    # Stopping, leaving, tabbing and window blur all preserve the settled location.
    page.wait_for_timeout(800)
    held=bubble.get_attribute('style')
    page.wait_for_timeout(450)
    assert bubble.get_attribute('style')==held
    page.locator('#contact').dispatch_event('pointerleave')
    page.wait_for_timeout(500)
    assert bubble.get_attribute('style')==held
    page.evaluate('window.dispatchEvent(new Event("blur"))')
    page.wait_for_timeout(150)
    assert bubble.get_attribute('style')==held
    page.keyboard.press('Tab')
    page.wait_for_timeout(150)
    assert bubble.get_attribute('style')==held
    print('PASS: no snap back or idle drift after stopping, leaving, blur or keyboard focus')

    page.locator('.contact-email').hover()
    page.wait_for_timeout(900)
    assert page.locator('.contact-email').evaluate('(e)=>getComputedStyle(e).cursor')=='pointer'
    assert_clear()
    page.locator('.theme').click()
    page.wait_for_timeout(900)
    assert_clear()
    page.screenshot(path=str(OUT/'contact-bubble-boundaries-dark.png'))
    print('PASS: email remains clickable and text remains clear in dark mode')

    # The whole footer strip and both side gutters are excluded, even where blank.
    for label,px,py in [('bottom-left',15,985),('bottom-middle',720,985),('bottom-right',1420,985),('right',1430,500),('top',720,8),('left',8,500)]:
        page.mouse.move(px,py,steps=10)
        page.wait_for_timeout(550)
        assert_clear()
        if label=='bottom-middle':
            page.screenshot(path=str(OUT/'contact-bubble-footer-limit.png'))
    print('PASS: the full paper outline stops above navigation, below the title and inside both content edges')

    page.emulate_media(reduced_motion='reduce')
    for width,height in [(320,568),(390,844),(768,1024),(844,390),(1920,1080),(2560,1440)]:
        page.set_viewport_size({'width':width,'height':height})
        page.locator('#contact').evaluate('(e)=>e.scrollIntoView({behavior:"instant"})')
        page.wait_for_timeout(120)
        assert_clear()
        for px,py in [(2,height/2),(width-2,height/2),(width/2,height-2),(width/2,2)]:
            page.mouse.move(px,py)
            page.wait_for_timeout(30)
            assert_clear()
        rect=bubble.bounding_box()
        assert rect['x']>=0 and rect['y']>=0 and rect['x']+rect['width']<=width and rect['y']+rect['height']<=height,(width,rect)
    assert not errors,errors
    print('PASS: text avoidance and viewport bounds at 320-2560px and in landscape')
    browser.close()
