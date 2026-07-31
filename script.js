// ---------- nav scroll state ----------
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 40);
}, { passive: true });

// ---------- mobile menu ----------
const burger = document.getElementById('navBurger');
const mobile = document.getElementById('navMobile');
burger.addEventListener('click', () => {
  mobile.classList.toggle('open');
});
mobile.querySelectorAll('a').forEach(a => a.addEventListener('click', () => mobile.classList.remove('open')));

// ---------- cursor glow ----------
const glow = document.getElementById('cursorGlow');
window.addEventListener('mousemove', (e) => {
  glow.style.left = e.clientX + 'px';
  glow.style.top = e.clientY + 'px';
}, { passive: true });

// ---------- reveal on scroll ----------
const revealEls = document.querySelectorAll('.reveal-up');
const io = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('in');
      io.unobserve(entry.target);
    }
  });
}, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });
revealEls.forEach(el => io.observe(el));

// ---------- animated counters ----------
const counters = document.querySelectorAll('.stat-num');
const countIO = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    const el = entry.target;
    const target = parseInt(el.dataset.count, 10);
    const suffix = el.dataset.suffix || '';
    const duration = 1400;
    const start = performance.now();
    function tick(now) {
      const p = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(eased * target) + suffix;
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
    countIO.unobserve(el);
  });
}, { threshold: 0.4 });
counters.forEach(el => countIO.observe(el));

// ---------- FAQ accordion ----------
document.querySelectorAll('.faq-item').forEach(item => {
  const q = item.querySelector('.faq-q');
  q.addEventListener('click', () => {
    const wasOpen = item.classList.contains('open');
    document.querySelectorAll('.faq-item.open').forEach(o => o.classList.remove('open'));
    if (!wasOpen) item.classList.add('open');
  });
});

// ---------- contact form ----------
const form = document.getElementById('quoteForm');
const note = document.getElementById('formNote');
form.addEventListener('submit', (e) => {
  e.preventDefault();
  note.textContent = "Thanks — we'll call you back within the hour.";
  form.reset();
});

// ---------- hero title char reveal ----------
window.addEventListener('load', () => {
  document.querySelectorAll('.hero-title .reveal').forEach((line, i) => {
    line.style.transform = 'translateY(110%)';
    line.style.opacity = '0';
    line.style.transition = `transform .9s cubic-bezier(.16,1,.3,1) ${0.15 + i * 0.12}s, opacity .9s ${0.15 + i * 0.12}s`;
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        line.style.transform = 'translateY(0)';
        line.style.opacity = '1';
      });
    });
  });
});
