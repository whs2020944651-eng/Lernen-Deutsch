# Lernen-Deutsch 🇩🇪

一個開源、由 AI 驅動的德語學習助手，提供互動式語言輔導、語法分析與詞彙管理功能。

## 🌟 核心功能

- **AI 對話助手：** 沉浸式德語對話練習，模擬真實語境。
- **語法解析：** 即時檢測德語語法錯誤，並提供詳細的規則解析。
- **詞彙管理：** 系統化整理德語單詞，追蹤學習進度。
- **開發者友好：** 提供 CLI 和 API 介面，方便整合到其他開源教育專案。

## 🚀 快速開始

### 方式一：在 GitHub Codespaces 中執行（推薦）

無需本地配置，直接在雲端開始：

1. 點擊頁面右上角綠色的 **Code** 按鈕。
2. 切換到 **Codespaces** 標籤頁。
3. 點擊 **Create codespace on main**。瀏覽器將自動配置並開啟完整的開發環境。

### 方式二：本地部署

1. 複製儲存庫到本地：

	```bash
	git clone https://github.com/whs2020944651-eng/Lernen-Deutsch.git
	cd Lernen-Deutsch
	```

2. 依照專案中的設定安裝相依套件並啟動應用程式。

### 詞彙管理功能 (Vocabulary Management CLI)

Lernen-Deutsch 內建 SQLite 詞彙庫與間隔重複（Spaced Repetition）記憶系統，支援離線管理與進度追蹤：

- **新增單詞：**
  ```bash
  python main.py vocab add [word] [translation] [difficulty]
  # 範例：python main.py vocab add Apfel apple easy
  ```
- **單詞複習 (間隔重複練習)：**
  ```bash
  python main.py vocab review
  ```
- **列出詞彙：**
  ```bash
  python main.py vocab list
  ```
- **匯出詞彙為 CSV：**
  ```bash
  python main.py vocab export [filename.csv]
  ```

在互動對話模式中，亦可直接輸入 `vocab`、`vocab add ...`、`vocab review` 或 `vocab export` 使用上述功能。

## 🤝 參與貢獻

歡迎提交 Issue 或 Pull Request，一起改善開源德語學習體驗。
