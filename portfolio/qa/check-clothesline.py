from playwright.sync_api import sync_playwright
import json
from pathlib import Path
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
 page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
 errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8765/',wait_until='networkidle')
 page.evaluate("document.documentElement.style.scrollBehavior='auto'; document.querySelector('#work').scrollIntoView()")
 page.wait_for_timeout(2200)
 assert page.locator('.hanging-card').count()==4
 assert page.locator('.work-signature,.work-back,.work-next').count()==0
 assert page.locator('.hanging-number').all_text_contents()==['Project 1','Project 2','Project 3','Project 4']
 page.wait_for_function("Array.from(document.querySelectorAll('.hanging-card')).every(el=>getComputedStyle(el).opacity==='1')")
 page.screenshot(path='portfolio/qa/clothesline-desktop.png')
 print(page.locator('.hanging-card').evaluate_all('(els)=>els.map(el=>({text:el.innerText,href:el.getAttribute("href"),rect:el.getBoundingClientRect().toJSON()}))'))
 page.locator('.hanging-card').nth(1).hover()
 page.wait_for_timeout(220)
 print('hover animations',page.locator('.card-swing').nth(1).evaluate('(el)=>el.getAnimations().length'))
 page.locator('.hanging-card').nth(1).click()
 page.wait_for_url('**/project-2.html')
 print('project navigation',page.url)
 page.goto('http://127.0.0.1:8765/#work',wait_until='networkidle')
 page.evaluate("document.documentElement.style.scrollBehavior='auto'; document.querySelector('#work').scrollIntoView()")
 page.locator('.theme').click()
 page.wait_for_timeout(1600)
 page.wait_for_function("Array.from(document.querySelectorAll('.hanging-card')).every(el=>getComputedStyle(el).opacity==='1')")
 page.screenshot(path='portfolio/qa/clothesline-dark.png')
 print('dark backgrounds',page.evaluate('({home:getComputedStyle(document.querySelector("#home")).backgroundColor,work:getComputedStyle(document.querySelector("#work")).backgroundColor,body:getComputedStyle(document.body).backgroundColor})'))
 page.locator('.theme').click()
 page.set_viewport_size({'width':390,'height':844})
 page.evaluate("document.querySelector('#work').scrollIntoView()")
 page.wait_for_timeout(1600)
 page.locator('#work').screenshot(path='portfolio/qa/clothesline-mobile.png')
 print('mobile overflow',page.evaluate('document.documentElement.scrollWidth>innerWidth'))
 for width in [320,390,768,1440]:
  page.set_viewport_size({'width':width,'height':1000})
  page.wait_for_timeout(100)
  for photo in page.locator('.hanging-photo').all():
   bounds=photo.bounding_box()
   assert bounds['x']>=0 and bounds['x']+bounds['width']<=width, (width,bounds)
  for i,link in enumerate(page.locator('.hanging-card').all(),1):
   assert link.get_attribute('href')==f'project-{i}.html'
   assert page.request.get('http://127.0.0.1:8765/'+link.get_attribute('href')).status==200
 page.emulate_media(reduced_motion='reduce')
 assert page.locator('.hanging-card').first.evaluate('(e)=>getComputedStyle(e).animationName')=='none'
 assert errors==[]
 print('PASS: all four links, card bounds at 320/390/768/1440, reduced motion, no browser errors')
 print('errors',errors)
 browser.close()
