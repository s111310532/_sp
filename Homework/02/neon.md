1. 語言願景與目標：Neon
Neon 是一個旨在兼具「極簡語法」與「強型態安全」的表達式導向（Expression-based）語言。

*型態系統：強型態 (Strongly Typed)，不允許隱式轉型（例如字串不能直接加數字）。現階段支援 Int（整數）與 Bool（布爾值）。

*執行模式：解譯執行 (Interpreted)。我們會直接走訪抽象語法樹 (AST) 來執行程式。

*記憶體管理：由於依賴 Python 執行期，間接使用 Python 的垃圾蒐集機制 (GC)。

*核心特色：所有東西都是表達式（包括 if），都有回傳值。

2. Neon 程式範例
以下是一段計算階乘（Factorial）的 Neon 程式碼範例：

let n: Int = 5;
let result: Int = 1;

while n > 0 {
    result = result * n;
    n = n - 1;
};

print result;

3. BNF 語法設計
我們使用類似 BNF 的語法來定義 Neon 的結構：

Program    ::= Statement*

Statement  ::= LetStmt | AssignStmt | WhileStmt | PrintStmt
LetStmt    ::= "let" Identifier ":" Type "=" Expression ";"
AssignStmt ::= Identifier "=" Expression ";"
WhileStmt  ::= "while" Expression "{" Program "}" ";"
PrintStmt  ::= "print" Expression ";"

Type       ::= "Int" | "Bool"

Expression ::= Equality
Equality   ::= Relational ( ("==" | "!=") Relational )*
Relational ::= Additive ( ("<" | ">") Additive )*
Additive   ::= Multiplicative ( ("+" | "-") Multiplicative )*
Multiplicative ::= Primary ( ("*" | "/") Primary )*
Primary    ::= Integer | Boolean | Identifier | "(" Expression ")"

4. 實作專案 (Python)
整個解譯器分為三個核心階段：掃描器 (Lexer)、解析器 (Parser)、與執行器 (Interpreter)。

5. 如何運行它？
1.確保你安裝了 Python 3。

2.將上面的程式碼儲存為 neon.py。

3.在終端機執行：

python neon.py

預期輸出結果：

--- 開始執行 Neon 程式 ---
120
--- 執行結束 ---

驗證強型態機制：
如果你嘗試修改 neon_code 內的程式，例如寫成：

let n: Int = true;

執行後解譯器就會當場彈出錯誤：Exception: 型態錯誤: 宣告為 Int 但初始值為 Bool，證明了我們的強型態檢查機制運作正常！


