(function () {
  // Mobile navigation
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  toggle.addEventListener('click', function () {
    var open = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', String(!open));
    nav.classList.toggle('open', !open);
  });

  // Services dropdown (click / tap; hover also opens it on desktop via CSS)
  var subToggle = document.querySelector('.sub-toggle');
  var subWrap = document.querySelector('.has-sub');
  if (subToggle) {
    subToggle.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = subToggle.getAttribute('aria-expanded') === 'true';
      subToggle.setAttribute('aria-expanded', String(!open));
      subWrap.classList.toggle('open', !open);
    });
    document.addEventListener('click', function (e) {
      if (!subWrap.contains(e.target)) {
        subToggle.setAttribute('aria-expanded', 'false');
        subWrap.classList.remove('open');
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        subToggle.setAttribute('aria-expanded', 'false');
        subWrap.classList.remove('open');
      }
    });
  }

  // Close the mobile menu after following an in-page link
  nav.addEventListener('click', function (e) {
    var link = e.target.closest('a');
    if (link && link.getAttribute('href').charAt(0) === '#') {
      toggle.setAttribute('aria-expanded', 'false');
      nav.classList.remove('open');
    }
  });

  // Header shadow once the page scrolls
  var header = document.querySelector('.site-header');
  var onScroll = function () { header.classList.toggle('scrolled', window.scrollY > 50); };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Fade content in as it scrolls into view
  var targets = document.querySelectorAll('.section-head, .card, .reasons li, .circle-art, .stats li, .about-img, .about-text, .contact-cards li, .contact-form, .service-main, .service-side, .mini-links a');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    targets.forEach(function (el) { el.classList.add('reveal'); io.observe(el); });
  }

  // Contact form: check required fields, then open the visitor's email app.
  // Swap for a form service (e.g. Formspree) or a backend when going live.
  var form = document.getElementById('contact-form');
  if (form) {
    var note = document.getElementById('form-note');
    var to = form.getAttribute('data-email');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = true;
      ['name', 'email', 'message'].forEach(function (id) {
        var input = document.getElementById(id);
        var valid = input.value.trim() !== '' && (id !== 'email' || /\S+@\S+\.\S+/.test(input.value));
        input.parentElement.classList.toggle('invalid', !valid);
        if (!valid) ok = false;
      });
      if (!ok) {
        note.textContent = 'Please fill in the highlighted fields.';
        return;
      }
      var d = new FormData(form);
      var body = 'Name: ' + d.get('name') +
        '\nCompany: ' + (d.get('company') || '-') +
        '\nEmail: ' + d.get('email') +
        '\nService: ' + (d.get('topic') || '-') +
        '\n\n' + d.get('message');
      window.location.href = 'mailto:' + to + '?subject=' +
        encodeURIComponent('Enquiry from ' + d.get('name')) +
        '&body=' + encodeURIComponent(body);
      note.textContent = 'Thank you. Your email app should open with the message ready to send.';
    });
  }

  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
})();
