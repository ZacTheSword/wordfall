-- Run this once if schema.sql was run before these grants were added.
-- Lets the website's key use the tables; row level security still limits
-- each player to writing their own rows.
grant usage on schema public to anon, authenticated;
grant select on public.profiles, public.scores to anon, authenticated;
grant insert, update on public.profiles, public.scores to authenticated;
grant select on public.leaderboard to anon, authenticated;
