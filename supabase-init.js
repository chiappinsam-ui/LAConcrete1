(() => {
  if (window.supabaseClient) return;

  const cfg = window.SUPABASE_CONFIG || {};
  if (!window.supabase) {
    console.warn("Supabase JS not loaded; inline admin will be disabled.");
    return;
  }

  if (!cfg.url || !cfg.anonKey) {
    console.warn("Supabase config missing url/anonKey; set them in supabase-config.js.");
    return;
  }

  const client = window.supabase.createClient(cfg.url, cfg.anonKey);
  window.supabaseClient = client;

  let currentSession = null;

  function broadcast() {
    const detail = { client, session: currentSession };
    document.dispatchEvent(new CustomEvent("supabase:auth-state", { detail }));
  }

  async function loadSession() {
    const { data, error } = await client.auth.getSession();
    if (error) {
      console.warn("Supabase session lookup failed:", error.message);
      return;
    }
    currentSession = data?.session || null;
    broadcast();
  }

  client.auth.onAuthStateChange((_event, session) => {
    currentSession = session;
    broadcast();
  });

  window.supabaseAuth = {
    client,
    async signIn(email, password) {
      if (!email || !password) return { error: "Email and password are required." };
      const { data, error } = await client.auth.signInWithPassword({ email, password });
      if (error) return { error: error.message || "Login failed." };
      currentSession = data.session;
      broadcast();
      return { data };
    },
    async signOut() {
      const { error } = await client.auth.signOut();
      if (error) return { error: error.message || "Sign-out failed." };
      currentSession = null;
      broadcast();
      return { data: null };
    },
    getSession() {
      return currentSession;
    },
  };

  loadSession();
})();
