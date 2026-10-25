// The notebook editor. One page; the URL hash says what is open:
// #/reading, #/reading/<slug>, #/about. Edits save themselves a moment after
// typing stops (or on cmd/ctrl-S) to the Markdown file on disk.
(function () {
  'use strict';

  var SERVE = 'http://localhost:4000';   // `make serve`, for the real render
  var SAVE_DELAY = 800;

  var $ = function (id) { return document.getElementById(id); };
  var el = {
    status: $('status'), list: $('entry-list'), search: $('search'),
    newForm: $('new-form'), newTitle: $('new-title'),
    sync: $('sync'), syncButton: $('sync-button'), syncOutput: $('sync-output'),
    editor: $('editor'), pick: $('pick'), title: $('title'), published: $('published'),
    file: $('file'), previewLink: $('preview-link'), note: $('note'),
    fm: $('front-matter'), body: $('body'), preview: $('preview')
  };

  var section = null;   // the open tab
  var entries = [];     // its list
  var doc = null;       // the open entry: {section, slug, file, url, mtime}
  var dirty = false;
  var saving = null;    // the in-flight save, a Promise
  var timer = null;
  var conflict = false;

  // --- Server ---------------------------------------------------------------

  function api(method, path, data) {
    var opts = { method: method, headers: {} };
    if (data !== undefined) {
      opts.headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(data);
    }
    return fetch(path, opts).then(function (res) {
      return res.json().then(function (json) {
        if (!res.ok) {
          var err = new Error(json.error || res.statusText);
          err.status = res.status;
          throw err;
        }
        return json;
      });
    });
  }

  function status(text, kind) {
    el.status.textContent = text;
    el.status.className = 'status' + (kind ? ' ' + kind : '');
  }

  // --- Front matter -----------------------------------------------------------
  // Only top-level `key: value` lines are read or written here; anything else
  // in the front matter (lists, nested keys) passes through untouched.

  function getField(fm, key) {
    var m = fm.match(new RegExp('^' + key + ':[ \\t]*(.*)$', 'm'));
    if (!m) return null;
    var v = m[1].trim();
    if (v.charAt(0) === '"') { try { return JSON.parse(v); } catch (e) { return v.replace(/^"|"$/g, ''); } }
    if (v.charAt(0) === "'" && v.length > 1 && v.slice(-1) === "'") return v.slice(1, -1).replace(/''/g, "'");
    return v;
  }

  function setField(fm, key, line) {
    var re = new RegExp('^' + key + ':.*(\\n|$)', 'm');
    var replacement = line === null ? '' : key + ': ' + line + '\n';
    if (re.test(fm)) return fm.replace(re, function () { return replacement; });
    if (line === null) return fm;
    if (fm && fm.slice(-1) !== '\n') fm += '\n';
    return fm + replacement;
  }

  // --- Lists ------------------------------------------------------------------

  function loadSection(name) {
    section = name;
    document.querySelectorAll('.tab').forEach(function (tab) {
      var on = tab.getAttribute('href') === '#/' + name;
      if (on) tab.setAttribute('aria-current', 'page'); else tab.removeAttribute('aria-current');
    });
    document.body.dataset.section = name;
    el.sync.hidden = name !== 'reading';
    el.newForm.hidden = name === 'about';
    el.search.hidden = name === 'about';
    return api('GET', '/api/entries?section=' + name).then(function (list) {
      entries = list;
      renderList();
    });
  }

  function renderList() {
    var q = el.search.value.trim().toLowerCase();
    el.list.textContent = '';
    var shown = 0;
    entries.forEach(function (e) {
      var hay = (e.title + ' ' + (e.author || '') + ' ' + e.slug).toLowerCase();
      if (q && hay.indexOf(q) === -1) return;
      shown++;
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = '#/' + e.section + '/' + e.slug;
      if (doc && doc.section === e.section && doc.slug === e.slug) a.setAttribute('aria-current', 'true');
      var t = document.createElement('span');
      t.className = 'entry-title' + (e.has_body ? ' has-body' : '');
      t.textContent = e.title;
      var meta = document.createElement('span');
      meta.className = 'entry-meta';
      var bits = [];
      if (e.author) bits.push(e.author.replace(/\s+/g, ' '));
      if (e.date_read) bits.push(e.date_read.slice(0, 4));
      if (e.date) bits.push(e.date);
      if (!e.published) bits.push('draft');
      meta.textContent = bits.join(' · ');
      a.appendChild(t);
      a.appendChild(meta);
      if (!e.published) a.classList.add('draft');
      li.appendChild(a);
      el.list.appendChild(li);
    });
    if (!shown) {
      var li = document.createElement('li');
      li.className = 'empty';
      li.textContent = q ? 'Nothing matches.' : 'Nothing here yet.';
      el.list.appendChild(li);
    }
  }

  // --- The open entry -------------------------------------------------------------

  function openEntry(sec, slug) {
    return flush().then(function () {
      return api('GET', '/api/entry/' + sec + '/' + slug);
    }).then(function (d) {
      doc = { section: d.section, slug: d.slug, file: d.file, url: d.url, mtime: d.mtime };
      dirty = false;
      conflict = false;
      el.fm.value = d.front_matter;
      // The body is shown without the blank line that usually follows the
      // front matter, and saved with it. A blank body is saved as it was.
      el.body.value = d.body.replace(/^\n/, '');
      doc.blank = d.body.trim() === '' ? d.body : '';
      doc.lead = d.body.charAt(0) === '\n' || doc.blank !== '' || d.body === '' ? '\n' : '';
      el.file.textContent = d.file;
      el.previewLink.href = SERVE + d.url;
      fromFrontMatter();
      el.editor.hidden = false;
      el.pick.hidden = true;
      if (!el.preview.hidden) renderPreview();
      status('');
      renderList();
    }).catch(function (err) {
      status(err.message, 'error');
    });
  }

  function closeEntry() {
    doc = null;
    el.editor.hidden = true;
    el.pick.hidden = false;
  }

  // Title and published controls are views onto the front matter text.
  function fromFrontMatter() {
    var fm = el.fm.value;
    if (document.activeElement !== el.title) el.title.value = getField(fm, 'title') || '';
    el.published.checked = getField(fm, 'published') !== 'false';
    var publishedWriting = doc.section === 'writing' && el.published.checked;
    el.note.hidden = !publishedWriting;
    el.note.textContent = publishedWriting ? 'Published: this went out on the feed. Edits show up there on the next deploy.' : '';
  }

  function changed() {
    dirty = true;
    if (conflict) return;
    status('Unsaved');
    clearTimeout(timer);
    timer = setTimeout(save, SAVE_DELAY);
  }

  function save() {
    clearTimeout(timer);
    if (!doc || !dirty || conflict) return Promise.resolve();
    if (saving) return saving.then(save);
    var target = doc;
    dirty = false;
    status('Saving…');
    saving = api('PUT', '/api/entry/' + target.section + '/' + target.slug, {
      front_matter: el.fm.value,
      body: el.body.value.trim() ? target.lead + el.body.value : target.blank,
      mtime: target.mtime
    }).then(function (res) {
      target.mtime = res.mtime;
      if (target === doc) {
        status(dirty ? 'Unsaved' : 'Saved', dirty ? '' : 'ok');
        updateListEntry();
      }
    }).catch(function (err) {
      if (target === doc) dirty = true;
      if (err.status === 409) {
        conflict = true;
        status('The file changed on disk. Copy anything you need, then reload the entry.', 'error');
        showReload();
      } else {
        status('Not saved: ' + err.message, 'error');
      }
    }).then(function () { saving = null; });
    return saving;
  }

  // Save what is pending before leaving the entry.
  function flush() {
    return dirty ? save() : (saving || Promise.resolve());
  }

  function showReload() {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'reload';
    b.textContent = 'Reload';
    b.addEventListener('click', function () { dirty = false; openEntry(doc.section, doc.slug); });
    el.status.appendChild(document.createTextNode(' '));
    el.status.appendChild(b);
  }

  function updateListEntry() {
    entries.forEach(function (e) {
      if (e.section === doc.section && e.slug === doc.slug) {
        e.title = getField(el.fm.value, 'title') || e.slug;
        e.published = getField(el.fm.value, 'published') !== 'false';
        e.has_body = el.body.value.trim() !== '';
      }
    });
    renderList();
  }

  // --- Preview ----------------------------------------------------------------------
  // A small Markdown renderer for the look of a draft: headings, paragraphs,
  // emphasis, links, images, lists, quotes, code and rules. Raw HTML and Liquid
  // show as text. `make serve` is the real render.

  function esc(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function safeUrl(u) {
    u = u.trim();
    return /^(https?:|mailto:|\/|#|\.)/i.test(u) ? u : '';
  }

  function inline(text) {
    var codes = [];
    var s = esc(text).replace(/`([^`]+)`/g, function (_, c) { codes.push(c); return '\u0000' + (codes.length - 1) + '\u0000'; });
    s = s.replace(/!\[([^\]]*)\]\(([^)\s]+)(?:\s+&quot;[^&]*&quot;)?\)/g, function (_, alt, u) {
      var url = safeUrl(u);
      return url ? '<img src="' + url + '" alt="' + alt + '">' : alt;
    });
    s = s.replace(/\[([^\]]+)\]\(([^)\s]+)(?:\s+&quot;[^&]*&quot;)?\)/g, function (_, t, u) {
      var url = safeUrl(u);
      return url ? '<a href="' + url + '" target="_blank" rel="noopener">' + t + '</a>' : t;
    });
    s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>').replace(/__([^_]+)__/g, '<strong>$1</strong>');
    s = s.replace(/(^|[^*])\*([^*\s][^*]*)\*/g, '$1<em>$2</em>').replace(/(^|\W)_([^_\s][^_]*)_(?=\W|$)/g, '$1<em>$2</em>');
    return s.replace(/\u0000(\d+)\u0000/g, function (_, i) { return '<code>' + codes[+i] + '</code>'; });
  }

  function markdown(src) {
    var lines = src.replace(/\r\n/g, '\n').split('\n');
    var out = [];
    var i = 0;
    while (i < lines.length) {
      var line = lines[i];
      var m;
      if (/^\s*$/.test(line)) { i++; continue; }
      if ((m = line.match(/^(```|~~~)/))) {
        var code = [];
        i++;
        while (i < lines.length && lines[i].indexOf(m[1]) !== 0) code.push(lines[i++]);
        i++;
        out.push('<pre><code>' + esc(code.join('\n')) + '</code></pre>');
        continue;
      }
      if ((m = line.match(/^(#{1,6})\s+(.*?)\s*#*\s*$/))) {
        out.push('<h' + m[1].length + '>' + inline(m[2]) + '</h' + m[1].length + '>');
        i++;
        continue;
      }
      if (/^\s*([-*_])(\s*\1){2,}\s*$/.test(line)) { out.push('<hr>'); i++; continue; }
      if (/^>/.test(line)) {
        var quote = [];
        while (i < lines.length && /^>/.test(lines[i])) quote.push(lines[i++].replace(/^>\s?/, ''));
        out.push('<blockquote>' + markdown(quote.join('\n')) + '</blockquote>');
        continue;
      }
      if ((m = line.match(/^\s*([-*+]|\d+[.)])\s+/))) {
        var ordered = /\d/.test(m[1]);
        var items = [];
        while (i < lines.length && /^\s*([-*+]|\d+[.)])\s+/.test(lines[i])) {
          var item = lines[i++].replace(/^\s*([-*+]|\d+[.)])\s+/, '');
          while (i < lines.length && /^\s{2,}\S/.test(lines[i]) && !/^\s*([-*+]|\d+[.)])\s+/.test(lines[i])) item += ' ' + lines[i++].trim();
          items.push('<li>' + inline(item) + '</li>');
        }
        out.push((ordered ? '<ol>' : '<ul>') + items.join('') + (ordered ? '</ol>' : '</ul>'));
        continue;
      }
      var para = [];
      while (i < lines.length && !/^\s*$/.test(lines[i]) && !/^(#{1,6}\s|```|~~~|>|\s*([-*+]|\d+[.)])\s+)/.test(lines[i])) para.push(lines[i++]);
      out.push('<p>' + inline(para.join('\n')) + '</p>');
    }
    return out.join('\n');
  }

  function renderPreview() {
    var src = el.body.value;
    el.preview.innerHTML = src.trim() ? markdown(src) : '<p class="empty">Nothing written yet.</p>';
  }

  function setMode(mode) {
    document.querySelectorAll('.mode button').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.mode === mode));
    });
    var preview = mode === 'preview';
    el.preview.hidden = !preview;
    el.body.hidden = preview;
    if (preview) renderPreview(); else el.body.focus();
  }

  // --- Routing ------------------------------------------------------------------------

  function route() {
    var parts = location.hash.replace(/^#\/?/, '').split('/');
    var sec = ['reading', 'writing', 'projects', 'about'].indexOf(parts[0]) >= 0 ? parts[0] : 'reading';
    var slug = sec === 'about' ? 'about' : parts[1];
    var ready = sec === section ? Promise.resolve() : loadSection(sec);
    ready.then(function () {
      if (slug) return openEntry(sec, slug);
      return flush().then(closeEntry).then(renderList);
    }).catch(function (err) { status(err.message, 'error'); });
  }

  // --- Wiring ---------------------------------------------------------------------------

  el.title.addEventListener('input', function () {
    var t = el.title.value.replace(/\n/g, ' ');
    el.fm.value = setField(el.fm.value, 'title', t ? JSON.stringify(t) : null);
    changed();
  });
  el.published.addEventListener('change', function () {
    // Published is the default, so publishing removes the line.
    el.fm.value = setField(el.fm.value, 'published', el.published.checked ? null : 'false');
    fromFrontMatter();
    changed();
  });
  el.fm.addEventListener('input', function () { fromFrontMatter(); changed(); });
  el.body.addEventListener('input', changed);

  document.querySelectorAll('.mode button').forEach(function (b) {
    b.addEventListener('click', function () { setMode(b.dataset.mode); });
  });

  el.search.addEventListener('input', renderList);

  el.newForm.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var title = el.newTitle.value.trim();
    if (!title) { el.newTitle.focus(); return; }
    flush().then(function () {
      return api('POST', '/api/new', { section: section, title: title });
    }).then(function (res) {
      el.newTitle.value = '';
      return loadSection(res.section).then(function () {
        location.hash = '#/' + res.section + '/' + res.slug;
      });
    }).catch(function (err) { status(err.message, 'error'); });
  });

  el.syncButton.addEventListener('click', function () {
    el.syncButton.disabled = true;
    el.syncOutput.hidden = false;
    el.syncOutput.textContent = 'Syncing…';
    flush().then(function () {
      return api('POST', '/api/sync-books', {});
    }).then(function (res) {
      el.syncOutput.textContent = (res.ok ? '' : 'The sync failed.\n') + res.output;
      return loadSection('reading');
    }).then(function () {
      // Pick up anything the sync changed in the open book.
      if (doc && doc.section === 'reading' && !dirty) return openEntry('reading', doc.slug);
    }).catch(function (err) {
      el.syncOutput.textContent = err.message;
    }).then(function () { el.syncButton.disabled = false; });
  });

  document.addEventListener('keydown', function (ev) {
    if ((ev.metaKey || ev.ctrlKey) && ev.key === 's') {
      ev.preventDefault();
      save();
    }
  });

  window.addEventListener('beforeunload', function (ev) {
    if (dirty || saving) { ev.preventDefault(); ev.returnValue = ''; }
  });

  window.addEventListener('hashchange', route);
  route();
})();
