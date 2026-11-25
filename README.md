# Wordfall

Tetris meets Wordle, in one HTML file.

## Layout

| Path | What it is |
|---|---|
| `wordfall.html` | The game. This is the source for everything else. |
| `deploy/build.py` | Builds the self-hosted copy into `deploy/site/index.html`. |
| `deploy/config.json` | Supabase project URL and publishable key for online play off claude.ai. |
| `supabase/schema.sql` | Accounts + leaderboard tables. Run once in the Supabase SQL Editor. |
| `deploy/site/` | The built site (not in git; Netlify builds it). |
| `netlify.toml` | Netlify settings (publish folder, build command). |
| `media/` | Audio previews (Rot & Thaw music). Local only, not in git. |
| `history/` | Earlier hand-kept copies of `wordfall.html`. Local only; git history replaces it. |
| `.claude/` | Local preview server used for testing (`serve.py`, port 8765). |

## Two places the game runs

1. **claude.ai artifact**: https://claude.ai/artifact/BLbjQjdZNuxynpwFXxZ39c
   Online uses claude.ai's own rooms (signed-in people invited to the page), and the
   leaderboard uses the artifact's database.
2. **Netlify (self-hosted)**: https://quiet-puffpuff-d05cf5.netlify.app, built from the same file.
   Online uses Supabase Realtime. Accounts (Google, or username + password) use Supabase Auth,
   and the leaderboard uses the `profiles`/`scores` tables. Anyone with the link can play;
   posting scores needs an account with a username.

The two have separate player pools: claude.ai players and Netlify players can't meet.

## Updating the Netlify site

**With GitHub connected (recommended):** push to `main`. Netlify runs `python3 deploy/build.py`
and publishes `deploy/site` on every push (settings in `netlify.toml`). To connect it once:
Netlify → Site configuration → Build & deploy → Link repository → pick this repo.

**By hand:**

```
python deploy/build.py
```

Then either drag the `deploy/site` folder onto the site's **Deploys** page in Netlify,
or, after `npx netlify-cli login` and `npx netlify-cli link` once:

```
npx netlify-cli deploy --prod --dir deploy/site
```

## Accounts and leaderboard (Supabase setup, once)

1. **SQL Editor** → New query → paste `supabase/schema.sql` → Run.
2. **Authentication → Sign In / Providers → Email**: keep it on, turn **Confirm email** off.
   Username accounts sign in with a placeholder address (`<name>@players.wordfall.invalid`)
   that can't receive mail.
3. **Authentication → URL Configuration**: Site URL `https://quiet-puffpuff-d05cf5.netlify.app`,
   and add `https://quiet-puffpuff-d05cf5.netlify.app/**` (plus `http://localhost:8765/**` for
   local testing) to Redirect URLs.
4. **Google sign-in**: in Google Cloud Console create an OAuth client (Web application) with
   authorized redirect URI `https://nwqvbvynwslzehcptqxh.supabase.co/auth/v1/callback`, then paste
   its Client ID and Client secret into **Authentication → Sign In / Providers → Google**.

Each account's UUID (Supabase Auth user id) is its Player ID. Players never see it.
`profiles.id` is that UUID and `profiles.username` is unique (case-insensitive), so every
username belongs to exactly one UUID.
