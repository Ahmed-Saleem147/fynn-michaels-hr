"""Builds the site's HTML pages from the page bodies in src/.

Each page gets the shared top bar, header, footer and SEO tags.
Edit the content in src/*.html (or the details below), then run:

    python build.py

and commit the regenerated .html files in the project root.
"""
from datetime import date
from pathlib import Path
import json

ROOT = Path(__file__).parent
SRC = ROOT / "src"

# ---------------------------------------------------------------- details
SITE_URL = "https://fynn-michealshrsolutions.com"   # live domain (used for canonical links and sitemap)
NAME = "Fynn-Micheals HR Solutions"
TAGLINE = "People. Performance. Progress."
# Forwards to fynnmichealshrsolutions@gmail.com via Cloudflare Email Routing.
EMAIL = "hrsolutions@fynn-michealshrsolutions.com"
PHONE_DISPLAY = "+233 24 444 6466"
PHONE_LINK = "+233244446466"
LOCATION = "Accra, Ghana"                  # PLACEHOLDER: confirm city
HOURS = "Mon &ndash; Fri, 8:00 &ndash; 17:00"  # PLACEHOLDER

SERVICES = [
    ("startup-hr.html", "Startup HR Foundation"),
    ("outsourced-hr.html", "Outsourced HR Department"),
    ("recruitment.html", "Recruitment &amp; Talent Acquisition"),
    ("hr-audit.html", "HR Audit &amp; Business Advisory"),
    ("hr-policies.html", "HR Policies &amp; Contracts"),
]

# file, SEO title, meta description, nav group
PAGES = [
    ("index.html",
     "HR Consulting &amp; Outsourcing for Startups in Ghana | Fynn-Micheals",
     "Fynn-Micheals HR Solutions helps startups and small businesses in Ghana set up HR, "
     "outsource HR administration, recruit the right people and fix people-management problems.",
     "home"),
    ("startup-hr.html",
     "Startup HR Services &amp; HR Setup in Ghana | Fynn-Micheals",
     "Hiring your first employees in Ghana? We set up your HR policies, employee handbook, "
     "contracts, job descriptions, organisational structure and onboarding.",
     "services"),
    ("outsourced-hr.html",
     "Outsourced HR Services for Small Businesses | Fynn-Micheals",
     "Your HR department without the full-time cost: monthly HR administration, employee relations, "
     "leave and attendance, performance management and HR reporting.",
     "services"),
    ("recruitment.html",
     "Recruitment &amp; Talent Acquisition Services in Ghana | Fynn-Micheals",
     "End-to-end recruitment for growing teams in Ghana: recruitment planning, job adverts, "
     "candidate screening, interview coordination, reference checks and placement.",
     "services"),
    ("hr-policies.html",
     "HR Policies, Contracts &amp; Employee Handbooks | Fynn-Micheals",
     "Clear, compliant HR policies, employment contracts and employee handbooks written for "
     "businesses in Ghana and aligned with the Labour Act.",
     "services"),
    ("hr-audit.html",
     "HR Audit &amp; Consulting Services for Businesses | Fynn-Micheals",
     "HR health checks, workforce assessments, HR process reviews, productivity systems and "
     "organisational restructuring for businesses facing people-management problems.",
     "services"),
    ("about.html",
     "About Fynn-Micheals HR Solutions",
     "Fynn-Micheals HR Solutions is a Ghana-based HR consultancy helping startups and small "
     "businesses build fair, workable HR. People. Performance. Progress.",
     "about"),
    ("contact.html",
     "Contact an HR Consultant in Ghana | Fynn-Micheals",
     "Speak to an HR consultant at Fynn-Micheals HR Solutions in Ghana. Call, email or send "
     "an enquiry and we'll reply within one working day.",
     "contact"),
]

# ---------------------------------------------------------------- icons
ICON_MAIL = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="1"/><path d="m3 7 9 6 9-6"/></svg>'
ICON_PHONE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1 1A16 16 0 0 1 4 5a1 1 0 0 1 1-1z"/></svg>'
ICON_PIN = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>'
ICON_CLOCK = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>'


def page_url(file):
    return SITE_URL + "/" if file == "index.html" else f"{SITE_URL}/{file}"


def header(current_file, group):
    def cls(g):
        return ' class="active"' if g == group else ""

    active = ' class="active"'
    sub = "\n".join(
        f'            <li><a href="{f}"{active if f == current_file else ""}>{label}</a></li>'
        for f, label in SERVICES
    )
    return f"""  <div class="topbar">
    <div class="wrap topbar-inner">
      <div class="topbar-info">
        <a href="mailto:{EMAIL}">{ICON_MAIL} {EMAIL}</a>
        <a href="tel:{PHONE_LINK}">{ICON_PHONE} {PHONE_DISPLAY}</a>
      </div>
      <span class="topbar-tagline">{TAGLINE}</span>
    </div>
  </div>

  <header class="site-header" id="top">
    <div class="wrap header-inner">
      <a href="index.html" class="brand" aria-label="{NAME}, home">
        <span class="mark" aria-hidden="true">FM</span>
        <span class="brand-text">
          <span class="brand-name">Fynn-Micheals</span>
          <span class="brand-sub">HR Solutions</span>
        </span>
      </a>

      <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav">
        <span class="sr-only">Menu</span>
        <span class="bar"></span><span class="bar"></span><span class="bar"></span>
      </button>

      <nav class="site-nav" id="site-nav" aria-label="Main">
        <a href="index.html"{cls("home")}>Home</a>
        <div class="has-sub">
          <button class="sub-toggle{" active" if group == "services" else ""}" aria-expanded="false">Services
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>
          </button>
          <ul class="sub-menu">
{sub}
          </ul>
        </div>
        <a href="about.html"{cls("about")}>About</a>
        <a href="contact.html"{cls("contact")}>Contact</a>
        <a href="contact.html" class="btn btn-gold btn-sm">Book a Consultation</a>
      </nav>
    </div>
  </header>
"""


def footer():
    links = "\n".join(f'          <li><a href="{f}">{label}</a></li>' for f, label in SERVICES)
    return f"""  <footer class="site-footer">
    <div class="wrap footer-grid">
      <div>
        <div class="brand">
          <span class="mark" aria-hidden="true">FM</span>
          <span class="brand-text">
            <span class="brand-name">Fynn-Micheals</span>
            <span class="brand-sub">HR Solutions</span>
          </span>
        </div>
        <p class="footer-tagline">{TAGLINE}</p>
        <p class="footer-about">HR consulting and outsourcing for startups and growing businesses in Ghana.</p>
      </div>
      <div>
        <h4>Services</h4>
        <ul>
{links}
        </ul>
      </div>
      <div>
        <h4>Company</h4>
        <ul>
          <li><a href="index.html">Home</a></li>
          <li><a href="about.html">About Us</a></li>
          <li><a href="contact.html">Contact</a></li>
        </ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li><a href="tel:{PHONE_LINK}">{PHONE_DISPLAY}</a></li>
          <li>{LOCATION}</li>
        </ul>
      </div>
    </div>
    <div class="wrap footer-bottom">
      <p>&copy; <span id="year">{date.today().year}</span> {NAME}. All rights reserved.</p>
    </div>
  </footer>
"""


def schema():
    data = {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "name": NAME.replace("&amp;", "&"),
        "slogan": TAGLINE,
        "url": SITE_URL + "/",
        "email": EMAIL,
        "areaServed": "Ghana",
        "address": {"@type": "PostalAddress", "addressCountry": "GH"},
        "description": "HR consulting and outsourcing for startups and small businesses in Ghana.",
    }
    return f'  <script type="application/ld+json">{json.dumps(data)}</script>\n'


def render(file, title, desc, group):
    body = (SRC / file).read_text(encoding="utf-8")
    body = (body.replace("{{EMAIL}}", EMAIL)
                .replace("{{PHONE_DISPLAY}}", PHONE_DISPLAY)
                .replace("{{PHONE_LINK}}", PHONE_LINK)
                .replace("{{LOCATION}}", LOCATION)
                .replace("{{HOURS}}", HOURS)
                .replace("{{ICON_MAIL}}", ICON_MAIL)
                .replace("{{ICON_PHONE}}", ICON_PHONE)
                .replace("{{ICON_PIN}}", ICON_PIN)
                .replace("{{ICON_CLOCK}}", ICON_CLOCK))
    url = page_url(file)
    plain_title = title.replace("&amp;", "&")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{NAME}">
  <meta property="og:title" content="{plain_title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="https://images.unsplash.com/photo-1758518730162-09a142505bfd?auto=format&amp;fit=crop&amp;w=1200&amp;h=630&amp;q=80">
  <meta name="theme-color" content="#111111">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&amp;family=Mulish:wght@400;500;600&amp;display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
{schema() if file == "index.html" else ""}</head>
<body>

{header(file, group)}
  <main>
{body}
  </main>

{footer()}
  <script src="script.js"></script>
</body>
</html>
"""


def main():
    for file, title, desc, group in PAGES:
        (ROOT / file).write_text(render(file, title, desc, group), encoding="utf-8", newline="\n")
        print("built", file)

    today = date.today().isoformat()
    urls = "\n".join(
        f"  <url><loc>{page_url(f)}</loc><lastmod>{today}</lastmod></url>" for f, *_ in PAGES
    )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n", encoding="utf-8", newline="\n")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8", newline="\n")
    print("built sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
