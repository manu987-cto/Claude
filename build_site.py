#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère le site multi-pages Ongles_by.Sarah à partir du CSV Planity."""
import csv, html, os

CSV = "/root/.claude/uploads/e84ceb8e-2af7-54be-9c87-766715a2180f/8eef9a42-planitycom20260614.csv"
PLANITY = "https://www.planity.com/ongles_bysarah-56000-vannes"
INSTA = "https://www.instagram.com/ongles_by.sarah"

# ---------------------------------------------------------------- parse CSV
def clean_price(*vals):
    for v in vals:
        v = (v or "").strip()
        if "€" in v:
            return v.replace(" ", " ").strip()
        if "devis" in v.lower():
            return "Sur devis"
        if v.lower() == "de":
            return "Sur devis"
    return ""

services = {}  # id -> dict
with open(CSV, newline="", encoding="utf-8-sig") as f:
    r = csv.DictReader(f)
    for row in r:
        sid = int(row["web_scraper_order"].split("-")[-1])
        name = (row["name"] or "").strip()
        duration = (row["data"] or "").strip()
        desc = (row["data2"] or "").strip()
        price = clean_price(row["data3"], row["data4"])
        blob = " ".join((row.get(k) or "") for k in ("data4", "data5", "data6"))
        bookable = "ne peut pas être réservée en ligne" not in blob
        services[sid] = dict(name=name, dur=duration, desc=desc,
                             price=price, bookable=bookable)

# ---------------------------------------------------------------- classify
ongles_ids = set(range(7, 32)) | {74, 77}
regard_ids = {48, 49, 50, 51, 52, 53}
cils_ids = (set(range(32, 74)) - regard_ids) | {75, 76}
infos_ids = {1, 2, 3, 4, 5, 6}

CATS = [
    ("Prothésie ongulaire", "Pose gel, remplissage, nail art, semi-permanent et soins des ongles.", sorted(ongles_ids)),
    ("Extensions de cils", "Cil à cil, volume russe, hybride et effets sur-mesure pour un regard envoûtant.", sorted(cils_ids)),
    ("Rehaussement & sourcils", "Rehaussement de cils, browlift, teinture : sublimez votre regard au naturel.", sorted(regard_ids)),
]

def card(s):
    badge = "" if s["bookable"] else '<span class="card-tag">Sur rendez-vous tél.</span>'
    desc = ""
    if s["desc"]:
        d = html.escape(s["desc"]).replace("\n", " ").strip()
        if len(d) > 230:
            d = d[:227].rsplit(" ", 1)[0] + "…"
        desc = f'<p class="card-desc">{d}</p>'
    dur = f'<span class="card-dur">⏱ {html.escape(s["dur"])}</span>' if s["dur"] and s["dur"] != "1min" else ""
    price = f'<span class="card-price">{html.escape(s["price"])}</span>' if s["price"] else '<span class="card-price muted">Sur devis</span>'
    return f"""        <article class="prest-card reveal-up">
          <div class="card-top"><h3>{html.escape(s['name'])}</h3>{price}</div>
          <div class="card-meta">{dur}{badge}</div>
          {desc}
        </article>"""

def prest_sections():
    out = []
    for title, sub, ids in CATS:
        cards = "\n".join(card(services[i]) for i in ids if i in services)
        out.append(f"""    <section class="prest-section">
      <div class="section-head">
        <p class="eyebrow reveal-up">{html.escape(title)}</p>
        <h2 class="reveal-up">{html.escape(title)}</h2>
        <p class="reveal-up sub">{html.escape(sub)}</p>
      </div>
      <div class="prest-grid">
{cards}
      </div>
    </section>""")
    # infos box
    infos = "".join(f"<li>{html.escape(services[i]['name'])}</li>" for i in sorted(infos_ids) if i in services and not services[i]['name'].lower().startswith('instagram'))
    out.append(f"""    <section class="prest-section">
      <div class="infos-box reveal-up">
        <h3>À savoir avant votre rendez-vous</h3>
        <ul>{infos}</ul>
        <p>Le règlement intérieur complet et les conditions d'acompte sont disponibles sur Planity lors de la réservation.</p>
      </div>
    </section>""")
    return "\n".join(out)

# ---------------------------------------------------------------- shared bits
def head(title, desc, rel=""):
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc)}" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=Jost:wght@300;400;500;600&display=swap" rel="stylesheet" />
  <link rel="icon" type="image/png" href="assets/logo.png" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <div class="cursor-glow" id="cursorGlow"></div>"""

NAV = [("index.html", "Accueil"), ("prestations.html", "Prestations"),
       ("galerie.html", "Galerie"), ("avis.html", "Avis"), ("contact.html", "Contact")]

def header(active):
    items = []
    for href, label in NAV:
        cls = ' class="active"' if href == active else ''
        items.append(f'      <a href="{href}"{cls}>{label}</a>')
    links = "\n".join(items)
    return f"""  <header class="header" id="header">
    <a href="index.html" class="brand">
      <img class="brand-logo" src="assets/logo.png" alt="Logo Ongles by Sarah" />
      <span class="brand-text">Ongles<span class="dot">_by.</span>Sarah</span>
    </a>
    <nav class="nav" id="nav">
{links}
      <a href="{PLANITY}" target="_blank" rel="noopener" class="nav-cta">Réserver</a>
    </nav>
    <button class="burger" id="burger" aria-label="Menu">
      <span></span><span></span><span></span>
    </button>
  </header>"""

def footer():
    return f"""  <footer class="footer">
    <div class="footer-brand">
      <img class="footer-logo" src="assets/logo.png" alt="Ongles by Sarah" />
    </div>
    <p>Salon de manucure &amp; prothésie ongulaire · Parc Pompidou, 56000 Vannes</p>
    <div class="footer-links">
      <a href="tel:+33669614755">06 69 61 47 55</a>
      <a href="{INSTA}" target="_blank" rel="noopener">@ongles_by.sarah</a>
      <a href="{PLANITY}" target="_blank" rel="noopener">Réserver sur Planity</a>
    </div>
    <p class="copy">© <span id="year"></span> Ongles_by.Sarah — Tous droits réservés.</p>
  </footer>
  <script src="script.js"></script>
</body>
</html>"""

def page_hero(eyebrow, title, sub):
    return f"""  <section class="page-hero">
    <div class="page-hero-overlay"></div>
    <div class="page-hero-content">
      <p class="hero-eyebrow reveal">{html.escape(eyebrow)}</p>
      <h1 class="reveal" style="--d:.1s">{html.escape(title)}</h1>
      <p class="reveal" style="--d:.25s">{html.escape(sub)}</p>
    </div>
  </section>"""

# ---------------------------------------------------------------- gallery items
LASH = {2, 8, 13, 16, 17}
NAIL_CAPS = ["Nude élégant", "Nail art", "French moderne", "Bijoux dorés",
             "Pose gel", "Chrome doré", "Finition raffinée", "Sur-mesure",
             "Élégance dorée", "Bleu intense", "Création unique", "Détail précieux"]
def gallery_items(ids, tall_lash=True):
    out = []
    ni = 0
    for n in ids:
        fn = f"assets/gallery/g{n:02d}.jpg"
        if not os.path.exists(fn):
            continue
        if n in LASH:
            cap = "Beauté du regard"
            cls = "g-item tall" if tall_lash else "g-item"
        else:
            cap = NAIL_CAPS[ni % len(NAIL_CAPS)]; ni += 1
            cls = "g-item"
        out.append(f'      <figure class="{cls} reveal-up"><img src="{fn}" alt="{cap} — Ongles by Sarah" loading="lazy"><figcaption>{cap}</figcaption></figure>')
    return "\n".join(out)

# ================================================================ build pages
os.makedirs("assets", exist_ok=True)

# ---------- INDEX
hero_cats = "".join(f"""        <a href="prestations.html" class="cat-card reveal-up">
          <span class="cat-ico">{ico}</span>
          <h3>{t}</h3>
          <p>{d}</p>
          <span class="cat-link">Voir les tarifs →</span>
        </a>\n""" for t, d, ico in [
    ("Prothésie ongulaire", "Pose gel, remplissage, nail art &amp; soins.", "✦"),
    ("Extensions de cils", "Cil à cil, volume russe, effets sur-mesure.", "❋"),
    ("Rehaussement &amp; sourcils", "Rehaussement, browlift, teinture.", "♛")])

index = f"""{head('Ongles_by.Sarah — Salon de manucure & cils de luxe à Vannes',
                  'Ongles_by.Sarah, salon de manucure, prothésie ongulaire et extensions de cils à Vannes. 5,0★ sur 8 avis. Réservez en ligne sur Planity.')}
{header('index.html')}
  <section class="hero" id="accueil">
    <div class="hero-photo"></div>
    <div class="hero-bg"></div>
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
    <div class="hero-content">
      <img class="hero-logo reveal" src="assets/logo.png" alt="Ongles by Sarah — Nails and Lashes" />
      <p class="hero-eyebrow reveal" style="--d:.05s">Salon de manucure &amp; cils · Vannes</p>
      <h1 class="hero-title">
        <span class="reveal" style="--d:.1s">L'art de</span>
        <span class="reveal italic" style="--d:.25s">sublimer</span>
        <span class="reveal" style="--d:.4s">vos mains &amp; votre regard</span>
      </h1>
      <p class="hero-sub reveal" style="--d:.55s">
        Prothésie ongulaire &amp; beauté du regard. Un travail propre, soigné et passionné,
        pensé pour révéler votre élégance naturelle.
      </p>
      <div class="hero-actions reveal" style="--d:.7s">
        <a href="{PLANITY}" target="_blank" rel="noopener" class="btn btn-primary">Réserver en ligne</a>
        <a href="prestations.html" class="btn btn-ghost">Nos prestations</a>
      </div>
      <div class="hero-rating reveal" style="--d:.85s">
        <span class="stars">★★★★★</span>
        <span><strong>5,0</strong> · 8 avis Google</span>
      </div>
    </div>
    <div class="scroll-hint"><span></span></div>
  </section>

  <div class="marquee">
    <div class="marquee-track">
      <span>Manucure ✦ Prothésie ongulaire ✦ Gel ✦ Nail Art ✦ Extension de cils ✦ Volume russe ✦ Rehaussement ✦ Browlift ✦</span>
      <span>Manucure ✦ Prothésie ongulaire ✦ Gel ✦ Nail Art ✦ Extension de cils ✦ Volume russe ✦ Rehaussement ✦ Browlift ✦</span>
    </div>
  </div>

  <section class="about" id="apropos">
    <div class="about-visual reveal-up">
      <div class="about-card">
        <img class="about-figure" src="assets/gallery/g15.jpg" alt="Réalisation Ongles by Sarah" loading="lazy" />
        <div class="badge-woman">♀ Géré par une femme</div>
      </div>
    </div>
    <div class="about-text">
      <p class="eyebrow reveal-up">À propos</p>
      <h2 class="reveal-up">Une passion devenue savoir-faire</h2>
      <p class="reveal-up">Depuis plusieurs années, Sarah accompagne sa clientèle vannetaise avec douceur, patience et exigence. Chaque pose est une création unique, réalisée avec des produits de qualité et un sens du détail irréprochable.</p>
      <p class="reveal-up">Douce, passionnée et à l'écoute, elle met un point d'honneur à offrir une expérience aussi soignée que ses ongles. Une fidélité que ses clientes lui rendent bien, année après année.</p>
      <div class="stats">
        <div class="stat reveal-up"><strong data-count="3">0</strong><span>ans d'expertise +</span></div>
        <div class="stat reveal-up"><strong data-count="5" data-suffix=",0">0</strong><span>note moyenne</span></div>
        <div class="stat reveal-up"><strong data-count="100">0</strong><span>% sur-mesure</span></div>
      </div>
    </div>
  </section>

  <section class="services">
    <div class="section-head">
      <p class="eyebrow reveal-up">Prestations</p>
      <h2 class="reveal-up">L'excellence du bout des doigts</h2>
    </div>
    <div class="cat-cards">
{hero_cats}    </div>
    <div class="center-cta reveal-up"><a href="prestations.html" class="btn btn-primary">Toutes les prestations &amp; tarifs</a></div>
  </section>

  <section class="gallery">
    <div class="section-head">
      <p class="eyebrow reveal-up">Galerie</p>
      <h2 class="reveal-up">Quelques inspirations</h2>
    </div>
    <div class="gallery-grid">
{gallery_items([3,7,16,12,15,18,17,19])}
    </div>
    <div class="center-cta reveal-up"><a href="galerie.html" class="btn btn-ghost">Voir toute la galerie</a></div>
  </section>

  <section class="reviews">
    <div class="section-head">
      <p class="eyebrow reveal-up">Avis vérifiés Google</p>
      <h2 class="reveal-up">Elles parlent de Sarah</h2>
      <div class="reviews-score reveal-up">
        <span class="big">5,0</span><span class="stars">★★★★★</span><span class="count">8 avis</span>
      </div>
    </div>
    <div class="reviews-grid">
      <blockquote class="review reveal-up"><div class="stars">★★★★★</div><p>« Je recommande Sarah les yeux fermés ! Travail toujours propre et soigné, très professionnel. Cela fait plus de 3 ans que je vais chez Sarah. »</p><footer><span class="avatar">IH</span><span><strong>Ines Huan</strong><small>il y a 10 mois</small></span></footer></blockquote>
      <blockquote class="review reveal-up"><div class="stars">★★★★★</div><p>« DE LOIN la number one dans la pause et l'entretien de cils 😍 Sarah est une jeune femme douce, passionnée et à l'écoute de sa clientèle. »</p><footer><span class="avatar">MR</span><span><strong>M Rv</strong><small>Local Guide · il y a 10 mois</small></span></footer></blockquote>
      <blockquote class="review reveal-up"><div class="stars">★★★★★</div><p>« Ça fait deux ans que Sarah fait mes ongles. Sarah s'est armée de patience avec moi et fait un boulot de dingue ! »</p><footer><span class="avatar">SL</span><span><strong>Solenn Liard</strong><small>il y a 10 mois</small></span></footer></blockquote>
    </div>
    <div class="center-cta reveal-up"><a href="avis.html" class="btn btn-ghost">Tous les avis</a></div>
  </section>

  <section class="cta-band">
    <div class="cta-inner reveal-up">
      <h2>Offrez-vous un moment rien qu'à vous</h2>
      <p>Réservez en quelques clics sur Planity ou contactez Sarah directement.</p>
      <div class="hero-actions">
        <a href="{PLANITY}" target="_blank" rel="noopener" class="btn btn-primary">Réserver en ligne</a>
        <a href="contact.html" class="btn btn-ghost">Nous contacter</a>
      </div>
    </div>
  </section>
{footer()}"""

# ---------- PRESTATIONS
prestations = f"""{head('Prestations & tarifs — Ongles_by.Sarah Vannes',
                        'Toutes les prestations et tarifs Ongles_by.Sarah : prothésie ongulaire, extensions de cils, volume russe, rehaussement et sourcils à Vannes.')}
{header('prestations.html')}
{page_hero('Prestations & tarifs', 'Nos prestations', 'Ongles, cils et regard — des créations sur-mesure réalisées avec passion. Réservation en ligne sur Planity.')}
  <main class="prest-main">
{prest_sections()}
    <section class="cta-band">
      <div class="cta-inner reveal-up">
        <h2>Prête à vous faire chouchouter ?</h2>
        <p>Réservez votre créneau en ligne, 7j/7.</p>
        <a href="{PLANITY}" target="_blank" rel="noopener" class="btn btn-primary">Réserver sur Planity</a>
      </div>
    </section>
  </main>
{footer()}"""

# ---------- GALERIE
galerie = f"""{head('Galerie — Ongles_by.Sarah Vannes',
                    'Galerie des réalisations Ongles_by.Sarah : poses gel, nail art, extensions de cils et rehaussement à Vannes.')}
{header('galerie.html')}
{page_hero('Galerie', 'Nos réalisations', 'Un aperçu du travail de Sarah : ongles et beauté du regard.')}
  <section class="gallery">
    <div class="gallery-grid full">
{gallery_items(list(range(1,23)), tall_lash=False)}
    </div>
    <div class="center-cta reveal-up"><a href="{INSTA}" target="_blank" rel="noopener" class="btn btn-ghost">Suivre sur Instagram</a></div>
  </section>
{footer()}"""

# ---------- AVIS
avis = f"""{head('Avis clients — Ongles_by.Sarah Vannes',
                 'Les avis clients Ongles_by.Sarah : 5,0★ sur 8 avis Google. Découvrez les témoignages.')}
{header('avis.html')}
{page_hero('Avis clients', 'Elles parlent de Sarah', '5,0 ★ sur 8 avis Google — une clientèle fidèle et conquise.')}
  <section class="reviews">
    <div class="section-head">
      <div class="reviews-score reveal-up">
        <span class="big">5,0</span><span class="stars">★★★★★</span><span class="count">8 avis Google</span>
      </div>
    </div>
    <div class="reviews-grid">
      <blockquote class="review reveal-up"><div class="stars">★★★★★</div><p>« Je recommande Sarah les yeux fermés ! Travail toujours propre et soigné, très professionnel. Cela fait maintenant plus de 3 ans que je vais chez Sarah et jamais déçue. »</p><footer><span class="avatar">IH</span><span><strong>Ines Huan</strong><small>7 avis · il y a 10 mois</small></span></footer></blockquote>
      <blockquote class="review reveal-up"><div class="stars">★★★★★</div><p>« C'est pour moi DE LOIN la number one dans la pose et l'entretien de cils 😍 Sarah est une jeune femme douce, passionnée et à l'écoute de sa clientèle. Je lui confie mes cils les yeux fermés ! »</p><footer><span class="avatar">MR</span><span><strong>M Rv</strong><small>Local Guide · 21 avis · il y a 10 mois</small></span></footer></blockquote>
      <blockquote class="review reveal-up"><div class="stars">★★★★★</div><p>« Ça fait deux ans que Sarah fait mes ongles. En toute sincérité, Sarah s'est armée de patience avec moi et fait un boulot de dingue ! Je la remercie énormément de sa fidélité et de son investissement. »</p><footer><span class="avatar">SL</span><span><strong>Solenn Liard</strong><small>4 avis · il y a 10 mois</small></span></footer></blockquote>
    </div>
    <div class="center-cta reveal-up"><a href="{PLANITY}" target="_blank" rel="noopener" class="btn btn-primary">Réserver à mon tour</a></div>
  </section>
{footer()}"""

# ---------- CONTACT
contact = f"""{head('Contact & Réservation — Ongles_by.Sarah Vannes',
                    'Contact et réservation Ongles_by.Sarah à Vannes : téléphone, adresse, Instagram et réservation en ligne Planity.')}
{header('contact.html')}
{page_hero('Contact & Réservation', 'Prenons rendez-vous', 'Réservez en ligne sur Planity ou contactez Sarah directement.')}
  <section class="contact">
    <div class="contact-inner">
      <div class="contact-text">
        <div class="planity-cta reveal-up">
          <h2>Réserver en ligne</h2>
          <p>Réservation simple et rapide, disponible 7j/7 sur Planity.</p>
          <a href="{PLANITY}" target="_blank" rel="noopener" class="btn btn-primary big">Réserver sur Planity</a>
        </div>
        <div class="contact-list">
          <a class="contact-row reveal-up" href="tel:+33669614755"><span class="ci">☎</span><span><small>Téléphone</small>06 69 61 47 55</span></a>
          <a class="contact-row reveal-up" href="https://maps.google.com/?q=Parc+Pompidou,+56000+Vannes" target="_blank" rel="noopener"><span class="ci">⌖</span><span><small>Adresse</small>Parc Pompidou, 56000 Vannes</span></a>
          <a class="contact-row reveal-up" href="{INSTA}" target="_blank" rel="noopener"><span class="ci">❋</span><span><small>Instagram</small>@ongles_by.sarah</span></a>
          <div class="contact-row reveal-up"><span class="ci">✦</span><span><small>Plus Code</small>M67M+3C Vannes</span></div>
        </div>
      </div>
      <div class="contact-map reveal-up">
        <iframe title="Localisation Ongles_by.Sarah" src="https://www.google.com/maps?q=Parc%20Pompidou%2C%2056000%20Vannes&output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
      </div>
    </div>
  </section>
{footer()}"""

for fn, content in [("index.html", index), ("prestations.html", prestations),
                    ("galerie.html", galerie), ("avis.html", avis), ("contact.html", contact)]:
    with open(fn, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", fn, len(content), "bytes")

print("services parsed:", len(services))
