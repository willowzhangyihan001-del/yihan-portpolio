(() => {
 const hero=document.querySelector('#home');
 if(!hero)return;
 const motion=window.matchMedia('(prefers-reduced-motion: reduce)');
 const pointer=window.matchMedia('(hover: hover) and (pointer: fine)');
 const title=hero.querySelector('h1');
 const artwork=hero.querySelector('.hero-artwork-wrap');
 const stage=hero.querySelector('.hero-stage');

 // Keep the original text readable without JavaScript and give screen readers one name.
 title.setAttribute('aria-label',title.textContent.trim());
 let letterIndex=0;
 const letters=[];
 const titleNodes=[...title.childNodes];
 const makeLetters=(text,parent)=>{
  for(const character of text){
   if(character===' '){parent.append(document.createTextNode(' '));continue}
   const letter=document.createElement('span');
   letter.className='hero-title-char';
   letter.textContent=character;
   letter.setAttribute('aria-hidden','true');
   letter.style.setProperty('--letter-index',letterIndex++);
   letter.style.setProperty('--letter-angle',`${letterIndex%2?-8:7}deg`);
   parent.append(letter);
   letters.push(letter);
  }
 };
 title.replaceChildren();
 for(const node of titleNodes){
  if(node.nodeType===Node.TEXT_NODE){makeLetters(node.textContent,title);continue}
  const word=node.cloneNode(false);
  makeLetters(node.textContent,word);
  title.append(word);
 }

 // Separate entrance, idle float, and pointer movement so their transforms compose.
 const entrance=document.createElement('div');
 entrance.className='hero-collage-enter';
 const floating=document.createElement('div');
 floating.className='hero-collage-float';
 floating.append(...artwork.childNodes);
 entrance.append(floating);
 artwork.append(entrance);

 const arrows=[
  ['.about-link','M9 7 C15 17 25 25 36 36 M22 34 L37 37 L35 22','3px','3px'],
  ['.work-link','M37 7 C28 16 20 25 10 36 M12 21 L9 37 L25 34','-3px','3px'],
  ['.contact-link','M9 37 C17 27 27 18 36 8 M21 10 L37 7 L35 23','3px','-3px']
 ];
 arrows.forEach(([selector,path,dx,dy],i)=>{
  const link=hero.querySelector(selector);
  const arrow=link.querySelector('span');
  const label=document.createElement('span');
  label.className='hero-link-label';
  label.textContent=link.firstChild.textContent;
  link.firstChild.replaceWith(label);
  arrow.className='hero-link-arrow';
  arrow.setAttribute('aria-hidden','true');
  arrow.innerHTML=`<svg viewBox="0 0 48 48" focusable="false"><path d="${path}"/></svg>`;
  link.style.setProperty('--note-delay',`${700+i*160}ms`);
  link.style.setProperty('--arrow-x',dx);
  link.style.setProperty('--arrow-y',dy);
 });

 const doodles=document.createElement('div');
 doodles.className='hero-motion-doodles';
 doodles.setAttribute('aria-hidden','true');
 doodles.innerHTML='<svg class="hero-sparkle hero-sparkle-one" viewBox="0 0 42 48" focusable="false"><path d="M22 4 Q23 21 38 23 Q22 25 20 43 Q19 26 4 24 Q20 22 22 4 Z"/><path class="hero-sparkle-trace" d="M21 6 Q24 20 36 23 M20 41 Q18 27 6 25"/></svg><svg class="hero-sparkle hero-sparkle-two" viewBox="0 0 36 40" focusable="false"><path d="M19 3 L21 14 L32 17 L22 21 L18 35 L15 23 L4 19 L15 15 Z"/></svg>';
 stage.append(doodles);

 letters.forEach((letter,i)=>letter.addEventListener('pointerenter',()=>{
  if(motion.matches||!pointer.matches)return;
  letter.getAnimations().forEach(animation=>animation.cancel());
  letter.animate([
   {transform:'translateY(0) rotate(0)'},
   {transform:`translateY(-9px) rotate(${i%2?6:-6}deg)`,offset:.3},
   {transform:'translateY(2px) rotate(1deg)',offset:.65},
   {transform:'translateY(0) rotate(0)'}
  ],{duration:650,easing:'cubic-bezier(.2,.8,.2,1)'});
 }));

 let visible=true,frame=0;
 let x=0,y=0,targetX=0,targetY=0;
 const paint=()=>{
  x+=(targetX-x)*.085;
  y+=(targetY-y)*.085;
  hero.style.setProperty('--hero-pointer-x',`${x.toFixed(3)}px`);
  hero.style.setProperty('--hero-pointer-y',`${y.toFixed(3)}px`);
  hero.style.setProperty('--hero-pointer-turn',`${(x*.055).toFixed(3)}deg`);
  frame=Math.abs(x-targetX)+Math.abs(y-targetY)>.025?requestAnimationFrame(paint):0;
 };
 const reset=()=>{
  if(frame)cancelAnimationFrame(frame);
  frame=0;x=0;y=0;targetX=0;targetY=0;
  hero.style.removeProperty('--hero-pointer-x');
  hero.style.removeProperty('--hero-pointer-y');
  hero.style.removeProperty('--hero-pointer-turn');
 };
 hero.addEventListener('pointermove',event=>{
  if(motion.matches||!pointer.matches||!visible||event.pointerType!=='mouse')return;
  const bounds=hero.getBoundingClientRect();
  targetX=Math.max(-1,Math.min(1,(event.clientX-bounds.left)/bounds.width*2-1))*9;
  targetY=Math.max(-1,Math.min(1,(event.clientY-bounds.top)/bounds.height*2-1))*6;
  if(!frame)frame=requestAnimationFrame(paint);
 },{passive:true});
 hero.addEventListener('pointerleave',()=>{
  targetX=0;targetY=0;
  if(!frame&&!motion.matches)frame=requestAnimationFrame(paint);
 });
 let visibilityFrame=0;
 const updateVisibility=()=>{
  const bounds=hero.getBoundingClientRect();
  visible=bounds.bottom>1&&bounds.top<innerHeight-1;
  hero.classList.toggle('hero-is-away',document.hidden||!visible);
  if(document.hidden||!visible)reset();
  visibilityFrame=0;
 };
 window.addEventListener('scroll',()=>{
  if(!visibilityFrame)visibilityFrame=requestAnimationFrame(updateVisibility);
 },{passive:true});
 document.addEventListener('visibilitychange',updateVisibility);
 motion.addEventListener('change',()=>{
  reset();
  if(motion.matches)letters.forEach(letter=>letter.getAnimations().forEach(animation=>animation.cancel()));
 });
 pointer.addEventListener('change',reset);
 window.addEventListener('resize',()=>{reset();updateVisibility()},{passive:true});
 updateVisibility();
 hero.classList.add('hero-motion-ready');
})();
