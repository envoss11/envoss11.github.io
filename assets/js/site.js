/* Day / night.

   The theme itself is already applied by the time this runs — the inline
   bootstrap in <head> sets `data-theme` on <html> before first paint, because
   a deferred script cannot get there in time and the alternative is a frame of
   the wrong sky. What is left for this file is everything that can wait: the
   toggles, the stored preference, and the bits of chrome outside the
   stylesheet's reach (the browser UI colour and the favicon).

   The contract with the bootstrap is three strings — the storage key and the
   two theme names. Change one, change both files.

   Nothing here is required for the site to be usable: with no script, CSS
   withdraws both toggles and the night theme stands on its own. */
(function () {
  "use strict";

  var KEY = "theme";
  var DAY = "day";
  var NIGHT = "night";

  var root = document.documentElement;
  var toggles = document.querySelectorAll("[data-theme-toggle]");
  var busy = false;

  var reduced =
    window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // The one thing about a theme that cannot be expressed in CSS.
  var FAVICON = { day: "favicon-day.svg", night: "favicon.svg" };

  function current() {
    return root.getAttribute("data-theme") === DAY ? DAY : NIGHT;
  }

  function apply(theme) {
    root.setAttribute("data-theme", theme);

    /* The browser paints its own chrome — address bar, tab strip — from
       theme-color, and a meta tag cannot hold a custom property. Read the
       token back out instead of keeping a second copy of the two colours
       here: the attribute is already set, so --bg has already flipped. */
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) {
      meta.setAttribute("content", getComputedStyle(root).getPropertyValue("--bg").trim());
    }

    // Rewrite only the filename, so this keeps working under a baseurl.
    var icon = document.querySelector('link[rel="icon"]');
    if (icon) {
      icon.setAttribute("href", icon.getAttribute("href").replace(/[^/]+$/, FAVICON[theme]));
    }
  }

  /* A stepped flash between the two skies, the way a 16-bit scene change
     faded out and back in. The swap happens at the peak, under the overlay,
     so none of the repaint is on screen. The overlay's fill is a token: it
     goes up in the outgoing sky's colour and comes down in the incoming one,
     which is the flash. */
  function wipe(swap, done) {
    if (reduced || !document.body) {
      swap();
      done();
      return;
    }

    var el = document.createElement("div");
    el.className = "theme-wipe";
    el.setAttribute("aria-hidden", "true");
    document.body.appendChild(el);

    // One frame in the resting state first, or the animation has nothing to
    // start from and the element simply appears at full opacity.
    requestAnimationFrame(function () {
      el.classList.add("is-in");
      window.setTimeout(function () {
        swap();
        el.classList.remove("is-in");
        el.classList.add("is-out");
        window.setTimeout(function () {
          if (el.parentNode) el.parentNode.removeChild(el);
          done();
        }, 260);
      }, 180);
    });
  }

  Array.prototype.forEach.call(toggles, function (button) {
    button.addEventListener("click", function () {
      // Ignore a second press mid-flash. Both toggles drive the same state,
      // and letting them queue would stack overlays and strobe the page.
      if (busy) return;
      busy = true;

      var next = current() === DAY ? NIGHT : DAY;
      try {
        localStorage.setItem(KEY, next);
      } catch (e) {
        // Private browsing, or storage is full. The theme still changes; it
        // just will not survive the next page load.
      }
      wipe(
        function () {
          apply(next);
        },
        function () {
          busy = false;
        }
      );
    });
  });

  /* Follow the system for as long as the visitor has not overridden it. Once
     they pick a side, that sticks until they pick the other one. */
  if (window.matchMedia) {
    var system = window.matchMedia("(prefers-color-scheme: light)");
    var onSystemChange = function (event) {
      var stored;
      try {
        stored = localStorage.getItem(KEY);
      } catch (e) {}
      if (stored === DAY || stored === NIGHT) return;
      apply(event.matches ? DAY : NIGHT);
    };
    if (system.addEventListener) {
      system.addEventListener("change", onSystemChange);
    } else if (system.addListener) {
      system.addListener(onSystemChange);
    }
  }

  // The bootstrap stops at the attribute — it blocks rendering, so it does the
  // one thing that has to happen before first paint and nothing else. The
  // browser-chrome colour and the icon can afford to land a frame later, so
  // they land here, in line with whatever it decided.
  apply(current());
})();

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
    // threshold 0, not a fraction: the hidden state clips the element down to a
    // narrow band, and if the observer counts that clip against the ratio, any
    // non-zero threshold would never be met and the section would stay hidden
    // forever. Firing on first contact sidesteps the question entirely.
    { rootMargin: "0px 0px -8% 0px", threshold: 0 }
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

/* Turn the photographs into sprites.

   `image-rendering: pixelated` only does anything when an image is scaled *up*.
   These portraits are all bigger than the box they sit in, so on its own the CSS
   buys us nothing. Redrawing each one down to a 64px source and letting the
   browser blow it back up nearest-neighbour is what actually produces the blocky
   look — and colours get snapped to a 5-bit-per-channel grid on the way through,
   which is the depth the hardware this is imitating actually had.

   Purely an enhancement: if any step fails, the original photo stays. */
(function () {
  "use strict";

  var SELECTOR = "[data-pixelate], .portrait, .cat img";
  var DEFAULT_EDGE = 64;

  var images = document.querySelectorAll(SELECTOR);
  if (!images.length) return;

  var canvas = document.createElement("canvas");
  var ctx = canvas.getContext && canvas.getContext("2d", { willReadFrequently: true });
  if (!ctx) return;

  function snap(v) {
    if (v < 0) v = 0;
    var q = Math.round(v / 8) * 8; // 32 steps per channel
    return q > 255 ? 255 : q;
  }

  function pixelate(img) {
    var w = img.naturalWidth;
    var h = img.naturalHeight;
    if (!w || !h) return;

    var edge = parseInt(img.getAttribute("data-pixelate"), 10);
    if (!edge || edge < 8 || edge > 256) edge = DEFAULT_EDGE;

    // Scale the long edge down to `edge`, keeping the aspect ratio so the
    // existing object-fit cropping still lands where it did before.
    var scale = edge / Math.max(w, h);
    var tw = Math.max(1, Math.round(w * scale));
    var th = Math.max(1, Math.round(h * scale));

    canvas.width = tw;
    canvas.height = th;
    ctx.clearRect(0, 0, tw, th);
    // Smoothing stays ON for the downscale — averaging the source is what keeps
    // the face readable. The blockiness comes from the upscale, which CSS does.
    ctx.imageSmoothingEnabled = true;
    ctx.drawImage(img, 0, 0, tw, th);

    var frame;
    try {
      frame = ctx.getImageData(0, 0, tw, th);
    } catch (e) {
      return; // cross-origin source — leave the photo alone
    }

    var d = frame.data;
    for (var i = 0; i < d.length; i += 4) {
      var r = d[i];
      var g = d[i + 1];
      var b = d[i + 2];
      // A gentle saturation push, the way these palettes always ran hot.
      var luma = 0.299 * r + 0.587 * g + 0.114 * b;
      d[i] = snap(luma + (r - luma) * 1.18);
      d[i + 1] = snap(luma + (g - luma) * 1.18);
      d[i + 2] = snap(luma + (b - luma) * 1.18);
    }
    ctx.putImageData(frame, 0, 0);

    var url;
    try {
      url = canvas.toDataURL("image/png");
    } catch (e) {
      return;
    }
    if (url && url.length > 22) {
      img.removeAttribute("srcset");
      img.src = url;
    }
  }

  Array.prototype.forEach.call(images, function (img) {
    if (img.complete && img.naturalWidth) {
      pixelate(img);
    } else {
      img.addEventListener("load", function handler() {
        img.removeEventListener("load", handler);
        pixelate(img);
      });
    }
  });
})();

/* The familiar.

   Press one of the cats on the About page and it walks out of its photo and
   follows you around the site — across page loads, because there is no client
   routing here and every navigation is a fresh document. Three localStorage
   keys carry it over: which cat, where it was standing, and whether the
   hold-to-dismiss hint has been shown. The position is stored as a fraction of
   the viewport rather than in pixels, so arriving on a narrower window puts the
   cat somewhere sensible instead of off the edge.

   `data-familiar` is already on <html> by the time this runs — the bootstrap in
   <head> sets it before first paint so the About card never flashes with the
   photo un-greyed. This file is the only thing that writes the keys; the
   bootstrap only reads them.

   About the animation loop, since the rest of this site makes a point of not
   having one: it parks. The moment the cat settles the loop is cancelled, and
   nothing runs again until you move the pointer or an idle timer fires. A cat
   sitting still costs nothing per frame. The sprite itself is animated entirely
   in CSS — this file moves the cat, it never draws it.

   Nothing here is required for the site to work. With no script the About card
   is two photographs, which is what it was before. */
(function () {
  "use strict";

  var KEY = "familiar";
  var AT_KEY = "familiar-at";
  var HINT_KEY = "familiar-hint";
  var ARTEMIS = "artemis";
  var APOLLO = "apollo";

  var root = document.documentElement;
  var el = document.getElementById("familiar");
  if (!el) return;

  var sprite = el.querySelector(".familiar-sprite");
  var hintTag = el.querySelector(".fam-hint");
  var buttons = document.querySelectorAll("[data-summon]");
  if (!sprite) return;

  var reduced =
    window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // The sprite is 20x16 drawn at 3x; the numbers below are in device pixels.
  var SPRITE_W = 60;
  var SPRITE_H = 48;
  var EDGE = 8;
  // How much room the cat insists on. It is also what keeps the sprite out
  // from under your clicks: it will not close the last stretch on its own.
  var NEAR = 110;
  var FAR = 420;
  var WALK = 115;
  var RUN = 265;
  var AMBLE = 62;
  var WANDER_AFTER = 4000;
  var SLEEP_AFTER = 20000;
  var HOLD_MS = 700;
  var NAV_FALLBACK = 64;

  // x, y is the sprite's centre-bottom — where the cat's feet are.
  var x = 0;
  var y = 0;
  var tx = 0;
  var ty = 0;
  var speed = WALK;
  var bias = 0;
  var pose = "sit";
  var mode = "rest";
  var cat = null;
  var pending = null;
  var pointerX = 0;
  var pointerY = 0;
  var seenPointer = false;
  var lastMove = 0;
  var lastFrame = 0;
  var lastSave = 0;
  var raf = 0;
  var restTimer = 0;
  var poseTimer = 0;
  var petTimer = 0;
  var holdTimer = 0;
  var stepTimer = 0;
  var holding = false;
  var heldLong = false;
  var hintDone = false;
  var navH = NAV_FALLBACK;

  // ------------------------------------------------------------------ storage

  function read(key) {
    try {
      return localStorage.getItem(key);
    } catch (e) {
      // Private browsing. The familiar still works; it just will not survive
      // the next page load.
      return null;
    }
  }

  function write(key, value) {
    try {
      if (value === null) localStorage.removeItem(key);
      else localStorage.setItem(key, value);
    } catch (e) {}
  }

  // ----------------------------------------------------------------- geometry

  function bounds() {
    return {
      minX: EDGE + SPRITE_W / 2,
      maxX: window.innerWidth - EDGE - SPRITE_W / 2,
      // The navbar is sticky and the cat is fixed, so without this the two
      // would occupy the same strip and the cat would sit on the site's name.
      minY: navH + EDGE + SPRITE_H,
      maxY: window.innerHeight - EDGE
    };
  }

  function clamp(v, lo, hi) {
    if (hi < lo) return lo;
    return v < lo ? lo : v > hi ? hi : v;
  }

  function place() {
    // Entering and leaving happen off-screen on purpose; everything else stays
    // inside the viewport.
    if (mode !== "enter" && mode !== "exit") {
      var b = bounds();
      x = clamp(x, b.minX, b.maxX);
      y = clamp(y, b.minY, b.maxY);
    }
    // Whole pixels only. A sprite scaled nearest-neighbour onto a half-pixel
    // offset goes soft, which would undo the entire look.
    el.style.transform =
      "translate3d(" +
      Math.round(x - SPRITE_W / 2) +
      "px," +
      Math.round(y - SPRITE_H) +
      "px,0)";
  }

  function setPose(next) {
    if (pose === next) return;
    pose = next;
    el.setAttribute("data-pose", next);
  }

  function face(towardX) {
    var dir = towardX < x ? "left" : "right";
    if (el.getAttribute("data-facing") !== dir) el.setAttribute("data-facing", dir);
  }

  function save() {
    if (!cat) return;
    write(
      AT_KEY,
      (x / window.innerWidth).toFixed(4) + "," + (y / window.innerHeight).toFixed(4)
    );
  }

  function restore() {
    var raw = read(AT_KEY);
    if (!raw) return false;
    var parts = raw.split(",");
    var fx = parseFloat(parts[0]);
    var fy = parseFloat(parts[1]);
    if (!isFinite(fx) || !isFinite(fy)) return false;
    x = fx * window.innerWidth;
    y = fy * window.innerHeight;
    return true;
  }

  // -------------------------------------------------------------------- loop

  function kick() {
    if (!cat || raf || stepTimer) return;
    if (reduced) {
      // No glide with reduced motion: the cat arrives in steps, on a slow
      // timer, rather than being animated across the screen.
      stepTimer = window.setTimeout(stepOnce, 800);
      return;
    }
    // lastFrame is deliberately left alone. tick() re-kicks itself every frame,
    // so resetting it here would pin dt to its fallback and tie the cat's speed
    // to the frame rate instead of to the clock — which in a throttled
    // background tab reduces a brisk exit to a crawl. Restarting after a long
    // park is already handled: the clamp in tick() caps the first step.
    raf = window.requestAnimationFrame(tick);
  }

  function arrived() {
    return Math.abs(tx - x) < 2 && Math.abs(ty - y) < 2;
  }

  function moveToward(dt) {
    var dx = tx - x;
    var dy = ty - y;
    var d = Math.sqrt(dx * dx + dy * dy);
    if (d < 0.5) {
      x = tx;
      y = ty;
      return;
    }
    var travel = Math.min(speed * dt, d);
    x += (dx / d) * travel;
    y += (dy / d) * travel;
  }

  function onArrive() {
    mode = "rest";
    setPose("sit");
    scheduleRest();
  }

  function decide() {
    // A cat being held does not wander off mid-hold.
    if (holding) {
      mode = "rest";
      return;
    }

    if (seenPointer) {
      var dx = pointerX - x;
      var dy = pointerY - y;
      var d = Math.sqrt(dx * dx + dy * dy);

      if (d > NEAR) {
        if (mode !== "follow") {
          mode = "follow";
          // A fresh sideways lean each leg, so it arrives at an angle and from
          // a different side each time rather than tracking dead-on.
          bias = (Math.random() * 2 - 1) * 42;
        }
        speed = d > FAR ? RUN : WALK;
        setPose(d > FAR ? "run" : "walk");
        // Stop a little inside the comfort ring — overshooting and settling
        // back reads as eagerness; braking exactly on the line reads as a
        // machine.
        var k = (d - NEAR * 0.92) / d;
        var b = bounds();
        tx = clamp(x + dx * k + (-dy / d) * bias, b.minX, b.maxX);
        ty = clamp(y + dy * k + (dx / d) * bias, b.minY, b.maxY);
        face(tx);
        return;
      }

      // Close enough. Sit down and watch.
      if (mode === "follow") {
        face(pointerX);
        onArrive();
        return;
      }
    }

    if (mode === "wander" && arrived()) onArrive();
  }

  function tick(now) {
    raf = 0;
    // Clamp dt so a backgrounded tab does not teleport the cat on return.
    var dt = lastFrame ? Math.min((now - lastFrame) / 1000, 0.05) : 0.016;
    lastFrame = now;

    if (mode === "exit") {
      moveToward(dt);
      if (arrived()) {
        finish();
        return;
      }
    } else if (mode === "enter") {
      moveToward(dt);
      if (arrived()) onArrive();
    } else {
      decide();
      moveToward(dt);
      if (mode !== "rest" && arrived()) onArrive();
    }

    place();

    // Per-frame writes to localStorage would be pathological; once a second is
    // plenty, and pagehide catches whatever the last second missed.
    var t = Date.now();
    if (t - lastSave > 1000) {
      lastSave = t;
      save();
    }

    if (mode !== "rest") kick();
  }

  // The reduced-motion loop: same decisions, no interpolation.
  function stepOnce() {
    stepTimer = 0;
    if (!cat) return;
    if (mode === "exit") {
      finish();
      return;
    }
    decide();
    if (mode !== "rest") {
      x = tx;
      y = ty;
      place();
      save();
      onArrive();
    }
  }

  // ------------------------------------------------------------------- idling

  function scheduleRest() {
    window.clearTimeout(restTimer);
    restTimer = window.setTimeout(idleBeat, WANDER_AFTER + Math.random() * 2600);
  }

  function idleBeat() {
    if (!cat || mode !== "rest" || holding) return;

    if (Date.now() - lastMove > SLEEP_AFTER) {
      setPose("sleep");
      scheduleRest();
      return;
    }

    // One idle beat in four is spent washing rather than moving.
    if (Math.random() < 0.25) {
      setPose("groom");
      scheduleRest();
      return;
    }

    wander();
  }

  function wander() {
    var b = bounds();
    var angle = Math.random() * Math.PI * 2;
    var reach = 60 + Math.random() * 90;
    // Flattened on the vertical, because it is meant to read as walking around
    // a floor rather than drifting through the air.
    var nx = x + Math.cos(angle) * reach;
    var ny = y + Math.sin(angle) * reach * 0.45;

    // Drift away from the pointer rather than into it — the cat keeps its
    // distance when it is the one choosing where to go.
    if (seenPointer && Math.abs(nx - pointerX) < NEAR) {
      nx += nx < pointerX ? -NEAR : NEAR;
    }

    tx = clamp(nx, b.minX, b.maxX);
    ty = clamp(ny, b.minY, b.maxY);
    mode = "wander";
    speed = AMBLE;
    setPose("walk");
    face(tx);
    kick();
  }

  function wake() {
    if (pose !== "sleep") return;
    setPose("alert");
    window.clearTimeout(poseTimer);
    poseTimer = window.setTimeout(function () {
      if (pose === "alert") setPose("sit");
    }, 260);
  }

  // --------------------------------------------------------- summon, dismiss

  function syncButtons() {
    Array.prototype.forEach.call(buttons, function (button) {
      button.setAttribute(
        "aria-pressed",
        button.getAttribute("data-summon") === cat ? "true" : "false"
      );
    });
  }

  function summon(which, walkIn) {
    cat = which;
    root.setAttribute("data-familiar", which);
    el.setAttribute("data-cat", which);
    el.hidden = false;
    write(KEY, which);
    syncButtons();

    var b = bounds();
    if (walkIn) {
      // Come in from whichever side is further from the pointer, so the cat
      // does not materialise under your hand.
      var fromLeft = !seenPointer || pointerX > window.innerWidth / 2;
      x = fromLeft ? -SPRITE_W : window.innerWidth + SPRITE_W;
      y = b.maxY;
      tx = clamp(fromLeft ? b.minX + 60 : b.maxX - 60, b.minX, b.maxX);
      ty = b.maxY;
      mode = "enter";
      speed = WALK;
      setPose("walk");
      face(tx);
    } else {
      if (!restore()) {
        x = b.minX + 60;
        y = b.maxY;
      }
      mode = "rest";
      setPose("sit");
      scheduleRest();
    }
    place();
    kick();
  }

  function dismiss() {
    if (!cat) return;
    window.clearTimeout(restTimer);
    window.clearTimeout(poseTimer);
    mode = "exit";
    speed = RUN;
    setPose("run");
    // Off whichever side it is already nearest.
    tx = x < window.innerWidth / 2 ? -SPRITE_W : window.innerWidth + SPRITE_W;
    ty = y;
    face(tx);
    kick();
  }

  function finish() {
    cat = null;
    mode = "rest";
    el.hidden = true;
    el.removeAttribute("data-cat");
    root.removeAttribute("data-familiar");
    write(KEY, null);
    write(AT_KEY, null);
    syncButtons();

    if (pending) {
      var next = pending;
      pending = null;
      summon(next, true);
    }
  }

  // ---------------------------------------------------------------- handling

  function pet() {
    // Restarting a running animation needs the class off, a reflow, then the
    // class back on — otherwise a second press inside the first hop does
    // nothing at all.
    el.classList.remove("is-petted");
    void el.offsetWidth;
    el.classList.add("is-petted");
    window.clearTimeout(petTimer);
    petTimer = window.setTimeout(function () {
      el.classList.remove("is-petted");
    }, 440);

    var heart = document.createElement("span");
    heart.className = "fam-heart";
    el.appendChild(heart);
    // Removed on a timer rather than on animationend: with reduced motion the
    // animation is clamped away, the event never arrives, and the heart would
    // stay pinned to the cat for the rest of the visit.
    window.setTimeout(function () {
      if (heart.parentNode) heart.parentNode.removeChild(heart);
    }, 950);

    setPose("alert");
    window.clearTimeout(poseTimer);
    poseTimer = window.setTimeout(function () {
      if (pose === "alert") setPose("sit");
    }, 340);
  }

  function endHold(petIt) {
    if (!holding) return;
    holding = false;
    window.clearTimeout(holdTimer);
    el.classList.remove("is-holding");
    if (petIt && !heldLong) pet();
    heldLong = false;
    kick();
  }

  // ------------------------------------------------------------------ wiring

  Array.prototype.forEach.call(buttons, function (button) {
    button.addEventListener("click", function () {
      var which = button.getAttribute("data-summon");
      if (cat === which) {
        dismiss();
      } else if (cat) {
        // Only one of them is ever out. The first leaves, and its exit brings
        // the other one on.
        pending = which;
        dismiss();
      } else {
        summon(which, true);
      }
    });
  });

  document.addEventListener(
    "pointermove",
    function (event) {
      pointerX = event.clientX;
      pointerY = event.clientY;
      seenPointer = true;
      lastMove = Date.now();
      wake();
      kick();
    },
    { passive: true }
  );

  // Taps count as the pointer for anything without a hover: on a phone this is
  // the whole of the input, and the cat walks to wherever you last touched.
  document.addEventListener(
    "pointerdown",
    function (event) {
      if (sprite.contains(event.target)) return;
      pointerX = event.clientX;
      pointerY = event.clientY;
      seenPointer = true;
      lastMove = Date.now();
      wake();
      kick();
    },
    { passive: true }
  );

  sprite.addEventListener("pointerdown", function (event) {
    if (!cat) return;
    event.preventDefault();
    holding = true;
    heldLong = false;
    el.classList.add("is-holding");
    // Capture, so the cat keeps receiving the release even if it shifts out
    // from under the pointer.
    if (sprite.setPointerCapture) {
      try {
        sprite.setPointerCapture(event.pointerId);
      } catch (e) {}
    }
    window.clearTimeout(holdTimer);
    holdTimer = window.setTimeout(function () {
      heldLong = true;
      holding = false;
      el.classList.remove("is-holding");
      dismiss();
    }, HOLD_MS);
  });

  sprite.addEventListener("pointerup", function () {
    endHold(true);
  });

  sprite.addEventListener("pointercancel", function () {
    endHold(false);
  });

  // The other way home, for anyone who reaches for it before finding the hold.
  sprite.addEventListener("contextmenu", function (event) {
    if (!cat) return;
    event.preventDefault();
    endHold(false);
    dismiss();
  });

  sprite.addEventListener("pointerenter", function () {
    if (hintDone || !cat || !hintTag) return;
    hintDone = true;
    write(HINT_KEY, "1");
    hintTag.hidden = false;
    window.setTimeout(function () {
      hintTag.hidden = true;
    }, 3200);
  });

  window.addEventListener("resize", function () {
    if (!cat) return;
    var b = bounds();
    tx = clamp(tx, b.minX, b.maxX);
    ty = clamp(ty, b.minY, b.maxY);
    place();
  });

  window.addEventListener("pagehide", save);

  // -------------------------------------------------------------------- start

  var nav = document.querySelector(".navbar");
  if (nav) navH = Math.round(nav.getBoundingClientRect().height) || NAV_FALLBACK;

  hintDone = read(HINT_KEY) === "1";
  lastMove = Date.now();

  var initial = root.getAttribute("data-familiar");
  if (initial === ARTEMIS || initial === APOLLO) {
    // Already chosen on a previous page. Pick up roughly where it was standing
    // rather than walking in again on every navigation.
    summon(initial, false);
  } else {
    syncButtons();
  }
})();
