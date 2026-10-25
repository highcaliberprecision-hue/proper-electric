/* Proper Electric — site behaviour
   Every block is null-guarded: this file is shared by index, faq,
   service-areas and every /services page. */

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// ---------- nav scroll state ----------
const nav = document.getElementById('nav');
if (nav) {
  const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 40);
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

// ---------- mobile menu ----------
const burger = document.getElementById('navBurger');
const mobile = document.getElementById('navMobile');
if (burger && mobile) {
  const setMenu = (open) => {
    mobile.classList.toggle('open', open);
    burger.setAttribute('aria-expanded', String(open));
  };
  burger.addEventListener('click', () => setMenu(!mobile.classList.contains('open')));
  mobile.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setMenu(false)));
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && mobile.classList.contains('open')) {
      setMenu(false);
      burger.focus();
    }
  });
}

// ---------- cursor glow ----------
const glow = document.getElementById('cursorGlow');
if (glow && !reduceMotion) {
  window.addEventListener('mousemove', (e) => {
    glow.style.left = e.clientX + 'px';
    glow.style.top = e.clientY + 'px';
  }, { passive: true });
}

// ---------- reveal on scroll ----------
const revealEls = document.querySelectorAll('.reveal-up');
if (revealEls.length) {
  if (reduceMotion || !('IntersectionObserver' in window)) {
    revealEls.forEach(el => el.classList.add('in'));
  } else {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach(el => io.observe(el));
  }
}

// ---------- animated counters ----------
const counters = document.querySelectorAll('.stat-num');
if (counters.length) {
  const paint = (el) => {
    el.textContent = (el.dataset.count || '0') + (el.dataset.suffix || '');
  };
  if (reduceMotion || !('IntersectionObserver' in window)) {
    counters.forEach(paint);
  } else {
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
  }
}

// ---------- gallery lightbox ----------
const lightbox = document.getElementById('lightbox');
if (lightbox) {
  const lightboxImg = document.getElementById('lightboxImg');
  const lightboxCaption = document.getElementById('lightboxCaption');
  const lightboxClose = document.getElementById('lightboxClose');
  let lastFocused = null;

  function openLightbox(item) {
    const img = item.querySelector('img');
    lightboxImg.src = img.src;
    lightboxImg.alt = img.alt;
    lightboxCaption.textContent = item.dataset.caption || '';
    lastFocused = item;
    lightbox.hidden = false;
    lightbox.classList.add('open');
    document.body.style.overflow = 'hidden';
    lightboxClose.focus();
  }

  function closeLightbox() {
    if (!lightbox.classList.contains('open')) return;
    lightbox.classList.remove('open');
    lightbox.hidden = true;
    document.body.style.overflow = '';
    if (lastFocused) lastFocused.focus();
  }

  document.querySelectorAll('.gallery-item').forEach(item => {
    item.addEventListener('click', () => openLightbox(item));
  });

  lightboxClose.addEventListener('click', closeLightbox);
  lightbox.addEventListener('click', (e) => { if (e.target === lightbox) closeLightbox(); });
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeLightbox();
    // keep focus inside the dialog while it is open
    if (e.key === 'Tab' && lightbox.classList.contains('open')) {
      e.preventDefault();
      lightboxClose.focus();
    }
  });
}

// ---------- FAQ accordion ----------
document.querySelectorAll('.faq-item').forEach(item => {
  const q = item.querySelector('.faq-q');
  if (!q) return;
  q.addEventListener('click', () => {
    const wasOpen = item.classList.contains('open');
    document.querySelectorAll('.faq-item.open').forEach(o => {
      o.classList.remove('open');
      const ob = o.querySelector('.faq-q');
      if (ob) ob.setAttribute('aria-expanded', 'false');
    });
    if (!wasOpen) {
      item.classList.add('open');
      q.setAttribute('aria-expanded', 'true');
    }
  });
});

// ---------- contact form ----------
/* Set FORM_ENDPOINT to a real POST endpoint (Formspree, Web3Forms, a
   Supabase edge function, whatever) and submissions go straight there.
   While it is empty the form opens a pre-filled email instead, so a
   lead is never silently dropped. */
const FORM_ENDPOINT = '';
const INBOX = 'properelectric@gmail.com';

const form = document.getElementById('quoteForm');
const note = document.getElementById('formNote');

if (form && note) {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const invalid = form.querySelector(':invalid');
    if (invalid) {
      note.textContent = 'Please fill in every field so we can call you back.';
      invalid.focus();
      return;
    }

    const data = Object.fromEntries(new FormData(form).entries());
    const submit = form.querySelector('button[type="submit"]');
    if (submit) submit.disabled = true;

    if (FORM_ENDPOINT) {
      try {
        const res = await fetch(FORM_ENDPOINT, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error(res.status);
        note.textContent = "Got it — we'll call you back within the hour.";
        form.reset();
      } catch (err) {
        note.innerHTML = 'That did not send. Please call <a href="tel:8477444625">(847) 744-4625</a>.';
      } finally {
        if (submit) submit.disabled = false;
      }
      return;
    }

    const body = [
      'Name: ' + (data.name || ''),
      'Phone: ' + (data.phone || ''),
      'Email: ' + (data.email || ''),
      'Address: ' + (data.address || ''),
      'Service: ' + (data.service || '')
    ].join('\n');

    window.location.href = 'mailto:' + INBOX
      + '?subject=' + encodeURIComponent('Quote request — ' + (data.service || 'electrical work'))
      + '&body=' + encodeURIComponent(body);

    note.innerHTML = 'Opening your email app to send this over. Prefer to talk? Call <a href="tel:8477444625">(847) 744-4625</a>.';
    if (submit) submit.disabled = false;
  });
}

// ---------- hero parallax ----------
const hero = document.getElementById('top');
if (hero && hero.classList.contains('hero') && !reduceMotion) {
  let ticking = false;
  const apply = () => {
    const r = hero.getBoundingClientRect();
    const p = Math.min(Math.max(-r.top / (r.height || 1), 0), 1);
    hero.style.setProperty('--p', p.toFixed(4));
    ticking = false;
  };
  window.addEventListener('scroll', () => {
    if (!ticking) { ticking = true; requestAnimationFrame(apply); }
  }, { passive: true });
  window.addEventListener('resize', apply, { passive: true });
  apply();
}
