from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
 page=b.new_page(viewport={'width':2559,'height':1308})
 errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 for width,height in [(2559,1308),(2560,1080),(1920,1080),(1440,1000),(1366,768),(1280,720),(768,1024),(390,844)]:
  page.set_viewport_size({'width':width,'height':height})
  page.goto('http://127.0.0.1:8765/?v=work-alignment',wait_until='networkidle')
  arrow=page.locator('.hero-bottom a').bounding_box()
  page.mouse.click(arrow['x']+arrow['width']/2,arrow['y']+arrow['height']/2)
  page.wait_for_function('location.hash=="#work"')
  page.wait_for_function('Math.abs(document.querySelector("#work").getBoundingClientRect().top)<1')
  page.wait_for_function('Array.from(document.querySelectorAll(".hanging-card")).every(e=>getComputedStyle(e).opacity==="1")')
  result=page.locator('#work').evaluate('''e=>{const section=e.getBoundingClientRect(),rects=Array.from(e.querySelectorAll('.card-swing,.work-title')).map(x=>x.getBoundingClientRect());const top=Math.min(...rects.map(r=>r.top)),bottom=Math.max(...rects.map(r=>r.bottom));return {width:innerWidth,height:innerHeight,sectionHeight:section.height,sectionTop:section.top,top,bottom,center:(top+bottom)/2,overflow:document.documentElement.scrollWidth>innerWidth}}''')
  if width>700:
   assert abs(result['sectionHeight']-height)<1,result
   assert result['top']>=0 and result['bottom']<=height,result
   assert abs(result['center']-height/2)<height*.07,result
  assert not result['overflow'],result
  print(json.dumps(result))
  if width in [2559,1366,390]:page.screenshot(path=f'portfolio/qa/work-centered-{width}.png')
 assert errors==[],errors
 page.goto('http://127.0.0.1:8765/#work',wait_until='networkidle')
 page.set_viewport_size({'width':2559,'height':1308})
 page.locator('#work').evaluate('(e)=>e.scrollIntoView({behavior:"instant",block:"start"})')
 page.wait_for_timeout(300)
 page.locator('.theme').click()
 page.wait_for_timeout(900)
 page.screenshot(path='portfolio/qa/work-centered-dark.png')
 print('PASS: actual down-arrow clicks, all desktop cards visible and centered; mobile unchanged; no script errors')
 b.close()
