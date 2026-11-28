-- Wordfall: operators. An operator can post and remove announcements, and remove chat
-- messages, from inside the game (the Announcements and Global chat tabs of the chat panel).
-- Run this once in Supabase, after chat.sql: Dashboard → SQL Editor → New query → paste → Run.
-- Safe to run again.
--
-- It makes the player named ZacTheSword an operator. That account has to exist (sign in to the
-- game as ZacTheSword once) before you run this. The account is matched by its username only
-- when this runs; after that it stays an operator by its account id, even if the name changes,
-- and nobody else becomes one by taking the name. The last query lists every operator, so you
-- can check it picked the right account.
--
-- Make someone else an operator later:
--   insert into public.admins (user_id) select id from public.profiles where lower(username) = lower('TheirName');
-- Take it away:
--   delete from public.admins where user_id = (select id from public.profiles where lower(username) = lower('TheirName'));

create table if not exists public.admins (
  user_id uuid primary key references public.profiles (id) on delete cascade,
  role text not null default 'operator',
  created_at timestamptz not null default now()
);
alter table public.admins enable row level security;
-- No policies: the game never reads this table. is_admin() answers for whoever is signed in.
revoke all on public.admins from anon, authenticated;

insert into public.admins (user_id)
  select id from public.profiles where lower(username) = 'zacthesword'
  on conflict (user_id) do nothing;

-- Is the signed-in player an operator?
create or replace function public.is_admin() returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.admins a where a.user_id = auth.uid());
$$;
revoke execute on function public.is_admin() from public, anon;
grant execute on function public.is_admin() to authenticated;

-- Announcements: operators post and remove them. The time is always the server's.
grant insert (title, body) on public.announcements to authenticated;
grant delete on public.announcements to authenticated;
drop policy if exists "operators post announcements" on public.announcements;
create policy "operators post announcements" on public.announcements for insert to authenticated
  with check ((select public.is_admin()));
drop policy if exists "operators remove announcements" on public.announcements;
create policy "operators remove announcements" on public.announcements for delete to authenticated
  using ((select public.is_admin()));

-- Global chat: operators remove messages.
grant delete on public.chat_messages to authenticated;
drop policy if exists "operators remove chat" on public.chat_messages;
create policy "operators remove chat" on public.chat_messages for delete to authenticated
  using ((select public.is_admin()));

-- Who the operators are now.
select p.username, a.role, a.created_at
from public.admins a join public.profiles p on p.id = a.user_id
order by a.created_at;
