Let's build this up in layers — the event loop only makes sense once you see *why* it exists.

## The core problem

JavaScript in Node runs on a single thread. If `fetch`-ing a file or a database call blocked that thread, your whole server would freeze for every other request while it waited. Node avoids this by handing slow operations (I/O, timers, network) off to the system/`libuv` thread pool, and using a loop to check "is anything ready to run?" — that loop is the event loop.

## The building blocks

1. **Call stack** — where your synchronous code executes, one frame at a time.
2. **Node APIs / libuv** — where async work (timers, file I/O, network) actually happens, off the main thread.
3. **Callback queues** — when async work finishes, its callback doesn't run immediately; it gets queued until the call stack is empty.
4. **The event loop** — repeatedly checks: is the stack empty? If so, pull the next callback from a queue and run it.

There isn't just one queue though — that's where microtasks/macrotasks confuse people.

## Macrotasks (the event loop's "phases")

The event loop actually runs in **phases**, each with its own queue, in this order, repeated every "tick":

1. **timers** — `setTimeout` / `setInterval` callbacks whose time has elapsed
2. **pending callbacks** — some system-level callbacks (rare, deferred from previous loop)
3. **poll** — retrieves new I/O events; executes I/O callbacks (file reads, network responses)
4. **check** — `setImmediate` callbacks
5. **close callbacks** — e.g. `socket.on('close', ...)`

Each of these is a "macrotask" phase. The loop moves through them in order, then loops back to `timers` again.

## Microtasks (the important twist)

Microtasks are a **separate, higher-priority queue**: `Promise.then/catch/finally` callbacks, `queueMicrotask()`, and `process.nextTick()` (which is actually even higher priority than promises — its own queue, checked first).

The key rule: **after every single callback finishes (not just after every phase), Node drains the entire microtask queue before doing anything else.** So it's not "one macrotask, then one microtask" — it's "one macrotask, then *all* currently queued microtasks, then the next macrotask."

Priority order when the queue is checked:
1. `process.nextTick` queue (fully drained)
2. Promise/microtask queue (fully drained)
3. Then move on to the next macrotask (timer, I/O callback, `setImmediate`, etc.)

## Walking through an example

```js
console.log('1: sync');

setTimeout(() => console.log('2: setTimeout'), 0);

Promise.resolve().then(() => console.log('3: promise'));

process.nextTick(() => console.log('4: nextTick'));

console.log('5: sync');
```

Output:
```
1: sync
5: sync
4: nextTick
3: promise
2: setTimeout
```

Why:
- Synchronous code runs first, top to bottom → `1`, `5`.
- Stack is now empty. Before touching any macrotask (timer), Node drains microtasks: `nextTick` queue first → `4`, then promise queue → `3`.
- Only now does the loop move into the **timers** phase and run the `setTimeout` callback → `2`.

## Why `setImmediate` vs `setTimeout(fn, 0)` is inconsistent

`setImmediate` runs in the **check** phase, `setTimeout(fn, 0)` runs in the **timers** phase. From the main module (top-level code), their order isn't guaranteed — it depends on process startup timing. But **inside an I/O callback**, `setImmediate` always fires before `setTimeout`, because after an I/O callback (poll phase), the loop naturally moves to check (setImmediate) before wrapping back around to timers.

```js
const fs = require('fs');

fs.readFile(__filename, () => {
  setTimeout(() => console.log('timeout'), 0);
  setImmediate(() => console.log('immediate'));
});
```
This always prints `immediate` then `timeout`, because we're already past the poll phase.

## The mental model to keep

Think of it as: **stack → microtasks (fully drained, nextTick before promises) → next macrotask → microtasks again → next macrotask → ...** repeating forever. Microtasks always get to fully empty their queue between every single macrotask, which is why chained `.then()`s can "starve" timers if you queue promises recursively without ever yielding to a macrotask.

Want me to go one level deeper into any piece — like how `async/await` maps onto this, or how the thread pool (libuv) size affects things like `fs` or `crypto` calls?
