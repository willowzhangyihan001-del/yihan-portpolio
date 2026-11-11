(() => {
 const section=document.querySelector('#contact');
 const figure=section?.querySelector('.contact-artwork');
 const original=figure?.querySelector('img');
 if(!original)return;

 const finePointer=matchMedia('(hover: hover) and (pointer: fine)');
 const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)');
 const ns='http://www.w3.org/2000/svg';
 // Coordinates belong to the original 1448 x 1086 illustration. Closed eyes stay drawn.
 const eyes=[
  {x:693.5,y:263,rx:6.2,ry:5.7,mask:9.5,rangeX:11,rangeY:8},
  {x:804.2,y:236.6,rx:6.2,ry:5.7,mask:9.5,rangeX:11,rangeY:8},
  {x:1043,y:664.1,rx:5.1,ry:5.1,mask:8,rangeX:7,rangeY:5},
  {x:1112.6,y:689.4,rx:1.9,ry:2,mask:4.5,rangeX:4.5,rangeY:4}
 ];
 const canvas=document.createElement('div');
 canvas.className='contact-cat-canvas';
 original.before(canvas);
 canvas.append(original);

 const drawing=document.createElementNS(ns,'svg');
 drawing.classList.add('contact-gaze');
 drawing.setAttribute('viewBox','0 0 1448 1086');
 drawing.setAttribute('aria-hidden','true');
 drawing.setAttribute('focusable','false');
 drawing.innerHTML=`<defs><mask id="contact-pupil-mask" maskUnits="userSpaceOnUse" x="0" y="0" width="1448" height="1086"><rect width="1448" height="1086" fill="white"/>${eyes.map(eye=>`<circle cx="${eye.x}" cy="${eye.y}" r="${eye.mask}" fill="black"/>`).join('')}</mask></defs><image class="contact-cat-drawing" width="1448" height="1086" mask="url(#contact-pupil-mask)"/><g class="contact-pupils">${eyes.map(eye=>`<ellipse class="contact-pupil" cx="${eye.x}" cy="${eye.y}" rx="${eye.rx}" ry="${eye.ry}"/>`).join('')}</g>`;
 const pupils=[...drawing.querySelectorAll('.contact-pupil')];
 const source=drawing.querySelector('image');

 const bubble=document.createElement('div');
 bubble.className='contact-bubble';
 bubble.setAttribute('aria-hidden','true');
 bubble.innerHTML='<svg viewBox="0 0 232 86" preserveAspectRatio="none" focusable="false"><path class="contact-bubble-outline" d="M23 10 C72 6 154 11 208 9 Q225 10 224 27 L223 54 Q222 69 206 69 L55 68 Q40 77 26 79 L31 66 Q10 65 10 51 L11 27 Q9 12 23 10 Z"/><path class="contact-bubble-trace" d="M24 12 C76 9 157 12 207 11 Q222 12 222 28 M221 52 Q223 66 206 67 L57 66 M28 77 L34 65"/></svg><span>Shall we talk?</span>';
 document.body.append(bubble);

 let ready=false,visible=false,following=false,frame=0,dirty=true,placed=false;
 let artBounds=null,inverse=null,bubbleWidth=0,bubbleHeight=0;
 let obstacles=[],limits={left:8,right:8,top:8,bottom:8};
 let motionBounds={left:0,right:0,top:0,bottom:0};
 let measuredWidth=0,measuredHeight=0;
 let x=0,y=0,mouseX=0,mouseY=0;
 const clamp=(value,min,max)=>Math.max(min,Math.min(max,value));
 const schedule=()=>{if(!frame)frame=requestAnimationFrame(paint)};
 const setActive=value=>{
  section.classList.toggle('has-bubble-cursor',value);
 };
 const overlaps=(px,py,rect)=>px<rect.right-.001&&px+bubbleWidth>rect.left+.001&&py<rect.bottom-.001&&py+bubbleHeight>rect.top+.001;
 const clampPosition=(px,py)=>({x:clamp(px,limits.left,limits.right),y:clamp(py,limits.top,limits.bottom)});
 const collectObstacles=()=>{
  const rects=[];
  const selectors=['.contact-kicker','.contact-name','.contact-note','.contact-footer>span'];
  // Text ranges follow the actual lines, rather than the empty space in block elements.
  section.querySelectorAll(selectors.join(',')).forEach(element=>{
   const walker=document.createTreeWalker(element,NodeFilter.SHOW_TEXT);
   while(walker.nextNode()){
    if(!walker.currentNode.textContent.trim())continue;
    const range=document.createRange();
    range.selectNodeContents(walker.currentNode);
    rects.push(...range.getClientRects());
   }
  });
  document.querySelectorAll('.contact-email,.contact-top,.theme').forEach(element=>rects.push(element.getBoundingClientRect()));
  return rects.filter(rect=>rect.width&&rect.height).map(rect=>({left:rect.left-12,right:rect.right+12,top:rect.top-12,bottom:rect.bottom+12}));
 };
 const nearestFreePosition=(px,py)=>{
  const point=clampPosition(px,py);
  if(!obstacles.some(rect=>overlaps(point.x,point.y,rect)))return point;
  const xs=[point.x,limits.left,limits.right];
  const ys=[point.y,limits.top,limits.bottom];
  obstacles.forEach(rect=>{
   xs.push(clamp(rect.left-bubbleWidth,limits.left,limits.right),clamp(rect.right,limits.left,limits.right));
   ys.push(clamp(rect.top-bubbleHeight,limits.top,limits.bottom),clamp(rect.bottom,limits.top,limits.bottom));
  });
  let best=point,distance=Infinity;
  for(const px of xs)for(const py of ys){
   if(obstacles.some(rect=>overlaps(px,py,rect)))continue;
   const d=(px-point.x)**2+(py-point.y)**2;
   if(d<distance){best={x:px,y:py};distance=d}
  }
  return best;
 };
 const sweep=(px,py,dx,dy,rect)=>{
  // Expand each text rectangle by the bubble size, then sweep its top-left point.
  const left=rect.left-bubbleWidth,right=rect.right;
  const top=rect.top-bubbleHeight,bottom=rect.bottom;
  if(!dx&&(px<=left||px>=right))return null;
  if(!dy&&(py<=top||py>=bottom))return null;
  const enterX=dx?Math.min((left-px)/dx,(right-px)/dx):-Infinity;
  const exitX=dx?Math.max((left-px)/dx,(right-px)/dx):Infinity;
  const enterY=dy?Math.min((top-py)/dy,(bottom-py)/dy):-Infinity;
  const exitY=dy?Math.max((top-py)/dy,(bottom-py)/dy):Infinity;
  const time=Math.max(enterX,enterY);
  if(time<0||time>1||time>Math.min(exitX,exitY))return null;
  return {time,blockX:enterX>=enterY,blockY:enterY>=enterX};
 };
 const moveAroundText=(px,py,dx,dy)=>{
  for(let pass=0;pass<4&&(Math.abs(dx)+Math.abs(dy)>.001);pass++){
   let hit=null;
   for(const rect of obstacles){
    const next=sweep(px,py,dx,dy,rect);
    if(next&&(!hit||next.time<hit.time))hit=next;
   }
   if(!hit){px+=dx;py+=dy;break}
   const travel=Math.max(0,hit.time-.0001);
   px+=dx*travel;py+=dy*travel;
   dx=hit.blockX?0:dx*(1-hit.time);
   dy=hit.blockY?0:dy*(1-hit.time);
  }
  return clampPosition(px,py);
 };
 const measure=()=>{
  const oldBubbleWidth=bubbleWidth,oldBubbleHeight=bubbleHeight;
  artBounds=canvas.getBoundingClientRect();
  const matrix=drawing.getScreenCTM();
  inverse=matrix?.inverse();
  bubbleWidth=bubble.offsetWidth;
  bubbleHeight=bubble.offsetHeight;
  const contentBounds=section.querySelector('.contact-main').getBoundingClientRect();
  const headingBounds=section.querySelector('.contact-topline').getBoundingClientRect();
  const footerBounds=section.querySelector('.contact-footer').getBoundingClientRect();
  const themeBounds=document.querySelector('.theme').getBoundingClientRect();
  // Reserve the entire title and footer bands, including the blank space beside controls.
  motionBounds={
   left:Math.max(8,contentBounds.left),
   right:Math.min(innerWidth-8,contentBounds.right),
   top:Math.max(8,contentBounds.top,headingBounds.bottom+12),
   bottom:Math.min(innerHeight-8,contentBounds.bottom,footerBounds.top-12,themeBounds.top-12)
  };
  // The paper is tilted: keep its full rotated outline inside the content frame.
  const angle=2*Math.PI/180;
  const overhangX=(bubbleWidth*Math.cos(angle)+bubbleHeight*Math.sin(angle)-bubbleWidth)/2;
  const overhangY=(bubbleHeight*Math.cos(angle)+bubbleWidth*Math.sin(angle)-bubbleHeight)/2;
  limits={
   left:motionBounds.left+8+overhangX,
   right:motionBounds.right-bubbleWidth-8-overhangX,
   top:motionBounds.top+8+overhangY,
   bottom:motionBounds.bottom-bubbleHeight-8-overhangY
  };
  visible=ready&&!document.hidden&&limits.right>=limits.left&&limits.bottom>=limits.top;
  obstacles=collectObstacles();
  if(placed&&visible){
   if(measuredWidth&&measuredHeight&&(measuredWidth!==innerWidth||measuredHeight!==innerHeight)){
    x=(x+oldBubbleWidth/2)/measuredWidth*innerWidth-bubbleWidth/2;
    y=(y+oldBubbleHeight/2)/measuredHeight*innerHeight-bubbleHeight/2;
   }
   const point=nearestFreePosition(x,y);
   x=point.x;y=point.y;
  }
  measuredWidth=innerWidth;measuredHeight=innerHeight;
  bubble.classList.toggle('is-visible',visible);
  if(!visible){setActive(false);following=false}
  dirty=false;
 };
 function paint(){
  frame=0;
  if(dirty)measure();
  if(!visible||!inverse)return;
  const quiet=reducedMotion.matches;
  if(!placed){
   const point=innerWidth<=700
    ?nearestFreePosition(artBounds.right-bubbleWidth,artBounds.top-bubbleHeight-8)
    :nearestFreePosition(artBounds.left+artBounds.width*.86-bubbleWidth/2,artBounds.top+artBounds.height*.34-bubbleHeight/2);
   x=point.x;y=point.y;placed=true;
  }
  const target=following?clampPosition(mouseX-bubbleWidth/2,mouseY-bubbleHeight/2):{x,y};
  const ease=quiet?1:.2;
  const point=moveAroundText(x,y,(target.x-x)*ease,(target.y-y)*ease);
  const moved=Math.hypot(point.x-x,point.y-y);
  x=point.x;y=point.y;
  bubble.style.transform=`translate3d(${x.toFixed(2)}px,${y.toFixed(2)}px,0) rotate(-2deg)`;

  // Use the same point for the visible bubble and the gaze, including SVG letterboxing
  // and the slight rotation of the original figure at desktop sizes.
  const gazeTarget=new DOMPoint(x+bubbleWidth/2,y+bubbleHeight/2).matrixTransform(inverse);
  eyes.forEach((eye,i)=>{
   const dx=gazeTarget.x-eye.x,dy=gazeTarget.y-eye.y;
   const length=Math.hypot(dx,dy);
   const strength=Math.min(1,length/210);
   const offsetX=length?dx/length*eye.rangeX*strength:0;
   const offsetY=length?dy/length*eye.rangeY*strength:0;
   pupils[i].setAttribute('transform',`translate(${offsetX.toFixed(3)} ${offsetY.toFixed(3)})`);
  });
  // A stopped pointer or a text edge leaves the bubble exactly where it settled.
  if(following&&!quiet&&moved>.01&&Math.hypot(target.x-x,target.y-y)>.08)schedule();
 }
 const refresh=()=>{dirty=true;schedule()};

 section.addEventListener('pointermove',event=>{
  if(event.pointerType!=='mouse'||!finePointer.matches||!ready)return;
  if(dirty)measure();
  mouseX=event.clientX;mouseY=event.clientY;
  const overControl=Boolean(event.target.closest('a,button,input,textarea,select'));
  const overText=obstacles.some(rect=>mouseX>=rect.left&&mouseX<=rect.right&&mouseY>=rect.top&&mouseY<=rect.bottom);
  const inContent=mouseX>=motionBounds.left&&mouseX<=motionBounds.right&&mouseY>=motionBounds.top&&mouseY<=motionBounds.bottom;
  following=visible;
  setActive(visible&&inContent&&!overControl&&!overText);
  schedule();
 },{passive:true});
 const stopFollowing=()=>{following=false;setActive(false);schedule()};
 section.addEventListener('pointerleave',stopFollowing);
 window.addEventListener('blur',stopFollowing);
 document.addEventListener('keydown',event=>{if(event.key==='Tab')stopFollowing()});
 document.addEventListener('visibilitychange',refresh);
 window.addEventListener('scroll',refresh,{passive:true});
 window.addEventListener('resize',()=>{stopFollowing();refresh()},{passive:true});
 finePointer.addEventListener('change',()=>{stopFollowing();refresh()});
 reducedMotion.addEventListener('change',refresh);
 new ResizeObserver(refresh).observe(canvas);
 document.fonts?.ready.then(refresh);

 source.addEventListener('load',()=>{
  ready=true;
  figure.classList.add('gaze-ready');
  refresh();
 },{once:true});
 source.addEventListener('error',()=>{
  ready=false;
  figure.classList.remove('gaze-ready');
  bubble.classList.remove('is-visible');
  setActive(false);
 },{once:true});
 source.setAttribute('href',original.getAttribute('src'));
 canvas.append(drawing);
})();
