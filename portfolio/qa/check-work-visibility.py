from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
    page = browser.new_page(viewport={'width': 2048, 'height': 1055})
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    for width, height, motion in [(2048, 1055, 'no-preference'), (1440, 1000, 'no-preference'), (390, 844, 'no-preference'), (390, 844, 'reduce')]:
        page.set_viewport_size({'width': width, 'height': height})
        page.emulate_media(reduced_motion=motion)
        page.goto('http://127.0.0.1:8765/#work', wait_until='load')
        # Check real elapsed animation time; seeking animations masked the visibility bug.
        page.wait_for_timeout(3300)
        cards = page.locator('.hanging-card')
        assert cards.count() == 4
        assert cards.evaluate_all('''es=>es.every(e=>getComputedStyle(e).visibility==='visible' && getComputedStyle(e.firstElementChild).opacity==='1')''')
        assert cards.locator('img').evaluate_all('es=>es.every(e=>e.complete && e.naturalWidth>0)')
        for i, card in enumerate(cards.all(), 1):
            assert card.get_attribute('href') == f'project-{i}.html'
            assert page.request.get(f'http://127.0.0.1:8765/project-{i}.html').status == 200
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        if width == 2048:
            page.screenshot(path='portfolio/qa/work-visibility-fixed.png')
            cards.nth(1).click()
            page.wait_for_url('**/project-2.html')
        print(f'PASS: {width}x{height}, {motion}, four visible cards, loaded images and project links')
    assert errors == [], errors
    browser.close()
