專案結構
my-agent/
├── main.py                       # CLI 入口
├── requirements.txt
├── .env.example
└── src/
    ├── core/
    │   ├── config.py             # 環境設定 (model, memory_path, plugins_enabled...)
    │   ├── memory.py             # 持久化記憶系統 (JSON 儲存)
    │   ├── agent.py              # ReAct 推理循環 (Reason → Act → Observe)
    │   └── planner.py            # 任務規劃器 (LLM 分解目標為子任務)
    ├── tools/
    │   ├── __init__.py           # ToolRegistry + BaseTool 基底類別
    │   ├── web_search.py         # DuckDuckGo 搜尋
    │   ├── web_fetch.py          # 網頁內容擷取
    │   ├── file_ops.py           # 檔案讀/寫/列表
    │   └── code_exec.py          # Python 程式碼執行 (沙箱)
    ├── scheduler/
    │   └── scheduler.py          # Cron 排程器 (背景執行緒)
    └── plugins/
        ├── __init__.py           # Plugin 自動發現/載入
        └── example.py            # 範例 Plugin (註冊 greet 工具)
使用方式
# 單次查詢（自動使用工具）
python main.py "2024 年諾貝爾獎得主有哪些？"

# 互動模式（支援對話記憶）
python main.py -i

# 任務規劃模式（自動分解複雜任務）
python main.py --plan "分析台灣半導體產業現況並寫成報告"

# 排程器模式（背景執行定時任務）
python main.py --scheduler

# 管理對話
python main.py --list-convs
python main.py --conv conv_123 --conv-clear
升級重點對比
功能	改造前	改造後
工具調用	字串解析 SEARCH:	OpenAI Function Calling
推理能力	單次查詢	ReAct 循環 (Reason→Act→Observe)
任務處理	一次性問答	Planner 自動分解複雜目標
記憶	無	JSON 持久化 + 對話歷史
自動化	無	Cron 排程背景執行
擴充性	修改原始碼	Plugin 機制動態載入
