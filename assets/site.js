/* Kynoss Studios site script: menu, search, catalog filter, support hub, 404 suggestions. */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---- mobile menu ---- */
  var bar = $(".ks-bar");
  var menuBtn = $(".ks-menu-btn");
  if (bar && menuBtn) {
    menuBtn.addEventListener("click", function () {
      var open = bar.classList.toggle("is-open");
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ---- shared: edit distance, for typo-tolerant matching ---- */
  var lev = function (a, b) {
      var m = [], i, j;
      for (i = 0; i <= b.length; i++) m[i] = [i];
      for (j = 0; j <= a.length; j++) m[0][j] = j;
      for (i = 1; i <= b.length; i++) for (j = 1; j <= a.length; j++)
        m[i][j] = b[i - 1] === a[j - 1] ? m[i - 1][j - 1] : Math.min(m[i - 1][j - 1] + 1, m[i][j - 1] + 1, m[i - 1][j] + 1);
      return m[b.length][a.length];
    };

  /* ---- search ---- */
  var index = null;
  function loadIndex() {
    if (index) return Promise.resolve(index);
    return fetch("/search-index.json").then(function (r) { return r.json(); }).then(function (d) { index = d; return d; });
  }
  function norm(s) { return (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }
  function score(item, terms) {
    var t = norm(item.t), d = norm(item.d), s = 0;
    for (var i = 0; i < terms.length; i++) {
      var q = terms[i];
      if (t === q) s += 12;
      else if (t.indexOf(q) === 0) s += 8;
      else if (t.indexOf(q) > -1) s += 5;
      else if (d.indexOf(q) > -1) s += 2;
      else if (q.length >= 4 && t.split(/[^a-z0-9]+/).some(function (w) { return w.length >= 3 && lev(w, q) <= (q.length > 5 ? 2 : 1); })) s += 4;
      else return 0;
    }
    if (item.k === "app") s += 3;
    if (item.k === "page") s += 1;
    return s;
  }
  function search(q) {
    var terms = norm(q).split(/\s+/).filter(Boolean);
    if (!terms.length || !index) return [];
    return index.map(function (it) { return [score(it, terms), it]; })
      .filter(function (p) { return p[0] > 0; })
      .sort(function (a, b) { return b[0] - a[0]; })
      .slice(0, 10).map(function (p) { return p[1]; });
  }
  var KIND = { app: "App", faq: "Help", page: "Page" };
  function renderResults(list, el, q) {
    el.innerHTML = "";
    if (!q) return;
    if (!list.length) {
      var li = document.createElement("li");
      li.className = "ks-search-empty";
      li.textContent = "Nothing matches “" + q + "”. Try an app name, or email support@kynossstudios.com.";
      el.appendChild(li);
      return;
    }
    list.forEach(function (it, i) {
      var li = document.createElement("li");
      var a = document.createElement("a");
      a.href = it.u;
      if (i === 0) a.className = "is-active";
      if (it.i) { var img = document.createElement("img"); img.src = it.i; img.alt = ""; a.appendChild(img); }
      else { var g = document.createElement("span"); g.className = "ks-sglyph"; g.textContent = it.k === "faq" ? "?" : "•"; a.appendChild(g); }
      var st = document.createElement("strong"); st.textContent = it.t; a.appendChild(st);
      var sp = document.createElement("span"); sp.textContent = (KIND[it.k] || "") + (it.a ? " · " + it.a : "") + (it.d ? " · " + it.d : ""); a.appendChild(sp);
      li.appendChild(a); el.appendChild(li);
    });
  }
  var dlg = $("#ks-search");
  if (dlg) {
    var input = $("input", dlg), results = $(".ks-search-results", dlg);
    var open = function () {
      loadIndex();
      if (typeof dlg.showModal === "function") dlg.showModal(); else dlg.setAttribute("open", "");
      input.value = ""; results.innerHTML = ""; input.focus();
    };
    $$("[data-ks-search]").forEach(function (b) { b.addEventListener("click", open); });
    document.addEventListener("keydown", function (e) {
      if ((e.key === "/" && !/input|textarea|select/i.test(document.activeElement.tagName)) || ((e.metaKey || e.ctrlKey) && e.key === "k")) {
        e.preventDefault(); open();
      }
    });
    input.addEventListener("input", function () {
      var q = input.value.trim();
      loadIndex().then(function () { renderResults(search(q), results, q); });
    });
    $("form", dlg).addEventListener("submit", function (e) {
      e.preventDefault();
      var first = $("a", results);
      if (first) location.href = first.href;
    });
    dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });
  }

  /* ---- icon shelf entrance (the one motion moment) ---- */
  $$(".ks-shelf li").forEach(function (t, i) { t.style.setProperty("--i", i); });

  /* ---- catalog filter ---- */
  var chips = $$(".ks-chip[data-cat]");
  if (chips.length) {
    var apply = function (cat) {
      chips.forEach(function (c) { c.setAttribute("aria-pressed", c.dataset.cat === cat ? "true" : "false"); });
      $$(".ks-cat").forEach(function (sec) { sec.hidden = !(cat === "all" || sec.dataset.cat === cat); });
      try { history.replaceState(null, "", cat === "all" ? location.pathname : "?category=" + cat); } catch (e) {}
    };
    chips.forEach(function (c) { c.addEventListener("click", function () { apply(c.dataset.cat); }); });
    var initial = new URLSearchParams(location.search).get("category");
    if (initial && chips.some(function (c) { return c.dataset.cat === initial; })) apply(initial);
  }

  /* ---- support hub ---- */
  var hub = $("#ks-hub");
  if (hub) {
    var data = JSON.parse($("#ks-hub-data").textContent);
    var filter = $(".ks-picker-input", hub);
    var buttons = $$(".ks-picker button", hub);
    var panel = $(".ks-help", hub);
    var show = function (id, scroll) {
      var app = data[id];
      if (!app) { panel.hidden = true; return; }
      buttons.forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.app === id ? "true" : "false"); });
      $(".ks-help-head img", panel).src = app.icon;
      $(".ks-help-name", panel).textContent = app.name + " help";
      $(".ks-help-sub", panel).textContent = app.kind;
      var faq = $(".ks-faq", panel); faq.innerHTML = "";
      app.faq.forEach(function (f) {
        var d = document.createElement("details");
        var s = document.createElement("summary"); s.textContent = f.q; d.appendChild(s);
        var p = document.createElement("div"); p.className = "ks-ans"; p.textContent = f.a; d.appendChild(p);
        faq.appendChild(d);
      });
      faq.hidden = !app.faq.length;
      $(".ks-help-full", panel).href = app.support;
      $(".ks-help-privacy", panel).href = app.privacy;
      var body = "App: " + app.name + "\nApp version (Settings in the app, or the App Store page): \niPhone model: \niOS version: \n\nWhat happened:\n\nWhat you expected:\n";
      $(".ks-help-mail", panel).href = "mailto:support@kynossstudios.com?subject=" + encodeURIComponent(app.name + " support") + "&body=" + encodeURIComponent(body);
      panel.hidden = false;
      try { history.replaceState(null, "", "?app=" + id); } catch (e) {}
      if (scroll) panel.scrollIntoView({ behavior: "smooth", block: "start" });
    };
    buttons.forEach(function (b) { b.addEventListener("click", function () { show(b.dataset.app, true); }); });
    filter.addEventListener("input", function () {
      var q = norm(filter.value.trim());
      buttons.forEach(function (b) { b.parentNode.hidden = q && norm(b.textContent + " " + data[b.dataset.app].kind).indexOf(q) < 0; });
    });
    filter.addEventListener("keydown", function (e) {
      if (e.key !== "Enter") return;
      var vis = buttons.filter(function (b) { return !b.parentNode.hidden; });
      if (vis.length) show(vis[0].dataset.app, true);
    });
    var pre = new URLSearchParams(location.search).get("app");
    if (pre) show(pre, false);
  }

  /* ---- 404 suggestions ---- */
  var sugg = $("#ks-404-suggest");
  if (sugg) {
    var apps = JSON.parse($("#ks-404-data").textContent);
    var path = norm(location.pathname.replace(/^\/KynossStudiosSupport\//, "/"));
    var words = path.split(/[^a-z0-9]+/).filter(function (w) { return w.length > 2; });
    var hits = [];
    apps.forEach(function (a) {
      var best = 99;
      words.forEach(function (w) { best = Math.min(best, lev(w, a.id), w.indexOf(a.id) > -1 ? 0 : 99); });
      if (best <= 2) hits.push([best, a]);
    });
    hits.sort(function (x, y) { return x[0] - y[0]; });
    var wantsPrivacy = /privacy/.test(path), wantsSupport = /support|help/.test(path);
    hits.slice(0, 3).forEach(function (h) {
      var a = h[1], li = document.createElement("li"), link = document.createElement("a");
      link.href = wantsPrivacy ? a.privacy : wantsSupport ? a.support : a.url;
      link.textContent = a.name + (wantsPrivacy ? " privacy policy" : wantsSupport ? " support" : "");
      li.appendChild(link); sugg.appendChild(li);
    });
    if (hits.length) $("#ks-404-maybe").hidden = false;
  }
  /* ---- contact form (home): posts to the kynoss-intake Worker ---- */
  $$("form[data-ks-intake]").forEach(function (form) {
    var started = Date.now();
    var status = $(".ks-form-status", form);
    var button = $("button[type=submit]", form);
    var say = function (text, bad) { status.textContent = text; status.classList.toggle("is-bad", !!bad); };
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var f = form.elements;
      if (!f.name.value.trim() || !f.contact.value.trim() || !f.about.value.trim()) {
        say("Please add your name, an email or phone number, and a few words about what you do.", true);
        return;
      }
      button.disabled = true;
      say("Sending…");
      fetch(form.getAttribute("data-ks-intake"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: f.name.value, contact: f.contact.value, business: f.business.value, about: f.about.value,
                               website: f.website.value, elapsed_ms: Date.now() - started, page: location.pathname })
      }).then(function (r) { return r.json().catch(function () { return {}; }).then(function (b) { return { r: r, b: b }; }); })
        .then(function (x) {
          if (x.r.ok && x.b.ok) {
            form.reset();
            say("Thanks, it's on its way. We'll be in touch soon.");
            return;
          }
          button.disabled = false;
          if (x.b.error === "contact") say("That email or phone number doesn't look right. Could you check it?", true);
          else if (x.b.error === "rate") say("That's a lot of messages in a short time. Please try again in an hour, or email us.", true);
          else say("Something went wrong sending that. Please try again, or email us.", true);
        })
        .catch(function () { button.disabled = false; say("We couldn't reach the server. Please try again, or email us.", true); });
    });
  });
  /* ---- home system core: the scan line spans the hero, and the readouts count up once ---- */
  var hud = $(".ks-hud-hero");
  if (hud) {
    hud.style.setProperty("--scan-h", hud.offsetHeight + "px");
    var still = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!still) {
      $$(".ks-hud-strip [data-count]").forEach(function (el, i) {
        var end = parseInt(el.getAttribute("data-count"), 10), plus = el.hasAttribute("data-plus") ? "+" : "";
        var t0 = null, delay = 1300 + i * 150, dur = 900;
        el.textContent = "0" + plus;
        var step = function (t) {
          if (t0 === null) t0 = t;
          var p = Math.min(1, Math.max(0, (t - t0 - delay) / dur));
          el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3))) + plus;
          if (p < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
      });
    }
  }
  /* ---- home operations view: the visitor steps through the example evening (no autoplay) ---- */
  var ops = $("[data-ks-ops]");
  if (ops) {
    var items = $$(".ks-ops-item", ops), nav = $(".ks-ops-nav", ops), count = $(".ks-ops-count", ops);
    var prev = $("[data-ops=prev]", ops), next = $("[data-ops=next]", ops), at = 0;
    var show = function (i) {
      at = i;
      items.forEach(function (it, n) { it.classList.toggle("is-current", n === i); });
      count.textContent = (i + 1) + " of " + items.length;
      prev.disabled = i === 0;
      next.textContent = i === items.length - 1 ? "Start over" : "Next";
    };
    ops.classList.add("is-stepper");
    nav.hidden = false; count.hidden = false;
    prev.addEventListener("click", function () { if (at > 0) show(at - 1); });
    next.addEventListener("click", function () { show(at === items.length - 1 ? 0 : at + 1); });
    show(0);
  }
  /* ---- home topic chooser: one panel at a time, opened by the visitor (or a #hash link) ---- */
  var panelsBox = $("[data-ks-panels]");
  if (panelsBox) {
    var panels = $$(".ks-panel", panelsBox), choices = $$("[data-choice]");
    var open = function (id, scroll) {
      panels.forEach(function (p) { p.classList.toggle("is-open", p.getAttribute("data-panel") === id); });
      choices.forEach(function (c) { c.setAttribute("aria-current", c.getAttribute("data-choice") === id ? "true" : "false"); });
      var chooser = $(".ks-chooser");
      if (id && scroll && chooser) chooser.scrollIntoView({ behavior: "smooth", block: "start" });
    };
    panelsBox.classList.add("is-chooser");
    choices.forEach(function (c) {
      c.addEventListener("click", function (e) {
        e.preventDefault();
        var id = c.getAttribute("data-choice");
        var wasOpen = c.getAttribute("aria-current") === "true";
        open(wasOpen ? null : id, !wasOpen);
        if (history.replaceState) history.replaceState(null, "", wasOpen ? location.pathname : "#" + id);
      });
    });
    var fromHash = function () {
      var id = location.hash.slice(1);
      if (panels.some(function (p) { return p.getAttribute("data-panel") === id; })) {
        open(id, false);
        setTimeout(function () { var ch = $(".ks-chooser"); if (ch) ch.scrollIntoView({ block: "start" }); }, 0);
      }
    };
    window.addEventListener("hashchange", fromHash);
    fromHash();
  }
  /* ---- home system map: tap a part to see what it does and how ready it is ---- */
  var map = $("[data-ks-map]");
  if (map) {
    var nodes = $$("[data-part]", map), cards = $$("[data-card]", map), lines = $$("[data-line]", map);
    var pick = function (id) {
      nodes.forEach(function (n) { n.setAttribute("aria-pressed", n.getAttribute("data-part") === id ? "true" : "false"); });
      cards.forEach(function (c) { c.classList.toggle("is-on", c.getAttribute("data-card") === id); });
      lines.forEach(function (l) { l.classList.toggle("is-on", id === "core" || l.getAttribute("data-line") === id); });
    };
    map.classList.add("is-js");
    nodes.forEach(function (n) { n.addEventListener("click", function () { pick(n.getAttribute("data-part")); }); });
    pick("texts");
  }
  /* ---- home hologram: a morphing orb of light at the map's core. Pulses run along the lines;
         picking a part makes it "respond". Pauses off screen; a still frame for reduced motion. ---- */
  var holo = $(".ks-holo");
  var holoMap = holo && holo.closest("[data-ks-map]");
  if (holo && holoMap && holo.getContext) {
    var still = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var ctx = holo.getContext("2d"), stage = holo.parentElement;
    var W = 0, H = 0, dpr = 1, cx = 0, cy = 0, R = 0, anchors = [], selected = "texts";
    var hud = [111, 227, 255], warm = [255, 181, 71];
    var rgba = function (c, a) { return "rgba(" + c[0] + "," + c[1] + "," + c[2] + "," + a.toFixed(3) + ")"; };
    var readColors = function () {
      var cs = getComputedStyle(stage);
      var hex = function (v, fb) { v = (v || "").trim(); var m = /^#([0-9a-f]{6})$/i.exec(v); if (!m) return fb; var n = parseInt(m[1], 16); return [n >> 16, (n >> 8) & 255, n & 255]; };
      hud = hex(cs.getPropertyValue("--hud"), hud); warm = hex(cs.getPropertyValue("--hud-warm"), warm);
    };
    // points on a sphere (Fibonacci), each with its own phase for the morph
    var N = 420, pts = [], g = Math.PI * (3 - Math.sqrt(5));
    for (var i = 0; i < N; i++) {
      var y = 1 - (2 * (i + 0.5)) / N, r = Math.sqrt(1 - y * y), ph = i * g;
      pts.push({ x: Math.cos(ph) * r, y: y, z: Math.sin(ph) * r, th: Math.acos(y), ph: ph });
    }
    var layout = function () {
      var b = stage.getBoundingClientRect();
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = b.width; H = b.height;
      holo.width = Math.round(W * dpr); holo.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      cx = W / 2; cy = H / 2; R = Math.min(W, H) * 0.2;
      anchors = $$("[data-part]", holoMap).filter(function (n) { return n.getAttribute("data-part") !== "core"; }).map(function (n) {
        var r = n.getBoundingClientRect(), left = n.classList.contains("is-l");
        return { id: n.getAttribute("data-part"), x: (left ? r.right : r.left) - b.left, y: r.top + r.height / 2 - b.top };
      });
    };
    var amp = 0.07, ampTarget = 0.07, packets = [], sparks = [], ripples = [], flashes = [], lastIdle = 0, lastSel = 0, lastSpark = 0;
    var morph = function (p, t) {
      return 1 + amp * (Math.sin(3 * p.th + t * 0.9) * Math.sin(2 * p.ph + t * 0.6) + 0.6 * Math.sin(5 * p.ph - t * 1.3) * Math.cos(4 * p.th + t * 0.7));
    };
    var project = function (x, y, z, t) {
      var a = t * 0.22, b = 0.38;
      var x1 = x * Math.cos(a) + z * Math.sin(a), z1 = -x * Math.sin(a) + z * Math.cos(a);
      var y2 = y * Math.cos(b) - z1 * Math.sin(b), z2 = y * Math.sin(b) + z1 * Math.cos(b);
      var p = 2.8 / (2.8 - z2);
      return { x: cx + x1 * R * p, y: cy + y2 * R * p, d: (z2 + 1) / 2 };
    };
    var anchorOf = function (id) { for (var i = 0; i < anchors.length; i++) if (anchors[i].id === id) return anchors[i]; return null; };
    var spawn = function (id, dir, now, strong) { packets.push({ id: id, dir: dir, t0: now, dur: strong ? 900 : 1500, strong: strong }); };
    var draw = function (now) {
      var t = now / 1000;
      amp += (ampTarget - amp) * 0.04;
      if (ampTarget > 0.07) ampTarget = Math.max(0.07, ampTarget - 0.0015);
      ctx.clearRect(0, 0, W, H);
      // lines from each part toward the core
      anchors.forEach(function (a) {
        var dx = a.x - cx, dy = (a.y - cy) * 0.55, len = Math.hypot(dx, dy) || 1;
        a.ex = cx + (dx / len) * R * 1.02; a.ey = cy + (dy / len) * R * 1.02;
        a.qx = cx + dx * 0.55; a.qy = a.y;
        // no drawn lines (Steven, 2026-10-14): the path is kept only for the pulses
      });
      // outer HUD: tick ring and two arc rings turning at different speeds
      ctx.save(); ctx.translate(cx, cy);
      ctx.rotate(t * 0.05);
      for (var k = 0; k < 72; k++) {
        var ang = (k / 72) * Math.PI * 2, r1 = R * 1.55, r2 = R * (k % 6 === 0 ? 1.45 : 1.5);
        ctx.strokeStyle = rgba(hud, k % 6 === 0 ? 0.45 : 0.18); ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(Math.cos(ang) * r1, Math.sin(ang) * r1); ctx.lineTo(Math.cos(ang) * r2, Math.sin(ang) * r2); ctx.stroke();
      }
      ctx.restore();
      [[1.2, -0.35, 0.55, 3], [1.32, 0.22, 0.3, 1.5]].forEach(function (ring) {
        ctx.save(); ctx.translate(cx, cy); ctx.rotate(t * ring[1]);
        ctx.strokeStyle = rgba(hud, ring[2]); ctx.lineWidth = ring[3]; ctx.lineCap = "round";
        for (var s = 0; s < 3; s++) { ctx.beginPath(); ctx.arc(0, 0, R * ring[0], s * 2.1, s * 2.1 + 1.1); ctx.stroke(); }
        ctx.restore();
      });
      // core glow, breathing, flaring on a ripple
      var flare = ripples.length ? 0.25 : 0;
      var gl = ctx.createRadialGradient(cx, cy, 0, cx, cy, R * 1.3);
      gl.addColorStop(0, rgba(warm, 0.32 + 0.08 * Math.sin(t * 2) + flare));
      gl.addColorStop(0.35, rgba(hud, 0.12 + flare / 3));
      gl.addColorStop(1, rgba(hud, 0));
      ctx.fillStyle = gl; ctx.beginPath(); ctx.arc(cx, cy, R * 1.3, 0, Math.PI * 2); ctx.fill();
      // wireframe latitudes, morphing with the surface
      for (var L = 1; L <= 5; L++) {
        var th = (L / 6) * Math.PI;
        ctx.beginPath();
        for (var j = 0; j <= 48; j++) {
          var ph = (j / 48) * Math.PI * 2, q = { th: th, ph: ph }, m = morph(q, t);
          var P = project(Math.sin(th) * Math.cos(ph) * m, Math.cos(th) * m, Math.sin(th) * Math.sin(ph) * m, t);
          if (j) ctx.lineTo(P.x, P.y); else ctx.moveTo(P.x, P.y);
        }
        ctx.strokeStyle = rgba(hud, 0.16); ctx.lineWidth = 1; ctx.stroke();
      }
      // the points of light
      var front = [];
      for (var n = 0; n < N; n++) {
        var p = pts[n], m2 = morph(p, t), P2 = project(p.x * m2, p.y * m2, p.z * m2, t);
        ctx.fillStyle = rgba(hud, 0.18 + 0.8 * P2.d * P2.d);
        var sz = 0.5 + 1.5 * P2.d;
        ctx.fillRect(P2.x - sz / 2, P2.y - sz / 2, sz, sz);
        if (P2.d > 0.62) front.push(P2);
      }
      // the living center: a heartbeat core, flickering tendrils and orbiting sparks
      var beat = function (x) { x = x % 1.6; return Math.exp(-Math.pow((x - 0.15) / 0.07, 2)) + 0.6 * Math.exp(-Math.pow((x - 0.42) / 0.08, 2)); };
      var pulse = still ? 0.4 : beat(t), boost = ripples.length ? 0.5 : 0;
      var r0 = R * (0.22 + 0.045 * pulse + 0.04 * boost);
      var cg = ctx.createRadialGradient(cx, cy, 0, cx, cy, r0 * 2.6);
      cg.addColorStop(0, "rgba(255,255,255," + Math.min(1, 0.85 + 0.15 * pulse).toFixed(3) + ")");
      cg.addColorStop(0.18, rgba(warm, 0.9));
      cg.addColorStop(0.45, rgba(warm, 0.28 + 0.2 * pulse + 0.2 * boost));
      cg.addColorStop(1, rgba(warm, 0));
      ctx.fillStyle = cg; ctx.beginPath(); ctx.arc(cx, cy, r0 * 2.6, 0, Math.PI * 2); ctx.fill();
      ctx.lineCap = "round";
      for (var tdl = 0; tdl < 7; tdl++) {
        var ta = tdl * 0.898 + t * (0.6 + 0.13 * tdl), tl = r0 * (1.4 + 0.8 * Math.sin(t * 1.7 + tdl * 2.1));
        var bend = Math.sin(t * 2.3 + tdl) * 0.9;
        ctx.strokeStyle = rgba(tdl % 2 ? hud : warm, 0.45 + 0.35 * Math.max(0, Math.sin(t * 3 + tdl * 1.3)));
        ctx.lineWidth = 1.6;
        ctx.beginPath(); ctx.moveTo(cx, cy);
        ctx.quadraticCurveTo(cx + Math.cos(ta + bend) * tl * 0.6, cy + Math.sin(ta + bend) * tl * 0.6, cx + Math.cos(ta) * tl, cy + Math.sin(ta) * tl);
        ctx.stroke();
      }
      for (var o = 0; o < 5; o++) {
        var oa = t * (0.9 + o * 0.35) * (o % 2 ? -1 : 1) + o * 1.3, orr = R * (0.32 + o * 0.06);
        ctx.fillStyle = rgba(o % 2 ? hud : warm, 0.85);
        ctx.beginPath(); ctx.arc(cx + Math.cos(oa) * orr, cy + Math.sin(oa) * orr * 0.55, 1.6, 0, Math.PI * 2); ctx.fill();
      }
      // neural sparks between nearby points on the front
      if (!still && now - lastSpark > 90 && front.length > 2) {
        lastSpark = now;
        var A = front[(Math.random() * front.length) | 0];
        for (var tries = 0; tries < 8; tries++) {
          var B = front[(Math.random() * front.length) | 0];
          var dd = Math.hypot(A.x - B.x, A.y - B.y);
          if (dd > R * 0.12 && dd < R * 0.5) { sparks.push({ a: A, b: B, t0: now }); break; }
        }
        if (sparks.length > 14) sparks.shift();
      }
      sparks = sparks.filter(function (sp) { return now - sp.t0 < 650; });
      sparks.forEach(function (sp) {
        var k2 = 1 - (now - sp.t0) / 650;
        ctx.strokeStyle = rgba(hud, 0.7 * k2); ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(sp.a.x, sp.a.y); ctx.lineTo(sp.b.x, sp.b.y); ctx.stroke();
      });
      // a flash where a pulse lands on the orb
      flashes = flashes.filter(function (fl) { return now - fl.t0 < 500; });
      flashes.forEach(function (fl) {
        var k5 = (now - fl.t0) / 500;
        ctx.fillStyle = rgba(warm, 0.8 * (1 - k5)); ctx.beginPath(); ctx.arc(fl.x, fl.y, 2 + 8 * k5, 0, Math.PI * 2); ctx.fill();
      });
      // ripples when the core takes something in
      ripples = ripples.filter(function (rp) { return now - rp < 800; });
      ripples.forEach(function (rp) {
        var k3 = (now - rp) / 800;
        ctx.strokeStyle = rgba(warm, 0.55 * (1 - k3)); ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(cx, cy, R * (1.05 + 0.45 * k3), 0, Math.PI * 2); ctx.stroke();
      });
      // pulses travelling along the lines: in to the core, then an answer back out
      if (!still) {
        if (now - lastIdle > 1700 && anchors.length) { lastIdle = now; spawn(anchors[(Math.random() * anchors.length) | 0].id, 1, now, false); }
        if (selected && selected !== "core" && now - lastSel > 520) { lastSel = now; spawn(selected, 1, now, true); }
        if (selected === "core" && now - lastSel > 260 && anchors.length) { lastSel = now; spawn(anchors[(Math.random() * anchors.length) | 0].id, 1, now, true); }
      }
      packets = packets.filter(function (pk) {
        var a = anchorOf(pk.id); if (!a || a.ex === undefined) return false;
        var k4 = (now - pk.t0) / pk.dur; if (k4 >= 1) {
          if (pk.dir === 1) { ripples.push(now); flashes.push({ x: a.ex, y: a.ey, t0: now }); ampTarget = Math.min(0.16, ampTarget + (pk.strong ? 0.02 : 0.008)); if (pk.strong) spawn(pk.id, -1, now, true); }
          return false;
        }
        var f = pk.dir === 1 ? k4 : 1 - k4;
        for (var tail = 0; tail < 5; tail++) {
          var ft = Math.max(0, Math.min(1, f - pk.dir * tail * 0.025)), u = 1 - ft;
          var px = u * u * a.x + 2 * u * ft * a.qx + ft * ft * a.ex, py = u * u * a.y + 2 * u * ft * a.qy + ft * ft * a.ey;
          ctx.fillStyle = rgba(pk.dir === 1 ? hud : warm, (pk.strong ? 0.95 : 0.6) * (1 - tail / 5));
          ctx.beginPath(); ctx.arc(px, py, (pk.strong ? 2.6 : 1.8) * (1 - tail / 7), 0, Math.PI * 2); ctx.fill();
        }
        return true;
      });
    };
    var running = false, visible = true, raf = 0;
    var loop = function (now) { draw(now); if (running) raf = requestAnimationFrame(loop); };
    var start = function () { if (still) { draw(4000); return; } if (!running && visible && !document.hidden) { running = true; raf = requestAnimationFrame(loop); } };
    var stop = function () { running = false; cancelAnimationFrame(raf); };
    readColors(); layout();
    holoMap.classList.add("has-holo");
    $$("[data-part]", holoMap).forEach(function (n) {
      n.addEventListener("click", function () { selected = n.getAttribute("data-part"); lastSel = 0; ampTarget = 0.15; if (still) draw(4000); });
    });
    if (window.ResizeObserver) new ResizeObserver(function () { layout(); if (still) draw(4000); }).observe(stage);
    if (window.IntersectionObserver) new IntersectionObserver(function (es) { visible = es[0].isIntersecting; if (visible) start(); else stop(); }).observe(stage);
    document.addEventListener("visibilitychange", function () { if (document.hidden) stop(); else start(); });
    if (window.matchMedia) window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function () { readColors(); if (still) draw(4000); });
    start();
  }
})();
