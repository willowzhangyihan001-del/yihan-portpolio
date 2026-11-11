(() => {
  function setupAboutCat() {
    const intro = document.querySelector('.about-intro');
    const track = document.querySelector('.about-cat-track');
    const cat = track?.querySelector('.about-cat');
    const figure = cat?.querySelector('.about-cat-figure');
    if (!intro || !track || !cat || !figure) return;

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
    let x = 0;
    let target = 0;
    let maxX = 0;
    let frame = 0;
    let previousTime = 0;
    let visible = !('IntersectionObserver' in window);
    let measured = false;
    let direction = 1;

    function render() {
      cat.style.transform = `translate3d(${x.toFixed(2)}px, 0, 0)`;
      figure.style.transform = `scaleX(${direction})`;
    }

    function stop() {
      if (frame) window.cancelAnimationFrame(frame);
      frame = 0;
      previousTime = 0;
      target = x;
      cat.classList.remove('is-walking');
    }

    function measure() {
      const nextMax = Math.max(0, track.getBoundingClientRect().width - cat.offsetWidth);
      if (measured && Math.abs(nextMax - maxX) < 0.25) return;
      const oldMax = maxX;
      maxX = nextMax;
      const ratio = measured && oldMax > 0 ? x / oldMax : 0.18;
      stop();
      x = Math.min(maxX, Math.max(0, maxX * ratio));
      target = x;
      measured = true;
      render();
    }

    function tick(time) {
      frame = 0;
      if (!visible || document.hidden || reducedMotion.matches) {
        stop();
        return;
      }
      const distance = target - x;
      if (Math.abs(distance) < 0.35) {
        x = target;
        render();
        stop();
        return;
      }

      const elapsed = previousTime ? Math.min(48, time - previousTime) : 16.67;
      previousTime = time;
      direction = distance < 0 ? -1 : 1;
      x += distance * (1 - Math.exp(-elapsed / 120));
      render();
      frame = window.requestAnimationFrame(tick);
    }

    function moveTo(clientX) {
      if (!visible || document.hidden || reducedMotion.matches) return;
      const bounds = track.getBoundingClientRect();
      maxX = Math.max(0, bounds.width - cat.offsetWidth);
      target = Math.min(maxX, Math.max(0, clientX - bounds.left - cat.offsetWidth / 2));
      if (Math.abs(target - x) < 0.35) return;
      cat.classList.add('is-walking');
      if (!frame) frame = window.requestAnimationFrame(tick);
    }

    intro.addEventListener('pointermove', event => {
      if (finePointer.matches && event.pointerType !== 'touch') moveTo(event.clientX);
    }, { passive: true });

    // A tap can reposition the decoration; native touch scrolling remains untouched.
    track.addEventListener('click', event => {
      if (event.detail > 0) moveTo(event.clientX);
    }, { passive: true });

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) stop();
    });
    window.addEventListener('pagehide', stop);
    reducedMotion.addEventListener('change', stop);

    if ('IntersectionObserver' in window) {
      const visibilityObserver = new IntersectionObserver(entries => {
        visible = entries[0].isIntersecting;
        if (!visible) stop();
      });
      visibilityObserver.observe(track);
    }

    measure();
    if ('ResizeObserver' in window) {
      const sizeObserver = new ResizeObserver(measure);
      sizeObserver.observe(track);
      sizeObserver.observe(cat);
    } else {
      window.addEventListener('resize', measure, { passive: true });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupAboutCat, { once: true });
  } else {
    setupAboutCat();
  }
})();
