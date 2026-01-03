(() => {
  const TOKEN_KEY = "__ADMIN_TOKEN__";
  const MODE_KEY = "__ADMIN_MODE__";

  const isEditMode = () => localStorage.getItem(MODE_KEY) === "1";
  const setEditMode = (on) => localStorage.setItem(MODE_KEY, on ? "1" : "0");

  const getToken = () => localStorage.getItem(TOKEN_KEY) || "";
  const setToken = (t) => localStorage.setItem(TOKEN_KEY, t || "");

  // ---- stable hash for images with no data-slot ----
  async function sha256Hex(str) {
    const enc = new TextEncoder().encode(str);
    const buf = await crypto.subtle.digest("SHA-256", enc);
    const arr = Array.from(new Uint8Array(buf));
    return arr.map(b => b.toString(16).padStart(2, "0")).join("");
  }

  function normalizeSrc(img) {
    const src = (img.currentSrc || img.src || "").trim();
    if (!src) return "";
    try {
      const u = new URL(src, location.href);
      u.search = "";
      u.hash = "";
      return u.pathname;
    } catch {
      return src.split("?")[0].split("#")[0];
    }
  }

  async function slotFor(img) {
    const ds = (img.dataset && img.dataset.slot) ? img.dataset.slot.trim() : "";
    if (ds) return ds;
    const key = normalizeSrc(img);
    const hex = await sha256Hex(key || ("img:" + Math.random()));
    return "img_" + hex.slice(0, 24);
  }

  function skippable(img) {
    const src = (img.currentSrc || img.src || "").toLowerCase();
    if (!src) return true;
    if (src.startsWith("data:")) return true;
    if (src.endsWith(".svg")) return true;
    // avoid tiny icons/logos
    const w = img.naturalWidth || img.width || 0;
    const h = img.naturalHeight || img.height || 0;
    if (w && h && (w < 60 || h < 60)) return true;
    return false;
  }

  // ---- overlay layer (does NOT wrap DOM, so it won't wreck layout) ----
  let overlay = null;
  let badge = null;
  const controls = new Map(); // img -> {replaceBtn, delBtn, slotPromise}

  function ensureOverlay() {
    if (overlay) return;
    overlay = document.createElement("div");
    overlay.id = "__adminOverlay";
    overlay.style.cssText = `
      position: fixed;
      inset: 0;
      pointer-events: none;
      z-index: 2147483647;
    `;
    document.body.appendChild(overlay);

    badge = document.createElement("div");
    badge.style.cssText = `
      position: fixed;
      left: 14px;
      bottom: 14px;
      z-index: 2147483647;
      background: rgba(0,0,0,0.72);
      color: #fff;
      border: 1px solid rgba(255,255,255,0.18);
      border-radius: 12px;
      padding: 10px 12px;
      font: 12px/1.2 Arial, sans-serif;
      pointer-events: auto;
    `;
    document.body.appendChild(badge);
  }

  function destroyOverlay() {
    if (overlay) overlay.remove();
    overlay = null;
    if (badge) badge.remove();
    badge = null;
    controls.clear();
  }

  function setBadgeText(t) {
    if (!badge) return;
    badge.textContent = t;
  }

  function createButton(text) {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = text;
    b.style.cssText = `
      pointer-events: auto;
      border: 1px solid rgba(255,255,255,0.18);
      background: rgba(0,0,0,0.62);
      color: #fff;
      border-radius: 10px;
      padding: 6px 10px;
      font: 12px/1 Arial, sans-serif;
      cursor: pointer;
      user-select: none;
    `;
    return b;
  }

  function positionFor(img) {
    const r = img.getBoundingClientRect();
    // hidden/offscreen
    if (r.width < 30 || r.height < 30) return null;
    if (r.bottom < 0 || r.top > window.innerHeight) return null;
    if (r.right < 0 || r.left > window.innerWidth) return null;
    return { top: r.top + 8, left: r.left + r.width - 8 };
  }

  let rafId = 0;
  function scheduleReposition() {
    if (!overlay) return;
    if (rafId) return;
    rafId = requestAnimationFrame(() => {
      rafId = 0;
      repositionAll();
    });
  }

  function repositionAll() {
    if (!overlay) return;
    for (const [img, obj] of controls.entries()) {
      const pos = positionFor(img);
      if (!pos) {
        obj.wrap.style.display = "none";
        continue;
      }
      obj.wrap.style.display = "flex";
      obj.wrap.style.position = "fixed";
      obj.wrap.style.gap = "8px";
      obj.wrap.style.top = pos.top + "px";
      obj.wrap.style.left = (pos.left - obj.wrap.offsetWidth) + "px";
    }
  }

  function ensureControlFor(img) {
    if (controls.has(img)) return;

    const wrap = document.createElement("div");
    wrap.style.cssText = `
      display: flex;
      gap: 8px;
      pointer-events: none;
    `;

    const replaceBtn = createButton("Replace");
    const delBtn = createButton("✕");
    delBtn.style.background = "rgba(150,0,0,0.62)";
    delBtn.title = "Delete replacement";

    wrap.appendChild(replaceBtn);
    wrap.appendChild(delBtn);

    // enable clicking
    wrap.style.pointerEvents = "none";
    replaceBtn.style.pointerEvents = "auto";
    delBtn.style.pointerEvents = "auto";

    overlay.appendChild(wrap);

    // store original src once
    if (!img.dataset.origSrc) img.dataset.origSrc = img.currentSrc || img.src || "";

    const slotPromise = slotFor(img);

    replaceBtn.addEventListener("click", async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const slot = await slotPromise;
      const file = await pickFile();
      if (!file) return;
      await doUpload(slot, file);
      // show immediately via /media/<slot>?v=...
      img.src = `/media/${encodeURIComponent(slot)}?v=${Date.now()}`;
      scheduleReposition();
    });

    delBtn.addEventListener("click", async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const slot = await slotPromise;
      if (!confirm("Delete replacement for this image?")) return;
      await doDelete(slot);
      // revert: if it was /media/slot, reload that; else go back to stored original
      const orig = img.dataset.origSrc || "";
      if (orig.includes("/media/")) {
        img.src = `/media/${encodeURIComponent(slot)}?v=${Date.now()}`;
      } else if (orig) {
        img.src = orig;
      }
      scheduleReposition();
    });

    controls.set(img, { wrap, replaceBtn, delBtn, slotPromise });
  }

  function clearControls() {
    for (const obj of controls.values()) {
      obj.wrap.remove();
    }
    controls.clear();
  }

  function scanImages() {
    const imgs = Array.from(document.images);
    for (const img of imgs) {
      if (skippable(img)) continue;
      ensureControlFor(img);
    }
    scheduleReposition();
  }

  async function doUpload(slot, file) {
    const token = getToken();
    if (!token) throw new Error("Missing admin token");
    const fd = new FormData();
    fd.append("file", file);

    const res = await fetch(`/admin/upload/${encodeURIComponent(slot)}`, {
      method: "POST",
      headers: { "X-Admin-Token": token },
      body: fd,
    });

    if (!res.ok) throw new Error(await res.text());
  }

  async function doDelete(slot) {
    const token = getToken();
    if (!token) throw new Error("Missing admin token");

    const res = await fetch(`/admin/delete/${encodeURIComponent(slot)}`, {
      method: "DELETE",
      headers: { "X-Admin-Token": token },
    });

    if (!res.ok) throw new Error(await res.text());
  }

  function pickFile() {
    return new Promise((resolve) => {
      const input = document.createElement("input");
      input.type = "file";
      input.accept = "image/*";
      input.onchange = () => resolve(input.files && input.files[0] ? input.files[0] : null);
      input.click();
    });
  }

  function enable() {
    ensureOverlay();
    setBadgeText("ADMIN MODE ON — Ctrl+Alt+E to exit");
    scanImages();
  }

  function disable() {
    setBadgeText("");
    clearControls();
    destroyOverlay();
  }

  // keep overlays aligned
  window.addEventListener("scroll", scheduleReposition, { passive: true });
  window.addEventListener("resize", scheduleReposition);

  // dynamic content
  const mo = new MutationObserver(() => {
    if (!isEditMode()) return;
    scanImages();
  });

  document.addEventListener("DOMContentLoaded", () => {
    mo.observe(document.documentElement, { childList: true, subtree: true });

    // apply saved mode
    if (isEditMode()) enable();
  });

  // Ctrl+Alt+E toggle
  window.addEventListener("keydown", (e) => {
    if (!(e.ctrlKey && e.altKey && (e.key || "").toLowerCase() === "e")) return;
    e.preventDefault();

    const on = !isEditMode();
    setEditMode(on);

    if (on) {
      let tok = getToken();
      if (!tok) {
        tok = prompt("Admin token:") || "";
        if (!tok) {
          setEditMode(false);
          return;
        }
        setToken(tok);
      }
      enable();
    } else {
      disable();
    }
  }, true);
})();
