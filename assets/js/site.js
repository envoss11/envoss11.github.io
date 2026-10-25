// Margin notes. Footnotes are written as ordinary Markdown footnotes ([^1]);
// this copies each one next to its reference so that on wide screens it can
// sit in the margin beside the text. The CSS decides where they show: in the
// margin when there is room, otherwise the footnotes stay at the bottom as
// usual. Without JavaScript, they are plain footnotes.
(function () {
  document.querySelectorAll('.prose').forEach(function (prose) {
    var refs = prose.querySelectorAll('a.footnote[href^="#fn"]');
    if (!refs.length) return;
    refs.forEach(function (link) {
      var sup = link.parentNode;
      var note = document.getElementById(decodeURIComponent(link.hash.slice(1)));
      if (!note) return;
      var side = document.createElement('span');
      side.className = 'sidenote';
      side.setAttribute('role', 'note');
      var num = document.createElement('span');
      num.className = 'sidenote-num';
      num.textContent = link.textContent;
      side.appendChild(num);
      note.querySelectorAll('p').forEach(function (p, i) {
        var part = p.cloneNode(true);
        part.querySelectorAll('.reversefootnote').forEach(function (a) { a.remove(); });
        if (i) side.appendChild(document.createElement('br'));
        while (part.firstChild) side.appendChild(part.firstChild);
      });
      sup.after(side);
    });
    prose.classList.add('has-sidenotes');
  });
})();
