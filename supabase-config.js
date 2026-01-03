(() => {
  const fromScript = (() => {
    const script = document.currentScript;
    if (!script) return {};
    return {
      url: script.dataset?.supabaseUrl || "",
      anonKey: script.dataset?.supabaseAnonKey || "",
    };
  })();

  const metaUrl = document.querySelector('meta[name="supabase-url"]')?.content?.trim() || "";
  const metaKey = document.querySelector('meta[name="supabase-key"]')?.content?.trim() || "";

  const existing = window.SUPABASE_CONFIG || {};

  window.SUPABASE_CONFIG = {
    url:
      existing.url ||
      window.SUPABASE_URL ||
      window.env?.SUPABASE_URL ||
      metaUrl ||
      fromScript.url ||
      "",
    anonKey:
      existing.anonKey ||
      window.SUPABASE_ANON_KEY ||
      window.env?.SUPABASE_ANON_KEY ||
      metaKey ||
      fromScript.anonKey ||
      "",
  };
})();
