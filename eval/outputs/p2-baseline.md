## Why it's happening

`order.customer` is `undefined` for some of the documents returned by `db.orders.findOne({ orderId })`. This is a data issue, not a code bug per se — some orders in the collection just don't have a `customer` field (or it's `null`). Common causes:

- **Guest checkouts** — orders placed without a logged-in user never got a `customer` object attached.
- **Orphaned/soft-deleted users** — the customer record was deleted (e.g. GDPR erasure, account deletion) but the order document wasn't updated or the reference wasn't populated.
- **Legacy data** — older orders were written before `customer` was a required field in the schema, or before a schema migration added it.
- **Join/populate failure** — if `customer` is normally populated from a reference (e.g. Mongoose `.populate('customer')`), a missing/broken reference resolves to `undefined` instead of an object.

Since it "works for most orders," this is almost certainly inconsistent data rather than a query bug — some subset of orders genuinely has no linked customer.

## How to fix it

1. **Guard the access** so it doesn't crash:

```js
const userId = order.customer?.id;
```

2. **Decide what should happen when there's no customer** — this is the real fix, not just avoiding the crash. Options depend on business logic:

```js
if (!order.customer) {
  // e.g. guest order — return a summary without user info
  return { ...otherSummaryFields, userId: null, isGuest: true };
}
const userId = order.customer.id;
```

Or throw a clear, expected error instead of a generic TypeError, if a missing customer really shouldn't happen for this order type:

```js
if (!order.customer) {
  throw new Error(`Order ${order.orderId} has no associated customer`);
}
```

3. **Find out how many orders are affected** — query for `customer: null` or missing `customer` in the DB to gauge scope, and check if this correlates with a specific order type (guest, refunded, migrated, etc.). That tells you whether the real fix belongs in `summary.js` (handle it gracefully) or upstream in whatever writes orders (make `customer` required, or explicitly set `customer: null` for guests so it's an intentional state, not a data gap).

4. Add a regression test that calls `getOrderSummary` with an order missing `customer` to make sure it no longer throws.
