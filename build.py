"""Builds the site's HTML pages from the page bodies in src/.

Each page gets the shared top bar, header, footer and SEO tags.
Edit the content in src/*.html (or the details below), then run:

    python build.py

and commit the regenerated .html files in the project root.
"""
from datetime import date
from pathlib import Path
from urllib.parse import quote
import hashlib
import json
import re

ROOT = Path(__file__).parent
SRC = ROOT / "src"

# ---------------------------------------------------------------- details
SITE_URL = "https://fynn-michealshrsolutions.com"   # live domain (used for canonical links and sitemap)
NAME = "Fynn-Micheals HR Solutions"
TAGLINE = "People. Performance. Progress."
# Her email, shown on the site and used for the enquiry form.
EMAIL = "fynnmichealshrsolutions@gmail.com"
PHONE_DISPLAY = "+233 24 444 6466"
PHONE_LINK = "+233244446466"
LOCATION = "Accra, Ghana"                  # PLACEHOLDER: confirm city
HOURS = "Mon &ndash; Fri, 8:00 &ndash; 17:00"  # PLACEHOLDER

# Enquiry form is delivered by FormSubmit (formsubmit.co) to EMAIL. After the one-time
# activation, FormSubmit emails a random alias; it can replace EMAIL in this URL.
FORM_ENDPOINT = "https://formsubmit.co/ajax/" + EMAIL
WHATSAPP = "233244446466"                 # number in international format, no +
WHATSAPP_TEXT = "Hello Fynn-Micheals HR Solutions, I'd like to enquire about your HR services."

SERVICES = [
    ("startup-hr.html", "Startup HR Foundation"),
    ("outsourced-hr.html", "Outsourced HR Department"),
    ("recruitment.html", "Recruitment &amp; Talent Acquisition"),
    ("hr-audit.html", "HR Audit &amp; Business Advisory"),
    ("performance-management.html", "Performance Management"),
    ("hr-policies.html", "HR Policies &amp; Documentation"),
    ("international-hr.html", "HR Support Beyond Borders"),
]

RESOURCES = [
    ("resources.html", "Resource Centre"),
    ("faq.html", "FAQs"),
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
     "Employee handbooks, HR policies, employment documents, leave, disciplinary and grievance "
     "procedures developed for your business in accordance with the Labour Act.",
     "services"),
    ("hr-audit.html",
     "HR Audit &amp; Consulting Services for Businesses | Fynn-Micheals",
     "HR health checks, workforce assessments, HR process reviews, productivity systems and "
     "organisational restructuring for businesses facing people-management problems.",
     "services"),
    ("performance-management.html",
     "Performance Management Systems &amp; KPI Development | Fynn-Micheals",
     "KPI development, performance appraisal systems, review templates, improvement plans and "
     "goal-setting frameworks that connect individual roles to business goals.",
     "services"),
    ("international-hr.html",
     "International &amp; Remote HR Support | Fynn-Micheals",
     "HR support beyond borders: HR consulting, recruitment coordination, HR documentation and "
     "remote people-management support for businesses in Ghana and international clients.",
     "services"),
    ("about.html",
     "About Fynn-Micheals HR Solutions",
     "Fynn-Micheals HR Solutions partners with business owners to simplify HR, strengthen "
     "workplace structures and create the foundation for sustainable growth.",
     "about"),
    ("resources.html",
     "HR Resource Centre for Small Businesses | Fynn-Micheals",
     "Practical HR guidance for startups and small businesses: the HR basics to put in place, "
     "the documents every employer needs and signs it's time for an HR review.",
     "resources"),
    ("faq.html",
     "HR Services FAQs | Fynn-Micheals HR Solutions",
     "Answers to common questions about startup HR, outsourced HR, recruitment, HR policies, "
     "international clients, fees and getting started with Fynn-Micheals HR Solutions.",
     "resources"),
    ("confidentiality.html",
     "Confidentiality Statement | Fynn-Micheals HR Solutions",
     "How Fynn-Micheals HR Solutions protects the business and employee information shared "
     "with us during enquiries and engagements.",
     "about"),
    ("contact.html",
     "Contact an HR Consultant in Ghana | Fynn-Micheals",
     "Speak to an HR consultant at Fynn-Micheals HR Solutions in Ghana. Call, WhatsApp, email "
     "or send an enquiry and we'll reply within one working day.",
     "contact"),
]

# ---------------------------------------------------------------- icons
ICON_MAIL = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="1"/><path d="m3 7 9 6 9-6"/></svg>'
ICON_PHONE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1 1A16 16 0 0 1 4 5a1 1 0 0 1 1-1z"/></svg>'
ICON_PIN = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>'
ICON_CLOCK = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>'


def asset_version(name):
    """Short content hash so browsers fetch a new copy whenever the file changes."""
    return hashlib.md5((ROOT / name).read_bytes()).hexdigest()[:8]


def page_url(file):
    return SITE_URL + "/" if file == "index.html" else f"{SITE_URL}/{file}"


def header(current_file, group):
    def cls(g):
        return ' class="active"' if g == group else ""

    active = ' class="active"'

    def sub_items(items):
        return "\n".join(
            f'            <li><a href="{f}"{active if f == current_file else ""}>{label}</a></li>'
            for f, label in items
        )

    def dropdown(label, items, grp):
        return f"""        <div class="has-sub">
          <button class="sub-toggle{" active" if group == grp else ""}" aria-expanded="false">{label}
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>
          </button>
          <ul class="sub-menu">
{sub_items(items)}
          </ul>
        </div>"""
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
{dropdown("Services", SERVICES, "services")}
        <a href="about.html"{cls("about")}>About</a>
{dropdown("Resources", RESOURCES, "resources")}
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
        <p class="footer-about">HR consulting and outsourcing for startups and growing businesses in Ghana and beyond.</p>
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
          <li><a href="about.html">About Us</a></li>
          <li><a href="resources.html">Resource Centre</a></li>
          <li><a href="faq.html">FAQs</a></li>
          <li><a href="confidentiality.html">Confidentiality</a></li>
          <li><a href="contact.html">Contact</a></li>
        </ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li><a href="tel:{PHONE_LINK}">{PHONE_DISPLAY}</a></li>
          <li><a href="{whatsapp_link()}" target="_blank" rel="noopener">WhatsApp us</a></li>
          <li>{LOCATION}</li>
        </ul>
      </div>
    </div>
    <div class="wrap footer-bottom">
      <p>&copy; <span id="year">{date.today().year}</span> {NAME}. All rights reserved.</p>
    </div>
  </footer>
"""


def whatsapp_link():
    return f"https://wa.me/{WHATSAPP}?text={quote(WHATSAPP_TEXT)}"


ICON_WHATSAPP = ('<svg viewBox="0 0 32 32" aria-hidden="true" class="wa-icon"><path d="M16 3a13 13 0 0 0-11.2 19.6L3 29l6.6-1.7A13 13 0 1 0 16 3zm0 23.6c-2 0-3.9-.5-5.6-1.5l-.4-.2-3.9 1 1-3.8-.3-.4A10.6 10.6 0 1 1 16 26.6zm5.8-7.9c-.3-.2-1.9-.9-2.2-1-.3-.1-.5-.2-.7.2l-1 1.2c-.2.2-.4.2-.7.1a8.7 8.7 0 0 1-4.3-3.8c-.3-.6.3-.5 1-1.7.1-.2 0-.4 0-.6l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4-.3.3-1.2 1.1-1.2 2.8s1.2 3.3 1.4 3.5c.2.2 2.4 3.7 5.9 5.2 2.2.9 3 1 4.1.8.7-.1 1.9-.8 2.2-1.5.3-.7.3-1.4.2-1.5l-.5-.3z"/></svg>')


def other_services(current_file):
    return "\n".join(
        f'          <a href="{f}">{label} <span aria-hidden="true">&rarr;</span></a>'
        for f, label in SERVICES if f != current_file
    )


def faq_schema(body):
    pairs = re.findall(r"<summary>(.*?)</summary>\s*<div class=\"faq-a\">(.*?)</div>", body, re.S)
    clean = lambda s: re.sub(r"<[^>]+>", "", s).replace("&amp;", "&").strip()
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": clean(q),
             "acceptedAnswer": {"@type": "Answer", "text": " ".join(clean(a).split())}}
            for q, a in pairs
        ],
    }
    return f'  <script type="application/ld+json">{json.dumps(data)}</script>\n'


def schema():
    data = {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "name": NAME.replace("&amp;", "&"),
        "slogan": TAGLINE,
        "url": SITE_URL + "/",
        "email": EMAIL,
        "telephone": PHONE_LINK,
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
                .replace("{{ICON_CLOCK}}", ICON_CLOCK)
                .replace("{{ICON_WHATSAPP}}", ICON_WHATSAPP)
                .replace("{{WHATSAPP_LINK}}", whatsapp_link())
                .replace("{{FORM_ENDPOINT}}", FORM_ENDPOINT)
                .replace("{{OTHER_SERVICES}}", other_services(file)))
    head_extra = schema() if file == "index.html" else ""
    if file == "faq.html":
        head_extra = faq_schema(body)
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
  <meta property="og:image" content="https://images.unsplash.com/photo-1573167101669-476636b96cea?auto=format&amp;fit=crop&amp;w=1200&amp;h=630&amp;q=80">
  <meta name="theme-color" content="#111111">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700&amp;family=Mulish:wght@400;500;600&amp;display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css?v={asset_version('styles.css')}">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
{head_extra}</head>
<body>

{header(file, group)}
  <main>
{body}
  </main>

{footer()}
  <a class="wa-float" href="{whatsapp_link()}" target="_blank" rel="noopener" aria-label="Chat with us on WhatsApp">
    {ICON_WHATSAPP}
    <span class="wa-label">WhatsApp us</span>
  </a>

  <script src="script.js?v={asset_version('script.js')}"></script>
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
