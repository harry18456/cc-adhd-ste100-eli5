Use a JSONB column on the `users` table with a GIN index. Do not use a separate table.

**Option A — JSONB column (recommended)**
Add one column: `preferences JSONB NOT NULL DEFAULT '{}'`. Add a GIN index for fast filtering:
```sql
CREATE INDEX idx_users_preferences ON users USING GIN (preferences jsonb_path_ops);
```
Filter like this:
```sql
SELECT * FROM users WHERE preferences @> '{"email_marketing": true}';
```
New flags need no migration. Just start writing the new key.

**Option B — separate key-value table**
Table: `user_preferences (user_id, pref_key, pref_value boolean)`. Filtering needs a JOIN or EXISTS per flag. Adding a flag needs no schema change either, but every query gets slower and harder to read as flags grow.

**Why A wins for your case:** 12 boolean flags is small. A JOIN-per-flag table adds cost with no benefit at this size. JSONB with `jsonb_path_ops` keeps single-flag filters fast and keeps queries simple.

**One exception:** if you later need per-flag metadata (who changed it, when, why), switch to Option B then. Boolean flags alone do not need it.

Next step: add the `preferences JSONB` column and the GIN index above.
