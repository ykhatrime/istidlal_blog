document.addEventListener('DOMContentLoaded', () => {
  document.body.classList.add('page-ready');

  document.querySelectorAll('form[method="post"], form[method="POST"]').forEach(form => {
    if (window.csrfToken && !form.querySelector('input[name="csrf_token"]')) {
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = 'csrf_token';
      input.value = window.csrfToken;
      form.prepend(input);
    }
  });

  const savedTheme = localStorage.getItem('istidlal-theme');
  if (savedTheme) document.documentElement.setAttribute('data-theme', savedTheme);
  document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
    btn.textContent = document.documentElement.getAttribute('data-theme') === 'dark' ? '☀' : '☾';
    btn.addEventListener('click', () => {
      const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      if (next === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
      else document.documentElement.removeAttribute('data-theme');
      localStorage.setItem('istidlal-theme', next === 'dark' ? 'dark' : 'light');
      document.querySelectorAll('[data-theme-toggle]').forEach(b => b.textContent = next === 'dark' ? '☀' : '☾');
    });
  });

  const topbar = document.querySelector('#topbar');
  const backTop = document.querySelector('.back-to-top');
  const onScroll = () => {
    if (topbar) topbar.classList.toggle('scrolled', window.scrollY > 20);
    if (backTop) backTop.classList.toggle('show', window.scrollY > 400);
  };
  window.addEventListener('scroll', onScroll); onScroll();
  if (backTop) backTop.addEventListener('click', () => window.scrollTo({top: 0, behavior: 'smooth'}));

  const menuBtn = document.querySelector('[data-menu-toggle]');
  const nav = document.querySelector('[data-nav]');
  if (menuBtn && nav) menuBtn.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('open');
    menuBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  });

  const revealEls = document.querySelectorAll('.reveal');
  const io = new IntersectionObserver(entries => {
    entries.forEach(entry => { if (entry.isIntersecting) entry.target.classList.add('visible'); });
  }, { threshold: .12 });
  revealEls.forEach(el => io.observe(el));

  document.querySelectorAll('form.inline:not(.safe)').forEach(form => {
    form.addEventListener('submit', e => {
      const msg = document.documentElement.lang === 'ar' ? 'هل أنت متأكد من الحذف؟' : 'Are you sure you want to delete?';
      if (!confirm(msg)) e.preventDefault();
    });
  });

  document.querySelectorAll('[data-card-search]').forEach(input => {
    input.addEventListener('input', () => {
      const q = input.value.trim().toLowerCase();
      document.querySelectorAll('[data-card-grid] .card').forEach(card => {
        const hay = (card.dataset.title || card.textContent).toLowerCase();
        card.style.display = hay.includes(q) ? '' : 'none';
      });
    });
  });

  document.querySelectorAll('[data-table-search]').forEach(input => {
    input.addEventListener('input', () => {
      const q = input.value.trim().toLowerCase();
      const table = input.closest('.admin-main')?.querySelector('[data-table]');
      if (!table) return;
      table.querySelectorAll('tr').forEach((row, i) => {
        if (i === 0) return;
        row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    });
  });
});

// Interactive hero dashboard: soft tilt + animated counters
(() => {
  const card = document.querySelector('[data-tilt-card]');
  if (card) {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - .5;
      const y = (e.clientY - rect.top) / rect.height - .5;
      card.style.transform = `perspective(1000px) rotateY(${x * 8 - 8}deg) rotateX(${-y * 8 + 2}deg) translateY(-8px)`;
    });
    card.addEventListener('mouseleave', () => {
      card.style.transform = '';
    });
  }

  document.querySelectorAll('[data-count]').forEach(el => {
    const target = Number(el.dataset.count || 0);
    let current = 0;
    const step = Math.max(1, Math.ceil(target / 42));
    const timer = setInterval(() => {
      current += step;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      el.textContent = current;
    }, 28);
  });
})();
