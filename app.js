const projects=[{id:'karios',name:'KARIOS',type:'Interaction / Product / Service Design',image:'assets/project1/01-background.png',url:'project-1.html'},{id:'token-office',name:'Token Office',type:'Simulation Game Design / Speculative Design',image:'assets/project2/01.png',url:'project-2.html'},{id:'constellia',name:'Constellia',type:'AI Agent Design',image:'assets/project3/01.png',url:'project-3.html'},{id:'neckotics',name:'Neckotics',type:'Wearable Product',image:'assets/project4/01.png',url:'project-4.html'}];

const $=s=>document.querySelector(s);
const projectRope=className=>`<svg class="${className}" viewBox="0 0 1200 100" preserveAspectRatio="none" aria-hidden="true"><path d="M-20 55 C95 64 192 48 300 52 S515 49 610 40 S809 31 914 34 S1089 41 1220 28"/><path class="rope-trace" d="M-20 59 C98 67 195 52 300 55 S518 53 612 44 S812 35 916 38 S1091 44 1220 32"/></svg>`;
const projectCards=projects.map((p,i)=>{
 const descriptions=['Hands holding the KARIOS mobile experience','Token Office installation and playtesting','Constellia community workshop','Neckotics wearable prototype testing'];
 return `<a class="hanging-card" href="${p.url}" data-project-key="${p.id}" aria-label="View ${p.name}" style="--tilt:${[-2,2.5,1.5,-2.5][i]}deg;--delay:${650+(i%2)*240}ms">
 ${projectRope('card-rope')}
 <span class="card-mount"><span class="card-swing"><svg class="card-hanger" viewBox="0 0 240 190" aria-hidden="true">
 <g fill="none" stroke="currentColor" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">
 <path d="M100 48 C100 27 119 -9 138 6 C157 21 132 42 132 57 L130 84 C101 91 62 117 29 148 C16 161 14 170 32 173 C85 181 166 179 216 171 C233 168 231 157 214 146 C185 126 157 100 130 84"/>
 <path d="M42 168 L43 191 M48 166 L51 190 M198 166 L201 188 M205 163 L210 185"/>
 </g></svg>
 <span class="hanging-photo"><img src="assets/work/project-${i+1}.jpg" alt="${descriptions[i]}" loading="lazy" decoding="async" draggable="false">
 <svg class="photo-frame" viewBox="0 0 400 300" preserveAspectRatio="none" aria-hidden="true"><path d="M3 4 C96 1 204 6 295 3 L396 4 C398 81 394 174 397 245 L396 296 C285 299 191 294 99 297 L4 296 C1 209 6 109 3 4 Z"/><path class="photo-frame-trace" d="M5 3 C99 4 207 3 297 5 L398 3 C396 84 398 176 395 247 L398 298 C283 296 190 298 97 295 L2 298 C4 208 2 107 5 3"/></svg></span>
 <span class="hanging-title">${p.name}</span>
 </span></span></a>`;
});
$('.hanging-projects').innerHTML=[0,1].map(row=>`<div class="project-row" style="--row-delay:${row*320}ms">${projectRope('work-rope')}${projectCards.slice(row*2,row*2+2).join('')}</div>`).join('');
const workSection=document.querySelector('#work');
const workRows=[...workSection.querySelectorAll('.project-row')];
const reduceMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
workSection.querySelectorAll('.work-rope path,.card-rope path').forEach(path=>path.setAttribute('pathLength','1'));
const workSeenKey='portfolio-work-entrance-seen';
const isReload=performance.getEntriesByType('navigation')[0]?.type==='reload';
let hasSeenWork=false;
try{
 if(isReload)sessionStorage.removeItem(workSeenKey);
 else hasSeenWork=sessionStorage.getItem(workSeenKey)==='true';
}catch{}
// Returning from a directly opened project also skips the entrance, even without storage.
if(!isReload&&location.hash==='#work'&&document.referrer){
 try{
  const referrer=new URL(document.referrer);
  if(referrer.origin===location.origin&&/\/project-[1-4]\.html$/.test(referrer.pathname))hasSeenWork=true;
 }catch{}
}
let workEntered=false,workEntrance=null;
const settleWork=()=>{
 workSection.classList.add('is-visible','is-settled');
 workRows.forEach(row=>row.classList.add('is-visible','is-settled'));
 workEntrance?.disconnect();
};
const enterWork=immediate=>{
 if(workEntered){if(immediate)settleWork();return}
 workEntered=true;
 try{sessionStorage.setItem(workSeenKey,'true')}catch{}
 workSection.classList.add('is-visible');
 if(immediate||reduceMotion.matches)settleWork();
};
window.addEventListener('portfolio:show-work',()=>enterWork(true));
workSection.classList.add('motion-ready');
if(hasSeenWork||reduceMotion.matches)enterWork(true);
else{
 workEntrance=new IntersectionObserver(entries=>{
  entries.forEach(entry=>{
   if(!entry.isIntersecting||entry.intersectionRatio<.12)return;
   enterWork(false);
   entry.target.classList.add('is-visible');
   workEntrance.unobserve(entry.target);
  });
 },{threshold:[0,.12]});
 workRows.forEach(row=>workEntrance.observe(row));
}
workSection.addEventListener('animationend',event=>{
 if(event.animationName!=='hang-project')return;
 const row=event.target.closest('.project-row');
 const cards=row?.querySelectorAll('.hanging-card');
 if(cards&&event.target.closest('.hanging-card')===cards[cards.length-1])row.classList.add('is-settled');
 if(workRows.every(row=>row.classList.contains('is-settled')))settleWork();
});
reduceMotion.addEventListener('change',()=>{
 if(reduceMotion.matches)enterWork(true);
});
// A cached page must return with settled cards, even if a project was opened mid-entrance.
window.addEventListener('pagehide',()=>{if(workEntered)settleWork()});
window.addEventListener('pageshow',event=>{if(event.persisted&&workEntered)settleWork()});
if(hasSeenWork&&location.hash==='#work'){
 const root=document.documentElement;
 const previousBehavior=root.style.scrollBehavior;
 root.style.scrollBehavior='auto';
 workSection.scrollIntoView({behavior:'instant',block:'start'});
 requestAnimationFrame(()=>{
  workSection.scrollIntoView({behavior:'instant',block:'start'});
  root.style.scrollBehavior=previousBehavior;
 });
}
document.querySelectorAll('.hanging-card').forEach(card=>{
 const swing=card.querySelector('.card-swing');
 card.addEventListener('pointerenter',()=>{
  if(reduceMotion.matches)return;
  swing.getAnimations().forEach(animation=>animation.cancel());
  swing.animate([{rotate:'0deg'},{rotate:'-2deg',offset:.22},{rotate:'1.4deg',offset:.48},{rotate:'-.6deg',offset:.73},{rotate:'0deg'}],{duration:1000,easing:'ease-in-out'});
 });
});
function setTheme(dark){
 document.body.classList.toggle('dark',dark);
 $('.theme').setAttribute('aria-pressed',String(dark));
 const themeLabel=dark?'Switch to light theme':'Switch to dark theme';
 $('.theme').title=themeLabel;
 $('.theme').setAttribute('aria-label',themeLabel);
}
let savedTheme='light';
try{savedTheme=localStorage.getItem('portfolio-theme')}catch{}
setTheme(savedTheme==='dark');
$('.theme').onclick=()=>{
 const dark=!document.body.classList.contains('dark');
 setTheme(dark);
 try{localStorage.setItem('portfolio-theme',dark?'dark':'light')}catch{}
};
const observer=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('visible');observer.unobserve(e.target)}}),{threshold:.12});document.querySelectorAll('.section-heading,.about-columns,.contact h2').forEach(el=>{el.classList.add('reveal');observer.observe(el)});
