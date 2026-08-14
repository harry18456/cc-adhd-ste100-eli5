The bug is `await`. `db.users.findById(req.params.id)` returns a Promise, and you're never awaiting it — so `user` is the Promise object itself, not the resolved data.

```js
app.get('/user/:id', async (req, res) => {
  const user = db.users.findById(req.params.id);
  res.json(user);
});
```

When `res.json()` serializes a Promise, `JSON.stringify` finds no enumerable own properties on it (the actual data lives inside the Promise's internal, non-enumerable state), so it serializes to `{}`. That's why the response is an empty object even though the row genuinely exists in the database — the query succeeded, you just never unwrapped the result.

Fix:

```js
app.get('/user/:id', async (req, res) => {
  const user = await db.users.findById(req.params.id);
  res.json(user);
});
```

Two things worth double-checking while you're in there:

1. **Error handling** — if `findById` rejects (bad ID format, DB hiccup), an unhandled rejection inside an async Express route won't crash cleanly and won't send a response by default (unless you're on Express 5, which auto-forwards rejected promises to your error handler). Wrap in try/catch or confirm you're on Express 5.
2. **Not-found case** — if `user` comes back `null`/`undefined` when no row matches, `res.json(null)` returns `200` with body `null`, which is usually not what callers expect. Consider a `404` explicitly:

```js
app.get('/user/:id', async (req, res) => {
  const user = await db.users.findById(req.params.id);
  if (!user) return res.status(404).json({ error: 'User not found' });
  res.json(user);
});
```
