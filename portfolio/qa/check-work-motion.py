from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
 page=b.new_page(viewport={'width':1440,'height':1000})
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8765/?v=work-motion#work',wait_until='networkidle')
 page.wait_for_selector('#work.is-visible')
 def seek(t):
  page.locator('#work').evaluate('(e,t)=>e.getAnimations({subtree:true}).forEach(a=>{a.pause();a.currentTime=t})',t)
  page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
  return page.locator('#work').evaluate('''e=>({rope:getComputedStyle(e.querySelector('.clothesline path')).strokeDashoffset,cards:Array.from(e.querySelectorAll('.hanging-card')).map(e=>({visibility:getComputedStyle(e).visibility,opacity:+getComputedStyle(e.querySelector('.card-mount')).opacity,rotate:getComputedStyle(e.querySelector('.card-mount')).rotate}))})''')
 for t in [0,650,1200,1500,1800,2200,3100]:
  state=seek(t);print(t,json.dumps(state))
  if t==0:assert all(c['opacity']==0 for c in state['cards'])
  if t==650:assert 0<float(state['rope'].replace('px',''))<1 and all(c['opacity']==0 for c in state['cards'])
  if t==1200:assert state['cards'][0]['opacity']>0 and state['cards'][1]['opacity']==0
  if t==1500:assert state['cards'][1]['opacity']>0 and state['cards'][2]['opacity']==0
  if t==3100:assert all(c['visibility']=='visible' and c['opacity']==1 for c in state['cards'])
  if t in [0,650,1200,1800,3100]:page.screenshot(path=f'portfolio/qa/work-motion-{t}.png')
 page.locator('.hanging-card').nth(1).hover()
 assert page.locator('.card-swing').nth(1).evaluate('(e)=>e.getAnimations().length')>0
 page.wait_for_selector('#work.is-settled')
 def assert_settled():
  assert page.locator('#work').evaluate('(e)=>e.classList.contains("is-visible") && e.classList.contains("is-settled")')
  assert page.locator('.card-mount').evaluate_all('(es)=>es.every(e=>getComputedStyle(e).opacity==="1" && getComputedStyle(e).animationName==="none")')
  assert page.locator('.hanging-card').evaluate_all('(es)=>es.every(e=>getComputedStyle(e).visibility==="visible")')
 assert_settled()
 page.evaluate("document.documentElement.style.scrollBehavior='auto';window.scrollTo(0,0)")
 page.wait_for_timeout(100)
 assert_settled()
 page.locator('#work').evaluate('(e)=>e.scrollIntoView({behavior:"instant"})')
 assert_settled()
 print('PASS: scrolling to the page top and back never replays the entrance')

 for project in range(1,5):
  page.locator('.hanging-card').nth(project-1).click()
  page.wait_for_url(f'**/project-{project}.html')
  project_view=page.frame_locator('.project-preview iframe')
  assert project_view.locator('.home-link').get_attribute('href')=='index.html#work'
  project_view.locator('body').evaluate('()=>window.scrollTo(0,document.documentElement.scrollHeight)')
  project_view.locator('.home-link').click()
  page.wait_for_url('**/index.html#work',wait_until='domcontentloaded')
  assert_settled()
  page.wait_for_function('Math.abs(document.querySelector("#work").getBoundingClientRect().top)<2')
  assert page.evaluate('scrollY>=innerHeight-2')
  print(f'PASS: Project {project} Home returns directly to visible, settled project cards')

 page.locator('.hanging-card').nth(1).click()
 page.wait_for_url('**/project-2.html')
 page.go_back(wait_until='domcontentloaded')
 assert_settled()
 print('PASS: browser Back preserves the settled cards')

 page.reload(wait_until='networkidle')
 assert page.url.endswith('index.html#home')
 assert page.evaluate('scrollY')<2
 assert page.evaluate('performance.getEntriesByType("navigation")[0].type')=='reload'
 assert not page.locator('#work').evaluate('(e)=>e.classList.contains("is-visible")')
 assert page.evaluate('sessionStorage.getItem("portfolio-work-entrance-seen")') is None
 page.locator('#work').evaluate('(e)=>e.scrollIntoView({behavior:"instant"})')
 page.wait_for_selector('#work.is-visible')
 assert page.locator('.card-mount').first.evaluate('(e)=>getComputedStyle(e).opacity')=='0'
 page.wait_for_selector('#work.is-settled',timeout=6000)
 assert_settled()
 print('PASS: an actual refresh resets the entrance and it plays once on the next visit to work')
 page.emulate_media(reduced_motion='reduce')
 page.wait_for_timeout(100)
 assert page.locator('.card-mount').evaluate_all('(es)=>es.every(e=>getComputedStyle(e).opacity==="1" && getComputedStyle(e).animationName==="none")')
 assert page.locator('.hanging-card').evaluate_all('(es)=>es.every(e=>getComputedStyle(e).visibility==="visible")')
 assert page.locator('.clothesline path').first.evaluate('(e)=>getComputedStyle(e).strokeDashoffset')=='0px'
 print('reduced-motion PASS')
 page.emulate_media(reduced_motion='no-preference')
 page.set_viewport_size({'width':390,'height':844})
 page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
 assert_settled()
 page.locator('#work').evaluate('(e)=>e.scrollIntoView({behavior:"instant"})')
 page.wait_for_selector('#work.is-visible')
 assert_settled()
 assert page.locator('.clothesline-mobile path').evaluate_all('(es)=>es.every(e=>getComputedStyle(e).strokeDashoffset==="0px")')
 assert page.locator('.card-mount').evaluate_all('(es)=>es.every(e=>getComputedStyle(e).opacity==="1")')
 page.screenshot(path='portfolio/qa/work-motion-mobile.png')
 assert errors==[],errors
 page.locator('.hanging-card').nth(1).hover()
 assert page.locator('.card-swing').nth(1).evaluate('(e)=>e.getAnimations().some(a=>a.playState==="running")')
 print('PASS: hover remains animated after returning; mobile and reduced-motion states stay visible')
 page.close()

 mobile=b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce')
 mobile_page=mobile.new_page()
 mobile_page.goto('http://127.0.0.1:8765/#work',wait_until='networkidle')
 mobile_page.locator('.hanging-card').nth(2).tap()
 mobile_page.wait_for_url('**/project-3.html')
 mobile_page.frame_locator('.project-preview iframe').locator('.home-link').tap()
 mobile_page.wait_for_url('**/index.html#work',wait_until='domcontentloaded')
 assert mobile_page.locator('.card-mount').evaluate_all('(es)=>es.every(e=>getComputedStyle(e).opacity==="1" && getComputedStyle(e).animationName==="none")')
 mobile_page.wait_for_function('Math.abs(document.querySelector("#work").getBoundingClientRect().top)<2')
 mobile.close()
 print('PASS: mobile touch Home goes directly to the project gallery')

 fallback=b.new_context()
 fallback.add_init_script('Object.defineProperty(window,"sessionStorage",{get(){throw new DOMException("Storage unavailable","SecurityError")}})')
 fallback_page=fallback.new_page()
 fallback_page.on('pageerror',lambda e:errors.append(str(e)))
 fallback_page.goto('http://127.0.0.1:8765/project-4.html',wait_until='networkidle')
 fallback_page.locator('.home-link').click()
 fallback_page.wait_for_url('**/index.html#work',wait_until='domcontentloaded')
 assert fallback_page.locator('#work').evaluate('(e)=>e.classList.contains("is-settled")')
 assert fallback_page.locator('.card-mount').evaluate_all('(es)=>es.every(e=>getComputedStyle(e).opacity==="1")')
 assert errors==[],errors
 print('PASS: a directly opened project returns without entrance even when session storage is unavailable; no browser errors')
 b.close()
