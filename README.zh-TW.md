[English](README.md) | 繁體中文

# adhd-ste100-eli5

一個 Claude Code **output style**，讓回答變得好讀、也好動手。

不只是變短，是**重新排過** —— 答案排在螢幕第一行、每一句只帶一個指令、不用任何需要你停下來解碼的詞。

不需要診斷證明。單純今天腦子不夠用也算。

## 差別長這樣

下面兩段都是真實的 `claude -p` 輸出（Sonnet、Claude Code v2.1.229、2026 年 8 月），同一個中文 prompt：正式環境 API 在 `order.customer.id` 噴 `TypeError`，因為少數訂單沒有 `customer` 欄位。每個條件各跑一次，沒有重抽。Prompt、原始輸出、評分腳本都在 [`eval/`](eval/)。

**改造前 —— 預設風格。** 修法埋在後半段。

> 這個錯誤的模式(「少數訂單」而非全部)代表**資料本身有缺失，不是程式邏輯對所有情況都錯**。`order.customer` 在某些訂單上是 `undefined`,代表 `db.orders.findOne({ orderId })` 回傳的物件裡沒有 `customer` 這個欄位或它是 null。
>
> ## 可能原因
>
> 1. **Guest 訂單 / 未登入結帳**:少數訂單本來就沒有綁定 customer(訪客下單),`customer` 欄位設計上就允許空值。
> 2. **Populate/Join 失敗**:如果 `customer` 是透過 reference 關聯查詢出來的(例如 Mongoose 的 `.populate('customer')`),當該顧客帳號被刪除或資料被清除時,populate 會回傳 `null` 而不是拋錯。
>
> *〔README 在此截斷 —— 後面還有兩個成因、排查步驟、三段修法。全文：[`eval/outputs/p6-zh-baseline.md`](eval/outputs/p6-zh-baseline.md)〕*

**改造後 —— 本 style。** 全文引用。

> **原因**
>
> `db.orders.findOne` 查到的 `order`,有些舊資料的 `customer` 欄位是 `undefined`。第 31 行直接讀 `order.customer.id`,遇到 `undefined.id` 就會噴錯。
>
> 常見成因,2 選 1:
> 1. 這些訂單建立時,`customer` 欄位沒被寫入(舊資料、或建單流程曾經漏寫)。
> 2. 訂單是「訪客結帳」建立的,本來就沒有綁 `customer`。
>
> **先確認是哪一種**
>
> 跑這行查詢,看有多少筆訂單的 `customer` 是空的:
>
> ```js
> db.orders.find({ customer: { $exists: false } }).count()
> ```
>
> - 數量很少且都是舊訂單 → 情況 1,資料問題。
> - 數量持續增加、且都是同一種訂單類型 → 情況 2,業務邏輯本來就允許沒有 customer。
>
> **怎麼修**
>
> 第 31 行改成:
>
> ```js
> const userId = order.customer?.id ?? null;
> ```
>
> `?.` 是 optional chaining,意思是「前面是 undefined 就整段回傳 undefined,不會噴錯」。`?? null` 是說「如果拿到 undefined,就換成 null」。
>
> 改完後,呼叫這個 `userId` 的地方要檢查是否能接受 `null`,不然錯誤只是往後延,不是真的解決。
>
> **下一步**
>
> 先跑上面那行查詢,確認是資料問題還是訪客訂單,再決定要不要修資料或加 null 判斷。

### 量測結果

五種英文題型各跑一次 —— bug 修復、錯誤診斷、schema 決策、觀念解釋、多步驟教學：

| 每則回答平均 | 預設 | 套用後 |
|---|---|---|
| 內文字數 | 367 | 176 |
| 超過 20 詞上限的句子 | 39% | 8% |
| 禁用開場白 / 收尾 | 5 次中 1 次 | 5 次中 0 次 |
| 結尾給一個 next action | 5 次中 0 次 | 5 次中 5 次 |

上方引用的中文題未納入表格 —— 評分腳本以英文詞數為單位。兩個誠實的觀察：第 1 層第 5 條（時間估計）在 5 次中 0 次觸發；中文那次的第一行是原因不是動作，第 1 層第 1 條沒完全跟上。方法與注意事項見 [`eval/README.md`](eval/README.md)。

## 為什麼要三個成分

因為它們各修一層不同的摩擦力。三者**不重疊**，所以疊起來是增加涵蓋範圍，不是重複。

| 層 | 來源 | 管什麼 | 規則舉例 |
|---|---|---|---|
| **1. 訊息架構** | ADHD 支持實務 | 什麼先講、什麼放最後、什麼要砍掉 | 每一輪複述進度 —— 讀的人記不住「第 3 步 / 共 5 步」 |
| **2. 句子力學** | ASD-STE100 受控英文 | 每一句怎麼組裝 | 指令句上限 20 詞（中文約 30 字），描述句 25 詞（約 40 字） |
| **3. 用詞語域** | ELI5 | 挑哪些字進去 | 術語當場解釋，不要丟到註腳 |

第 2 層的價值在於它把另外兩層**變成可量測的**。ELI5 說「短句」，STE100 說**20 詞、中文 30 字**。ADHD 說「別廢話」，STE100 說**一句一指令，而且不准出現兩次 and then**。

### ASD-STE100 是什麼

一套受控英文標準，1986 年應歐洲航空公司要求誕生。他們的維修技師大多不是英語母語者，而飛機上一句看錯的指令會死人。所以整個產業訂了一版「不可能被誤讀的英文」：一字一義、主動語態、簡單時態、一句一指令、不准為了短就省略字詞。

同樣的紀律搬到這裡，理由完全一樣：一個腦力耗盡的讀者，跟停機坪上的技師一樣，不會停下來問你到底是什麼意思。

（「ASD」是發布這份標準的產業協會 —— AeroSpace and Defence Industries Association of Europe，歐洲航太暨國防工業協會。那是機構名稱，不是形容詞。）

## 三層互相打架時怎麼辦

三條裁決規則，位階高於上面所有規則。這部分上游兩個專案都沒有，是這個專案自己推導的。

1. **砍句子，不砍字。**
   第 1 層要訊息短，第 2 層禁止省略主詞和冠詞。兩邊都成立：**整句**沒有資訊量就整句刪掉，而活下來的每一句都要寫完整。

2. **可以縮短路徑，但不可以靜默縮短。**
   第 1 層說「跑完的短路徑勝過半途而廢的完整路徑」，第 2 層說「不准無聲無息丟掉條件或限定詞」。兩邊都成立：跳過那一步，然後用一行講出你跳過了什麼。

3. **複述進度不算重複。**
   第 3 層只要必要資訊，第 1 層要每輪複述狀態。狀態**就是**必要資訊 —— 它是讀的人放在腦袋外面的工作記憶。

## 刻意不採用的部分

三個來源都只取了一部分。拿這個 style 對照原典會發現落差，而落差是刻意的，不是漏抄。重要的有三個：

**ELI5 的比喻。** 真正的 ELI5 用比喻加去術語，講到五歲小孩懂。這裡反著做：術語保留、當場定義一次（第 2 層第 10 條），identifier 一字不改（第 3 層第 4 條）。比喻多花字數，還會蓋住精確名稱 —— 對腦力耗盡的讀者是加稅，不是減稅。名字取的是原推文的精神，不是字面做法。

**ADHD 支持實務的情緒面。** 真實的 ADHD 支持有一大塊是情緒工作：鼓勵、慶祝、處理 RSD（rejection sensitive dysphoria，對批評的過度情緒反應）。這裡只留防守面：錯誤講平淡、不歸咎任何人（第 1 層第 9 條），「Make the win visible」用具體事實代替慶祝。打氣句整個不採 —— 它過不了第 3 層第 1 條，而且模型一打氣就容易滑向諂媚，那是另一種認知稅。

**STE100 的核准字典與次要檢查。** 官方標準附一本約 900 字的核准字典，授權限制轉載，所以用第 3 層「最平常的字」規則替代。semicolon 禁令、名詞化檢查、phrasal verb 檢查也被砍掉：效益低，而每多一條規則，模型遵守其餘規則的穩定度就會再被稀釋。

## 語言

語言中性。這個 style 會跟著你使用的語言走。所有規則管的都是結構和用詞，跟你用哪種語言無關。

有兩條規則會自動調整：

- 句長上限在中文、日文、韓文改**算字元**而非算單字（約 30 / 40 字）。
- 簡單時態那條在沒有時態變化的語言直接跳過。

## 安裝

```
/plugin marketplace add harry18456/cc
/plugin install adhd-ste100-eli5@harry18456
```

## 啟用

裝好 plugin **不等於**啟用這個 style，要自己選（Claude Code v2.1.269 以上）：

```
/output-style adhd-ste100-eli5:ADHD STE100 ELI5
```

名稱不分大小寫，但 `adhd-ste100-eli5:` 前綴一定要加。也可以執行 `/config`，選 **Output style** → **ADHD STE100 ELI5**。兩種做法都會把選擇存進 `.claude/settings.local.json`。

v2.1.251 起，中途切換會從下一則訊息開始生效：Claude Code 把 style 附在之後的訊息上。不過對話裡前面的回覆還是舊的語氣，模型容易跟著舊的走。切完執行 `/clear` 或開新的 session，style 才會完整生效。

> `/output-style` 在 v2.1.73 標為棄用、v2.1.91 移除，v2.1.269 又加回來。中間那幾版請用 `/config`。

不想用指令或選單的話，直接寫進 `.claude/settings.local.json`：

```json
{
  "outputStyle": "adhd-ste100-eli5:ADHD STE100 ELI5"
}
```

`adhd-ste100-eli5:` 這個前綴是 plugin 命名空間，設定和指令都**必須加** —— 在 v2.1.229 和 v2.1.291 都實測過，style 來自 plugin 時裸名 `ADHD STE100 ELI5` 解析不到。裸名只在檔案直接放進 `.claude/output-styles/` 時有效。

## 作用範圍

output style **只作用於主對話**。subagent 有自己的 system prompt，所以這個 style 不會改變 subagent 的回覆方式。唯一例外是 fork，因為它繼承 parent 的完整 system prompt。

這個 style 設了 `keep-coding-instructions: true`，所以 Claude Code 內建的軟體工程行為完整保留。**它改的是 Claude 怎麼跟你講話，不是 Claude 怎麼寫程式。**

## 自己調

Fork 之後改 `output-styles/adhd-ste100-eli5.md`，然後直接載入你的版本，不用先推上 GitHub：

```
claude --plugin-dir <你 fork 的路徑>
```

headless（`-p`）執行時要明確指定 style：

```
claude -p "..." --plugin-dir <路徑> \
  --settings '{"outputStyle":"adhd-ste100-eli5:ADHD STE100 ELI5"}'
```

常見的調整：

- 覺得 20 字太緊就放寬句長上限。
- 覺得時間估計是雜訊就拿掉第 1 層第 5 條。
- 常看長清單就把 5 條上限往上調。

## 致謝

第 1 層（訊息架構）改編自
**[ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd)**（MIT），該專案本身鬆散參考了 J. Russell Ramsay 與 Anthony L. Rostain 的 *The Adult ADHD Tool Kit*。

第 2 層（句子力學）改編自
**[danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill)**（MIT）。

第 3 層（用詞語域）改編自 **[Lydia Hallie](https://x.com/lydiahallie)** 在
[X 上分享](https://x.com/lydiahallie/status/2080378470111256907)的 `ELI5` output style。

三層模型與三條裁決規則是本專案自己的。

## 授權

MIT。第三方授權聲明見 [LICENSE](LICENSE)。

與 ASD 無隸屬關係，未獲其背書。這不是醫療或診斷工具 —— 它只處理文字輸出，僅此而已。
