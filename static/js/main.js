/* ImmigVision — JavaScript corrigé */
document.addEventListener('DOMContentLoaded', () => {

  // ── NAVBAR SCROLL ────────────────────────────────────────────
  const navbar   = document.getElementById('navbar');
  const backToTop= document.getElementById('backToTop');
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    if (navbar)    navbar.classList.toggle('scrolled', y > 40);
    if (backToTop) backToTop.classList.toggle('visible', y > 400);
  }, { passive: true });
  if (backToTop)
    backToTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

  // ── HAMBURGER ────────────────────────────────────────────────
  const hamburger = document.getElementById('hamburger');
  const navLinks  = document.getElementById('navLinks');
  if (hamburger && navLinks) {
    hamburger.addEventListener('click', (e) => {
      e.stopPropagation();
      const open = navLinks.classList.toggle('open');
      const bars = hamburger.querySelectorAll('span');
      if (open) {
        bars[0].style.cssText = 'transform:rotate(45deg) translate(5px,5px)';
        bars[1].style.cssText = 'opacity:0';
        bars[2].style.cssText = 'transform:rotate(-45deg) translate(5px,-5px)';
      } else {
        bars.forEach(b => b.style.cssText = '');
      }
    });
    document.addEventListener('click', (e) => {
      if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
        navLinks.classList.remove('open');
        hamburger.querySelectorAll('span').forEach(b => b.style.cssText = '');
      }
    });
    navLinks.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => {
        navLinks.classList.remove('open');
        hamburger.querySelectorAll('span').forEach(b => b.style.cssText = '');
      });
    });
  }

  // ── BARRE DE RECHERCHE ───────────────────────────────────────
  const searchToggle = document.getElementById('searchToggle');
  const searchBar    = document.getElementById('searchBar');
  const searchClose  = document.getElementById('searchClose');
  if (searchToggle && searchBar) {
    searchToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      const open = searchBar.classList.toggle('open');
      if (open) setTimeout(() => searchBar.querySelector('input')?.focus(), 80);
    });
    if (searchClose) searchClose.addEventListener('click', () => searchBar.classList.remove('open'));
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') searchBar.classList.remove('open');
    });
  }

  // ── FLASH AUTO-CLOSE ─────────────────────────────────────────
  document.querySelectorAll('.flash').forEach(flash => {
    setTimeout(() => {
      flash.style.transition = 'opacity .4s,transform .4s';
      flash.style.opacity = '0'; flash.style.transform = 'translateX(20px)';
      setTimeout(() => flash.remove(), 400);
    }, 5000);
  });

  // ── PASSWORD TOGGLE ──────────────────────────────────────────
  document.querySelectorAll('.toggle-pw').forEach(btn => {
    btn.addEventListener('click', () => {
      const inp = btn.previousElementSibling;
      if (!inp || inp.tagName !== 'INPUT') return;
      inp.type = inp.type === 'password' ? 'text' : 'password';
      btn.innerHTML = inp.type === 'text'
        ? '<i class="fas fa-eye-slash"></i>'
        : '<i class="fas fa-eye"></i>';
    });
  });

  // ── PASSWORD STRENGTH ────────────────────────────────────────
  const pwReg = document.getElementById('reg-password');
  const pwBar = document.getElementById('pwStrength');
  if (pwReg && pwBar) {
    pwReg.addEventListener('input', () => {
      const v = pwReg.value; let s = 0;
      if (v.length >= 8) s++; if (/[A-Z]/.test(v)) s++;
      if (/[0-9]/.test(v)) s++; if (/[^A-Za-z0-9]/.test(v)) s++;
      pwBar.style.width = ['0%','25%','50%','75%','100%'][s];
      pwBar.style.background = ['','#E74C3C','#F5A623','#F5A623','#27AE60'][s] || '';
    });
  }

  // ── SCROLL REVEAL ────────────────────────────────────────────
  if ('IntersectionObserver' in window) {
    const items = document.querySelectorAll(
      '.article-card, .why-card, .stat-block, .featured-card, .featured-main, .reveal'
    );
    items.forEach((el, i) => {
      el.style.cssText += `opacity:0;transform:translateY(18px);transition:opacity .5s ease ${i*.05}s,transform .5s ease ${i*.05}s`;
    });
    const obs = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.style.opacity = '1';
          e.target.style.transform = 'translateY(0)';
          obs.unobserve(e.target);
        }
      });
    }, { threshold: 0.07 });
    items.forEach(el => obs.observe(el));
  }

  // ── PROGRESS BAR (article) ───────────────────────────────────
  if (document.getElementById('articleBody')) {
    const bar = Object.assign(document.createElement('div'), {
      style: 'position:fixed;top:70px;left:0;height:3px;background:linear-gradient(90deg,#00C2CB,#1A3A5C);width:0%;z-index:999;pointer-events:none'
    });
    document.body.appendChild(bar);
    window.addEventListener('scroll', () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.width = max > 0 ? (window.scrollY / max * 100) + '%' : '0%';
    }, { passive: true });
  }

  // ── USER DROPDOWN ────────────────────────────────────────────
  const userMenu = document.querySelector('.user-menu');
  if (userMenu) {
    const btn = userMenu.querySelector('.user-avatar-btn');
    const dd  = userMenu.querySelector('.user-dropdown');
    if (btn && dd) {
      btn.addEventListener('click', e => { e.stopPropagation(); dd.classList.toggle('show'); });
      document.addEventListener('click', () => dd.classList.remove('show'));
    }
  }

  // ── COPY LINK ────────────────────────────────────────────────
  window.copyLink = function() {
    const btn = document.querySelector('.share-btn.copy');
    const url = window.location.href;
    const done = () => {
      if (btn) {
        const orig = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> Copié !';
        btn.style.cssText = 'background:#27AE60;color:white';
        setTimeout(() => { btn.innerHTML = orig; btn.style.cssText = ''; }, 2000);
      }
    };
    if (navigator.clipboard) {
      navigator.clipboard.writeText(url).then(done).catch(() => legacyCopy(url, done));
    } else {
      legacyCopy(url, done);
    }
  };
  function legacyCopy(text, cb) {
    const ta = document.createElement('textarea');
    ta.value = text; ta.style.cssText = 'position:fixed;opacity:0';
    document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); cb(); } catch(e) {}
    document.body.removeChild(ta);
  }

  // ── NEWSLETTER VALIDATION ────────────────────────────────────
  document.querySelectorAll('form[action="/newsletter"]').forEach(form => {
    form.addEventListener('submit', e => {
      const inp = form.querySelector('input[type="email"]');
      if (inp && !inp.value.includes('@')) {
        e.preventDefault();
        inp.style.borderColor = '#E74C3C'; inp.focus();
        setTimeout(() => inp.style.borderColor = '', 2000);
      }
    });
  });

  // NOTE : Le smooth-scroll sur ancres internes fonctionne via CSS scroll-behavior:smooth

  console.log('%c🌍 ImmigVision JS OK', 'color:#00C2CB;font-weight:bold;font-size:13px');
});
