(function () {
  // Mobile navigation
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  toggle.addEventListener('click', function () {
    var open = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', String(!open));
    nav.classList.toggle('open', !open);
  });
  nav.addEventListener('click', function (e) {
    if (e.target.closest('a')) {
      toggle.setAttribute('aria-expanded', 'false');
      nav.classList.remove('open');
    }
  });

  // Header shadow once the page scrolls
  var header = document.querySelector('.site-header');
  var onScroll = function () { header.classList.toggle('scrolled', window.scrollY > 50); };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Fade sections in as they scroll into view
  var targets = document.querySelectorAll('.section-head, .card, .reasons li, .circle-art, .stats li, .about-img, .about-text, .contact-cards li, .contact-form');
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
  var note = document.getElementById('form-note');
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
    window.location.href = 'mailto:hello@fynnmichaels.com?subject=' +
      encodeURIComponent('Enquiry from ' + d.get('name')) +
      '&body=' + encodeURIComponent(body);
    note.textContent = 'Thank you. Your email app should open with the message ready to send.';
  });

  document.getElementById('year').textContent = new Date().getFullYear();
})();
