// Uses the public key only. Authorization and answer checking run in Postgres.
export function createSupabaseAPI(config, loadSDK = defaultSDK) {
  let clientPromise;
  const fail = code => Object.assign(new Error(code), { code });
  const client = () => clientPromise ||= loadSDK().then(createClient => createClient(config.url, config.publishableKey, {
    auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true,
      storageKey: 'codeplay-auth-' + new URL(config.url).hostname.split('.')[0], flowType: 'implicit' }
  })).catch(() => { clientPromise = null; throw fail('offline'); });
  const convert = error => {
    const known = ['login_required', 'pro_required', 'lesson_missing', 'invalid_name', 'invalid_answer'];
    if (known.includes(error.message)) return fail(error.message);
    if (error.code === 'PGRST202' || error.code === '42883') return fail('setup_required');
    if (error.code === 'email_not_confirmed') return fail('email_not_confirmed');
    if (error.code === 'invalid_credentials') return fail('wrong_credentials');
    if (error.status === 429 || error.code?.includes('rate_limit')) return fail('too_many_attempts');
    if (['email_address_invalid', 'email_address_not_authorized', 'over_email_send_rate_limit', 'unexpected_failure'].includes(error.code)) return fail('email_delivery');
    if (error.code === 'weak_password') return fail('weak_password');
    if (error.status === 401 || error.code === '42501') return fail('login_required');
    return fail('offline');
  };
  async function rpc(name, args) {
    const api = await client();
    const { data, error } = await api.rpc('codeplay_' + name, args);
    if (error) throw convert(error);
    return data;
  }
  async function request(path, data) {
    const api = await client();
    if (path === 'session') {
      await rpc('status');
      const { data: sessionData, error } = await api.auth.getSession();
      if (error) throw convert(error);
      return sessionData.session ? rpc('profile') : { profile: null };
    }
    if (path === 'register' || path === 'login') {
      const email = String(data.email || '').trim();
      if (!email || typeof data.password !== 'string' || data.password.length < 10 || data.password.length > 128) throw fail('invalid_email_credentials');
      if (path === 'register' && (!data.display_name?.trim() || data.display_name.trim().length > 60)) throw fail('invalid_name');
      // Check setup before creating accounts or sending confirmation emails.
      await rpc('status');
      const result = path === 'register'
        ? await api.auth.signUp({ email, password: data.password, options: {
          data: { display_name: data.display_name.trim() },
          emailRedirectTo: new URL('./', window.location.href).href
        } })
        : await api.auth.signInWithPassword({ email, password: data.password });
      if (result.error) throw convert(result.error);
      if (!result.data.session) return { profile: null, confirmation_required: true };
      return rpc('profile');
    }
    if (path === 'logout') {
      const { error } = await api.auth.signOut({ scope: 'local' });
      if (error) throw convert(error);
      return { ok: true };
    }
    if (path === 'profile') return rpc(data ? 'update_profile' : 'profile', data ? { display_name: data.display_name } : undefined);
    if (path === 'lessons') return rpc('catalog');
    if (path.startsWith('lessons/')) return rpc('lesson', { lesson_id: decodeURIComponent(path.slice(8)) });
    if (path === 'answer') return rpc('answer', { lesson_id: data.lesson_id, submitted: data.answer });
    throw fail('lesson_missing');
  }
  return { request };
}

async function defaultSDK() {
  if (!globalThis.supabase?.createClient) throw new Error('SDK missing');
  return globalThis.supabase.createClient;
}
