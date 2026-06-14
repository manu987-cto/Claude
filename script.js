// Année dynamique
document.getElementById('year').textContent = new Date().getFullYear();

// Header au scroll
const header = document.getElementById('header');
window.addEventListener('scroll', () => {
  header.classList.toggle('scrolled', window.scrollY > 40);
});

// Menu mobile
const burger = document.getElementById('burger');
const nav = document.getElementById('nav');
burger.addEventListener('click', () => {
  burger.classList.toggle('open');
  nav.classList.toggle('open');
  document.body.style.overflow = nav.classList.contains('open') ? 'hidden' : '';
});
nav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
  burger.classList.remove('open');
  nav.classList.remove('open');
  document.body.style.overflow = '';
}));

// Curseur lueur
const glow = document.getElementById('cursorGlow');
window.addEventListener('mousemove', e => {
  glow.style.left = e.clientX + 'px';
  glow.style.top = e.clientY + 'px';
});

// Reveal au scroll
const io = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('in');
      io.unobserve(entry.target);
    }
  });
}, { threshold: 0.15 });
document.querySelectorAll('.reveal, .reveal-up').forEach(el => io.observe(el));

// Compteurs animés
const counters = document.querySelectorAll('[data-count]');
const counterIO = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    const el = entry.target;
    const target = +el.dataset.count;
    const suffix = el.dataset.suffix || '';
    let cur = 0;
    const step = Math.max(1, Math.ceil(target / 40));
    const tick = () => {
      cur = Math.min(target, cur + step);
      el.textContent = cur + suffix;
      if (cur < target) requestAnimationFrame(tick);
    };
    tick();
    counterIO.unobserve(el);
  });
}, { threshold: 0.6 });
counters.forEach(c => counterIO.observe(c));

// Parallaxe légère des orbes
const orbs = document.querySelectorAll('.orb');
window.addEventListener('scroll', () => {
  const y = window.scrollY;
  orbs.forEach((orb, i) => {
    orb.style.transform = `translateY(${y * (0.05 + i * 0.03)}px)`;
  });
}, { passive: true });

/* ===== Lightbox plein écran ===== */
(function(){
  const imgs = document.querySelectorAll('img.zoomable');
  if(!imgs.length) return;
  const box = document.createElement('div');
  box.className = 'lightbox';
  box.innerHTML = '<button class="lb-close" aria-label="Fermer">×</button><button class="lb-nav lb-prev" aria-label="Précédent">‹</button><img alt="Réalisation Ongles by Sarah"><button class="lb-nav lb-next" aria-label="Suivant">›</button>';
  document.body.appendChild(box);
  const lbImg = box.querySelector('img');
  const list = [...imgs];
  let idx = 0;
  function show(i){ idx = (i + list.length) % list.length; lbImg.src = list[idx].src; }
  function open(i){ show(i); box.classList.add('open'); document.body.style.overflow = 'hidden'; }
  function close(){ box.classList.remove('open'); document.body.style.overflow = ''; }
  list.forEach((im, i) => {
    im.style.cursor = 'zoom-in';
    im.addEventListener('click', () => open(i));
    im.addEventListener('keydown', e => { if(e.key === 'Enter' || e.key === ' '){ e.preventDefault(); open(i); } });
  });
  box.querySelector('.lb-close').addEventListener('click', close);
  box.querySelector('.lb-next').addEventListener('click', e => { e.stopPropagation(); show(idx + 1); });
  box.querySelector('.lb-prev').addEventListener('click', e => { e.stopPropagation(); show(idx - 1); });
  box.addEventListener('click', e => { if(e.target === box) close(); });
  document.addEventListener('keydown', e => {
    if(!box.classList.contains('open')) return;
    if(e.key === 'Escape') close();
    if(e.key === 'ArrowRight') show(idx + 1);
    if(e.key === 'ArrowLeft') show(idx - 1);
  });
})();

/* ===== Formulaire de devis ===== */
(function(){
  const form = document.getElementById('quoteForm');
  if(!form) return;
  const WHATSAPP = '33669614755';
  const checks = [...form.querySelectorAll('.opt input[type=checkbox]')];
  const totalEl = document.getElementById('quoteTotal');
  const depositEl = document.getElementById('quoteDeposit');
  const noteEl = document.getElementById('quoteNote');
  const DEPOSIT_RATE = 0.15;
  const deposit = total => Math.round(total * DEPOSIT_RATE);

  function selected(){
    const items = []; let total = 0; let devis = false;
    checks.forEach(c => {
      if(!c.checked) return;
      const p = parseInt(c.dataset.price, 10) || 0;
      if(p > 0){ total += p; items.push(c.dataset.name + ' — ' + p + ' €'); }
      else { devis = true; items.push(c.dataset.name + ' — sur devis'); }
    });
    return { items, total, devis };
  }
  function update(){
    const { items, total, devis } = selected();
    totalEl.textContent = total + ' €';
    if(depositEl) depositEl.textContent = deposit(total) + ' €';
    noteEl.textContent = devis ? '+ certaines prestations sur devis' : (items.length ? '' : 'Sélectionnez vos prestations ci-dessus.');
  }
  checks.forEach(c => c.addEventListener('change', update));
  update();

  form.addEventListener('submit', e => {
    e.preventDefault();
    const f = form.elements;
    const { items, total, devis } = selected();
    if(!items.length){
      noteEl.textContent = 'Merci de sélectionner au moins une prestation.';
      form.querySelector('.qf-select').scrollIntoView({ behavior:'smooth', block:'center' });
      return;
    }
    let msg = 'Bonjour Sarah, je souhaite une demande / un devis :\n\n';
    msg += 'Prestations :\n' + items.map(i => '• ' + i).join('\n') + '\n\n';
    msg += 'Total estimé : ' + total + ' €' + (devis ? ' (+ sur devis)' : '') + '\n';
    msg += 'Acompte (15 %) pour bloquer le RDV : ' + deposit(total) + ' €\n\n';
    msg += 'Nom : ' + (f.nom.value || '-') + '\n';
    msg += 'Téléphone : ' + (f.tel.value || '-') + '\n';
    if(f.email.value) msg += 'E-mail : ' + f.email.value + '\n';
    if(f.date.value) msg += 'Date souhaitée : ' + f.date.value + '\n';
    if(f.message.value) msg += 'Message : ' + f.message.value + '\n';
    window.open('https://wa.me/' + WHATSAPP + '?text=' + encodeURIComponent(msg), '_blank');
  });
})();
