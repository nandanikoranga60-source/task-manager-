/* LifeHub — shared browser auth + site header.
   Included on every page. On protected pages it guards access (redirecting to
   login.html when signed out) and injects a consistent grouped header.
   NOTE: this is browser-only auth (localStorage) — convenient and it works,
   but it is NOT real security. Do not use it to protect sensitive data. */
(function () {
  "use strict";
  var USERS_KEY = "lifehub.users";
  var SESSION_KEY = "lifehub.session";
  var file = (location.pathname.split("/").pop() || "index.html").toLowerCase();
  var isLogin = file === "login.html" || file === "";

  // ---------------- auth core ----------------
  function getUsers() { try { return JSON.parse(localStorage.getItem(USERS_KEY)) || {}; } catch (e) { return {}; } }
  function saveUsers(u) { localStorage.setItem(USERS_KEY, JSON.stringify(u)); }
  function session() { try { return JSON.parse(localStorage.getItem(SESSION_KEY)); } catch (e) { return null; } }
  function setSession(email, name) { localStorage.setItem(SESSION_KEY, JSON.stringify({ email: email, name: name, ts: Date.now() })); }

  async function sha256(text) {
    var buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
    return Array.from(new Uint8Array(buf)).map(function (b) { return b.toString(16).padStart(2, "0"); }).join("");
  }

  async function signup(name, email, password) {
    name = (name || "").trim(); email = (email || "").trim().toLowerCase();
    if (!name) throw new Error("Please enter your name.");
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) throw new Error("Please enter a valid email address.");
    if ((password || "").length < 6) throw new Error("Password must be at least 6 characters.");
    var users = getUsers();
    if (users[email]) throw new Error("An account with this email already exists — try logging in.");
    var salt = Math.random().toString(36).slice(2) + Date.now().toString(36);
    users[email] = { name: name, salt: salt, hash: await sha256(salt + password) };
    saveUsers(users);
    setSession(email, name);
  }

  async function login(email, password) {
    email = (email || "").trim().toLowerCase();
    var users = getUsers();
    var u = users[email];
    if (!u) throw new Error("No account found for this email. Please sign up first.");
    if ((await sha256(u.salt + password)) !== u.hash) throw new Error("Incorrect password. Please try again.");
    setSession(email, u.name);
  }

  function logout() { localStorage.removeItem(SESSION_KEY); location.replace("login.html"); }

  window.LifeHub = { signup: signup, login: login, logout: logout, session: session, getUsers: getUsers };

  // ---------------- route guard (runs immediately) ----------------
  if (!isLogin && !session()) { location.replace("login.html"); return; }

  // ---------------- shared header ----------------
  var GROUPS = [
    { label: "", items: [{ k: "index", t: "🏠 Home", h: "index.html" }] },
    { label: "Money", items: [{ k: "expenses", t: "💰 Expenses", h: "expenses.html" }] },
    { label: "Health", items: [
      { k: "healthcare", t: "🧑‍⚕️ Healthcare", h: "healthcare.html" },
      { k: "medicine", t: "💊 Medicine", h: "medicine.html" },
      { k: "wellness", t: "🌿 Wellness", h: "wellness.html" },
      { k: "dashboard", t: "🏥 ED Ops", h: "dashboard.html" },
      { k: "triage", t: "🩺 Triage", h: "triage.html" },
    ] },
    { label: "Tools", items: [
      { k: "tasks", t: "✅ Tasks", h: "tasks.html" },
      { k: "tailor", t: "🧵 Tailor", h: "tailor.html" },
    ] },
  ];

  var CSS =
    ".lh-hd{position:sticky;top:0;z-index:50;background:var(--lh-bar,rgba(250,250,249,.85));backdrop-filter:blur(10px);" +
    "border-bottom:1px solid rgba(128,128,128,.2);font-family:system-ui,-apple-system,'Segoe UI','Nirmala UI',sans-serif;}" +
    "@media (prefers-color-scheme:dark){.lh-hd{background:var(--lh-bar,rgba(18,18,20,.85));}}" +
    ".lh-top{display:flex;align-items:center;gap:.75rem;max-width:1180px;margin:0 auto;padding:.55rem 1rem;}" +
    ".lh-brand{font-weight:800;font-size:1.02rem;letter-spacing:-.01em;text-decoration:none;color:inherit;display:flex;align-items:center;gap:.4rem;}" +
    ".lh-brand .dot{width:9px;height:9px;border-radius:50%;background:#2e9e6b;box-shadow:0 0 0 3px rgba(46,158,107,.2);}" +
    ".lh-spacer{flex:1;}" +
    ".lh-user{font-size:.82rem;opacity:.8;white-space:nowrap;}" +
    ".lh-btn{font:inherit;font-size:.8rem;font-weight:600;cursor:pointer;border:1px solid rgba(128,128,128,.35);background:transparent;color:inherit;padding:.32rem .6rem;border-radius:8px;}" +
    ".lh-btn:hover{border-color:rgba(128,128,128,.7);}" +
    ".lh-nav{display:flex;flex-wrap:wrap;gap:.3rem .5rem;align-items:center;max-width:1180px;margin:0 auto;padding:0 1rem .55rem;}" +
    ".lh-grp{display:flex;align-items:center;gap:.3rem;}" +
    ".lh-grp-l{font-size:.62rem;font-weight:800;text-transform:uppercase;letter-spacing:.06em;opacity:.5;margin:0 .15rem 0 .5rem;}" +
    ".lh-nav a{font-size:.8rem;font-weight:600;text-decoration:none;color:inherit;opacity:.78;padding:.3rem .6rem;border-radius:999px;border:1px solid rgba(128,128,128,.3);white-space:nowrap;}" +
    ".lh-nav a:hover{opacity:1;border-color:rgba(128,128,128,.6);}" +
    ".lh-nav a[aria-current=page]{background:rgba(128,128,128,.18);opacity:1;border-color:rgba(128,128,128,.55);}" +
    ".lh-sep{width:1px;align-self:stretch;background:rgba(128,128,128,.2);margin:.1rem .2rem;}";

  function injectHeader() {
    // remove any legacy per-page nav bars
    var old = document.querySelectorAll(".app-nav");
    for (var i = 0; i < old.length; i++) old[i].remove();

    var s = session() || { name: "Guest" };
    var style = document.createElement("style");
    style.textContent = CSS;
    document.head.appendChild(style);

    var navHtml = GROUPS.map(function (g, gi) {
      var links = g.items.map(function (it) {
        var cur = it.k === file.replace(".html", "") ? ' aria-current="page"' : "";
        return '<a href="' + it.h + '"' + cur + ">" + it.t + "</a>";
      }).join("");
      var lbl = g.label ? '<span class="lh-grp-l">' + g.label + "</span>" : "";
      return (gi > 0 ? '<span class="lh-sep"></span>' : "") + '<span class="lh-grp">' + lbl + links + "</span>";
    }).join("");

    var hd = document.createElement("header");
    hd.className = "lh-hd";
    hd.innerHTML =
      '<div class="lh-top">' +
      '<a class="lh-brand" href="index.html"><span class="dot"></span>LifeHub</a>' +
      '<span class="lh-spacer"></span>' +
      '<span class="lh-user">Hi, ' + escapeHtml(s.name.split(" ")[0]) + "</span>" +
      '<button class="lh-btn" id="lh-logout" type="button">Log out</button>' +
      "</div>" +
      '<nav class="lh-nav">' + navHtml + "</nav>";
    document.body.insertBefore(hd, document.body.firstChild);
    document.getElementById("lh-logout").addEventListener("click", function () {
      if (confirm("Log out of LifeHub?")) LifeHub.logout();
    });
  }

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  if (!isLogin) {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", injectHeader);
    else injectHeader();
  }
})();
