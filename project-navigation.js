(() => {
 const work=document.querySelector('#work');
 if(!work)return;
 const homeURL=new URL('index.html#work',location.href);
 const homeTitle=document.title;
 const main=document.querySelector('body>main');
 const theme=document.querySelector('.theme');
 history.scrollRestoration='manual';
 let preview=null,previewPath='',returnFocus=null;

 const showWork=()=>{
  preview?.remove();
  preview=null;previewPath='';
  document.body.classList.remove('project-open');
  main.inert=false;
  theme.inert=false;
  document.title=homeTitle;
  window.dispatchEvent(new Event('portfolio:show-work'));
  work.scrollIntoView({behavior:'instant',block:'start'});
  returnFocus?.focus({preventScroll:true});
  window.dispatchEvent(new Event('scroll'));
 };
 const showProject=(url,focusHome=false)=>{
  if(preview&&previewPath===url.pathname)return;
  window.dispatchEvent(new Event('portfolio:show-work'));
  preview?.remove();
  preview=document.createElement('div');
  preview.className='project-preview';
  const frame=document.createElement('iframe');
  const card=[...work.querySelectorAll('.hanging-card')].find(link=>new URL(link.href).pathname===url.pathname);
  returnFocus=card;
  frame.title=card?.getAttribute('aria-label')?.replace('View ','')||'Project preview';
  frame.src=url.href;
  frame.addEventListener('load',()=>{
   if(frame!==preview?.firstElementChild)return;
   try{
    document.title=frame.contentDocument.title;
    if(focusHome)frame.contentDocument.querySelector('.home-link')?.focus({preventScroll:true});
   }catch{}
  });
  preview.append(frame);
  document.body.append(preview);
  previewPath=url.pathname;
  document.body.classList.add('project-open');
  main.inert=true;
  theme.inert=true;
 };
 document.addEventListener('click',event=>{
  const card=event.target.closest('.hanging-card');
  if(!card||event.defaultPrevented||event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
  const url=new URL(card.href);
  if(url.origin!==location.origin||!/\/project-[1-4]\.html$/.test(url.pathname))return;
  event.preventDefault();
  // Keep the existing gallery document and its animation state in the previous entry.
  history.replaceState({...history.state,portfolioView:'home'},'',homeURL.href);
  history.pushState({portfolioView:'project',projectPath:url.pathname},'',url.href);
  showProject(url,event.detail===0);
 });
 window.addEventListener('message',event=>{
  if(event.origin!==location.origin||event.source!==preview?.firstElementChild?.contentWindow||event.data?.type!=='portfolio:return-work')return;
  if(history.state?.portfolioView==='project')history.back();
  else{history.replaceState({portfolioView:'home'},'',homeURL.href);showWork()}
 });
 window.addEventListener('popstate',event=>{
  if(event.state?.portfolioView==='project')showProject(new URL(event.state.projectPath,location.origin));
  else if(preview)showWork();
 });
})();
