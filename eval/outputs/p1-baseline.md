Here's what's likely going on:

**1. Your caret range shouldn't have crossed a major version — so check what's actually installed.**
`^8.5.1` restricts npm to `>=8.5.1 <9.0.0`. If the teammate ran `npm install jsonwebtoken@latest` (or `npm update jsonwebtoken` after someone changed the range and later reverted `package.json` without reverting the lockfile), `package.json` can show `^8.5.1` while `package-lock.json`/`node_modules` actually resolved to a `9.x`. Run `npm ls jsonwebtoken` to see the real installed version before assuming the pin is honored.

**2. If it did jump to v9, here's what breaks code shaped like yours:**

- **Bundled TypeScript types.** As of v9, `jsonwebtoken` ships its own `.d.ts` files instead of relying on `@types/jsonwebtoken`. If `@types/jsonwebtoken` is still in `devDependencies`, you can get duplicate/conflicting declarations, which fails type-checked test runs (`ts-jest`, `vitest` with `typecheck`, etc.) even though the runtime logic is untouched.
- **Node engine bump.** v9 requires Node ≥ 12. Unlikely your problem in 2026, but worth a glance at CI runner versions.
- **Stricter secret/algorithm validation.** The v9 line hardened checks around `secretOrPublicKey` and algorithm matching (part of the fixes for CVE-2022-23540/23541). Code that used to pass with a falsy/misconfigured secret, or fixtures signed with a mismatched algorithm, now throws where it silently didn't before. Since your call already pins `algorithms: ['HS256']`, the most probable trigger here is `process.env.JWT_SECRET` being `undefined` in the test environment — v9 is less forgiving about that than v8 was.

**3. What I'd actually do:**

- Look at the real failure message/stack from `auth.spec.ts` first — it tells you which of the above it is (TS compile error vs. `JsonWebTokenError` vs. something about `secretOrPublicKey`). I don't have that output, so I can't pin it down further without it.
- Run `npm ls jsonwebtoken` to confirm the resolved version matches what you expect.
- If `@types/jsonwebtoken` is present, remove it — v9's bundled types supersede it.
- Confirm `JWT_SECRET` is actually set in the test env (`.env.test`, CI secrets), since your `verifyToken` has no guard for it being missing.
- Decide intentionally: either lock back to true 8.x (`"jsonwebtoken": "8.5.1"` exact, then `rm package-lock.json node_modules && npm install`) to restore old behavior, or accept the v9 upgrade and fix the root cause (missing env var / stale types) rather than fighting the pin.
