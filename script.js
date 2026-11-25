(function () {
  // Mobile navigation
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  toggle.addEventListener('click', function () {
    var open = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', String(!open));
    nav.classList.toggle('open', !open);
  });

  // Dropdown menus (click / tap; hover also opens them on desktop via CSS)
  var subWraps = Array.prototype.slice.call(document.querySelectorAll('.has-sub'));
  var closeSub = function (wrap) {
    wrap.classList.remove('open');
    wrap.querySelector('.sub-toggle').setAttribute('aria-expanded', 'false');
  };
  subWraps.forEach(function (wrap) {
    var btn = wrap.querySelector('.sub-toggle');
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = btn.getAttribute('aria-expanded') === 'true';
      subWraps.forEach(closeSub);
      if (!open) {
        btn.setAttribute('aria-expanded', 'true');
        wrap.classList.add('open');
      }
    });
  });
  document.addEventListener('click', function (e) {
    subWraps.forEach(function (wrap) { if (!wrap.contains(e.target)) closeSub(wrap); });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') subWraps.forEach(closeSub);
  });

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
  var targets = document.querySelectorAll('.section-head, .card, .reasons li, .circle-art, .stats li, .about-img, .about-text, .contact-cards li, .contact-form, .service-main, .service-side, .mini-links a, .steps li, .borders-band, .faq details, .guide, .partners li');
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
      var data = {};
      var lines = [];
      new FormData(form).forEach(function (value, key) {
        value = String(value).trim();
        data[key] = value;
        if (key !== 'Message' && key !== '_honey') lines.push(key + ': ' + (value || '-'));
      });
      var who = document.getElementById('name').value.trim();
      var subject = 'Website enquiry from ' + who;

      // Fallback: open the visitor's email app with the enquiry filled in.
      var openMail = function () {
        window.location.href = 'mailto:' + to + '?subject=' + encodeURIComponent(subject) +
          '&body=' + encodeURIComponent(lines.join('\n') + '\n\n' + (data.Message || ''));
        note.textContent = 'We could not send the form directly, so your email app has opened with the message ready to send.';
      };

      var endpoint = form.getAttribute('data-endpoint');
      if (!endpoint || !window.fetch) { openMail(); return; }

      data._subject = subject;
      data._template = 'table';
      data._captcha = 'false';
      if (data.Email) data._replyto = data.Email;

      var button = form.querySelector('button[type="submit"]');
      button.disabled = true;
      note.textContent = 'Sending...';

      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(data)
      })
        .then(function (res) { return res.json().then(function (j) { return { ok: res.ok, body: j }; }); })
        .then(function (r) {
          if (r.ok && String(r.body.success) === 'true') {
            form.reset();
            note.textContent = 'Thank you, ' + who + '. Your enquiry has been sent and we will reply within one working day.';
            note.classList.add('ok');
          } else {
            openMail();
          }
        })
        .catch(openMail)
        .then(function () { button.disabled = false; });
    });
  }

  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
})();
