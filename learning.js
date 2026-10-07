// Account and quest UI. Answers and access checks belong to the server.
export function createLearning({ language, notify, changed }) {
  let profile = null;
  let csrf = null;
  let available = true;
  let generation = 0;
  let returnTo = 'dashboard';
  let catalog = [];
  const e = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const text = (en, fa) => language() === 'fa' ? fa : en;
  const localized = value => typeof value === 'object' ? value[language()] || value.en : value;
  const types = { quiz: ['Choose an answer', 'انتخاب پاسخ'], blank: ['Complete the code', 'تکمیل کد'], output: ['Predict the output', 'پیش‌بینی خروجی'], debug: ['Find and fix the error', 'پیدا کردن و اصلاح خطا'], order: ['Arrange the lines', 'مرتب‌سازی خطوط'], project: ['Guided mini project', 'پروژه‌ی کوچک هدایت‌شده'] };
  const errors = {
    login_required: ['Sign in to play this quest.', 'برای بازی کردن این مرحله وارد شو.'],
    pro_required: ['This quest requires a Pro account.', 'این مرحله به حساب پرو نیاز دارد.'],
    invalid_credentials: ['Use a 3–32 character username (letters, numbers, underscore) and a 10–128 character password.', 'نام کاربری ۳ تا ۳۲ حرف انگلیسی، رقم یا زیرخط و رمز ۱۰ تا ۱۲۸ نویسه باشد.'],
    wrong_credentials: ['Username or password is incorrect.', 'نام کاربری یا رمز عبور نادرست است.'],
    username_taken: ['This username is already taken.', 'این نام کاربری قبلاً ثبت شده است.'],
    invalid_name: ['Enter a display name of 1–60 characters.', 'نام نمایشی بین ۱ تا ۶۰ نویسه وارد کن.'],
    too_many_attempts: ['Too many attempts. Try again in five minutes.', 'تلاش‌ها زیاد است؛ پنج دقیقه‌ی دیگر دوباره امتحان کن.'],
    lesson_missing: ['Quest not found.', 'مرحله پیدا نشد.'],
    invalid_csrf: ['Your session changed. Reload and sign in again.', 'نشست تغییر کرده؛ صفحه را تازه کن و دوباره وارد شو.'],
    offline: ['The account server is unavailable. Run server.py or open the hosted server site.', 'سرور حساب‌ها در دسترس نیست. server.py را اجرا کن یا سایتِ دارای سرور را باز کن.']
  };
  const errorText = error => text(...(errors[error.code] || ['Something went wrong. Please try again.', 'مشکلی پیش آمد؛ دوباره تلاش کن.']));
  async function request(path, data) {
    let response;
    try {
      response = await fetch(`/api/${path}`, {
        method: data === undefined ? 'GET' : 'POST', credentials: 'same-origin', cache: 'no-store',
        headers: data === undefined ? {} : { 'Content-Type': 'application/json', 'X-CSRF-Token': csrf || '' },
        ...(data === undefined ? {} : { body: JSON.stringify(data) })
      });
      if (!response.headers.get('Content-Type')?.includes('application/json')) throw new Error('offline');
    } catch { throw Object.assign(new Error('offline'), { code: 'offline' }); }
    const result = await response.json();
    if (!response.ok) {
      if (response.status === 401 && profile) {
        profile = null;
        csrf = null;
        changed(profile);
      }
      throw Object.assign(new Error(result.error), { code: result.error });
    }
    return result;
  }
  function setProfile(value) { profile = value; changed(profile); }
  async function init() {
    try {
      const result = await request('session');
      csrf = result.csrf;
      available = true;
      setProfile(result.profile);
    } catch { available = false; }
  }
  function nav() {
    return `<a href="#${profile ? 'profile' : 'login'}">${text(profile ? 'My profile' : 'Sign in', profile ? 'پروفایل من' : 'ورود')}</a>`;
  }
  function shell(body) {
    return `<div class="container dashboard-shell"><aside class="sidebar"><a href="#dashboard">${text('Quest map', 'نقشه‌ی مراحل')}</a><a href="#profile">${text('My profile', 'پروفایل من')}</a><a href="#practice">${text('Practice lab', 'آزمایشگاه تمرین')}</a><a href="#dashboard/pro">${text('Pro missions', 'مأموریت‌های پرو')}</a><a href="#home">${text('Home', 'خانه')}</a></aside><div class="dashboard-content">${body}</div></div>`;
  }
  function auth(main, register) {
    main.innerHTML = `<section class="container section"><div class="card auth-card"><div class="eyebrow">CODEPLAY</div><h1>${text(register ? 'Create your account' : 'Welcome back', register ? 'حساب خودت را بساز' : 'دوباره خوش آمدی')}</h1><p>${text('Sign in before starting a quest. Your progress belongs to your account.', 'پیش از شروع مرحله وارد شو. پیشرفت در حساب شخصی تو ذخیره می‌شود.')}</p>${!available ? `<p class="hint">${text(...errors.offline)}</p>` : ''}<form id="account-form" class="account-form">${register ? `<label>${text('Display name', 'نام نمایشی')}<input name="display_name" required maxlength="60" autocomplete="nickname"></label>` : ''}<label>${text('Username', 'نام کاربری')}<input name="username" required pattern="[A-Za-z0-9_]{3,32}" minlength="3" maxlength="32" autocomplete="username" dir="ltr" autocapitalize="none" spellcheck="false"></label><label>${text('Password (at least 10 characters)', 'رمز عبور (حداقل ۱۰ نویسه)')}<input name="password" type="password" required minlength="10" maxlength="128" autocomplete="${register ? 'new-password' : 'current-password'}" dir="ltr"></label><p id="account-error" role="alert" class="form-error" hidden></p><button class="button">${text(register ? 'Create account' : 'Sign in', register ? 'ثبت‌نام' : 'ورود')}</button></form><p class="meta">${text(register ? 'Already registered?' : 'New to CodePlay?', register ? 'قبلاً ثبت‌نام کرده‌ای؟' : 'حساب نداری؟')} <a class="text-link" href="#${register ? 'login' : 'register'}">${text(register ? 'Sign in' : 'Create account', register ? 'ورود' : 'ثبت‌نام')}</a></p></div></section>`;
    main.querySelector('#account-form').addEventListener('submit', async event => {
      event.preventDefault();
      const form = event.currentTarget;
      const button = form.querySelector('button');
      const error = form.querySelector('#account-error');
      button.disabled = true;
      error.hidden = true;
      try {
        const result = await request(register ? 'register' : 'login', Object.fromEntries(new FormData(form)));
        csrf = result.csrf;
        available = true;
        setProfile(result.profile);
        form.reset();
        const sameRoute = location.hash === '#' + returnTo;
        location.hash = returnTo;
        if (sameRoute) window.dispatchEvent(new HashChangeEvent('hashchange'));
      } catch (failure) { error.textContent = errorText(failure); error.hidden = false; }
      finally { button.disabled = false; }
    });
  }
  function totals() {
    return `<div class="grid three">${[[profile.xp, text('Total XP', 'کل امتیاز')], [profile.completed.length, text('Completed quests', 'مراحل تکمیل‌شده')], [profile.streak, text('Day streak', 'روز متوالی')]].map(([value, label]) => `<article class="card stat"><div class="stat-number">${new Intl.NumberFormat(language()).format(value)}</div><h3>${label}</h3></article>`).join('')}</div>`;
  }
  async function dashboard(main, route, ticket) {
    const result = await request('lessons');
    if (ticket !== generation) return;
    catalog = result.lessons;
    const track = route.endsWith('/pro') ? 'pro' : 'free';
    const completed = new Set(profile.completed.map(x => x.lesson_id));
    main.innerHTML = shell(`<div class="eyebrow">${e(profile.plan.toUpperCase())} · ${text('ACCOUNT PROGRESS', 'پیشرفت حساب')}</div><h1>${text('Your adventure,', 'ماجراجویی تو،')} ${e(profile.display_name)}</h1>${totals()}<div class="actions track-tabs"><a class="button ${track === 'free' ? '' : 'secondary'}" href="#dashboard">${text('Free path · 24 quests', 'مسیر رایگان · ۲۴ مرحله')}</a><a class="button ${track === 'pro' ? '' : 'secondary'}" href="#dashboard/pro">${text('Pro path · 20 quests', 'مسیر پرو · ۲۰ مرحله')}</a><a class="button secondary" href="#quest/${profile.next_lesson || 'free-01'}">${text('Continue learning', 'ادامه‌ی یادگیری')}</a></div><p>${text(track === 'free' ? 'Python foundations and a broad introduction to Django. All free quests are open after sign-in.' : 'Advanced Python and detailed Django missions. Pro access is assigned by the site administrator.', track === 'free' ? 'مبانی پایتون و معرفی کلی جنگو. همه‌ی مراحل رایگان پس از ورود باز هستند.' : 'پایتون پیشرفته و مأموریت‌های دقیق جنگو. دسترسی پرو توسط مدیر سایت فعال می‌شود.')}</p><label class="sr-only" for="lesson-search">${text('Search quests', 'جست‌وجوی مراحل')}</label><input id="lesson-search" type="search" placeholder="${text('Search quests…', 'جست‌وجوی مراحل…')}"><div class="grid three lesson-grid">${catalog.filter(x => x.track === track).map((item, index) => `<article class="card lesson-card" data-lesson-search="${e((localized(item.title) + ' ' + item.topic + ' ' + text(...types[item.kind])).toLowerCase())}"><div class="eyebrow">${item.topic.toUpperCase()} · ${index + 1}</div><h3>${e(localized(item.title))}</h3><p>${text(...types[item.kind])}</p><span class="pill">${completed.has(item.id) ? text('Completed', 'تکمیل‌شده') : item.locked ? text('Pro required', 'نیازمند پرو') : '+50 XP'}</span><a class="button secondary" href="#quest/${item.id}">${text(completed.has(item.id) ? 'Review quest' : item.locked ? 'View access details' : 'Start quest', completed.has(item.id) ? 'مرور مرحله' : item.locked ? 'شرایط دسترسی' : 'شروع مرحله')}</a></article>`).join('')}</div><p id="lesson-empty" class="empty" hidden>${text('No matching quests.', 'مرحله‌ای پیدا نشد.')}</p>`);
    main.querySelector('#lesson-search').addEventListener('input', event => {
      let found = 0;
      main.querySelectorAll('[data-lesson-search]').forEach(card => { card.hidden = !card.dataset.lessonSearch.includes(event.target.value.trim().toLowerCase()); if (!card.hidden) found++; });
      main.querySelector('#lesson-empty').hidden = found > 0;
    });
  }
  async function showProfile(main, ticket) {
    const result = await request('profile');
    if (ticket !== generation) return;
    setProfile(result.profile);
    const lessons = await request('lessons');
    if (ticket !== generation) return;
    const titleFor = id => localized(lessons.lessons.find(x => x.id === id)?.title || text('Not started', 'هنوز شروع نشده'));
    main.innerHTML = shell(`<div class="eyebrow">${text('PERSONAL PROFILE', 'پروفایل شخصی')}</div><h1>${e(profile.display_name)}</h1><p dir="ltr">@${e(profile.username)} · ${e(profile.plan.toUpperCase())}</p>${totals()}<div class="grid three lesson-grid">${Object.entries(profile.tracks).map(([track, progress]) => `<article class="card"><h3>${text(track === 'free' ? 'Free path' : 'Pro path', track === 'free' ? 'مسیر رایگان' : 'مسیر پرو')}</h3><progress value="${progress.completed}" max="${progress.total}" aria-label="${track}"></progress><p>${progress.completed} / ${progress.total}</p></article>`).join('')}<article class="card"><h3>${text('Current quest', 'مرحله‌ی فعلی')}</h3><p>${e(titleFor(profile.current_lesson))}</p><a class="text-link" href="#quest/${profile.current_lesson || profile.next_lesson || 'free-01'}">${text('Continue', 'ادامه')}</a></article></div><article class="card"><h3>${text('Next recommended quest', 'مرحله‌ی پیشنهادی بعدی')}</h3><p>${profile.next_lesson ? e(titleFor(profile.next_lesson)) : text('You completed your available path!', 'مسیر در دسترس را کامل کرده‌ای!')}</p></article><form id="profile-form" class="card account-form"><label>${text('Display name', 'نام نمایشی')}<input name="display_name" value="${e(profile.display_name)}" maxlength="60" required></label><button class="button">${text('Save profile', 'ذخیره‌ی پروفایل')}</button><p id="profile-status" role="status"></p></form><details class="card"><summary>${text('Completed quests', 'مراحل تکمیل‌شده')}</summary><ul>${profile.completed.map(x => `<li><a class="text-link" href="#quest/${x.lesson_id}">${e(titleFor(x.lesson_id))}</a> · ${e(x.day)}</li>`).join('') || `<li>${text('Complete a quest to start your story.', 'با تکمیل یک مرحله داستانت را شروع کن.')}</li>`}</ul></details><div class="actions"><a class="button" href="#dashboard">${text('Quest map', 'نقشه‌ی مراحل')}</a><button id="logout" class="button secondary">${text('Sign out', 'خروج از حساب')}</button></div>`);
    main.querySelector('#profile-form').addEventListener('submit', async event => {
      event.preventDefault();
      const button = event.currentTarget.querySelector('button');
      button.disabled = true;
      try {
        const result = await request('profile', Object.fromEntries(new FormData(event.currentTarget)));
        setProfile(result.profile);
        main.querySelector('#profile-status').textContent = text('Saved. Your name updates when you open the profile again.', 'ذخیره شد. نام با باز کردن دوباره‌ی پروفایل به‌روز می‌شود.');
      } catch (error) { main.querySelector('#profile-status').textContent = errorText(error); }
      finally { button.disabled = false; }
    });
    main.querySelector('#logout').addEventListener('click', async event => {
      event.currentTarget.disabled = true;
      try { await request('logout', {}); csrf = null; setProfile(null); location.hash = 'login'; }
      catch (error) { notify(errorText(error)); event.currentTarget.disabled = false; }
    });
  }
  async function quest(main, id, ticket) {
    const result = await request(`lessons/${encodeURIComponent(id)}`);
    if (ticket !== generation) return;
    const item = result.lesson;
    const done = profile.completed.some(x => x.lesson_id === id);
    let order = [];
    let fields;
    if (item.kind === 'quiz' || item.kind === 'debug') {
      fields = `<fieldset class="answer-options"><legend class="sr-only">${text('Choose an answer', 'انتخاب پاسخ')}</legend>${item.options.map((option, index) => `<label class="answer-option"><input type="radio" name="answer" value="${e(typeof option === 'object' ? option.value : option)}" required><span>${typeof option === 'object' ? e(localized(option.label)) : `<code dir="ltr">${e(option)}</code>`}</span></label>`).join('')}</fieldset>`;
    } else if (item.kind === 'order') {
      const shuffled = item.options.map((line, index) => ({ line, index }));
      // A new shuffle on each attempt; never present the solved sequence initially.
      for (let i = shuffled.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]; }
      if (shuffled.every((x, i) => x.index === i)) [shuffled[0], shuffled[1]] = [shuffled[1], shuffled[0]];
      fields = `<p class="meta">${text('Click lines in order. Remove the last line to change your sequence.', 'خطوط را به ترتیب انتخاب کن. برای اصلاح ترتیب، خط آخر را بردار.')}</p><div class="order-pool">${shuffled.map(x => `<button class="button secondary order-line" type="button" data-line="${x.index}"><code dir="ltr">${e(x.line)}</code></button>`).join('')}</div><pre id="ordered-code" class="lesson-code" dir="ltr" aria-live="polite"></pre><button id="undo-line" class="button secondary small" type="button">${text('Remove last line', 'برداشتن خط آخر')}</button>`;
    } else if (item.kind === 'project') {
      fields = `<div class="account-form">${(item.code.match(/___/g) || []).map((_, i) => `<label>${text('Gap', 'جای خالی')} ${i + 1}<input name="gap${i}" required maxlength="100" autocomplete="off" dir="ltr" spellcheck="false"></label>`).join('')}</div>`;
    } else {
      fields = `<label class="account-form">${text(item.kind === 'output' ? 'Your predicted output' : 'Code for the gap', item.kind === 'output' ? 'خروجی پیش‌بینی‌شده' : 'کد جای خالی')}<textarea name="answer" class="answer-input" required maxlength="1000" dir="ltr" spellcheck="false" rows="${item.kind === 'output' ? 3 : 1}"></textarea></label>`;
    }
    main.innerHTML = shell(`<a class="text-link" href="#dashboard${item.track === 'pro' ? '/pro' : ''}">${text('Back to map', 'بازگشت به نقشه')}</a><div class="eyebrow" style="margin-top:24px">${item.topic.toUpperCase()} · ${item.track.toUpperCase()} · +${item.xp} XP</div><h1>${e(localized(item.title))}</h1><p>${text(...types[item.kind])}</p><article class="card quest-exercise"><h3>${e(localized(item.prompt))}</h3>${item.code ? `<pre class="lesson-code" dir="ltr"><code>${e(item.code)}</code></pre>` : ''}<form id="answer-form">${fields}<div class="actions"><button id="check-answer" class="button">${text('Check answer', 'بررسی پاسخ')}</button><button id="lesson-hint-toggle" type="button" class="button secondary" aria-expanded="false">${text('Show hint', 'نمایش راهنما')}</button></div><p id="lesson-hint" class="hint" hidden>${e(localized(item.hint))}</p><div id="answer-feedback" class="answer-feedback" role="status" tabindex="-1" hidden></div></form><p class="meta">${text('Correct answers save progress automatically. Reviewing earns no extra XP.', 'پاسخ درست، پیشرفت را خودکار ذخیره می‌کند. مرور دوباره امتیاز اضافه ندارد.')}${done ? ' · ' + text('Already completed', 'قبلاً تکمیل شده') : ''}</p></article>`);
    const form = main.querySelector('#answer-form');
    form.querySelector('#lesson-hint-toggle').addEventListener('click', event => {
      const hint = form.querySelector('#lesson-hint');
      hint.hidden = !hint.hidden;
      event.currentTarget.setAttribute('aria-expanded', String(!hint.hidden));
    });
    if (item.kind === 'order') {
      const syncOrder = () => {
        form.querySelector('#ordered-code').textContent = order.map(index => item.options[index]).join('\n') || text('Your sequence will appear here.', 'ترتیب انتخابی اینجا نمایش داده می‌شود.');
        form.querySelectorAll('[data-line]').forEach(button => { button.disabled = order.includes(Number(button.dataset.line)); });
      };
      form.querySelectorAll('[data-line]').forEach(button => button.addEventListener('click', () => { order.push(Number(button.dataset.line)); syncOrder(); }));
      form.querySelector('#undo-line').addEventListener('click', () => { order.pop(); syncOrder(); });
      syncOrder();
    }
    form.addEventListener('submit', async event => {
      event.preventDefault();
      const button = form.querySelector('#check-answer');
      const feedback = form.querySelector('#answer-feedback');
      const data = new FormData(form);
      const answer = item.kind === 'order' ? order : item.kind === 'project' ? (item.code.match(/___/g) || []).map((_, i) => data.get(`gap${i}`)) : data.get('answer');
      button.disabled = true;
      try {
        const result = await request('answer', { lesson_id: id, answer });
        if (ticket !== generation) return;
        setProfile(result.profile);
        feedback.classList.toggle('passed', result.correct);
        feedback.innerHTML = `<strong>${text(result.correct ? 'Correct!' : 'Try again.', result.correct ? 'درست است!' : 'دوباره تلاش کن.')}</strong><p>${e(localized(result.explanation))}</p>${result.correct ? `<p>+${result.earned} XP${result.earned === 0 ? ' · ' + text('Review saved', 'مرور ثبت شد') : ''}</p><a class="button small" href="#quest/${profile.next_lesson || id}">${text('Next quest', 'مرحله‌ی بعد')}</a> <a class="text-link" href="#dashboard">${text('Quest map', 'نقشه‌ی مراحل')}</a>` : ''}`;
        feedback.hidden = false;
        feedback.focus();
      } catch (error) {
        feedback.textContent = errorText(error); feedback.hidden = false;
      } finally { button.disabled = false; }
    });
  }
  function handles(route) { return /^(dashboard|badges|profile|login|register|quest)(\/|$)/.test(route) || (route === 'practice' && !profile); }
  function render(main, route) {
    const ticket = ++generation;
    if (route === 'login' || route === 'register') { auth(main, route === 'register'); return; }
    if (!profile) { returnTo = route; auth(main, false); return; }
    main.innerHTML = shell(`<p role="status">${text('Loading your adventure…', 'در حال بارگیری ماجراجویی…')}</p>`);
    const work = route === 'profile' || route === 'badges' ? showProfile(main, ticket) : route.startsWith('quest') ? quest(main, route.split('/')[1] || profile.next_lesson || 'free-01', ticket) : dashboard(main, route, ticket);
    work.catch(error => {
      if (ticket !== generation) return;
      main.innerHTML = shell(`<article class="card"><h1>${text('Quest access', 'دسترسی به مرحله')}</h1><p role="alert">${e(errorText(error))}</p><a class="button" href="#${error.code === 'login_required' ? 'login' : 'dashboard'}">${text(error.code === 'login_required' ? 'Sign in' : 'Back to free quests', error.code === 'login_required' ? 'ورود' : 'بازگشت به مراحل رایگان')}</a></article>`);
    });
  }
  return { init, nav, handles, render, get profile() { return profile; }, invalidate() { generation++; } };
}
