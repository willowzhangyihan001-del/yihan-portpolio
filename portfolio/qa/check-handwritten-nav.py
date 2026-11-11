from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
 page=b.new_page(viewport={'width':1440,'height':1000})
 errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8765/#education',wait_until='networkidle')
 page.evaluate("document.documentElement.style.scrollBehavior='auto'")
 page.wait_for_timeout(1200)
 assert page.locator('.resume-nav-label').count()==0
 assert page.locator('.resume-nav-text').count()==6
 for section in ['education','research','awards','interests']:
  page.locator('.resume-nav a[href="#'+section+'"]').click()
  page.wait_for_timeout(650)
  assert page.locator('.resume-nav a[aria-current]').get_attribute('href')=='#'+section
  result=page.locator('.resume-nav a[aria-current] .resume-nav-text').evaluate('e=>({font:getComputedStyle(e).fontFamily,wave:getComputedStyle(e,"::after").opacity,color:getComputedStyle(e,"::after").backgroundColor,background:getComputedStyle(e.parentElement).backgroundColor,shadow:getComputedStyle(e.parentElement).boxShadow})')
  assert 'Caveat' in result['font'] and result['wave']=='1' and result['shadow']=='none',result
  print(section,result)
 page.locator('.resume-nav').screenshot(path='portfolio/qa/navigation-handwritten-light.png')
 page.locator('.theme').click()
 page.wait_for_timeout(900)
 page.locator('.resume-nav').screenshot(path='portfolio/qa/navigation-handwritten-dark.png')
 print('dark wave',page.locator('.resume-nav a[aria-current] .resume-nav-text').evaluate('e=>getComputedStyle(e,"::after").backgroundColor'))
 page.set_viewport_size({'width':390,'height':844})
 page.locator('.resume-nav').scroll_into_view_if_needed()
 page.locator('.resume-nav').screenshot(path='portfolio/qa/navigation-handwritten-mobile.png')
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 assert errors==[],errors
 print('PASS: navigation follows all tested sections, light/dark waves, mobile bounds, no browser errors')
 b.close()
