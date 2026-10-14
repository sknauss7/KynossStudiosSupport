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
})();
