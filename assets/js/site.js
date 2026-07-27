/* Reveal sections as they come into view. Everything is visible without JS —
   the `.js` class added in <head> is what opts the page into the animation. */
(function () {
  "use strict";

  var targets = document.querySelectorAll(".reveal");
  if (!targets.length) return;

  var reduced =
    window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function showAll() {
    Array.prototype.forEach.call(targets, function (el) {
      el.classList.add("is-visible");
    });
  }

  if (reduced || typeof window.IntersectionObserver !== "function") {
    showAll();
    return;
  }

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { rootMargin: "0px 0px -8% 0px", threshold: 0.05 }
  );

  Array.prototype.forEach.call(targets, function (el, i) {
    // Anything already on screen at load reveals immediately, in order.
    var box = el.getBoundingClientRect();
    if (box.top < window.innerHeight && box.bottom > 0) {
      window.setTimeout(function () {
        el.classList.add("is-visible");
      }, Math.min(i, 5) * 70);
    } else {
      observer.observe(el);
    }
  });
})();
