[English](README.md) | 繁體中文

# adhd-ste100-eli5

一個 Claude Code **output style**，讓回答變得好讀、也好動手。

不只是變短，是**重新排過** —— 答案排在螢幕第一行、每一句只帶一個指令、不用任何需要你停下來解碼的詞。

不需要診斷證明。單純今天腦子不夠用也算。

## 差別長這樣

**改造前**

> 這是個好問題！讓我先看一下你的驗證流程。從 `src/auth.ts` 的程式碼看起來，token 驗證的邏輯似乎是用比較舊版的 jsonwebtoken API 實作的，而那個 API 在第 9 版就已經被棄用了。一個可能可行的做法是更新套件，然後把那個函式重構一下。改完之後，應該要跑一下 auth 的測試，確認沒有東西被弄壞。另外順帶一提，你或許也可以找個時間整體檢視一下你的相依套件版本。希望這有幫助！如果想再深入討論再跟我說。

**改造後**

> 執行 `npm install jsonwebtoken@latest`。
>
> 1. 打開 `src/auth.ts`
> 2. 把 `verifyToken`（第 42 到 58 行）換成下面這段
> 3. 執行 `npm test -- auth.spec.ts`
>
> 大約 10 分鐘。舊 API 在 jsonwebtoken 9 就停止運作了。新 API 會回傳 promise，所以 `verifyToken` 要改成 async。
>
> 略過：整體相依套件盤點。想做的話跟我說。
>
> 下一步：跑第 1 步。有測試失敗就把第一行錯誤貼給我。

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

裝好 plugin **不等於**啟用這個 style，要自己選：

```
/config
```

選 **Output style** → **ADHD STE100 ELI5**。

然後執行 `/clear` 或開新的 session。output style 是 system prompt 的一部分，Claude Code 只在 session 開始時讀一次，所以中途切換不會生效。

> `/output-style` 這個獨立指令在 Claude Code v2.1.73 標為棄用、v2.1.91 已移除。請用 `/config`。

不想用選單的話，直接寫進 `.claude/settings.local.json`：

```json
{
  "outputStyle": "ADHD STE100 ELI5"
}
```

## 作用範圍

output style **只作用於主對話**。subagent 有自己的 system prompt，所以這個 style 不會改變 subagent 的回覆方式。唯一例外是 fork，因為它繼承 parent 的完整 system prompt。

這個 style 設了 `keep-coding-instructions: true`，所以 Claude Code 內建的軟體工程行為完整保留。**它改的是 Claude 怎麼跟你講話，不是 Claude 怎麼寫程式。**

## 自己調

Fork 之後改 `output-styles/adhd-ste100-eli5.md`，然後直接載入你的版本，不用先推上 GitHub：

```
claude --plugin-dir <你 fork 的路徑>
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

第 3 層（用詞語域）源自個人自用的 ELI5 output style。

三層模型與三條裁決規則是本專案自己的。

## 授權

MIT。第三方授權聲明見 [LICENSE](LICENSE)。

與 ASD 無隸屬關係，未獲其背書。這不是醫療或診斷工具 —— 它只處理文字輸出，僅此而已。
