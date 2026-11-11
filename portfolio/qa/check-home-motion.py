from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8765/'
OUT = Path(__file__).resolve().parent

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
    page = browser.new_page(viewport={'width': 1440, 'height': 1000})
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(BASE, wait_until='networkidle')
    page.wait_for_selector('.hero-motion-ready')
    page.wait_for_timeout(1800)
    assert page.locator('h1').get_attribute('aria-label') == 'Yihan Zhang'
    assert page.locator('.hero-title-char').count() == 10
    assert page.locator('.hero-title-char').evaluate_all('es=>es.every(e=>getComputedStyle(e).opacity==="1")')
    assert page.locator('.hero-link-arrow svg').count() == 3
    assert page.locator('.hero-sparkle').count() == 2
    page.screenshot(path=str(OUT / 'home-motion-desktop.png'))

    page.mouse.move(1300, 280)
    page.wait_for_timeout(850)
    x = page.locator('#home').evaluate('(e)=>parseFloat(e.style.getPropertyValue("--hero-pointer-x"))')
    assert x > 4, x
    page.locator('#home').dispatch_event('pointerleave')
    page.wait_for_timeout(1400)
    assert abs(page.locator('#home').evaluate('(e)=>parseFloat(e.style.getPropertyValue("--hero-pointer-x"))')) < .1
    page.locator('.hero-title-char').nth(1).hover()
    assert page.locator('.hero-title-char').nth(1).evaluate('(e)=>e.getAnimations().some(a=>a.playState==="running")')
    page.locator('.about-link').hover()
    page.wait_for_timeout(500)
    page.screenshot(path=str(OUT / 'home-motion-hover.png'))
    page.locator('.theme').click()
    page.mouse.move(20, 980)
    page.wait_for_timeout(1000)
    page.screenshot(path=str(OUT / 'home-motion-dark.png'))
    assert page.locator('.hero-dark-decoration').evaluate('(e)=>getComputedStyle(e).display') == 'block'
    print('PASS: title entrance and hover, pointer movement and reset, light/dark collage')

    page.locator('.work-link').click()
    page.wait_for_function('document.querySelector("#home").classList.contains("hero-is-away")')
    assert page.locator('.hero-collage-float').evaluate('(e)=>getComputedStyle(e).animationPlayState') == 'paused'
    page.wait_for_timeout(3100)
    assert page.locator('.hanging-card').evaluate_all('es=>es.every(e=>getComputedStyle(e).visibility==="visible")')
    page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
    page.wait_for_function('scrollY < 2')
    page.wait_for_function('!document.querySelector("#home").classList.contains("hero-is-away")')
    page.locator('.about-link').click()
    page.wait_for_function('location.hash==="#about" && scrollY>innerHeight')
    page.goto(BASE, wait_until='networkidle')
    page.locator('.contact-link').click()
    page.wait_for_function('location.hash==="#contact" && document.querySelector("#contact").getBoundingClientRect().top<100')
    print('PASS: all home navigation, offscreen animation pause, project cards remain visible')

    page.emulate_media(reduced_motion='reduce')
    page.goto(BASE, wait_until='networkidle')
    for selector in ['.hero-title-char', '.hero-collage-enter', '.hero-collage-float', '.hero-link-arrow', '.hero-sparkle', '.hero-bottom > a']:
        assert page.locator(selector).first.evaluate('(e)=>getComputedStyle(e).animationName') == 'none', selector
    assert page.locator('.hero-title-char').evaluate_all('es=>es.every(e=>getComputedStyle(e).opacity==="1")')
    page.mouse.move(1300, 280)
    page.wait_for_timeout(100)
    assert page.locator('.hero-artwork-wrap').evaluate('(e)=>getComputedStyle(e).transform') == 'none'
    print('PASS: reduced motion leaves all content visible and static')

    for width, height in [(320, 720), (390, 844), (768, 1024), (2048, 1055)]:
        page.set_viewport_size({'width': width, 'height': height})
        page.goto(BASE, wait_until='networkidle')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), width
        for link in page.locator('.hero-stage > a').all():
            box = link.bounding_box()
            assert box['x'] >= -1 and box['x'] + box['width'] <= width + 1, (width, box)
        page.screenshot(path=str(OUT / f'home-motion-{width}.png'))
        print(f'PASS: {width}px, no horizontal overflow; home navigation within viewport')

    mobile = browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    mobile_page = mobile.new_page()
    mobile_page.goto(BASE, wait_until='networkidle')
    mobile_page.wait_for_timeout(1800)
    mobile_page.locator('.contact-link').tap()
    mobile_page.wait_for_function('location.hash==="#contact" && document.querySelector("#contact").getBoundingClientRect().top<100')
    print('PASS: mobile touch navigation')

    fallback = browser.new_page(java_script_enabled=False)
    fallback.goto(BASE, wait_until='networkidle')
    assert fallback.locator('h1').inner_text() == 'Yihan Zhang'
    assert fallback.locator('.hero-artwork').evaluate('(e)=>e.complete && e.naturalWidth>0')
    assert fallback.locator('.hero-stage > a').count() == 3
    assert errors == [], errors
    print('PASS: static fallback and no browser errors')
    browser.close()
