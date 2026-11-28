-- Wordfall: global chat and announcements on the home page.
-- Run this once in Supabase: Dashboard → SQL Editor → New query → paste → Run.
-- Safe to run again; it only creates what's missing.
--
-- To post an announcement: Table Editor → announcements → Insert row (title, body),
-- or run:  insert into public.announcements (title, body) values ('Season 1 is here', 'New tiles in the shop.');
-- To remove a chat message: Table Editor → chat_messages → delete the row.
-- Or, after supabase/admins.sql, sign in to the game as an operator and post or remove them from the chat panel.

-- Chat messages: anyone can read, signed-in players with a username can post their own.
create table if not exists public.chat_messages (
  id bigint generated always as identity primary key,
  user_id uuid not null references public.profiles (id) on delete cascade,
  body text not null check (char_length(body) between 1 and 200),
  created_at timestamptz not null default now()
);
create index if not exists chat_messages_user_time on public.chat_messages (user_id, created_at desc);

-- Announcements: read by everyone; written from the dashboard, or in the game by operators (supabase/admins.sql).
create table if not exists public.announcements (
  id bigint generated always as identity primary key,
  title text not null check (char_length(title) between 1 and 80),
  body text not null default '' check (char_length(body) <= 1000),
  created_at timestamptz not null default now()
);

grant usage on schema public to anon, authenticated;
grant select on public.chat_messages, public.announcements to anon, authenticated;
grant insert (user_id, body) on public.chat_messages to authenticated;

alter table public.chat_messages enable row level security;
alter table public.announcements enable row level security;

drop policy if exists "chat is public" on public.chat_messages;
create policy "chat is public" on public.chat_messages for select using (true);
drop policy if exists "post own chat" on public.chat_messages;
create policy "post own chat" on public.chat_messages for insert to authenticated
  with check (auth.uid() = user_id
    and exists (select 1 from public.profiles p where p.id = user_id and p.username is not null));
drop policy if exists "announcements are public" on public.announcements;
create policy "announcements are public" on public.announcements for select using (true);

-- One message every 3 seconds per player; spaces trimmed; the time is always the server's.
create or replace function public.chat_guard() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  new.body := btrim(regexp_replace(new.body, '\s+', ' ', 'g'));
  new.created_at := now();
  if exists (select 1 from public.chat_messages
             where user_id = new.user_id and created_at > now() - interval '3 seconds') then
    raise exception 'Slow down a little' using errcode = 'P0001';
  end if;
  return new;
end $$;
drop trigger if exists chat_guard on public.chat_messages;
create trigger chat_guard before insert on public.chat_messages
  for each row execute function public.chat_guard();

-- Keep only the newest 500 messages.
create or replace function public.chat_trim() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  delete from public.chat_messages
  where id <= (select id from public.chat_messages order by id desc offset 500 limit 1);
  return null;
end $$;
drop trigger if exists chat_trim on public.chat_messages;
create trigger chat_trim after insert on public.chat_messages
  for each statement execute function public.chat_trim();

-- What the game reads: messages with the sender's username and icon.
create or replace view public.chat_feed with (security_invoker = on) as
  select m.id, m.user_id, m.body, m.created_at, p.username as name, p.icon
  from public.chat_messages m
  join public.profiles p on p.id = m.user_id;
grant select on public.chat_feed to anon, authenticated;

-- Live updates: tell the game when someone posts.
do $$ begin
  alter publication supabase_realtime add table public.chat_messages;
exception when duplicate_object then null;
end $$;
do $$ begin
  alter publication supabase_realtime add table public.announcements;
exception when duplicate_object then null;
end $$;
