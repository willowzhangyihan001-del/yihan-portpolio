from playwright.sync_api import sync_playwright
import json
from pathlib import Path
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
 page=browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
 errors=[];missing=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('response',lambda r:missing.append(r.url) if r.status>=400 and '127.0.0.1:8765' in r.url else None)
 page.goto('http://127.0.0.1:8765/?v=contact-cats#contact',wait_until='networkidle')
 page.evaluate("document.documentElement.style.scrollBehavior='auto'")
 page.locator('.contact-artwork img').evaluate('(img)=>img.decode()')
 assert page.locator('.contact-email').get_attribute('href')=='mailto:yihan_zz212@126.com'
 assert page.locator('.contact-email span').inner_text()=='yihan_zz212@126.com'
 assert page.locator('.contact-name').inner_text()=='YIHAN'
 results=[]
 for width,height in [(1440,1000),(1920,1080),(1366,768),(768,1024),(390,844),(320,740),(375,667),(320,568),(844,390)]:
  page.set_viewport_size({'width':width,'height':height})
  page.locator('#contact').evaluate('(e)=>e.scrollIntoView({block:"start",behavior:"instant"})')
  page.wait_for_timeout(250)
  result=page.locator('#contact').evaluate('''e=>{const r=e.getBoundingClientRect();return {width:innerWidth,height:innerHeight,sectionHeight:r.height,top:r.top,overflow:e.scrollWidth>e.clientWidth,bodyOverflow:document.documentElement.scrollWidth>innerWidth,items:Array.from(e.querySelectorAll('h2,.contact-email,.contact-note,.contact-footer,.contact-artwork')).map(x=>({class:x.className,left:x.getBoundingClientRect().left,right:x.getBoundingClientRect().right,top:x.getBoundingClientRect().top,bottom:x.getBoundingClientRect().bottom}))}}''')
  page.screenshot(path=f'portfolio/qa/contact-{width}-light.png')
  assert abs(result['sectionHeight']-height)<1, result
  assert abs(result['top'])<1, result
  assert not result['overflow'] and not result['bodyOverflow'], result
  for item in result['items']:
   assert item['left']>=-1 and item['right']<=width+1, item
   assert item['top']>=-1 and item['bottom']<=height+1, (width,height,item)
  results.append(result)
  print(json.dumps(result))
 page.set_viewport_size({'width':1440,'height':1000})
 page.locator('#contact').evaluate('(e)=>e.scrollIntoView({block:"start",behavior:"instant"})')
 page.locator('.theme').click()
 page.wait_for_timeout(1000)
 page.screenshot(path='portfolio/qa/contact-1440-dark.png')
 page.set_viewport_size({'width':390,'height':844})
 page.locator('#contact').evaluate('(e)=>e.scrollIntoView({block:"start",behavior:"instant"})')
 page.screenshot(path='portfolio/qa/contact-390-dark.png')
 assert errors==[] and missing==[],(errors,missing)
 assert page.locator('.contact-artwork img').evaluate('(e)=>getComputedStyle(e).filter')=='invert(1)'
 page.locator('.contact-email').focus()
 page.keyboard.press('Tab')
 page.keyboard.press('Shift+Tab')
 assert page.locator('.contact-email').evaluate('(e)=>e.matches(":focus-visible")')
 theme=page.locator('.theme').bounding_box();back=page.locator('.contact-top').bounding_box()
 assert back['x']+back['width']<theme['x'] or back['y']+back['height']<theme['y']
 page.locator('.contact-top').click()
 page.wait_for_function('scrollY < 2')
 print('PASS: full viewport at all sizes, keyboard email, footer controls, dark illustration, Back to top; no script/asset errors')
 print('errors',errors,'missing',missing)
 Path('portfolio/qa/contact-checks.json').write_text(json.dumps({'viewports':results,'errors':errors,'missing':missing},indent=2))
 browser.close()
