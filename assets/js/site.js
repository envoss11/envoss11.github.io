// The Reading filter. "All" shows every book, "With notes" the ones with a
// body, and a year the books read that year. The choice goes in the URL hash
// so /reading/#2025 is a link. Without JavaScript the row stays hidden and
// every book shows.
(function () {
  var bar = document.querySelector('.filters');
  if (!bar) return;
  var buttons = bar.querySelectorAll('button[data-filter]');
  var books = document.querySelectorAll('.book-card');
  bar.hidden = false;

  function matches(book, key) {
    if (key === 'all') return true;
    if (key === 'notes') return book.dataset.notes === 'true';
    return book.dataset.year === key;
  }

  function apply(key) {
    var valid = Array.prototype.some.call(buttons, function (b) {
      return b.dataset.filter === key;
    });
    if (!valid) key = 'all';
    buttons.forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.dataset.filter === key));
    });
    books.forEach(function (book) {
      book.hidden = !matches(book, key);
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
  apply(location.hash.slice(1));
})();
