-- Wordfall: player profiles. Clicking a player's name or picture shows their scores, accolades and recent
-- runs, so everyone can read the runs table (each player's last 100 games: mode, score, words, speed).
-- Players still only add or delete their own runs (schema.sql).
-- Run this once in Supabase: Dashboard → SQL Editor → New query → paste → Run. Needs schema.sql first.
-- Safe to run again.
grant select on public.runs to anon, authenticated;
drop policy if exists "runs are public" on public.runs;
create policy "runs are public" on public.runs for select using (true);
