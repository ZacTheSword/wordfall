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
-- Best Today's drop as a score-over-time line (see daily-timeline.sql).
alter table public.scores add column if not exists daily_tl jsonb;
alter table public.scores drop constraint if exists daily_tl_size;
alter table public.scores add constraint daily_tl_size check (daily_tl is null or pg_column_size(daily_tl) < 8000);

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

-- Each player's last 100 runs and the rest of their progress (see player-sync.sql).
create table if not exists public.runs (
  user_id uuid not null references public.profiles (id) on delete cascade,
  at bigint not null,                       -- when the run ended (ms since 1970), unique per player
  data jsonb not null,
  created_at timestamptz not null default now(),
  primary key (user_id, at),
  constraint run_size check (pg_column_size(data) < 32000)
);

create table if not exists public.player_data (
  user_id uuid primary key references public.profiles (id) on delete cascade,
  data jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  constraint player_data_size check (pg_column_size(data) < 200000)
);

grant select, insert, delete on public.runs to authenticated;
grant select, insert, update on public.player_data to authenticated;

alter table public.runs enable row level security;
alter table public.player_data enable row level security;

drop policy if exists "read own runs" on public.runs;
create policy "read own runs" on public.runs for select to authenticated using (auth.uid() = user_id);
drop policy if exists "add own runs" on public.runs;
create policy "add own runs" on public.runs for insert to authenticated with check (auth.uid() = user_id);
drop policy if exists "delete own runs" on public.runs;
create policy "delete own runs" on public.runs for delete to authenticated using (auth.uid() = user_id);

drop policy if exists "read own data" on public.player_data;
create policy "read own data" on public.player_data for select to authenticated using (auth.uid() = user_id);
drop policy if exists "add own data" on public.player_data;
create policy "add own data" on public.player_data for insert to authenticated with check (auth.uid() = user_id);
drop policy if exists "edit own data" on public.player_data;
create policy "edit own data" on public.player_data for update to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- Keep only each player's newest 100 runs.
create or replace function public.trim_runs() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  delete from public.runs r
  where r.user_id = new.user_id
    and r.at < (select x.at from public.runs x where x.user_id = new.user_id order by x.at desc offset 99 limit 1);
  return null;
end $$;

drop trigger if exists runs_keep_100 on public.runs;
create trigger runs_keep_100 after insert on public.runs
  for each row execute function public.trim_runs();

-- Wordfall: remembers which game speed (slow, normal or fast) each leaderboard score was played at,
-- so the board can show a small speed tag next to it.
--   best_pace   the speed of the player's best game ever
--   daily_pace  the speed of their best Today's drop on `day`

alter table public.scores add column if not exists best_pace text;
alter table public.scores add column if not exists daily_pace text;
alter table public.scores drop constraint if exists scores_pace_ok;
alter table public.scores add constraint scores_pace_ok check (
  (best_pace is null or best_pace in ('slow', 'normal', 'fast')) and
  (daily_pace is null or daily_pace in ('slow', 'normal', 'fast')));

-- The public board view, now with the two speeds (new columns go on the end).
create or replace view public.leaderboard with (security_invoker = on) as
  select s.user_id as id, s.best, s.daily, s.day::text as day, p.username as name, p.icon,
         s.best_pace, s.daily_pace
  from public.scores s
  join public.profiles p on p.id = s.user_id
  where p.username is not null;
grant select on public.leaderboard to anon, authenticated;
