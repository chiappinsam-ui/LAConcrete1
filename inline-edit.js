(() => {
  if (window.__INLINE_EDIT_LOADED) return;
  window.__INLINE_EDIT_LOADED = true;

  const state = {
    open: false,
    editing: false,
    session: null,
  };

  const style = document.createElement("style");
  style.textContent = `
    #inline-admin {
      position: fixed;
      right: 16px;
      bottom: 16px;
      z-index: 99999;
      width: 320px;
      max-width: calc(100% - 24px);
      padding: 14px;
      border-radius: 12px;
      border: 1px solid rgba(255,255,255,0.14);
      background: rgba(0,0,0,0.82);
      color: #fff;
      font-family: Arial, sans-serif;
      box-shadow: 0 12px 38px rgba(0,0,0,0.45);
      display: none;
    }
    #inline-admin[data-open="1"] { display: block; }
    #inline-admin h4 { margin: 0 0 8px 0; font-size: 15px; letter-spacing: 0.4px; }
    #inline-admin .inline-admin-row { margin-bottom: 8px; }
    #inline-admin label { display: block; font-size: 12px; opacity: 0.82; margin-bottom: 2px; }
    #inline-admin input {
      width: 100%;
      box-sizing: border-box;
      padding: 8px 10px;
      border-radius: 8px;
      border: 1px solid rgba(255,255,255,0.18);
      background: rgba(255,255,255,0.08);
      color: #fff;
      font-size: 13px;
    }
    #inline-admin button {
      cursor: pointer;
      border: 1px solid rgba(255,255,255,0.24);
      background: rgba(255,255,255,0.08);
      color: #fff;
      padding: 8px 10px;
      border-radius: 8px;
      font-size: 13px;
      transition: background 0.12s ease, border-color 0.12s ease;
    }
    #inline-admin button:hover { background: rgba(255,255,255,0.16); border-color: rgba(255,255,255,0.32); }
    #inline-admin .inline-actions { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin-top: 6px; }
    #inline-admin .inline-status { font-size: 12px; opacity: 0.82; }
    #inline-admin .inline-error { font-size: 12px; color: #fca5a5; min-height: 16px; margin-top: 4px; }
    #inline-admin .inline-hint { font-size: 11px; opacity: 0.7; margin-top: 6px; }
  `;
  document.head.appendChild(style);

  const modal = document.createElement("div");
  modal.id = "inline-admin";
  modal.innerHTML = `
    <h4>Inline Admin</h4>
    <div class="inline-admin-row">
      <div class="inline-status" data-inline="status">Loading auth…</div>
      <div class="inline-error" data-inline="error"></div>
    </div>
    <div class="inline-admin-row">
      <label>Email</label>
      <input type="email" data-inline="email" placeholder="admin@example.com" />
    </div>
    <div class="inline-admin-row">
      <label>Password</label>
      <input type="password" data-inline="password" placeholder="••••••••" />
    </div>
    <div class="inline-actions">
      <button type="button" data-inline="login">Log in</button>
      <button type="button" data-inline="logout">Log out</button>
      <button type="button" data-inline="toggle">Toggle edit</button>
      <button type="button" data-inline="close">Close</button>
    </div>
    <div class="inline-hint">Press Ctrl + Alt + E to open/close</div>
  `;
  document.body.appendChild(modal);

  const statusEl = modal.querySelector('[data-inline="status"]');
  const errorEl = modal.querySelector('[data-inline="error"]');
  const emailEl = modal.querySelector('[data-inline="email"]');
  const passEl = modal.querySelector('[data-inline="password"]');
  const loginBtn = modal.querySelector('[data-inline="login"]');
  const logoutBtn = modal.querySelector('[data-inline="logout"]');
  const toggleBtn = modal.querySelector('[data-inline="toggle"]');
  const closeBtn = modal.querySelector('[data-inline="close"]');

  function setError(msg) {
    errorEl.textContent = msg || "";
  }

  function setStatus(msg) {
    statusEl.textContent = msg;
  }

  function setEditMode(enabled) {
    state.editing = !!enabled;
    document.documentElement.dataset.inlineEdit = state.editing ? "1" : "0";
    document.dispatchEvent(new CustomEvent("inline-edit:toggle", { detail: { active: state.editing, session: state.session } }));
    toggleBtn.textContent = state.editing ? "Disable edit" : "Enable edit";
  }

  function updateSession(session) {
    state.session = session || null;
    if (!state.session) {
      setEditMode(false);
      setStatus("Not signed in.");
      return;
    }
    const email = state.session.user?.email || "Signed in";
    setStatus(`Signed in as ${email}`);
  }

  function toggleModal() {
    state.open = !state.open;
    modal.dataset.open = state.open ? "1" : "0";
  }

  function requireClient() {
    if (!window.supabaseClient || !window.supabaseAuth) {
      setError("Supabase not configured. Set url/key in supabase-config.js.");
      return false;
    }
    setError("");
    return true;
  }

  loginBtn.addEventListener("click", async () => {
    if (!requireClient()) return;
    const email = emailEl.value.trim();
    const password = passEl.value.trim();
    const res = await window.supabaseAuth.signIn(email, password);
    if (res?.error) {
      setError(typeof res.error === "string" ? res.error : "Login failed.");
      return;
    }
    setError("");
  });

  logoutBtn.addEventListener("click", async () => {
    if (!requireClient()) return;
    const res = await window.supabaseAuth.signOut();
    if (res?.error) {
      setError(typeof res.error === "string" ? res.error : "Sign-out failed.");
      return;
    }
    setError("");
    setEditMode(false);
  });

  toggleBtn.addEventListener("click", () => {
    if (!state.session) {
      setError("Log in before enabling edit mode.");
      return;
    }
    setError("");
    setEditMode(!state.editing);
  });

  closeBtn.addEventListener("click", () => {
    state.open = false;
    modal.dataset.open = "0";
  });

  window.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.altKey && e.key.toLowerCase() === "e") {
      e.preventDefault();
      toggleModal();
    }
  });

  document.addEventListener("supabase:auth-state", (event) => {
    updateSession(event.detail?.session || null);
  });

  if (window.supabaseAuth?.getSession) {
    updateSession(window.supabaseAuth.getSession());
  } else {
    setStatus("Waiting for Supabase…");
  }
})();
