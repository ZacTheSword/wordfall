-- Wordfall: keeps each signed-in player's history and progress on the server, so clearing the
-- browser or switching devices doesn't lose it.
--   runs         one row per finished run; only the newest 100 per player are kept.
--   player_data  one small row per player: quests, gems, unlocks, level, owned tiles and
--                icons, stats and settings.
-- Only the owner can read or change their own rows.
-- Run this once in Supabase: Dashboard → SQL Editor → New query → paste → Run.
-- Safe to run again. Until it has run, the game works as before and keeps everything on the device.

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
