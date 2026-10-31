-- CP-105: run once in the Supabase SQL Editor after checking any existing table.
begin;
create table if not exists public.contact_messages (
  id bigint generated always as identity primary key,
  name text not null check (char_length(btrim(name)) between 1 and 60),
  email text not null check (char_length(btrim(email)) between 3 and 254 and email ~ '^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$'),
  message text not null check (char_length(btrim(message)) between 10 and 5000),
  created_at timestamptz not null default now()
);
alter table public.contact_messages enable row level security;
revoke all on public.contact_messages from public, anon, authenticated;
grant insert (name, email, message) on public.contact_messages to anon, authenticated;
drop policy if exists "contact_messages_insert" on public.contact_messages;
create policy "contact_messages_insert" on public.contact_messages for insert to anon, authenticated
  with check (true);
notify pgrst, 'reload schema';
commit;
