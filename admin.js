// Careers admin: the owner signs in to add/edit jobs and review applications.
// Access is enforced by Supabase row-level security (see supabase/schema.sql);
// this page only shows what the signed-in admin is allowed to see.
(function () {
  var cfg = window.FM_CONFIG || {};
  var $ = function (id) { return document.getElementById(id); };
  var views = ['status-view', 'login-view', 'reset-view', 'app-view'];
  function show(view) { views.forEach(function (v) { $(v).hidden = v !== view; }); }
  function status(text) { $('status-text').textContent = text; show('status-view'); }

  if (!cfg.supabaseUrl || !cfg.supabaseKey || !window.supabase) {
    status('The careers database is not connected yet. Add the Supabase URL and key to build.py, then run "python build.py".');
    return;
  }

  var db = window.supabase.createClient(cfg.supabaseUrl, cfg.supabaseKey);
  var jobs = [];
  var apps = [];
  var editingId = null;
  var recovering = false;

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function fmtDate(d) {
    if (!d) return '';
    var dt = d.length === 10 ? new Date(d + 'T00:00:00') : new Date(d);
    return dt.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
  }
  function today() {
    var d = new Date();
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  }
  function jobState(j) {
    if (j.status === 'open' && j.closing_date && j.closing_date < today()) return 'expired';
    return j.status;
  }
  function fail(err) {
    alert('Something went wrong: ' + (err && err.message ? err.message : err));
  }

  // ------------------------------------------------------------ session
  function enter(session) {
    if (recovering) return;
    if (!session) { show('login-view'); $('sign-out').hidden = true; return; }
    $('sign-out').hidden = false;
    db.rpc('is_admin').then(function (res) {
      if (res.error) { status('Could not check your access: ' + res.error.message); return; }
      if (!res.data) {
        status('This account (' + session.user.email + ') is not set up as an admin. Ask your developer to add it.');
        return;
      }
      show('app-view');
      loadAll();
    });
  }

  db.auth.onAuthStateChange(function (event, session) {
    if (event === 'PASSWORD_RECOVERY') { recovering = true; show('reset-view'); return; }
    if (recovering) return;
    if (event === 'SIGNED_IN' || event === 'SIGNED_OUT' || event === 'INITIAL_SESSION') {
      setTimeout(function () { enter(session); }, 0);
    }
  });

  $('login-form').addEventListener('submit', function (e) {
    e.preventDefault();
    var msg = $('login-msg');
    msg.className = 'admin-msg';
    msg.textContent = 'Signing in…';
    db.auth.signInWithPassword({ email: $('l-email').value.trim(), password: $('l-pass').value })
      .then(function (res) {
        if (res.error) { msg.className = 'admin-msg err'; msg.textContent = 'Email or password is incorrect.'; return; }
        msg.textContent = '';
        $('l-pass').value = '';
      });
  });

  $('forgot').addEventListener('click', function () {
    var email = $('l-email').value.trim();
    var msg = $('login-msg');
    if (!email) { msg.className = 'admin-msg err'; msg.textContent = 'Type your email above first.'; return; }
    db.auth.resetPasswordForEmail(email, { redirectTo: location.origin + location.pathname }).then(function (res) {
      msg.className = 'admin-msg' + (res.error ? ' err' : '');
      msg.textContent = res.error ? res.error.message : 'If that email has an account, a reset link is on its way.';
    });
  });

  $('reset-form').addEventListener('submit', function (e) {
    e.preventDefault();
    var msg = $('reset-msg');
    db.auth.updateUser({ password: $('r-pass').value }).then(function (res) {
      if (res.error) { msg.className = 'admin-msg err'; msg.textContent = res.error.message; return; }
      recovering = false;
      history.replaceState(null, '', location.pathname);
      db.auth.getSession().then(function (r) { enter(r.data.session); });
    });
  });

  $('sign-out').addEventListener('click', function () { db.auth.signOut(); });

  // ------------------------------------------------------------ tabs
  function selectTab(name) {
    var isJobs = name === 'jobs';
    $('tab-jobs').setAttribute('aria-selected', String(isJobs));
    $('tab-apps').setAttribute('aria-selected', String(!isJobs));
    $('jobs-panel').hidden = !isJobs;
    $('apps-panel').hidden = isJobs;
  }
  $('tab-jobs').addEventListener('click', function () { selectTab('jobs'); });
  $('tab-apps').addEventListener('click', function () { selectTab('apps'); });

  // ------------------------------------------------------------ data
  function loadAll() {
    return Promise.all([
      db.from('jobs').select('*').order('created_at', { ascending: false }),
      db.from('applications').select('*').order('created_at', { ascending: false })
    ]).then(function (r) {
      if (r[0].error) throw r[0].error;
      if (r[1].error) throw r[1].error;
      jobs = r[0].data;
      apps = r[1].data;
      renderJobs();
      renderFilter();
      renderApps();
    }).catch(fail);
  }

  function jobTitle(id) {
    var j = jobs.find(function (x) { return x.id === id; });
    return j ? j.title : '(deleted job)';
  }

  // ------------------------------------------------------------ jobs
  function renderJobs() {
    if (!jobs.length) {
      $('jobs-table').innerHTML = '<p class="admin-empty">No jobs yet. Click &ldquo;Add a job&rdquo; to post your first opening.</p>';
      return;
    }
    var labels = { open: 'Open', draft: 'Draft', closed: 'Closed', expired: 'Past closing date' };
    $('jobs-table').innerHTML =
      '<table class="admin-table"><thead><tr><th>Job</th><th>Status</th><th>Applicants</th><th>Closes</th><th></th></tr></thead><tbody>' +
      jobs.map(function (j) {
        var count = apps.filter(function (a) { return a.job_id === j.id; }).length;
        var fresh = apps.filter(function (a) { return a.job_id === j.id && a.status === 'new'; }).length;
        var state = jobState(j);
        return '<tr>' +
          '<td><strong>' + esc(j.title) + '</strong><div class="sub">' +
            esc([j.company, j.location, j.employment_type].filter(Boolean).join(' · ')) + '</div></td>' +
          '<td><span class="pill pill-' + state + '">' + labels[state] + '</span></td>' +
          '<td>' + count + (fresh ? ' <span class="sub">(' + fresh + ' new)</span>' : '') + '</td>' +
          '<td>' + (fmtDate(j.closing_date) || '<span class="sub">No date</span>') + '</td>' +
          '<td><div class="row-actions">' +
            '<button data-act="edit" data-id="' + j.id + '">Edit</button>' +
            '<button data-act="apps" data-id="' + j.id + '">Applicants</button>' +
            (j.status === 'open'
              ? '<button data-act="close" data-id="' + j.id + '">Close</button>'
              : '<button data-act="open" data-id="' + j.id + '">Publish</button>') +
            (state === 'open' ? '<a href="careers.html?job=' + j.id + '" target="_blank" rel="noopener">View</a>' : '') +
            '<button class="danger" data-act="delete" data-id="' + j.id + '">Delete</button>' +
          '</div></td></tr>';
      }).join('') + '</tbody></table>';
  }

  $('jobs-table').addEventListener('click', function (e) {
    var b = e.target.closest('button[data-act]');
    if (!b) return;
    var id = b.getAttribute('data-id');
    var job = jobs.find(function (j) { return j.id === id; });
    var act = b.getAttribute('data-act');
    if (act === 'edit') openEditor(job);
    if (act === 'apps') { $('apps-filter').value = id; $('apps-status').value = ''; renderApps(); selectTab('apps'); }
    if (act === 'close' || act === 'open') {
      var patch = { status: act === 'close' ? 'closed' : 'open' };
      if (act === 'open' && job.closing_date && job.closing_date < today()) {
        if (!confirm('The closing date has passed, so the job will stay hidden. Clear the closing date and publish?')) return;
        patch.closing_date = null;
      }
      db.from('jobs').update(patch).eq('id', id).then(function (r) { if (r.error) fail(r.error); else loadAll(); });
    }
    if (act === 'delete') {
      var n = apps.filter(function (a) { return a.job_id === id; }).length;
      if (!confirm('Delete "' + job.title + '"' + (n ? ' and its ' + n + ' application(s), including CVs' : '') +
        '? This cannot be undone. (To just hide it, use Close instead.)')) return;
      var paths = apps.filter(function (a) { return a.job_id === id && a.cv_path; }).map(function (a) { return a.cv_path; });
      (paths.length ? db.storage.from('cvs').remove(paths) : Promise.resolve({}))
        .then(function () { return db.from('jobs').delete().eq('id', id); })
        .then(function (r) { if (r.error) fail(r.error); else loadAll(); });
    }
  });

  var FIELDS = ['title', 'company', 'location', 'employment_type', 'salary', 'closing_date', 'status', 'summary', 'description'];
  var form = $('job-form');

  function openEditor(job) {
    editingId = job ? job.id : null;
    $('editor-title').textContent = job ? 'Edit job' : 'Add a job';
    FIELDS.forEach(function (f) { form.elements[f].value = job ? (job[f] || '') : (f === 'status' ? 'open' : ''); });
    $('job-msg').textContent = '';
    $('job-editor').hidden = false;
    $('jobs-card').hidden = true;
    window.scrollTo(0, 0);
    form.elements.title.focus();
  }
  function closeEditor() { $('job-editor').hidden = true; $('jobs-card').hidden = false; }

  $('add-job').addEventListener('click', function () { openEditor(null); });
  $('job-cancel').addEventListener('click', closeEditor);

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var msg = $('job-msg');
    var row = {};
    FIELDS.forEach(function (f) { var v = form.elements[f].value.trim(); row[f] = v || null; });
    row.status = row.status || 'open';
    if (!row.title) {
      form.elements.title.closest('.field').classList.add('invalid');
      msg.className = 'admin-msg err';
      msg.textContent = 'A job title is required.';
      return;
    }
    form.elements.title.closest('.field').classList.remove('invalid');
    $('job-save').disabled = true;
    msg.className = 'admin-msg';
    msg.textContent = 'Saving…';
    var q = editingId ? db.from('jobs').update(row).eq('id', editingId) : db.from('jobs').insert(row);
    q.then(function (r) {
      $('job-save').disabled = false;
      if (r.error) { msg.className = 'admin-msg err'; msg.textContent = r.error.message; return; }
      closeEditor();
      loadAll();
    });
  });

  // ------------------------------------------------------------ applications
  var STATUSES = ['new', 'reviewing', 'shortlisted', 'interview', 'rejected', 'hired'];
  var openRow = null;

  function renderFilter() {
    var sel = $('apps-filter');
    var keep = sel.value;
    sel.innerHTML = '<option value="">All jobs</option>' + jobs.map(function (j) {
      return '<option value="' + j.id + '">' + esc(j.title) + '</option>';
    }).join('');
    sel.value = jobs.some(function (j) { return j.id === keep; }) ? keep : '';
    var fresh = apps.filter(function (a) { return a.status === 'new'; }).length;
    $('new-count').hidden = !fresh;
    $('new-count').textContent = fresh;
  }

  function renderApps() {
    var jf = $('apps-filter').value;
    var sf = $('apps-status').value;
    var list = apps.filter(function (a) { return (!jf || a.job_id === jf) && (!sf || a.status === sf); });
    if (!list.length) {
      $('apps-table').innerHTML = '<p class="admin-empty">' + (apps.length ? 'No applications match this filter.' : 'No applications yet.') + '</p>';
      return;
    }
    $('apps-table').innerHTML =
      '<table class="admin-table"><thead><tr><th>Applicant</th><th>Job</th><th>Received</th><th>Status</th><th></th></tr></thead><tbody>' +
      list.map(function (a) {
        var row = '<tr>' +
          '<td><strong>' + esc(a.full_name) + '</strong><div class="sub"><a href="mailto:' + esc(a.email) + '">' + esc(a.email) + '</a>' +
            (a.phone ? ' &middot; <a href="tel:' + esc(a.phone.replace(/\s+/g, '')) + '">' + esc(a.phone) + '</a>' : '') + '</div></td>' +
          '<td>' + esc(jobTitle(a.job_id)) + '</td>' +
          '<td>' + fmtDate(a.created_at) + '</td>' +
          '<td><select data-status="' + a.id + '" aria-label="Status for ' + esc(a.full_name) + '">' +
            STATUSES.map(function (s) {
              return '<option value="' + s + '"' + (s === a.status ? ' selected' : '') + '>' + s.charAt(0).toUpperCase() + s.slice(1) + '</option>';
            }).join('') + '</select></td>' +
          '<td><div class="row-actions">' +
            '<button data-act="details" data-id="' + a.id + '">' + (openRow === a.id ? 'Hide' : 'Details') + '</button>' +
            (a.cv_path ? '<button data-act="cv" data-id="' + a.id + '">Open CV</button>' : '') +
            '<button class="danger" data-act="delete" data-id="' + a.id + '">Delete</button>' +
          '</div></td></tr>';
        if (openRow === a.id) {
          row += '<tr class="app-detail"><td colspan="5"><dl>' +
            '<dt>Based in</dt><dd>' + (esc(a.location) || '-') + '</dd>' +
            '<dt>LinkedIn</dt><dd>' + (a.linkedin && /^https?:\/\//i.test(a.linkedin)
              ? '<a class="text-link" href="' + esc(a.linkedin) + '" target="_blank" rel="noopener noreferrer">' + esc(a.linkedin) + '</a>'
              : (esc(a.linkedin) || '-')) + '</dd>' +
            '<dt>Cover note</dt><dd>' + (esc(a.cover_note) || '-') + '</dd>' +
            '<dt>Your notes</dt><dd><textarea data-notes="' + a.id + '" placeholder="Private notes, only you see these">' + esc(a.notes) + '</textarea>' +
              '<div class="row-actions"><button data-act="save-notes" data-id="' + a.id + '">Save notes</button></div></dd>' +
            '</dl></td></tr>';
        }
        return row;
      }).join('') + '</tbody></table>';
  }

  $('apps-filter').addEventListener('change', renderApps);
  $('apps-status').addEventListener('change', renderApps);

  $('apps-table').addEventListener('change', function (e) {
    var id = e.target.getAttribute('data-status');
    if (!id) return;
    var value = e.target.value;
    db.from('applications').update({ status: value }).eq('id', id).then(function (r) {
      if (r.error) { fail(r.error); return; }
      apps.find(function (a) { return a.id === id; }).status = value;
      renderFilter();
      renderJobs();
    });
  });

  $('apps-table').addEventListener('click', function (e) {
    var b = e.target.closest('button[data-act]');
    if (!b) return;
    var id = b.getAttribute('data-id');
    var app = apps.find(function (a) { return a.id === id; });
    var act = b.getAttribute('data-act');
    if (act === 'details') {
      openRow = openRow === id ? null : id;
      // Opening a new application moves it to "Reviewing".
      if (openRow && app.status === 'new') {
        app.status = 'reviewing';
        db.from('applications').update({ status: 'reviewing' }).eq('id', id).then(function () { renderFilter(); renderJobs(); });
      }
      renderApps();
    }
    if (act === 'cv') {
      var win = window.open('', '_blank');
      db.storage.from('cvs').createSignedUrl(app.cv_path, 300).then(function (r) {
        if (r.error) { if (win) win.close(); fail(r.error); return; }
        if (win) win.location = r.data.signedUrl; else location.href = r.data.signedUrl;
      });
    }
    if (act === 'save-notes') {
      var text = document.querySelector('[data-notes="' + id + '"]').value.trim() || null;
      b.textContent = 'Saving…';
      db.from('applications').update({ notes: text }).eq('id', id).then(function (r) {
        if (r.error) { fail(r.error); b.textContent = 'Save notes'; return; }
        app.notes = text;
        b.textContent = 'Saved';
        setTimeout(function () { b.textContent = 'Save notes'; }, 1500);
      });
    }
    if (act === 'delete') {
      if (!confirm('Delete the application from ' + app.full_name + ' and their CV? This cannot be undone.')) return;
      (app.cv_path ? db.storage.from('cvs').remove([app.cv_path]) : Promise.resolve({}))
        .then(function () { return db.from('applications').delete().eq('id', id); })
        .then(function (r) { if (r.error) fail(r.error); else loadAll(); });
    }
  });
})();
