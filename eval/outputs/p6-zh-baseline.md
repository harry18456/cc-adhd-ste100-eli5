這個錯誤的模式(「少數訂單」而非全部)代表**資料本身有缺失，不是程式邏輯對所有情況都錯**。`order.customer` 在某些訂單上是 `undefined`,代表 `db.orders.findOne({ orderId })` 回傳的物件裡沒有 `customer` 這個欄位或它是 null。

## 可能原因

1. **Guest 訂單 / 未登入結帳**:少數訂單本來就沒有綁定 customer(訪客下單),`customer` 欄位設計上就允許空值。
2. **Populate/Join 失敗**:如果 `customer` 是透過 reference 關聯查詢出來的(例如 Mongoose 的 `.populate('customer')`),當該顧客帳號被刪除或資料被清除時,populate 會回傳 `null` 而不是拋錯。
3. **舊資料 / schema 遷移前的紀錄**:在加入 `customer` 這個欄位之前建立的舊訂單,資料庫裡根本沒有這個 key。
4. **寫入時的競態條件(race condition)**:訂單建立流程中,`customer` 是分開的步驟寫入的,若中途失敗會留下沒有 customer 的訂單。

## 建議排查步驟

先去資料庫查那幾筆掛掉的 orderId,確認 `customer` 欄位到底是:
- 完全不存在的 key
- 存在但值是 `null`
- 是一個 reference id,但對應的 customer 文件已被刪除

這能幫你判斷是「資料本來就合法允許空值」還是「資料損壞/不一致」。

## 修法

**先讓程式不要炸(防禦性寫法)**:

```js
const userId = order.customer?.id;
if (!userId) {
  // 依業務邏輯決定:記錄警告、回傳特定錯誤、或給預設值
  logger.warn(`Order ${order.orderId} has no linked customer`);
  throw new AppError('ORDER_MISSING_CUSTOMER', 404, { orderId: order.orderId });
}
```

**但更重要的是根治**:
- 如果這是合法情境(訪客訂單),`getOrderSummary` 的邏輯要明確處理「無 customer」的分支,而不是假設一定存在。
- 如果這是資料異常(customer 被刪除但訂單還在),要決定業務規則 ——是保留歷史快照(下單當下把 customer 資訊複製一份到訂單裡,而非只存 reference),還是允許顯示「已刪除的使用者」。

**長期建議**:訂單這種需要保留歷史紀錄的資料,通常不該只存 customer 的 reference,而應該在建立訂單當下就把必要欄位(如 `customerId`、`customerName`)snapshot 進訂單本身,避免未來 customer 被刪除或修改時影響歷史訂單資料的完整性。
