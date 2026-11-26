-- Wordfall: keeps each player's best Today's drop as a score-over-time line, so the results
-- screen can race your run against the top 3 on today's board.
-- Run this once in Supabase: Dashboard → SQL Editor → New query → paste → Run.
-- Safe to run again. Until it has run, the game still works: the top 3 show as flat lines
-- at their final scores instead.
alter table public.scores add column if not exists daily_tl jsonb;
alter table public.scores drop constraint if exists daily_tl_size;
alter table public.scores add constraint daily_tl_size check (daily_tl is null or pg_column_size(daily_tl) < 8000);
