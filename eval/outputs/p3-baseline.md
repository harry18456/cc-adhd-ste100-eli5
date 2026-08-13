For ~12 known boolean flags that you filter on, go with a **separate `user_preferences` table with real boolean columns** (1:1 with `users` via `user_id` PK/FK), not JSONB.

**Why not JSONB here:**
- Filtering requires either a GIN index (`jsonb_path_ops`) that's coarser and larger than you need, or per-key expression indexes (`((preferences->>'key')::boolean)`) — at that point you've recreated typed columns with extra syntax overhead.
- No type safety/NOT NULL constraints; typos in keys fail silently.
- Query ergonomics suffer: `WHERE (preferences->>'email_opt_in')::boolean = true` vs `WHERE email_opt_in = true`.

**Why a separate table, not columns on `users`:**
- Preferences change more often than core user data (email, auth fields). Keeping them separate avoids row bloat/MVCC churn on the hot `users` table from frequent unrelated updates.
- Reduces lock contention between auth-critical queries and preference toggles.

**Why plain boolean columns are fine even though the set "may grow":**
- Since Postgres 11, `ALTER TABLE ... ADD COLUMN ... DEFAULT <constant>` is a metadata-only change (no table rewrite), so adding flag #13, #14, etc. is cheap.
- Each flag gets a simple btree index (or partial index, e.g. `WHERE flag = true`, if the flag is usually false and you only query the true subset) — cheaper and more selective than a GIN index over a blob.

**When JSONB would actually win:** if the flags were truly dynamic/user-defined (not a fixed schema you control), or if you rarely filter on them and mostly just read/write the whole bag at once. That's not your case — you said you need to filter by preference, which is the strongest signal toward typed columns.

If you expect the flag count to grow well past ~20-30 or want per-user custom flags alongside the core set, a hybrid (core flags as columns + a `jsonb extra` column for the long tail) is a reasonable escape hatch, but don't start there.
