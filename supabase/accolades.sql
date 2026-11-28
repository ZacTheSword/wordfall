-- Wordfall: accolades, earned by your place on Today's drop.
--   1st 10, 2nd 7, 3rd 5, 4th to 10th 2, everyone else on the board 1.
-- A day's drop is over everywhere at 12:00 UTC the next day (the last time zone's midnight). From then its
-- reward waits in the player's Inbox until they claim it. The all-time leaderboard ranks players by the
-- accolades they've claimed.
-- Run this once in Supabase: Dashboard → SQL Editor → New query → paste → Run. Needs schema.sql first.
-- Safe to run again.

-- Each day's best Today's drop per player. scores only holds the latest day, so this keeps the
-- older days' boards for paying out. It's filled from scores (see the trigger below), never by the game.
create table if not exists public.daily_scores (
  day date not null,
  user_id uuid not null references public.profiles (id) on delete cascade,
  score integer not null check (score between 1 and 99999999),
  updated_at timestamptz not null default now(),
  primary key (day, user_id)
);
grant select on public.daily_scores to anon, authenticated;
alter table public.daily_scores enable row level security;
drop policy if exists "daily scores are public" on public.daily_scores;
create policy "daily scores are public" on public.daily_scores for select using (true);

-- Whenever a player posts a Today's drop, keep it for that day. Only days that are still being played
-- somewhere count (a day runs from 10:00 UTC the day before to 12:00 UTC the day after), so nobody can
-- add a score to a day that has already paid out.
create or replace function public.keep_daily_score() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  if new.day is not null and new.daily > 0
     and now() >= new.day::timestamp at time zone 'utc' - interval '14 hours'
     and now() < new.day::timestamp at time zone 'utc' + interval '36 hours' then
    insert into public.daily_scores (day, user_id, score) values (new.day, new.user_id, new.daily)
    on conflict (day, user_id) do update
      set score = greatest(public.daily_scores.score, excluded.score), updated_at = now();
  end if;
  return null;
end $$;
drop trigger if exists scores_keep_daily on public.scores;
create trigger scores_keep_daily after insert or update on public.scores
  for each row execute function public.keep_daily_score();

-- Scores already posted for a day that's still going count too.
insert into public.daily_scores (day, user_id, score)
  select s.day, s.user_id, s.daily from public.scores s
  where s.day is not null and s.daily > 0
    and now() < s.day::timestamp at time zone 'utc' + interval '36 hours'
on conflict (day, user_id) do update set score = greatest(public.daily_scores.score, excluded.score);

-- Accolades paid out: one row per player per day, written only by accolade_claim() below.
create table if not exists public.accolades (
  user_id uuid not null references public.profiles (id) on delete cascade,
  day date not null,
  place integer not null check (place >= 1),
  players integer not null check (players >= 1),
  amount integer not null check (amount between 1 and 10),
  claimed_at timestamptz not null default now(),
  primary key (user_id, day)
);
grant select on public.accolades to anon, authenticated;
alter table public.accolades enable row level security;
drop policy if exists "accolades are public" on public.accolades;
create policy "accolades are public" on public.accolades for select using (true);

-- What a place pays.
create or replace function public.accolade_pay(place integer) returns integer
language sql immutable set search_path = '' as $$
  select case when place = 1 then 10 when place = 2 then 7 when place = 3 then 5 when place <= 10 then 2 else 1 end
$$;

-- Your days from the last two weeks that haven't been claimed: your place on each (ties share the
-- better place), how many were on that board, what it pays, and when it can be claimed.
create or replace function public.accolade_pending()
returns table (day date, place integer, players integer, amount integer, ready_at timestamptz)
language sql stable security definer set search_path = '' as $$
  select m.day, x.place, x.players, public.accolade_pay(x.place),
         m.day::timestamp at time zone 'utc' + interval '36 hours'
  from public.daily_scores m
  cross join lateral (
    select (1 + count(*) filter (where o.score > m.score))::integer as place, greatest(count(*), 1)::integer as players
    from public.daily_scores o join public.profiles p on p.id = o.user_id
    where o.day = m.day and p.username is not null
  ) x
  where m.user_id = auth.uid()
    and m.day > (now() at time zone 'utc')::date - 15
    and not exists (select 1 from public.accolades a where a.user_id = m.user_id and a.day = m.day)
  order by m.day desc
$$;

-- Claim one day's reward. The place is worked out here from that day's final board, so the game
-- can't pick its own amount. Returns what was paid (0 if it was already claimed).
create or replace function public.accolade_claim(p_day date) returns integer
language plpgsql security definer set search_path = '' as $$
declare
  me uuid := auth.uid();
  mine integer; pl integer; n integer; amt integer;
begin
  if me is null then raise exception 'Sign in to claim accolades' using errcode = 'P0001'; end if;
  if now() < p_day::timestamp at time zone 'utc' + interval '36 hours' then
    raise exception 'That day''s drop isn''t over everywhere yet' using errcode = 'P0001';
  end if;
  if p_day <= (now() at time zone 'utc')::date - 15 then
    raise exception 'That reward has expired' using errcode = 'P0001';
  end if;
  select score into mine from public.daily_scores where day = p_day and user_id = me;
  if mine is null then raise exception 'You didn''t play that day''s drop' using errcode = 'P0001'; end if;
  select (1 + count(*) filter (where o.score > mine))::integer, greatest(count(*), 1)::integer into pl, n
    from public.daily_scores o join public.profiles p on p.id = o.user_id
    where o.day = p_day and p.username is not null;
  amt := public.accolade_pay(pl);
  insert into public.accolades (user_id, day, place, players, amount) values (me, p_day, pl, n, amt)
    on conflict (user_id, day) do nothing;
  if not found then return 0; end if;
  return amt;
end $$;

revoke all on function public.accolade_pending() from public, anon;
revoke all on function public.accolade_claim(date) from public, anon;
grant execute on function public.accolade_pending() to authenticated;
grant execute on function public.accolade_claim(date) to authenticated;

-- The board view gains each player's accolade total (score-speed.sql's columns are added here too,
-- in case that file hasn't been run; new columns always go on the end).
alter table public.scores add column if not exists best_pace text;
alter table public.scores add column if not exists daily_pace text;
create or replace view public.leaderboard with (security_invoker = on) as
  select s.user_id as id, s.best, s.daily, s.day::text as day, p.username as name, p.icon,
         s.best_pace, s.daily_pace,
         coalesce((select sum(a.amount) from public.accolades a where a.user_id = s.user_id), 0)::integer as acc
  from public.scores s
  join public.profiles p on p.id = s.user_id
  where p.username is not null;
grant select on public.leaderboard to anon, authenticated;
