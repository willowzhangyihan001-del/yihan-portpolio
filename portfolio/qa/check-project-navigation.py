from pathlib import Path
from playwright.sync_api import sync_playwright

BASE='http://127.0.0.1:8765/'
OUT=Path(__file__).resolve().parent

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[]
    navigations=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r:navigations.append(r.url) if r.is_navigation_request() and r.frame==page.main_frame else None)
    page.goto(BASE,wait_until='networkidle')
    page.evaluate('window.__galleryDocument={work:document.querySelector("#work"),origin:performance.timeOrigin}')
    page.locator('#work').evaluate('(e)=>e.scrollIntoView({behavior:"instant"})')
    page.wait_for_selector('#work.is-settled',timeout=6000)

    def assert_preserved():
        assert page.evaluate('window.__galleryDocument.work===document.querySelector("#work") && window.__galleryDocument.origin===performance.timeOrigin')
        assert page.locator('.project-preview').count()==0
        assert page.locator('#work').evaluate('(e)=>e.classList.contains("is-settled")')
        assert page.locator('.card-mount').evaluate_all('es=>es.every(e=>getComputedStyle(e).opacity==="1" && getComputedStyle(e).animationName==="none")')
        page.wait_for_function('Math.abs(document.querySelector("#work").getBoundingClientRect().top)<2')
        assert not page.locator('body>main').evaluate('(e)=>e.inert')

    for project in range(1,5):
        page.locator('.hanging-card').nth(project-1).click()
        page.wait_for_url(f'**/project-{project}.html')
        view=page.frame_locator('.project-preview iframe')
        view.locator('.home-link').wait_for()
        assert view.locator('.project-board').count()==6
        assert page.locator('body>main').evaluate('(e)=>e.inert')
        assert page.evaluate('window.__galleryDocument.origin===performance.timeOrigin')
        view.locator('body').evaluate('()=>window.scrollTo(0,document.documentElement.scrollHeight)')
        view.locator('.home-link').click()
        page.wait_for_url('**/index.html#work')
        page.wait_for_selector('.project-preview',state='detached')
        assert_preserved()
        assert len(navigations)==1,navigations
        assert len(page.frames)==1
        print(f'PASS: Project {project} Home keeps the same gallery DOM and navigation count, returns directly to all four visible cards')
    page.screenshot(path=str(OUT/'project-return-preserved-gallery.png'))

    page.locator('.hanging-card').nth(1).hover()
    assert page.locator('.card-swing').nth(1).evaluate('(e)=>e.getAnimations().some(a=>a.playState==="running")')
    page.locator('.hanging-card').nth(1).click()
    page.wait_for_url('**/project-2.html')
    page.go_back(wait_until='domcontentloaded')
    assert_preserved()
    page.go_forward(wait_until='domcontentloaded')
    page.wait_for_selector('.project-preview')
    page.frame_locator('.project-preview iframe').locator('.home-link').click()
    page.wait_for_selector('.project-preview',state='detached')
    assert_preserved()
    assert len(navigations)==1,navigations
    print('PASS: hover, browser Back and Forward preserve the homepage without a document request')

    page.locator('.hanging-card').nth(2).focus()
    page.keyboard.press('Enter')
    view=page.frame_locator('.project-preview iframe')
    view.locator('.home-link').wait_for()
    page.wait_for_function('document.querySelector(".project-preview iframe").contentDocument.activeElement.matches(".home-link")')
    page.keyboard.press('Enter')
    page.wait_for_selector('.project-preview',state='detached')
    assert page.locator('.hanging-card').nth(2).evaluate('(e)=>e===document.activeElement')
    assert_preserved()
    print('PASS: keyboard focus enters the project and returns to the same project card')

    old_origin=page.evaluate('performance.timeOrigin')
    page.reload(wait_until='networkidle')
    page.wait_for_url('**/index.html#home')
    assert page.evaluate('scrollY')<2
    assert page.evaluate('performance.timeOrigin')!=old_origin
    assert not page.locator('#work').evaluate('(e)=>e.classList.contains("is-visible")')
    page.locator('#work').evaluate('(e)=>e.scrollIntoView({behavior:"instant"})')
    page.wait_for_selector('#work.is-visible')
    assert page.locator('.card-mount').first.evaluate('(e)=>getComputedStyle(e).opacity')=='0'
    page.wait_for_selector('#work.is-settled',timeout=6000)
    page.locator('.hanging-card').nth(3).click()
    page.wait_for_url('**/project-4.html')
    page.frame_locator('.project-preview iframe').locator('.home-link').wait_for()
    page.reload(wait_until='networkidle')
    page.wait_for_url('**/index.html#home')
    assert page.evaluate('scrollY')<2
    assert page.locator('.project-preview').count()==0
    assert not page.locator('#work').evaluate('(e)=>e.classList.contains("is-visible")')
    print('PASS: browser refresh from either gallery or project goes to the hero and resets the entrance')
    assert not errors,errors
    page.close()

    mobile=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce')
    page=mobile.new_page()
    mobile_navigations=[]
    page.on('request',lambda r:mobile_navigations.append(r.url) if r.is_navigation_request() and r.frame==page.main_frame else None)
    page.goto(BASE+'#work',wait_until='networkidle')
    for project in range(1,5):
        page.locator('.hanging-card').nth(project-1).tap()
        page.wait_for_url(f'**/project-{project}.html')
        page.frame_locator('.project-preview iframe').locator('.home-link').tap()
        page.wait_for_url('**/index.html#work')
        page.wait_for_selector('.project-preview',state='detached')
        page.wait_for_function('Math.abs(document.querySelector("#work").getBoundingClientRect().top)<2')
        assert page.locator('.card-mount').evaluate_all('es=>es.every(e=>getComputedStyle(e).opacity==="1")')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    assert len(mobile_navigations)==1,mobile_navigations
    page.screenshot(path=str(OUT/'project-return-preserved-mobile.png'))
    print('PASS: all four mobile touch previews return without reloading or replaying the gallery')
    browser.close()
