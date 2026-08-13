Bug: `jwt.verify()` calls `jwt.sign()`'s callback-style overload wrong, or more likely — jsonwebtoken v9 changed default behavior. Check which version got installed.

**Cause**: `^8.5.1` allows any 8.x. If the teammate ran `npm install jsonwebtoken@latest` or similar, it likely installed v9. Version 9 dropped support for some algorithm and options handling that v8 had. Also, v9 made `process.env.JWT_SECRET` (type `string | undefined`) fail TypeScript checks — v8's types were looser.

**Do this now**:

1. Run `npm ls jsonwebtoken`. Check the installed version.
2. If it's v9.x, read the migration notes: `node_modules/jsonwebtoken/CHANGELOG.md`.
3. Fix the type error first — add a guard:
   ```ts
   const secret = process.env.JWT_SECRET;
   if (!secret) throw new Error('JWT_SECRET not configured');
   return jwt.verify(token, secret, { algorithms: ['HS256'] });
   ```

**Next action**: run `npm ls jsonwebtoken` and tell me the version. I'll pinpoint the exact breaking change.
