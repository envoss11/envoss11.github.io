// The filter on /writing/. Each button shows one section of the list; "All" shows
// every section. The choice goes in the URL hash so /writing/#evaluation is a link.
(function () {
  var bar = document.querySelector('.filters');
  if (!bar) return;
  var buttons = bar.querySelectorAll('button[data-filter]');
  var sections = document.querySelectorAll('.feed-section');

  function apply(key) {
    var valid = Array.prototype.some.call(buttons, function (b) {
      return b.dataset.filter === key;
    });
    if (!valid) key = 'all';
    buttons.forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.filter === key));
    });
    sections.forEach(function (s) {
      s.hidden = key !== 'all' && s.dataset.topic !== key;
    });
  }

  bar.addEventListener('click', function (e) {
    var b = e.target.closest('button[data-filter]');
    if (!b) return;
    var key = b.dataset.filter;
    history.replaceState(null, '', key === 'all' ? location.pathname : '#' + key);
    apply(key);
  });
  window.addEventListener('hashchange', function () {
    apply(location.hash.slice(1));
  });

  bar.hidden = false;
  apply(location.hash.slice(1));
})();
