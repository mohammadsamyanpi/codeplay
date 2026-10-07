-- CodePlay-owned schema only. Does not modify existing application tables.
begin;
create schema if not exists codeplay_private;
revoke all on schema codeplay_private from public, anon, authenticated;
grant usage on schema codeplay_private to authenticated;

create table if not exists codeplay_private.lessons (
  id text primary key,
  position integer not null unique,
  content jsonb not null
);
create table if not exists codeplay_private.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text not null check (char_length(display_name) between 1 and 60),
  plan text not null default 'free' check (plan in ('free', 'pro')),
  current_lesson text references codeplay_private.lessons(id)
);
create table if not exists codeplay_private.completions (
  user_id uuid not null references codeplay_private.profiles(id) on delete cascade,
  lesson_id text not null references codeplay_private.lessons(id),
  day date not null default (now() at time zone 'UTC')::date,
  primary key (user_id, lesson_id)
);
alter table codeplay_private.lessons enable row level security;
alter table codeplay_private.profiles enable row level security;
alter table codeplay_private.completions enable row level security;
revoke all on all tables in schema codeplay_private from public, anon, authenticated;
-- There are deliberately no direct client table grants or write policies.

create or replace function codeplay_private.profile()
returns jsonb language plpgsql security definer set search_path = '' set timezone = 'UTC'
as $$
declare
  who uuid := auth.uid();
  person codeplay_private.profiles%rowtype;
  completed jsonb; total_xp integer; next_id text; tracks jsonb;
  cursor_day date := current_date; days integer := 0; username text;
begin
  if who is null then raise exception 'login_required' using errcode = '42501'; end if;
  insert into codeplay_private.profiles(id, display_name)
    select who, left(coalesce(nullif(btrim(u.raw_user_meta_data->>'display_name'), ''), split_part(u.email, '@', 1), 'Learner'), 60)
    from auth.users u where u.id = who on conflict(id) do nothing;
  select * into strict person from codeplay_private.profiles p where p.id = who;
  select split_part(u.email, '@', 1) into username from auth.users u where u.id = who;
  select coalesce(jsonb_agg(jsonb_build_object('lesson_id', c.lesson_id, 'day', c.day) order by c.day, c.lesson_id), '[]'::jsonb),
    coalesce(sum((l.content->>'xp')::integer), 0)::integer
    into completed, total_xp from codeplay_private.completions c
    join codeplay_private.lessons l on l.id = c.lesson_id where c.user_id = who;
  select l.id into next_id from codeplay_private.lessons l
    where (l.content->>'track' = 'free' or person.plan = 'pro')
    and not exists(select 1 from codeplay_private.completions c where c.user_id = who and c.lesson_id = l.id)
    order by l.position limit 1;
  select jsonb_object_agg(t.track, jsonb_build_object('completed', t.done, 'total', t.total)) into tracks
    from (select l.content->>'track' as track, count(c.lesson_id) as done, count(*) as total
      from codeplay_private.lessons l left join codeplay_private.completions c on c.lesson_id = l.id and c.user_id = who
      group by l.content->>'track') t;
  if not exists(select 1 from codeplay_private.completions c where c.user_id = who and c.day = cursor_day) then cursor_day := cursor_day - 1; end if;
  while exists(select 1 from codeplay_private.completions c where c.user_id = who and c.day = cursor_day) loop
    days := days + 1; cursor_day := cursor_day - 1;
  end loop;
  return jsonb_build_object('profile', jsonb_build_object('username', username, 'display_name', person.display_name,
    'plan', person.plan, 'current_lesson', person.current_lesson, 'next_lesson', next_id,
    'completed', completed, 'xp', total_xp, 'streak', days, 'tracks', tracks));
end;
$$;

create or replace function codeplay_private.catalog()
returns jsonb language plpgsql security definer set search_path = ''
as $$
declare result jsonb; account jsonb;
begin
  account := codeplay_private.profile()->'profile';
  select jsonb_agg((l.content - array['answer','explanation','prompt','code','hint','options']) ||
    jsonb_build_object('locked', l.content->>'track' = 'pro' and account->>'plan' <> 'pro') order by l.position)
    into result from codeplay_private.lessons l;
  return jsonb_build_object('lessons', result);
end;
$$;

create or replace function codeplay_private.lesson(lesson_id text)
returns jsonb language plpgsql security definer set search_path = ''
as $$
declare item jsonb; account jsonb;
begin
  account := codeplay_private.profile()->'profile';
  select l.content into item from codeplay_private.lessons l where l.id = lesson_id;
  if item is null then raise exception 'lesson_missing' using errcode = 'P0001'; end if;
  if item->>'track' = 'pro' and account->>'plan' <> 'pro' then raise exception 'pro_required' using errcode = '42501'; end if;
  update codeplay_private.profiles set current_lesson = lesson_id where id = auth.uid();
  return jsonb_build_object('lesson', item - array['answer','explanation']);
end;
$$;

create or replace function codeplay_private.correct(item jsonb, submitted jsonb)
returns boolean language plpgsql immutable set search_path = ''
as $$
declare expected jsonb := item->'answer'; value jsonb; choices jsonb; i integer; normalized text;
begin
  if submitted is null or submitted = 'null'::jsonb then return false; end if;
  if item->>'kind' = 'order' then
    return jsonb_typeof(submitted) = 'array' and submitted = expected;
  elsif item->>'kind' = 'project' then
    if jsonb_typeof(submitted) <> 'array' then return false; end if;
    if jsonb_array_length(submitted) <> jsonb_array_length(expected) then return false; end if;
    for i in 0..jsonb_array_length(expected)-1 loop
      value := submitted->i;
      if jsonb_typeof(value) <> 'string' then return false; end if;
      normalized := btrim(replace(value #>> '{}', E'\r\n', E'\n'), E' \t\r\n');
      if not (expected->i @> jsonb_build_array(normalized)) then return false; end if;
    end loop;
    return true;
  end if;
  if jsonb_typeof(submitted) <> 'string' then return false; end if;
  choices := case when jsonb_typeof(expected) = 'array' then expected else jsonb_build_array(expected) end;
  normalized := btrim(replace(submitted #>> '{}', E'\r\n', E'\n'), E' \t\r\n');
  return choices @> jsonb_build_array(normalized);
end;
$$;

create or replace function codeplay_private.answer(lesson_id text, submitted jsonb)
returns jsonb language plpgsql security definer set search_path = '' set timezone = 'UTC'
as $$
declare item jsonb; passed boolean; inserted integer := 0;
begin
  perform codeplay_private.lesson(lesson_id); -- Authorizes the caller and plan first.
  if pg_column_size(submitted) > 16384 then raise exception 'invalid_answer'; end if;
  select l.content into item from codeplay_private.lessons l where l.id = lesson_id;
  passed := codeplay_private.correct(item, submitted);
  if passed then
    insert into codeplay_private.completions(user_id, lesson_id) values(auth.uid(), lesson_id) on conflict do nothing;
    get diagnostics inserted = row_count;
  end if;
  return jsonb_build_object('correct', passed, 'earned', inserted * (item->>'xp')::integer,
    'explanation', item->'explanation') || codeplay_private.profile();
end;
$$;

create or replace function codeplay_private.update_profile(display_name text)
returns jsonb language plpgsql security definer set search_path = ''
as $$
begin
  perform codeplay_private.profile();
  if display_name is null or char_length(btrim(display_name)) not between 1 and 60 then raise exception 'invalid_name'; end if;
  update codeplay_private.profiles p set display_name = btrim(update_profile.display_name) where p.id = auth.uid();
  return codeplay_private.profile();
end;
$$;

-- Exposed RPC wrappers run with the caller's privileges. Only the private,
-- explicitly granted routines elevate privileges, and each checks auth.uid().
create or replace function public.codeplay_status() returns jsonb
language sql stable security invoker set search_path = '' as $$ select '{"schema_version":1}'::jsonb $$;
create or replace function public.codeplay_profile() returns jsonb
language sql security invoker set search_path = '' as $$ select codeplay_private.profile() $$;
create or replace function public.codeplay_catalog() returns jsonb
language sql security invoker set search_path = '' as $$ select codeplay_private.catalog() $$;
create or replace function public.codeplay_lesson(lesson_id text) returns jsonb
language sql security invoker set search_path = '' as $$ select codeplay_private.lesson(lesson_id) $$;
create or replace function public.codeplay_answer(lesson_id text, submitted jsonb) returns jsonb
language sql security invoker set search_path = '' as $$ select codeplay_private.answer(lesson_id, submitted) $$;
create or replace function public.codeplay_update_profile(display_name text) returns jsonb
language sql security invoker set search_path = '' as $$ select codeplay_private.update_profile(display_name) $$;

revoke all on all functions in schema codeplay_private from public, anon, authenticated;
grant execute on function codeplay_private.profile(), codeplay_private.catalog(), codeplay_private.lesson(text),
  codeplay_private.answer(text,jsonb), codeplay_private.update_profile(text) to authenticated;
revoke all on function public.codeplay_status(), public.codeplay_profile(), public.codeplay_catalog(),
  public.codeplay_lesson(text), public.codeplay_answer(text,jsonb), public.codeplay_update_profile(text) from public, anon, authenticated;
grant execute on function public.codeplay_status() to anon, authenticated;
grant execute on function public.codeplay_profile(), public.codeplay_catalog(), public.codeplay_lesson(text),
  public.codeplay_answer(text,jsonb), public.codeplay_update_profile(text) to authenticated;
-- Lesson seed and COMMIT are appended by build_migration.py.
