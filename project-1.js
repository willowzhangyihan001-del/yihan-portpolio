const progress = document.querySelector('.reading-progress');
// Embedded project previews return to the existing gallery, without a document navigation.
if(window.parent!==window){
 document.querySelector('.home-link').addEventListener('click',event=>{
  if(event.button!==0||event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;
  event.preventDefault();
  window.parent.postMessage({type:'portfolio:return-work'},location.origin);
 });
}
const fill = progress.querySelector('span');
let frame = 0;

function updateProgress() {
  const distance = document.documentElement.scrollHeight - innerHeight;
  const value = distance > 0 ? Math.max(0, Math.min(1, scrollY / distance)) : 1;
  fill.style.transform = `scaleX(${value})`;
  progress.setAttribute('aria-valuenow', String(Math.round(value * 100)));
  frame = 0;
}

function scheduleProgress() {
  if (!frame) frame = requestAnimationFrame(updateProgress);
}

window.addEventListener('scroll', scheduleProgress, {passive: true});
window.addEventListener('resize', scheduleProgress);
window.addEventListener('pageshow', scheduleProgress);
window.addEventListener('load', scheduleProgress);
updateProgress();

// Leave every board visible when JavaScript or motion effects are unavailable.
const projectBoards = [...document.querySelectorAll('.project-board')];
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');

if (!reducedMotion.matches && 'IntersectionObserver' in window) {
  const revealImage = board => {
    const image = board.querySelector('img');
    const show = () => requestAnimationFrame(() => board.classList.add('is-visible'));
    if (image.complete) show();
    else {
      image.addEventListener('load', show, {once: true});
      image.addEventListener('error', show, {once: true});
    }
  };

  const imageObserver = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      revealImage(entry.target);
      imageObserver.unobserve(entry.target);
    }
  }, {rootMargin: '0px 0px -24px 0px', threshold: 0});

  for (const board of projectBoards) {
    board.classList.add('scroll-reveal');
    imageObserver.observe(board);
  }

  reducedMotion.addEventListener('change', event => {
    if (!event.matches) return;
    imageObserver.disconnect();
    projectBoards.forEach(board => board.classList.add('is-visible'));
  });
}
