Node.js runs one task, then empties the microtask queue, then repeats. That single rule explains almost every confusing case you've seen.

## The engine: one thread, one loop

Node.js runs your code on **one thread** (a single line of execution — no parallel JS). The **event loop** is the loop that decides what runs next.

Each loop cycle does two things, in order:

1. Run one item from a queue (a macrotask — see below).
2. Run every item currently in the microtask queue, until it's empty.

Then it repeats.

## The two queues

**Macrotask** = a big scheduled job. Examples: `setTimeout`, `setInterval`, I/O callbacks (file reads, network responses).

**Microtask** = a small follow-up job. Examples: `Promise.then/catch/finally`, `queueMicrotask`.

**The rule that matters:** after every single macrotask, Node drains the *entire* microtask queue before it touches the next macrotask. Not some of it — all of it, even microtasks added by other microtasks.

## Worked example

```js
console.log('1');

setTimeout(() => console.log('2'), 0);   // macrotask

Promise.resolve().then(() => console.log('3'));  // microtask

console.log('4');
```

Output: `1, 4, 3, 2`

Why, step by step:

1. `console.log('1')` runs now. It's normal code, not a task.
2. `setTimeout` schedules `'2'` as a macrotask. Node doesn't run it yet.
3. `.then` schedules `'3'` as a microtask. Node doesn't run it yet.
4. `console.log('4')` runs now.
5. Main code is done. Node drains microtasks: `'3'` prints.
6. Microtask queue is empty. Node runs the next macrotask: `'2'` prints.

## The one trap to remember

A microtask that schedules another microtask still runs **before** the next macrotask. Microtasks can starve macrotasks if you keep chaining `.then()` calls — the loop won't move on until that queue is empty.

**Next step:** paste that example into Node and run it. Watching the order print (`1 4 3 2`) locks the rule in faster than reading about it.
