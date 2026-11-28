-- Wordfall: friends, friend requests, private messages and match invites.
-- Run this once in Supabase: Dashboard → SQL Editor → New query → paste → Run.
-- Safe to run again; it only creates what's missing. Needs schema.sql (profiles) first.
--
-- Only the two players involved can read a friend link or a message between them.

-- Friend links: a asked b. Pending until b accepts. Either of them can remove it (decline, cancel, unfriend).
create table if not exists public.friend_links (
  a uuid not null references public.profiles (id) on delete cascade,
  b uuid not null references public.profiles (id) on delete cascade,
  status text not null default 'pending' check (status in ('pending', 'accepted')),
  created_at timestamptz not null default now(),
  primary key (a, b),
  check (a <> b)
);
create index if not exists friend_links_b on public.friend_links (b);

-- Private messages between friends. kind 'invite' carries a room code to join a match.
create table if not exists public.direct_messages (
  id bigint generated always as identity primary key,
  sender uuid not null references public.profiles (id) on delete cascade,
  recipient uuid not null references public.profiles (id) on delete cascade,
  body text not null check (char_length(body) between 1 and 200),
  kind text not null default 'msg' check (kind in ('msg', 'invite')),
  code text check (code is null or code ~ '^[a-z0-9]{3,6}$'),
  mode text check (mode is null or char_length(mode) <= 16),
  created_at timestamptz not null default now(),
  check (sender <> recipient)
);
create index if not exists direct_messages_recipient on public.direct_messages (recipient, id desc);
create index if not exists direct_messages_sender on public.direct_messages (sender, id desc);

grant usage on schema public to authenticated;
grant select, delete on public.friend_links to authenticated;
grant insert (a, b) on public.friend_links to authenticated;
grant update (status) on public.friend_links to authenticated;
grant select on public.direct_messages to authenticated;
grant insert (sender, recipient, body, kind, code, mode) on public.direct_messages to authenticated;

alter table public.friend_links enable row level security;
alter table public.direct_messages enable row level security;

-- Friend links: either side reads; only the asker creates a request (with a username, to someone else);
-- only the one asked accepts; either side removes.
drop policy if exists "friend links: either side reads" on public.friend_links;
create policy "friend links: either side reads" on public.friend_links for select to authenticated
  using (auth.uid() = a or auth.uid() = b);
drop policy if exists "friend links: ask" on public.friend_links;
create policy "friend links: ask" on public.friend_links for insert to authenticated
  with check (auth.uid() = a and status = 'pending'
    and exists (select 1 from public.profiles p where p.id = a and p.username is not null));
drop policy if exists "friend links: accept" on public.friend_links;
create policy "friend links: accept" on public.friend_links for update to authenticated
  using (auth.uid() = b) with check (auth.uid() = b and status = 'accepted');
drop policy if exists "friend links: remove" on public.friend_links;
create policy "friend links: remove" on public.friend_links for delete to authenticated
  using (auth.uid() = a or auth.uid() = b);

-- Messages: only the sender and the recipient read them; you can only message a friend.
drop policy if exists "messages: the two of them read" on public.direct_messages;
create policy "messages: the two of them read" on public.direct_messages for select to authenticated
  using (auth.uid() = sender or auth.uid() = recipient);
drop policy if exists "messages: send to a friend" on public.direct_messages;
create policy "messages: send to a friend" on public.direct_messages for insert to authenticated
  with check (auth.uid() = sender and exists (
    select 1 from public.friend_links f where f.status = 'accepted'
      and ((f.a = sender and f.b = recipient) or (f.a = recipient and f.b = sender))));

-- One message a second per player; spaces trimmed; the time is always the server's.
create or replace function public.dm_guard() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  new.body := btrim(regexp_replace(new.body, '\s+', ' ', 'g'));
  new.created_at := now();
  if exists (select 1 from public.direct_messages
             where sender = new.sender and created_at > now() - interval '1 second') then
    raise exception 'Slow down a little' using errcode = 'P0001';
  end if;
  return new;
end $$;
drop trigger if exists dm_guard on public.direct_messages;
create trigger dm_guard before insert on public.direct_messages
  for each row execute function public.dm_guard();

-- Keep the newest 100 messages per conversation.
create or replace function public.dm_trim() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  delete from public.direct_messages d
  where d.id in (
    select id from public.direct_messages
    where (sender = new.sender and recipient = new.recipient) or (sender = new.recipient and recipient = new.sender)
    order by id desc offset 100);
  return null;
end $$;
drop trigger if exists dm_trim on public.direct_messages;
create trigger dm_trim after insert on public.direct_messages
  for each row execute function public.dm_trim();

-- Unfriending also clears the messages between the two players.
create or replace function public.friend_gone() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  delete from public.direct_messages
  where (sender = old.a and recipient = old.b) or (sender = old.b and recipient = old.a);
  return null;
end $$;
drop trigger if exists friend_gone on public.friend_links;
create trigger friend_gone after delete on public.friend_links
  for each row execute function public.friend_gone();

-- Live updates: tell the game when a request, an answer or a message arrives.
do $$ begin
  alter publication supabase_realtime add table public.friend_links;
exception when duplicate_object then null;
end $$;
do $$ begin
  alter publication supabase_realtime add table public.direct_messages;
exception when duplicate_object then null;
end $$;
