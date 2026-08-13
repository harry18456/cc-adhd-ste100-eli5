Add optional chaining and a guard clause in `summary.js:31`.

```js
const userId = order.customer?.id;
if (!userId) {
  throw new Error(`Order ${order.orderId} has no customer attached`);
}
```

**Cause**: `order.customer` is `undefined` for some documents. `db.orders.findOne` returns whatever is stored. Some order records were saved without a `customer` field — likely guest checkouts, deleted-user orders, or old records from before `customer` was required.

**Steps**:
1. Open `/app/src/orders/summary.js`.
2. Replace line 31 with the code above.
3. Decide what should happen for orders with no customer — throw, skip, or return a fallback summary. The example throws a clear error instead of crashing with `TypeError`.
4. Redeploy and check logs for the new "has no customer attached" message. It tells you which orders are missing data.

**Root fix**: query your database for orders where `customer` is missing or null. Decide if those records need a data backfill.

Next: run that query against production data to see how many orders are affected.
