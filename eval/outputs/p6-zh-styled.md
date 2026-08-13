**原因**

`db.orders.findOne` 查到的 `order`,有些舊資料的 `customer` 欄位是 `undefined`。第 31 行直接讀 `order.customer.id`,遇到 `undefined.id` 就會噴錯。

常見成因,2 選 1:
1. 這些訂單建立時,`customer` 欄位沒被寫入(舊資料、或建單流程曾經漏寫)。
2. 訂單是「訪客結帳」建立的,本來就沒有綁 `customer`。

**先確認是哪一種**

跑這行查詢,看有多少筆訂單的 `customer` 是空的:

```js
db.orders.find({ customer: { $exists: false } }).count()
```

- 數量很少且都是舊訂單 → 情況 1,資料問題。
- 數量持續增加、且都是同一種訂單類型 → 情況 2,業務邏輯本來就允許沒有 customer。

**怎麼修**

第 31 行改成:

```js
const userId = order.customer?.id ?? null;
```

`?.` 是 optional chaining,意思是「前面是 undefined 就整段回傳 undefined,不會噴錯」。`?? null` 是說「如果拿到 undefined,就換成 null」。

改完後,呼叫這個 `userId` 的地方要檢查是否能接受 `null`,不然錯誤只是往後延,不是真的解決。

**下一步**

先跑上面那行查詢,確認是資料問題還是訪客訂單,再決定要不要修資料或加 null 判斷。
