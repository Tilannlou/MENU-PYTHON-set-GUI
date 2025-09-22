# 🖥️ MENU002 GUI 指令系統

## 📖 快速導航
- [🏁 快速開始](#1️⃣-指令最範例簡單語法)
- [🌳 指令總覽 TREE](#2️⃣-指令總覽-tree)
- [📚 詳細文法參考](#-指令文法參考詳細說明)
- [🎯 系統特性](#-系統特性)
- [📁 架構說明](#-項目結構與架構演進)
- [🧚 終極願景](#-終極願景---ai桌面小精靈助理)

一個**領域特定語言 (DSL)**，專門為GUI應用開發設計的程式語言。讓你用純文字指令快速創建桌面應用程式，隱藏Tkinter複雜性，提供直觀的聲明式語法。

## 1️⃣ 指令最範例（簡單語法）

```menu
menu clear
menu window main 600 400 "My App"
menu style button bg="#3498db" color="#fff" font="Arial,12,bold"
menu control label title text="Welcome!" x=50 y=30 w=400 h=40 class=header
menu control button btnOK text="OK" x=250 y=150 w=120 h=35 class=button
menu grid-setup rows=4 cols=2 row_weight="1,1,1,1" col_weight="1,1"
menu layout-grid rows=4 cols=2
menu binding btnOK click "title.text = 'Clicked!'"
menu api-set demo "https://api.example.com"
menu api-call btnOK demo GET "/status" -> title.text
menu popup-window popupA "Settings" size="400x300" offset_x=100 offset_y=100
menu popup-content popupA "control label msg text='Hello'" "control button close text='Close'"
menu popup-send-data popupA "Done!" -> main.title.text
menu show
```

## 2️⃣ 指令總覽 TREE

```
📋 MENU002 指令系統
├── 🎯 核心指令
│   ├── clear           # 初始化系統
│   ├── window          # 建立主視窗
│   ├── style           # 定義UI樣式
│   └── show            # 顯示GUI界面
├── 🏗️ UI建構指令
│   ├── control         # 建立控件 (label/button/entry)
│   ├── workspace       # 建立工作區容器
│   └── workspace-add   # 在工作區中添加控件
├── 📐 佈局指令
│   ├── grid-setup      # 設定網格佈局
│   ├── layout-grid     # 啟用網格佈局
│   ├── relative        # 相對定位
│   └── grid-pos        # 網格定位
├── 🔗 互動指令
│   ├── binding         # 事件綁定
│   ├── exec            # 執行命令
│   └── emoji-picker    # 表情符號選擇器
├── 🌐 API指令
│   ├── api-set         # 設定API配置
│   └── api-call        # 執行API請求
├── 🪟 窗口管理指令
│   ├── popup-window    # 建立彈出窗口
│   ├── popup-content   # 設定彈出內容
│   ├── popup-send-data # 傳送數據
│   ├── popup-close     # 關閉彈出窗口
│   └── popup-list      # 列出彈出窗口
├── 🎛️ 視窗控制指令
│   ├── window-maximize # 最大化窗口
│   ├── window-minimize # 最小化窗口
│   ├── window-hide     # 隱藏窗口
│   └── window-show     # 顯示窗口
├── 😀 表情符號指令
│   ├── emoji-show      # 顯示表情符號
│   └── emoji-set       # 設定表情符號
├── 🔍 查詢指令
│   ├── get             # 統一狀態查詢
│   └── show_window_info # 窗口信息查詢
└── 💬 工具指令
    ├── show_message    # 顯示訊息
    ├── display-area    # 建立顯示區域
    ├── display-content # 更新顯示內容
    └── clear-display   # 清除顯示內容
```

## 2️⃣ 指令解說（中文氣分類）

| 指令分類 | 代表指令 | 語氣類型 | 功能說明 |
|------|----------|----------|
| clear | 重置語氣 | 清除所有控制項和樣式，初始化鷹架 |
| window | 建立語氣 | 建立主視窗，設定尺寸與標題 |
| style | 定義語氣 | 定義風格類別，提供控制項套用用途 |
| control | 建立語氣 | 建立UI控制項（Label, Button, Entry） |
| grid-setup | 佈局語氣 | 設定回應方式架構佈局的行列與權重 |
| layout-grid | 佈局語氣 | 實現網格佈局模式 |
| binding | 綁定語氣 | 綁定控制項事件與表達式更新 |
| api-set | 設定語氣 | 設定API資源與權限 |
| api-call | 請求語氣 | 綁定按鈕事件執行API並更新控件 |
| popup-window | 建立語氣 | 建立彈出視窗並定位 |
| popup-content | 表現語氣 | 輸入 GUI 指令至 popup 視窗 |
| popup-send-data | 傳送語氣 | 將資料從彈出視窗傳至主視窗控件 |
| popup-close | 結束語氣 | 關閉指定彈出視窗 |
| popup-list | 查詢語氣 | 列出所有彈出視窗並顯示狀態 |
| window-maximize | 擴展語氣 | 最大化指定窗視 |
| window-minimize | 收縮語氣 | 最小化指定視窗 |
| window-hide | 隱藏語氣 | 隱藏指定窗視 |
| window-show | 顯示語氣 | 顯示指定視窗 |
| workspace | 建立語氣 | 創建工作區（有邊框的容器區域） |
| workspace-add | 建立語氣 | 在工作區中添加控件 |
| emoji-picker | 建立語氣 | 創建表情符號選擇器 |
| emoji-show | 顯示語氣 | 顯示選擇的表情符號 |
| emoji-set | 設定語氣 | 直接設置表情符號到目標控件 |
| get | 查詢語氣 | 統一的狀態查詢指令，取得各種組件信息 |
| show_window_info | 查詢語氣 | 顯示當前窗口資訊 |
| show_message | 通知語氣 | 顯示訊息對話框 |
| show | 顯示語氣 | 顯示所有已建立的GUI元件 |

## 3️⃣ 鷹架設計哲學（文法原則）

所有指令使用中文動作詞，避免中英文混用造成文法錯誤
中文文法分類僅用於註解與檔案說明，不可混入指令本體
語法結構遵循：`menu {command} [參數...]`

## 🧩 指令文法 + 中文氣註解

```menu
menu clear
# menu {清除} → 重置 scaffold，清空所有控件與樣式

menu window main 600 400 "My App"
# menu {開啟視窗} → 建立主視窗，視窗名=main，尺寸=600x400，標題="My App"

menu style button bg="#3498db" color="#ffffff" font="Arial,12,bold"
# menu {定義樣式} → 為 button 類型控件設定背景色、文字色與字型

menu control label title text="歡迎使用" x=50 y=30 w=400 h=40 class=header
# menu {建立控件} → 建立標籤控件，位置與尺寸指定，套用 header 樣式

menu control button btnOK text="確定" x=250 y=150 w=120 h=35 class=button
# menu {建立控件} → 建立按鈕控件，位置與尺寸指定，套用 button 樣式

menu grid-setup rows=4 cols=2 row_weight="1,1,1,1" col_weight="1,1"
# menu {佈局設定} → 設定網格佈局行列數與權重，支援響應式調整

menu layout-grid rows=4 cols=2
# menu {啟用佈局} → 啟用網格佈局，指定行列數

menu binding btnOK click "title.text = '已點擊'"
# menu {事件綁定} → 綁定 btnOK 的點擊事件，更新 title 控件的文字

menu api-set demo "https://api.example.com"
# menu {API設定} → 設定名為 demo 的 API 基礎網址

menu api-call btnOK demo GET "/status" -> title.text
# menu {API呼叫} → 綁定 btnOK 點擊事件，呼叫 demo API 並將結果寫入 title.text

menu popup-window popupA "設定視窗" size="400x300" offset_x=100 offset_y=100
# menu {建立彈窗} → 建立名為 popupA 的彈出視窗，指定尺寸與偏移位置

menu popup-content popupA "control label msg text='Hello'" "control button close text='關閉'"
# menu {彈窗內容} → 為 popupA 注入控件指令，建立標籤與按鈕

menu popup-send-data popupA "完成" -> main.title.text
# menu {彈窗傳送} → 將 popupA 的資料傳送至主視窗控件 title.text

menu popup-close popupA
# menu {關閉彈窗} → 關閉 popupA 視窗

menu popup-list
# menu {列出彈窗} → 顯示所有已建立的 popup 視窗狀態

menu window-maximize main
# menu {最大化視窗} → 將主視窗最大化

menu window-hide popupA
# menu {隱藏視窗} → 隱藏 popupA 視窗

menu workspace work_area 50 70 350 400 bg="#f8f8f8"
# menu {建立工作區} → 創建帶邊框的工作區容器，指定位置尺寸與背景色

menu workspace-add work_area button btn1 text="按鈕" x=10 y=50 w=80 h=30
# menu {工作區添加} → 在工作區中添加按鈕控件

menu show
# menu {顯示介面} → 顯示所有已建立的 GUI 元件
```

## 🧩 進階功能指令展示（含語法註解）

### 視窗管理指令
```menu
menu window-maximize main
# menu {最大化視窗} → 將主視窗最大化顯示

menu window-minimize main
# menu {最小化視窗} → 將主視窗縮至任務列

menu window-hide popupA
# menu {隱藏視窗} → 暫時隱藏 popupA 視窗，不銷毀

menu window-show popupA
# menu {顯示視窗} → 顯示 popupA 視窗（若先前被隱藏）
```

### Popup 管理指令
```menu
menu popup-close popupA
# menu {關閉彈窗} → 關閉 popupA 視窗並移除記憶體引用

menu popup-list
# menu {列出彈窗} → 顯示目前所有已建立的 popup 視窗與狀態

menu popup-send-data popupA "完成" -> main.statusLabel.text
# menu {彈窗傳送} → 將 popupA 的資料傳送至主視窗控件 statusLabel.text
```

### 佈局與定位指令
```menu
menu relative title relx=0.1 rely=0.1 relwidth=0.8 relheight=0.2 anchor="nw"
# menu {相對定位} → 將控件 title 以相對比例定位於主視窗

menu grid-pos btnOK row=2 col=1 rowspan=1 colspan=2 sticky="nsew"
# menu {網格定位} → 將控件 btnOK 放置於網格位置，支援黏附方向
```

### 資料處理指令
```menu
menu process json-filter dataSource "status == 'active'" -> filteredData
# menu {資料處理} → 對 dataSource 執行 JSON 過濾，結果存入 filteredData

menu output "Hello World" "/output/log.txt" encoding=utf8
# menu {資料輸出} → 將文字寫入指定檔案，使用 UTF-8 編碼

menu output-console "Log message" level=INFO
# menu {控制台輸出} → 將訊息輸出至控制台，指定日誌等級
```

### 系統整合指令
```menu
menu exec btnRun "echo Hello"
# menu {命令執行} → 綁定 btnRun 點擊事件，執行 shell 命令

menu status "載入完成" type=success duration=3000
# menu {狀態提示} → 顯示成功訊息，持續 3 秒（規劃中）

menu theme dark
# menu {主題切換} → 套用 dark 主題樣式（規劃中）

menu plugin-load "custom-layout"
# menu {載入插件} → 載入名為 custom-layout 的外部插件模組（規劃中）
```

### 🎨 視覺效果與動畫（規劃中）
```menu
menu animate title fadeIn duration=300
# menu {動畫效果} → 對控件 title 套用淡入動畫，持續 300 毫秒（規劃中）

menu delay 500ms then "statusLabel.text = '完成'"
# menu {延遲執行} → 延遲 500 毫秒後執行指定語句（規劃中）

menu particle-effect title type=sparkle
# menu {粒子效果} → 為控件添加粒子動畫效果（規劃中）

menu get window position size title
# menu {取得} → 統一的狀態查詢指令，取得窗口的位置、尺寸和標題

menu get control:btnOK text position size font color
# menu {取得} → 取得指定控件的文字、位置、尺寸、字體和顏色信息

menu get workspace:workArea position size color
# menu {取得} → 取得工作區的位置、尺寸和背景色信息

menu get system time controls memory version
# menu {取得} → 取得系統的時間、控件數量、記憶體使用和版本信息
```

## 📚 指令文法參考（詳細說明）

### 1. `menu control` - 建立控件
```menu
menu control label title text="歡迎使用" x=50 y=30 w=400 h=40 class=header
# menu {建立控件} → 建立標籤控件，位置與尺寸指定，套用 header 樣式
```

| 參數 | 說明 | 範例 |
|------|------|------|
| `label/button/entry` | 控制項類型 | `button` |
| `控件名稱` | 唯一識別名稱 | `title` |
| `text="文字"` | 顯示文字 | `text="按鈕"` |
| `x,y` | 絕對座標位置 | `x=50 y=30` |
| `w,h` | 控制寬高 | `w=100 h=30` |
| `class="樣式名"` | 套用風格類別 | `class=header` |
| `placeholder="提示"` | 輸入框預設文字 | `placeholder="請輸入"` |

### 2. `menu grid-pos` - 網格定位
```menu
menu grid-pos btnOK row=2 col=1 rowspan=1 colspan=2 sticky="nsew"
# menu {網格定位} → 將控件 btnOK 放置於網格位置，支援黏附方向
```

| 參數 | 說明 | 範例 |
|------|------|------|
| `row,col` | 控件所在的行列位置 | `row=2 col=1` |
| `rowspan,colspan` | 控件覆蓋的行列數 | `rowspan=1 colspan=2` |
| `sticky` | 控制貼附方向 | `sticky="nsew"` |

### 3. `menu api-call` - API呼叫
```menu
menu api-call btnOK demo POST "/submit" "{'name': '{entryName}', 'email': '{entryEmail}'}" -> resultLabel.text
# menu {API呼叫} → 綁定 btnOK 點擊事件，送出資料並更新 resultLabel.text
```

| 參數 | 說明 | 範例 |
|------|------|------|
| `按鈕名稱` | 綁定的按鈕 | `btnOK` |
| `API名稱` | 由 api-set 設定 | `demo` |
| `HTTP方法` | GET/POST/PUT/DELETE | `POST` |
| `API路徑` | 請求路徑 | `"/submit"` |
| `資料模板` | 支援 {控件名} 變數 | `"{'name': '{entryName}'}"` |
| `-> 目標` | 結果寫入位置 | `-> resultLabel.text` |

### 4. `menu popup-window` - 建立彈窗
```menu
menu popup-window popupA "設定視窗" size="400x300" offset_x=100 offset_y=100
# menu {建立彈窗} → 建立名為 popupA 的彈出視窗，指定尺寸與偏移位置
```

| 參數 | 說明 | 範例 |
|------|------|------|
| `視窗ID` | 唯一識別名稱 | `popupA` |
| `標題` | 視窗標題文字 | `"設定視窗"` |
| `size` | 視窗尺寸 (寬x高) | `size="400x300"` |
| `offset_x,offset_y` | 相對主視窗偏移 | `offset_x=100 offset_y=100` |

### 5. `menu style` - 定義樣式
```menu
menu style button bg="#3498db" color="#ffffff" font="Arial,12,bold"
# menu {定義樣式} → 為 button 類型控件設定背景色、文字色與字型
```

| 屬性 | 說明 | 範例 |
|------|------|------|
| `bg` | 背景顏色 (HEX) | `bg="#3498db"` |
| `color` | 文字顏色 (HEX) | `color="#ffffff"` |
| `font` | 字型設定 | `font="Arial,12,bold"` |

### 6. `menu get` - 統一狀態查詢
```menu
menu get window position size title
# menu {取得} → 取得窗口的位置、尺寸和標題信息

menu get control:btnOK text position size font color type
# menu {取得} → 取得指定控件的多項屬性信息

menu get workspace:workArea position size color
# menu {取得} → 取得工作區的狀態信息

menu get system time controls workspaces memory version
# menu {取得} → 取得系統級別的信息
```

| 目標對象 | 可用屬性 | 說明 |
|----------|----------|------|
| `window[:name]` | position, size, title, visible, state | 窗口信息 |
| `control:name` | text, position, size, font, color, type, state | 控件屬性 |
| `workspace:name` | position, size, color | 工作區狀態 |
| `popup:name` | position, size, title, visible, state | 彈出窗口信息 |
| `emoji[:name]` | selected, count, available, status | 表情符號狀態 |
| `system` | time, controls, workspaces, popups, memory, version | 系統信息 |

## 📋 文法分類總表

| 分類 | 語氣類型 | 代表指令 | 功能說明 | 實現狀態 |
|------|----------|----------|----------|----------|
| **建立語氣** | 創建新元素 | `window`, `control`, `popup-window`, `workspace` | 建立視窗、控件等UI元素 | ✅ 已實現 |
| **定義語氣** | 設定屬性 | `style`, `api-set` | 定義樣式、配置等屬性 | ✅ 已實現 |
| **佈局語氣** | 排列元素 | `grid-setup`, `relative`, `grid-pos` | 控制元素位置與佈局 | ✅ 已實現 |
| **綁定語氣** | 事件處理 | `binding`, `api-call`, `exec` | 設定事件響應與互動 | ✅ 已實現 |
| **請求語氣** | 數據操作 | `api-call` | 處理數據請求 | ✅ 已實現 |
| **表現語氣** | 視覺效果 | `show` | 控制視覺表現 | ✅ 已實現 |
| **傳送語氣** | 數據傳遞 | `popup-send-data` | 在組件間傳遞數據 | ✅ 已實現 |
| **結束語氣** | 清理資源 | `popup-close`, `clear` | 關閉和清理資源 | ✅ 已實現 |
| **查詢語氣** | 獲取資訊 | `popup-list`, `debug-info` | 查詢系統狀態與資訊 | ✅ 已實現 |
| **擴展語氣** | 視窗控制 | `window-maximize` | 控制視窗顯示狀態 | ✅ 已實現 |
| **收縮語氣** | 視窗控制 | `window-minimize` | 縮小視窗顯示 | ✅ 已實現 |
| **隱藏語氣** | 視窗控制 | `window-hide` | 隱藏視窗元素 | ✅ 已實現 |
| **顯示語氣** | 視窗控制 | `window-show`, `show` | 顯示視窗元素 | ✅ 已實現 |
||||||
| **🎨 進階效果（規劃中）** | 視覺特效 | `animate`, `delay`, `particle-effect` | 動畫與特效 | 📅 規劃中 |
| **🎭 主題系統（規劃中）** | 介面主題 | `theme` | 主題切換 | 📅 規劃中 |
| **🔌 插件系統（規劃中）** | 擴展功能 | `plugin-load` | 插件載入 | 📅 規劃中 |
| **📊 資料處理（規劃中）** | 數據操作 | `process`, `output` | 進階數據處理 | 📅 規劃中 |

## 💡 使用建議與語法原則

### 📝 語法原則
1. **統一格式**: `menu {command} [參數...]`
2. **中文友好**: 指令名稱使用中文動詞分類
3. **參數靈活**: 支持鍵值對和位置參數混合
4. **變數支援**: 在字串中使用 `{控件名}` 插入變數
5. **錯誤包容**: 單個指令錯誤不影響整體執行

### 🎯 使用建議
1. **按順序執行**: 先建立視窗，再建立控件，最後綁定事件
2. **命名規範**: 使用有意義的英文名稱，方便識別
3. **樣式先行**: 先定義 `style`，再在控件中引用
4. **測試為先**: 使用 `output-console` 指令除錯
5. **模組化**: 將複雜佈局拆分為多個 `.menu` 文件

### 🚨 錯誤排查與文法提示

#### 常見錯誤
- **缺少引號**: `text=hello` → `text="hello"`
- **參數順序**: `menu control button btnOK text="OK"` (正確)
- **變數語法**: `"{btnName}"` 而非 `{btnName}`
- **路徑分隔**: 使用 `/` 而非 `\` 在路徑中

#### 除錯技巧
```menu
# 輸出除錯訊息
menu output-console "控件已建立: {controlName}" level=DEBUG

# 檢查API連接
menu api-call testBtn apiName GET "/test" -> debugLabel.text

# 顯示視窗資訊
menu binding infoBtn click "show_window_info"
```

## 🚀 快速開始

### 運行特定演示
```bash
# 運行基礎演示
python main.py demo.menu

# 測試工作區功能
python main.py workspace_demo.menu

# 測試自適應佈局
python main.py responsive_title_demo.menu
python main.py responsive_workspaces_demo.menu

# 測試取得指令功能
python main.py get_demo.menu
```

### 開發調試
```bash
# 詳細日誌模式
python main.py -l DEBUG demo.menu

# 自定義配置
python main.py --config config/default_config.json demo.menu
```

## 🎯 系統特性

- ✅ **純Tkinter實現** - 無外部依賴，輕量化
- ✅ **自適應佈局** - 窗口大小改變時自動調整元素
- ✅ **模塊化架構** - 9個模塊，代碼組織清晰
- ✅ **完整Popup系統** - 創建、管理、數據傳輸
- ✅ **表情符號支持** - 內建表情符號選擇器
- ✅ **多語言就緒** - 完整的語言管理系統
- ✅ **API集成** - 模擬API功能，支援真實HTTP請求

## 📁 項目結構與架構演進

**📖 詳細架構說明**: 請參考 [`ARCHITECTURE.md`](ARCHITECTURE.md) 獲取完整的系統架構圖、模組依賴關係和工作流程說明。

### 當前架構 (v2.1.0)
```
e:/MENU-TEST/
├── core/                 # 核心模塊 (6個)
│   ├── command_handlers.py # 指令處理器 (1456行)
│   ├── menu_app.py       # 主應用類
│   └── ui_components.py  # UI組件
├── utils/                # 工具函數 (4個)
├── config/               # 配置管理
├── examples/             # 演示文件 (7個)
├── main.py               # 主入口
└── *.menu               # 腳本文件 (10個)
```

### 未來架構 (v3.0.0) - AI與動畫擴展
```
e:/MENU-TEST/
├── ai/                   # AI模組 (新)
│   ├── model.py         # 小型AI模型
│   ├── rag.py           # RAG檢索系統
│   └── dialogue.py      # 對話引擎
├── animation/           # 動畫模組 (新)
│   ├── sprite.py        # 精靈動畫系統
│   ├── behavior.py      # 行為邏輯
│   └── effects.py       # 視覺效果
├── audio/               # 音頻模組 (新)
│   ├── speech.py        # 語音合成
│   ├── recognition.py   # 語音識別
│   └── audio.py         # 音頻處理
├── knowledge/           # 知識模組 (新)
│   ├── library.py       # 知識庫管理
│   ├── search.py        # 檢索增強
│   └── storage.py       # 數據持久化
├── core/                # 核心模塊 (優化)
├── utils/               # 工具函數 (擴展)
├── config/              # 配置管理 (增強)
└── examples/            # 演示文件 (更多)
```

**架構原則**: 功能擴展 ≠ 代碼混亂，我們會及時重構保持清潔架構！

## 🎯 適用場景

- 快速原型製作
- 桌面工具開發
- 表單應用程式
- 數據視覺化界面
- API 測試工具
- 教學演示程式

## 🧚 終極願景 - AI桌面小精靈助理

MENU002 的終極目標是實現一個**AI驅動的動畫化桌面小精靈助理**，整合小型AI模型和RAG知識庫，成為真正懂"人話"的智能桌面夥伴：

### 🤖 AI核心能力
- 🧠 **小型AI模型**: 整合輕量級AI，懂自然語言對話
- 📚 **RAG圖書館**: 知識檢索增強系統，提供準確資訊
- ❓ **智能查詢**: 遇到未知資訊時自動查詢RAG，而非亂答
- 💬 **自然對話**: 理解"人話"，提供友好的互動體驗

### 🎭 動畫與互動
- 🏃‍♂️ **智能移動**: 在GUI中自由移動，跑到需要幫助的地方
- 🔊 **語音互動**: 溫暖的語音播報，配合視覺指引
- 💭 **泡泡對話**: 顯示AI生成的對話和實時提示
- 😠 **行為互動**: 視窗縮小時可愛抗議，"抱走"GUI的趣味行為
- 🎭 **豐富表情**: 根據AI情緒和對話內容顯示表情
- 👆 **點擊互動**: 點擊精靈啟動AI對話或功能

### ⚡ 技術優化（對比Clippy）
- 🚀 **輕量化**: 小型AI模型，不消耗大量資源
- 🎯 **實用AI**: 真正的幫助，而非死板的說明
- 🔄 **動態學習**: 通過RAG持續更新知識
- 🛡️ **安全可控**: 助手活動範圍限制在GUI內

這將把 MENU002 從靜態GUI腳本語言，進化為一個**AI驅動的智能桌面助手**，遠超Clippy的水平！

現在就開始用 MENU002 創建你的第一個 GUI 應用吧！🎉