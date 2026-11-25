-- Wordfall: accounts + leaderboard.
-- Run this once in Supabase: Dashboard → SQL Editor → New query → paste → Run.
-- Safe to run again; it only creates what's missing.

-- One profile per account. id is the account's UUID from Supabase Auth,
-- so every username is paired with exactly one UUID.
create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  username text,
  icon text not null default 'tile',
  created_at timestamptz not null default now(),
  constraint username_format check (username is null or username ~ '^[A-Za-z0-9_.-]{3,16}$'),
  constraint icon_format check (icon ~ '^[a-z]{1,16}$')
);
-- Usernames are unique, ignoring case (Sam and sam can't both exist).
create unique index if not exists profiles_username_unique on public.profiles (lower(username));

-- One score row per account: best game ever, and best Today's drop on `day`.
create table if not exists public.scores (
  user_id uuid primary key references public.profiles (id) on delete cascade,
  best integer not null default 0 check (best between 0 and 99999999),
  daily integer not null default 0 check (daily between 0 and 99999999),
  day date,
  updated_at timestamptz not null default now()
);

-- Let the website's key use these tables at all. Newer Supabase projects don't
-- grant this automatically. Row level security below still decides which rows.
grant usage on schema public to anon, authenticated;
grant select on public.profiles, public.scores to anon, authenticated;
grant insert, update on public.profiles, public.scores to authenticated;

-- Row level security: everyone can read, people can only write their own rows.
alter table public.profiles enable row level security;
alter table public.scores enable row level security;

drop policy if exists "profiles are public" on public.profiles;
create policy "profiles are public" on public.profiles for select using (true);
drop policy if exists "create own profile" on public.profiles;
create policy "create own profile" on public.profiles for insert to authenticated with check (auth.uid() = id);
drop policy if exists "edit own profile" on public.profiles;
create policy "edit own profile" on public.profiles for update to authenticated using (auth.uid() = id) with check (auth.uid() = id);

drop policy if exists "scores are public" on public.scores;
create policy "scores are public" on public.scores for select using (true);
drop policy if exists "post own score" on public.scores;
create policy "post own score" on public.scores for insert to authenticated with check (auth.uid() = user_id);
drop policy if exists "update own score" on public.scores;
create policy "update own score" on public.scores for update to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- Every new account gets a profile. Username/password sign-ups pass their username;
-- Google sign-ups start without one and pick it in the game.
create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = '' as $$
declare
  u text := new.raw_user_meta_data ->> 'username';
begin
  if u is not null and (u !~ '^[A-Za-z0-9_.-]{3,16}$'
      or exists (select 1 from public.profiles where lower(username) = lower(u))) then
    u := null;
  end if;
  insert into public.profiles (id, username) values (new.id, u) on conflict (id) do nothing;
  return new;
end $$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

-- What the leaderboard reads: scores with the owner's username and icon.
create or replace view public.leaderboard with (security_invoker = on) as
  select s.user_id as id, s.best, s.daily, s.day::text as day, p.username as name, p.icon
  from public.scores s
  join public.profiles p on p.id = s.user_id
  where p.username is not null;
grant select on public.leaderboard to anon, authenticated;

-- Live updates: tell the game when any score changes.
do $$ begin
  alter publication supabase_realtime add table public.scores;
exception when duplicate_object then null;
end $$;
