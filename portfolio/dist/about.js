const resumeSections = [...document.querySelectorAll('.resume-section')];
const resumeLinks = [...document.querySelectorAll('.resume-nav a[href^="#"]')];
let resumeFrame = 0;

function updateResumeNavigation() {
  const about = document.getElementById('about').getBoundingClientRect();
  const work = document.getElementById('work').getBoundingClientRect();
  const contact = document.getElementById('contact').getBoundingClientRect();
  document.body.classList.toggle('contact-in-view', contact.top <= 80 && contact.bottom > 80);
  document.body.classList.toggle('work-in-view', work.top <= 80 && work.bottom > 80);
  document.body.classList.toggle('reading-about', about.top <= 80 && about.bottom > 0);
  let current = null;
  if (about.top < innerHeight && about.bottom > 0) {
    current = resumeSections[0]?.id;
    for (const section of resumeSections) {
      if (section.getBoundingClientRect().top <= innerHeight * 0.4) current = section.id;
    }
  }
  for (const link of resumeLinks) {
    if (link.hash === `#${current}`) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  }
  resumeFrame = 0;
}

window.addEventListener('scroll', () => {
  if (!resumeFrame) resumeFrame = requestAnimationFrame(updateResumeNavigation);
}, {passive: true});
window.addEventListener('resize', updateResumeNavigation);
updateResumeNavigation();
