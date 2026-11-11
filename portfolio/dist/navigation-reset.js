(() => {
 // Only the browser's top-level refresh starts a new portfolio visit.
 if(window.top!==window||performance.getEntriesByType('navigation')[0]?.type!=='reload')return;
 try{sessionStorage.removeItem('portfolio-work-entrance-seen')}catch{}
 history.scrollRestoration='manual';
 const home=new URL('index.html#home',location.href);
 if(/\/project-[1-4]\.html$/.test(location.pathname)){
  location.replace(home.href);
  return;
 }
 history.replaceState(null,'',home.href);
 const root=document.documentElement;
 const behavior=root.style.scrollBehavior;
 root.style.scrollBehavior='auto';
 const reset=()=>window.scrollTo({top:0,behavior:'instant'});
 reset();
 window.addEventListener('DOMContentLoaded',reset,{once:true});
 window.addEventListener('pageshow',()=>{reset();root.style.scrollBehavior=behavior},{once:true});
})();
