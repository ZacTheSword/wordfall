-- Wordfall: remembers which game speed (slow, normal or fast) each leaderboard score was played at,
-- so the board can show a small speed tag next to it.
--   best_pace   the speed of the player's best game ever
--   daily_pace  the speed of their best Today's drop on `day`
-- Run this once in Supabase: Dashboard → SQL Editor → New query → paste → Run.
-- Safe to run again. Until it has run, the game still works and scores just show no speed tag.

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
