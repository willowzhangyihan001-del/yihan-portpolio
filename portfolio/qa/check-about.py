from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa'
BASE = 'http://127.0.0.1:8765'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
    page = context.new_page()
    errors = []
    missing = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('response', lambda response: missing.append(response.url) if response.status >= 400 and response.url.startswith(BASE) else None)
    page.goto(BASE + '/#about', wait_until='networkidle')
    page.evaluate('document.fonts.ready')
    page.locator('.about-portrait img').evaluate('(img) => img.decode()')
    page.locator('#about').evaluate('(el) => el.scrollIntoView()')
    page.screenshot(path=str(OUT / 'about-desktop.png'))
    page.locator('#about').screenshot(path=str(OUT / 'about-desktop-full.png'))

    assert page.locator('#about').get_attribute('lang') == 'en'
    assert page.locator('.resume-section').count() == 6
    assert page.locator('.resume-entry').count() == 8
    assert page.locator('.award-list li').count() == 6
    assert page.locator('.resume-entry li').count() == 19
    assert page.locator('.about-portrait img').evaluate('(img) => img.naturalWidth') == 4584

    # Verify the actual rendered typeface, not only the declared CSS family.
    cdp = context.new_cdp_session(page)
    cdp.send('DOM.enable')
    cdp.send('CSS.enable')
    root = cdp.send('DOM.getDocument')['root']['nodeId']
    fonts = {}
    for selector in ['.about-statement > p', '#about-title', '#education h4', '.resume-entry li']:
        node = cdp.send('DOM.querySelector', {'nodeId': root, 'selector': selector})['nodeId']
        used = cdp.send('CSS.getPlatformFontsForNode', {'nodeId': node})['fonts']
        fonts[selector] = used
        if selector == '.about-statement > p':
            home_node = cdp.send('DOM.querySelector', {'nodeId': root, 'selector': '.about-link'})['nodeId']
            home_fonts = cdp.send('CSS.getPlatformFontsForNode', {'nodeId': home_node})['fonts']
            # Use the same font as the homepage, including its existing offline fallback.
            assert {f['familyName'] for f in used} <= {f['familyName'] for f in home_fonts}, (used, home_fonts)
        else:
            assert all('Outfit' in f['familyName'] and f['isCustomFont'] for f in used), (selector, used)

    original_copy = page.locator('#about').inner_text()
    page.locator('#language').click()
    assert page.locator('#about').inner_text() == original_copy, 'Language toggle changed resume text'
    assert page.locator('#about').get_attribute('lang') == 'en'
    page.locator('#language').click()

    page.locator('.resume-nav a[href="#research"]').click()
    assert page.url.endswith('#research')
    assert page.locator('#research').evaluate('(el) => {const r=el.getBoundingClientRect();return r.top>=0 && r.top<300}')
    page.wait_for_timeout(100)
    assert page.locator('.resume-nav a[href="#research"]').get_attribute('aria-current') == 'location'
    page.screenshot(path=str(OUT / 'about-research.png'))

    with page.expect_download() as download:
        page.locator('.resume-download').click()
    assert download.value.suggested_filename == 'Yihan-Zhang-Resume.png'
    assert page.request.get(BASE + '/assets/yihan-resume.png').status == 200

    page.locator('.theme').click()
    page.locator('#about').evaluate('(el) => el.scrollIntoView()')
    page.wait_for_timeout(100)
    page.screenshot(path=str(OUT / 'about-pink.png'))
    page.locator('.theme').click()

    widths = {}
    for width in [1280, 1024, 768, 390, 320]:
        page.set_viewport_size({'width': width, 'height': 900})
        page.locator('#about').evaluate('(el) => el.scrollIntoView()')
        measurements = page.evaluate('''() => ({viewport: innerWidth, width: document.documentElement.scrollWidth,
          overflow: [...document.querySelectorAll('#about *')].filter(el => {
            const r=el.getBoundingClientRect(); return r.width && (r.right > innerWidth + 1 || r.left < -1);
          }).map(el => ({tag: el.tagName, cls: el.className, text: el.textContent.slice(0,60)}))})''')
        widths[width] = measurements
        assert not measurements['overflow'], measurements
        assert measurements['width'] <= width, measurements
        if width in [390, 768]:
            page.screenshot(path=str(OUT / f'about-{width}.png'))
        if width == 390:
            page.locator('#education').evaluate('(el) => el.scrollIntoView()')
            page.screenshot(path=str(OUT / 'about-mobile-education.png'))

    assert not errors, errors
    assert not missing, missing
    report = {'fonts': fonts, 'widths': widths, 'console_errors': errors, 'missing_local_assets': missing,
              'checks': ['English text unchanged by language toggle', 'all six sections present',
                         'all 19 experience bullets present', 'navigation and active state',
                         'original resume download', 'portrait loaded', 'pink theme', '320–1440px layout']}
    (OUT / 'about-checks.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True))
    browser.close()
