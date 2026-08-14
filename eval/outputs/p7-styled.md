`res.json(user)` sends a `Promise` object, not the resolved data. `findById` is `async`, but the handler never awaits it.

Fix: add `await`.

```js
app.get('/user/:id', async (req, res) => {
  const user = await db.users.findById(req.params.id);
  res.json(user);
});
```

Without `await`, `user` is a pending `Promise`. `res.json()` serializes that object, and a `Promise` has no visible own properties, so JSON.stringify outputs `{}`.
