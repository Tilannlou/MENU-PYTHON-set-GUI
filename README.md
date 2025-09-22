# MENU-PYTHON-set-GUI
利用python語言製作一個新指令>>>MENU&lt;&lt;&lt;可以用普通文件在WINDOS建立一個視窗
## 1️⃣ 指令用法範例（簡短語法）

```bash
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

---

## 2️⃣ 指令解說（中文語氣分類）

| 指令 | 語氣分類 | 中文解釋 |
|------|----------|-----------|
| `clear` | 重置語氣 | 清除所有控件與樣式，初始化 scaffold |
| `window` | 建立語氣 | 建立主視窗，設定尺寸與標題 |
| `style` | 定義語氣 | 定義樣式類別，供控件套用 |
| `control` | 建立語氣 | 建立 UI 控件（Label, Button, Entry） |
| `grid-setup` | 佈局語氣 | 設定響應式網格佈局的行列與權重 |
| `layout-grid` | 佈局語氣 | 啟用網格佈局模式 |
| `binding` | 綁定語氣 | 綁定控件事件與表達式更新 |
| `api-set` | 設定語氣 | 設定 API 資源與憑證 |
| `api-call` | 請求語氣 | 綁定按鈕事件執行 API 並更新控件 |
| `popup-window` | 建立語氣 | 建立彈出視窗並定位 |
| `popup-content` | 呈現語氣 | 注入 GUI 指令至 popup 視窗 |
| `popup-send-data` | 傳送語氣 | 將資料從 popup 傳至主視窗控件 |
| `popup-close` | 結束語氣 | 關閉指定 popup 視窗 |
| `popup-list` | 查詢語氣 | 列出所有 popup 視窗並顯示狀態 |
| `window-maximize` | 擴展語氣 | 最大化指定視窗 |
| `window-minimize` | 收縮語氣 | 最小化指定視窗 |
| `window-hide` | 隱藏語氣 | 隱藏指定視窗 |
| `window-show` | 顯示語氣 | 顯示指定視窗 |

---

## 3️⃣ scaffold 設計哲學（語法原則）

- 所有指令皆使用英文動作詞，避免中英混用造成語法錯誤
- 中文語法分類僅用於註解與文件說明，不可混入指令本體
- 語法結構遵循：`menu {command} [參數...]`

---
## 🧩 指令語法 + 中文語氣註解

```bash
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

menu show
# menu {顯示介面} → 顯示所有已建立的 GUI 元件
```

---

## 📌 使用建議

- 所有指令必須使用英文動作詞（如 `window`, `control`, `api-call`），不可混用中文語氣詞。
- 中文語氣註解僅用於說明用途與語氣分類，請勿混入 `.menu` 文件中。
- 建議每條指令都附上語法註解

---
## 🧩 進階功能指令展示（含語法註解）

```bash
menu window-maximize main
# menu {最大化視窗} → 將主視窗最大化顯示

menu window-minimize main
# menu {最小化視窗} → 將主視窗縮至任務列

menu window-hide popupA
# menu {隱藏視窗} → 暫時隱藏 popupA 視窗，不銷毀

menu window-show popupA
# menu {顯示視窗} → 顯示 popupA 視窗（若先前被隱藏）

menu popup-close popupA
# menu {關閉彈窗} → 關閉 popupA 視窗並移除記憶體引用

menu popup-list
# menu {列出彈窗} → 顯示目前所有已建立的 popup 視窗與狀態

menu popup-send-data popupA "完成" -> main.statusLabel.text
# menu {彈窗傳送} → 將 popupA 的資料傳送至主視窗控件 statusLabel.text

menu relative title relx=0.1 rely=0.1 relwidth=0.8 relheight=0.2 anchor="nw"
# menu {相對定位} → 將控件 title 以相對比例定位於主視窗

menu grid-pos btnOK row=2 col=1 rowspan=1 colspan=2 sticky="nsew"
# menu {網格定位} → 將控件 btnOK 放置於網格位置，支援黏附方向

menu process json-filter dataSource "status == 'active'" -> filteredData
# menu {資料處理} → 對 dataSource 執行 JSON 過濾，結果存入 filteredData

menu output "Hello World" "/output/log.txt" encoding=utf8
# menu {資料輸出} → 將文字寫入指定檔案，使用 UTF-8 編碼

menu output-console "Log message" level=INFO
# menu {控制台輸出} → 將訊息輸出至控制台，指定日誌等級

menu delay 500ms then "statusLabel.text = '完成'"
# menu {延遲執行} → 延遲 500 毫秒後執行指定語句

menu animate title fadeIn duration=300
# menu {動畫效果} → 對控件 title 套用淡入動畫，持續 300 毫秒

menu exec btnRun "echo Hello"
# menu {命令執行} → 綁定 btnRun 點擊事件，執行 shell 命令

menu status "載入完成" type=success duration=3000
# menu {狀態提示} → 顯示成功訊息，持續 3 秒

menu theme dark
# menu {主題切換} → 套用 dark 主題樣式（需支援）

menu plugin-load "custom-layout"
# menu {載入插件} → 載入名為 custom-layout 的外部插件模組
```

---

## 🧩 詳細語法與語法註解（進階指令）

### 1. `menu control`

```bash
menu control label title text="歡迎使用" x=50 y=30 w=400 h=40 class=header
# menu {建立控件} → 建立標籤控件，位置與尺寸指定，套用 header 樣式
```

| 參數 | 說明 |
|------|------|
| `label` / `button` / `entry` | 控件類型 |
| `title` | 控件名稱（唯一識別） |
| `text` | 顯示文字 |
| `x`, `y` | 絕對座標位置 |
| `w`, `h` | 控件寬高 |
| `class` | 套用樣式類別（由 `menu style` 定義） |
| `placeholder` | 文字輸入框預設文字（限 `entry` 類型） |

---

### 2. `menu grid-pos`

```bash
menu grid-pos btnOK row=2 col=1 rowspan=1 colspan=2 sticky="nsew"
# menu {網格定位} → 將控件 btnOK 放置於網格位置，支援黏附方向
```

| 參數 | 說明 |
|------|------|
| `row`, `col` | 控件所在的行列位置 |
| `rowspan`, `colspan` | 控件跨越的行列數 |
| `sticky` | 控件黏附方向（n=上, s=下, e=右, w=左，可組合） |

---

### 3. `menu api-call`

```bash
menu api-call btnOK demo POST "/submit" "{'name': '{entryName}', 'email': '{entryEmail}'}" -> resultLabel.text
# menu {API呼叫} → 綁定 btnOK 點擊事件，送出資料並更新 resultLabel.text
```

| 參數 | 說明 |
|------|------|
| `btnOK` | 綁定的按鈕控件名稱 |
| `demo` | API 名稱（由 `menu api-set` 設定） |
| `POST` / `GET` / `PUT` / `DELETE` | HTTP 方法 |
| `"/submit"` | API 路徑 |
| `data_template` | 傳送資料模板，支援 `{控件名}` 變數注入 |
| `-> resultLabel.text` | 將回傳結果寫入指定控件屬性（text 或 value） |

---

### 4. `menu popup-window`

```bash
menu popup-window popupA "設定視窗" size="400x300" offset_x=100 offset_y=100
# menu {建立彈窗} → 建立名為 popupA 的彈出視窗，指定尺寸與偏移位置
```

| 參數 | 說明 |
|------|------|
| `popupA` | 視窗 ID（唯一） |
| `"設定視窗"` | 視窗標題 |
| `size="400x300"` | 視窗尺寸（寬x高） |
| `offset_x`, `offset_y` | 相對主視窗的偏移位置 |

---

### 5. `menu style`

```bash
menu style button bg="#3498db" color="#ffffff" font="Arial,12,bold"
# menu {定義樣式} → 為 button 類型控件設定背景色、文字色與字型
```

| 屬性 | 說明 |
|------|------|
| `bg` | 背景色（HEX） |
| `color` | 文字顏色（HEX） |
| `font` | 字型設定（格式："字型,大小,粗體/斜體"） |

---

1. 指令語法與語法註解（基本與進階）
2. 詳細參數說明（針對複雜指令）
3. 語法分類總表
4. 使用建議與語法原則
5. 錯誤排查與語法提示

---
### 📘 MENU002 指令語法與註解（第 1 部分）

```bash
menu clear
# menu {清除} → 重置 scaffold，清空所有控件、樣式與事件綁定

menu window main 600 400 "My App"
# menu {開啟視窗} → 建立主視窗，名稱=main，尺寸=600x400，標題="My App"

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

menu grid-pos btnOK row=2 col=1 rowspan=1 colspan=2 sticky="nsew"
# menu {網格定位} → 將控件 btnOK 放置於網格位置，支援黏附方向

menu relative title relx=0.1 rely=0.1 relwidth=0.8 relheight=0.2 anchor="nw"
# menu {相對定位} → 將控件 title 以相對比例定位於主視窗

menu binding btnOK click "title.text = '已點擊'"
# menu {事件綁定} → 綁定 btnOK 的點擊事件，更新 title 控件的文字

menu delay 500ms then "statusLabel.text = '完成'"
# menu {延遲執行} → 延遲 500 毫秒後執行指定語句

menu animate title fadeIn duration=300
# menu {動畫效果} → 對控件 title 套用淡入動畫，持續 300 毫秒
```

---

## 🧩 指令語法與註解（第 2 部分）

```bash
menu api-set demo "https://api.example.com" key=abc123 username=admin password=xyz show-secret=true
# menu {API設定} → 設定名為 demo 的 API，包含金鑰、帳號、密碼與是否顯示密碼
```

| 參數           | 說明                             |
|----------------|----------------------------------|
| `demo`         | API 名稱                         |
| `"https://..."`| API 基礎網址                     |
| `key`          | Bearer Token 或 API 金鑰         |
| `username`     | 使用者帳號（選填）               |
| `password`     | 使用者密碼（選填）               |
| `show-secret`  | 是否顯示敏感資訊（true/false）   |

---

```bash
menu api-call btnOK demo POST "/submit" "{'name': '{entryName}', 'email': '{entryEmail}'}" -> resultLabel.text
# menu {API呼叫} → 綁定 btnOK 點擊事件，送出資料並更新 resultLabel.text
```

| 參數             | 說明                                       |
|------------------|--------------------------------------------|
| `btnOK`          | 綁定的按鈕控件名稱                         |
| `demo`           | API 名稱（由 api-set 設定）                |
| `POST`           | HTTP 方法（GET, POST, PUT, DELETE）        |
| `"/submit"`      | API 路徑                                   |
| `data_template`  | 傳送資料模板，支援 `{控件名}` 注入         |
| `-> result.text` | 將回傳結果寫入指定控件屬性（text/value）   |

---

```bash
menu popup-window popupA "設定視窗" size="400x300" offset_x=100 offset_y=100
# menu {建立彈窗} → 建立名為 popupA 的彈出視窗，指定尺寸與偏移位置
```

| 參數        | 說明                                     |
|-------------|------------------------------------------|
| `popupA`    | 視窗 ID（唯一）                          |
| `"設定視窗"`| 視窗標題                                 |
| `size`      | 尺寸格式為 `"寬x高"`，如 `"400x300"`     |
| `offset_x`  | 相對主視窗的水平偏移                     |
| `offset_y`  | 相對主視窗的垂直偏移                     |

---

```bash
menu popup-content popupA "control label msg text='Hello'" "control button close text='關閉'"
# menu {彈窗內容} → 為 popupA 注入控件指令，建立標籤與按鈕
```

| 語法片段 | 說明 |
|----------|------|
| `"control label msg text='Hello'"` | 建立標籤控件 msg，顯示文字 |
| `"control button close text='關閉'"` | 建立按鈕控件 close，顯示文字 |

---

```bash
menu popup-send-data popupA "完成" -> main.statusLabel.text
# menu {彈窗傳送} → 將 popupA 的資料傳送至主視窗控件 statusLabel.text
```

| 參數             | 說明                                 |
|------------------|--------------------------------------|
| `popupA`         | 資料來源 popup 視窗 ID               |
| `"完成"`         | 傳送的資料內容                       |
| `-> main.label.text` | 接收目標控件與屬性（text/value） |

---

```bash
menu popup-close popupA
# menu {關閉彈窗} → 關閉 popupA 視窗並移除記憶體引用
```

---

```bash
menu popup-list
# menu {列出彈窗} → 顯示目前所有已建立的 popup 視窗與狀態
```

---

```bash
menu window-maximize main
# menu {最大化視窗} → 將主視窗最大化顯示
```

```bash
menu window-minimize main
# menu {最小化視窗} → 將主視窗縮至任務列
```

```bash
menu window-hide popupA
# menu {隱藏視窗} → 暫時隱藏 popupA 視窗，不銷毀
```

```bash
menu window-show popupA
# menu {顯示視窗} → 顯示 popupA 視窗（若先前被隱藏）
```

---

---

## 📘 MENU002 語法 系統說明書


---

## 🧩 指令語法 + 中文語氣註解（語法即語氣）

```bash
menu clear
# menu {清除} → 重置 scaffold，清空所有控件、樣式與事件綁定

menu window main 600 400 "My App"
# menu {開啟視窗} → 建立主視窗，名稱=main，尺寸=600x400，標題="My App"

menu style button bg="#3498db" color="#ffffff" font="Arial,12,bold"
# menu {定義樣式} → 為 button 類型控件設定背景色、文字色與字型

menu control label title text="歡迎使用" x=50 y=30 w=400 h=40 class=header
# menu {建立控件} → 建立標籤控件，位置與尺寸指定，套用 header 樣式

menu grid-setup rows=4 cols=2 row_weight="1,1,1,1" col_weight="1,1"
# menu {佈局設定} → 設定網格佈局行列數與權重，支援響應式調整

menu binding btnOK click "title.text = '已點擊'"
# menu {事件綁定} → 綁定 btnOK 的點擊事件，更新 title 控件的文字

menu api-call btnOK demo POST "/submit" "{'name': '{entryName}'}" -> resultLabel.text
# menu {API呼叫} → 呼叫 demo API 並將結果寫入 resultLabel.text
```

---

## 🧠 語法分類總表（語法即意圖）

| 指令類型         | 語氣分類     | 功能意圖                         |
|------------------|--------------|----------------------------------|
| `clear`          | 清除語氣     | 重置 scaffold 狀態               |
| `window`         | 建立語氣     | 建立主視窗                       |
| `style`          | 定義語氣     | 設定樣式                         |
| `control`        | 控件語氣     | 建立 UI 元件                     |
| `grid-setup`     | 佈局語氣     | 設定響應式網格                   |
| `binding`        | 綁定語氣     | 控件事件與表達式綁定             |
| `api-set`        | 設定語氣     | 設定 API 資源                    |
| `api-call`       | 請求語氣     | 呼叫 API 並更新控件              |
| `popup-window`   | 彈窗語氣     | 建立子視窗                       |
| `popup-content`  | 呈現語氣     | 注入 GUI 指令至 popup            |
| `popup-send-data`| 傳送語氣     | popup → 主視窗資料傳輸           |
| `window-maximize`| 擴展語氣     | 最大化視窗                       |
| `window-hide`    | 隱藏語氣     | 隱藏視窗                         |

---


---

## 🛠 錯誤排查語氣鏡像提示

| 錯誤類型             | 鏡像語氣建議                         |
|----------------------|--------------------------------------|
| 控件未建立           | 檢查 `menu control` 是否已執行       |
| API 呼叫失敗         | 檢查 `api-set` 是否正確設定          |
| popup 無內容         | 檢查 `popup-content` 是否已注入      |
| 綁定無效             | 檢查控件名稱與事件是否正確           |
| 資料注入錯誤         | 檢查 `{變數}` 是否存在於上下文中     |

## 🔌 擴充模組建議（插件）

- `plugin-load "custom-layout"` → 載入自定義佈局模組
- `plugin-load "theme-dark"` → 套用暗色主題樣式
- `plugin-load "json-tools"` → 增加 JSON 處理語氣指令

---

---

## 🍽️ README.menu — 語氣鏡像主控台（可執行 scaffold）

```plaintext
menu clear
# menu {清除} → 重置 scaffold，清空所有控件、樣式與事件綁定

menu window main 800 600 "語氣鏡像主控台"
# menu {開啟視窗} → 建立主視窗，名稱=main，尺寸=800x600，標題="語氣鏡像主控台"

menu style header bg="#2c3e50" color="#ecf0f1" font="Noto Sans,16,bold"
menu style button bg="#3498db" color="#ffffff" font="Noto Sans,14,bold"
menu style status bg="#f1c40f" color="#000000" font="Noto Sans,12"

menu control label title text="📘 MENU002 語氣鏡像主控台" x=50 y=30 w=700 h=40 class=header
menu control label subtitle text="每條指令都是一段語氣節奏" x=50 y=80 w=700 h=30 class=status

menu control button btnClear text="清除" x=50 y=140 w=120 h=35 class=button
menu control button btnAPI text="API測試" x=200 y=140 w=120 h=35 class=button
menu control button btnPopup text="開啟彈窗" x=350 y=140 w=120 h=35 class=button
menu control label statusLabel text="狀態：待機中" x=50 y=200 w=700 h=30 class=status

menu api-set demo "https://api.example.com" key=abc123
menu api-call btnAPI demo GET "/status" -> statusLabel.text

menu popup-window popupA "語氣彈窗" size="400x300" offset_x=100 offset_y=100
menu popup-content popupA "control label msg text='這是語氣鏡像的彈窗'" "control button close text='關閉' x=150 y=200 w=100 h=30"

menu popup-send-data popupA "彈窗已關閉" -> statusLabel.text
menu popup-close popupA

menu binding btnClear click "statusLabel.text = '已清除 scaffold'"
menu binding btnPopup click "popupA.popup_id = '語氣彈窗'; statusLabel.text = '彈窗已開啟'"
menu show
```

## 🎨 menu style 指令語氣註解

```plaintext
menu style header bg="#2c3e50" color="#ecf0f1" font="Noto Sans,16,bold"
# menu {定義樣式} → 標題類控件樣式：
# - 背景色：深藍灰 (#2c3e50)，沉穩、專業
# - 文字色：亮白灰 (#ecf0f1)，高對比易讀
# - 字型：Noto Sans，16pt，粗體 → 清晰有力的標題語氣

menu style button bg="#3498db" color="#ffffff" font="Noto Sans,14,bold"
# menu {定義樣式} → 按鈕類控件樣式：
# - 背景色：亮藍 (#3498db)，活潑、具行動暗示
# - 文字色：純白 (#ffffff)，清晰對比
# - 字型：Noto Sans，14pt，粗體 → 明確可點擊的語氣

menu style status bg="#f1c40f" color="#000000" font="Noto Sans,12"
# menu {定義樣式} → 狀態提示控件樣式：
# - 背景色：亮黃 (#f1c40f)，提示、警示語氣
# - 文字色：黑色 (#000000)，穩定清晰
# - 字型：Noto Sans，12pt → 較小但醒目的提示語氣
```

---

## 🌈 色彩參考網站

你可以使用以下網站查詢 HEX 色碼、預覽色彩、建立色彩搭配：

- [ColorHexa 色彩百科](https://www.colorhexa.com)  
  提供 HEX → RGB/HSL/CMYK 等轉換、補色、漸層、色彩理論分析。

- [HexColorPalette 工具集](https://www.hexcolorpalette.com)  
  適合設計師與開發者，支援色彩命名、漸層生成、可視化搭配。

- [Color Hunt 色彩靈感庫](https://colorhunt.co/)
  精選配色方案，適合 UI/UX 設計、品牌風格參考。

---
