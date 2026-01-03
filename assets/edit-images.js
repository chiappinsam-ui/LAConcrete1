(() => {
  // turn on only when ?edit=1
  const params = new URLSearchParams(location.search);
  const isEdit = params.get("edit") === "1";
  if (!isEdit) return;

  // YOUR BACKEND URL (FastAPI on Render)
  const BACKEND = "https://YOUR-BACKEND.onrender.com";

  // Ask for token so it isn't hardcoded
  const token = prompt("Admin token:");
  if (!token) return;

  // helper: stable slot id from image src (so same image always maps to same slot)
  async function slotFromSrc(src) {
    // normalize to avoid cache params changing slot
    const clean = src.split("?")[0].split("#")[0];

    // use SHA-256 so slot ids are safe and stable
    const enc = new TextEncoder().encode(clean);
    const hashBuf = await crypto.subtle.digest("SHA-256", enc);
    const hashArr = Array.from(new Uint8Array(hashBuf));
    const hashHex = hashArr.map(b => b.toString(16).padStart(2, "0")).join("");
    return "img_" + hashHex.slice(0, 24); // short id
  }

  // hidden file picker
  const picker = document.createElement("input");
  picker.type = "file";
  picker.accept = "image/*";
  picker.style.display = "none";
  document.body.appendChild(picker);

  // overlay style for edit mode
  const style = document.createElement("style");
  style.textContent = `
    img.__editable { outline: 2px dashed rgba(0,255,255,.35); cursor: pointer; }
    img.__editable:hover { outline-color: rgba(0,255,255,.85); }
    .__editBadge {
      position: fixed; right: 14px; bottom: 14px; z-index: 999999;
      background: rgba(0,0,0,.75); color: #fff; font: 12px/1.2 Arial;
      padding: 10px 12px; border: 1px solid rgba(255,255,255,.18);
      border-radius: 12px;
    }
  `;
  document.head.appendChild(style);

  const badge = document.createElement("div");
  badge.className = "__editBadge";
  badge.textContent = "EDIT MODE ON — click any image to replace";
  document.body.appendChild(badge);

  let currentImg = null;
  let currentSlot = null;

  function isSkippable(img) {
    // skip tiny icons, SVGs, data URLs, empty src, and anything you mark as data-noedit
    if (img.dataset.noedit === "1") return true;
    const src = img.currentSrc || img.src || "";
    if (!src) return true;
    if (src.startsWith("data:")) return true;
    if (src.endsWith(".svg")) return true;
    if ((img.naturalWidth && img.naturalWidth < 80) || (img.naturalHeight && img.naturalHeight < 80)) return true;
    return false;
  }

  async function makeEditable(img) {
    if (isSkippable(img)) return;

    img.classList.add("__editable");
    img.title = "Click to replace this image";

    img.addEventListener("click", async (e) => {
      e.preventDefault();
      e.stopPropagation();

      const src = img.currentSrc || img.src;
      currentSlot = await slotFromSrc(src);
      currentImg = img;

      picker.value = "";
      picker.click();
    }, true);
  }

  picker.addEventListener("change", async () => {
    const file = picker.files[0];
    if (!file || !currentImg || !currentSlot) return;

    const form = new FormData();
    form.append("file", file);

    const res = await fetch(`${BACKEND}/admin/upload/${encodeURIComponent(currentSlot)}`, {
      method: "POST",
      headers: { "X-Admin-Token": token },
      body: form
    });

    if (!res.ok) {
      alert("Upload failed: " + await res.text());
      return;
    }

    const out = await res.json();
    // swap instantly (cache-busted url from backend)
    currentImg.src = out.url;
  });

  // make ALL images editable
  const imgs = Array.from(document.images);
  imgs.forEach(makeEditable);

  // also watch for images that load later (sliders etc.)
  const mo = new MutationObserver((mutations) => {
    for (const m of mutations) {
      for (const node of m.addedNodes) {
        if (node && node.tagName === "IMG") makeEditable(node);
        if (node && node.querySelectorAll) node.querySelectorAll("img").forEach(makeEditable);
      }
    }
  });
  mo.observe(document.documentElement, { childList: true, subtree: true });
})();
