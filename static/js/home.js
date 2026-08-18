// ── NAVBAR SCROLL
window.addEventListener('scroll', () => {
  document.getElementById('navbar').classList.toggle('scrolled', window.scrollY > 20);
});

// ── HAMBURGER
const btn = document.getElementById('hamburgerBtn');
const drawer = document.getElementById('mobileDrawer');
btn.addEventListener('click', () => {
  btn.classList.toggle('open');
  drawer.classList.toggle('open');
  document.body.style.overflow = drawer.classList.contains('open') ? 'hidden' : '';
});
drawer.addEventListener('click', (e) => { if (e.target === drawer) closeDrawer(); });
function closeDrawer() {
  btn.classList.remove('open');
  drawer.classList.remove('open');
  document.body.style.overflow = '';
}

// ── ROTATING WORDS
const words = ['Future-Ready', 'Scalable', 'Innovative', 'Intelligent'];
let wi = 0;
const el = document.getElementById('rotatingWord');
function rotateWord() {
  el.style.opacity = '0';
  el.style.transform = 'translateY(-12px)';
  setTimeout(() => {
    wi = (wi + 1) % words.length;
    el.textContent = words[wi];
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    el.style.opacity = '1';
    el.style.transform = 'translateY(0)';
  }, 350);
}
el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
setInterval(rotateWord, 2800);

// ── INTERSECTION OBSERVER: fade-up
const faders = document.querySelectorAll('.fade-up');
const obs = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); } });
}, { threshold: 0.12 });
faders.forEach(f => obs.observe(f));

// ── COUNT-UP
function countUp(el, target) {
  let start = 0;
  const duration = 1800;
  const step = target / (duration / 16);
  const timer = setInterval(() => {
    start += step;
    if (start >= target) { el.textContent = target; clearInterval(timer); return; }
    el.textContent = Math.floor(start);
  }, 16);
}
const countObs = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.querySelectorAll('.count-up').forEach(c => countUp(c, parseInt(c.dataset.target)));
      countObs.unobserve(e.target);
    }
  });
}, { threshold: 0.3 });
document.querySelectorAll('#trust').forEach(s => countObs.observe(s));

// ── TESTIMONIAL CAROUSEL
let current = 0;
const track = document.getElementById('testimonialTrack');
const dots = document.querySelectorAll('.carousel-dot');
const slides = document.querySelectorAll('.testimonial-slide');
function goTo(n) {
  current = (n + slides.length) % slides.length;
  track.style.transform = `translateX(-${current * 100}%)`;
  dots.forEach((d, i) => d.classList.toggle('active', i === current));
}
document.getElementById('prevBtn').addEventListener('click', () => goTo(current - 1));
document.getElementById('nextBtn').addEventListener('click', () => goTo(current + 1));
dots.forEach(d => d.addEventListener('click', () => goTo(+d.dataset.index)));
let autoSlide = setInterval(() => goTo(current + 1), 6000);
track.parentElement.addEventListener('mouseenter', () => clearInterval(autoSlide));
track.parentElement.addEventListener('mouseleave', () => { autoSlide = setInterval(() => goTo(current + 1), 6000); });
