# Odoo Docker 開發環境

這是一個完整的 Odoo 最新版本 Docker 開發環境，用於開發藍新金流支付模組。

## 環境需求

在開始之前，請確認您已安裝：

- ✅ Docker Desktop（最新版本）
- ✅ Docker Compose（通常包含在 Docker Desktop 中）
- ✅ 至少 5GB 可用磁碟空間
- ✅ 端口 8069 未被其他服務佔用

## 快速開始

### 1. 複製環境變數檔案（可選）

```bash
cp .env.example .env
```

然後編輯 `.env` 檔案，修改資料庫密碼等設定（預設值通常可以正常運作）。

### 2. 啟動服務

```bash
docker-compose up -d
```

這將會：
- 下載 Odoo 和 PostgreSQL 的 Docker 映像（首次執行時）
- 啟動 PostgreSQL 資料庫服務
- 啟動 Odoo 服務
- 建立必要的資料卷

### 3. 存取 Odoo

開啟瀏覽器，前往：
```
http://localhost:8069
```

首次存取時，Odoo 會引導您建立資料庫。

### 4. 啟用開發者模式

1. 登入 Odoo
2. 前往「設定」>「啟用開發者模式」
3. 前往「應用程式」>「更新應用程式列表」
4. 搜尋並安裝「藍新金流支付模組」

## 專案結構

```
odoo/
├── docker-compose.yml          # Docker Compose 配置
├── config/
│   └── odoo.conf               # Odoo 伺服器配置
├── addons/
│   └── newebpay_payment/       # 藍新金流支付模組
│       ├── models/             # 資料模型
│       ├── controllers/        # HTTP 控制器
│       ├── views/              # 視圖定義
│       ├── security/           # 權限設定
│       └── data/               # 初始資料
├── .env.example                # 環境變數範例
├── .gitignore                  # Git 忽略檔案
├── .dockerignore               # Docker 忽略檔案
└── README.md                   # 本檔案
```

## 常用指令

### 啟動服務
```bash
docker-compose up -d
```

### 停止服務
```bash
docker-compose down
```

### 查看日誌
```bash
# 查看所有服務日誌
docker-compose logs -f

# 僅查看 Odoo 日誌
docker-compose logs -f odoo

# 僅查看資料庫日誌
docker-compose logs -f db
```

### 重啟服務
```bash
docker-compose restart
```

### 進入 Odoo 容器
```bash
docker-compose exec odoo bash
```

### 進入資料庫容器
```bash
docker-compose exec db psql -U odoo -d odoo
```

### 更新模組
在 Odoo 介面中：
1. 啟用開發者模式
2. 前往「應用程式」>「更新應用程式列表」
3. 或使用「升級」功能更新特定模組

### 清除所有資料（重新開始）
```bash
# 停止並刪除容器、網路和卷
docker-compose down -v

# 重新啟動
docker-compose up -d
```

## 開發模式

此環境已啟用開發模式（`dev_mode = reload`），當您修改模組程式碼時，Odoo 會自動重新載入模組，無需重啟容器。

### 模組開發流程

1. 在 `addons/newebpay_payment/` 目錄中編輯程式碼
2. 在 Odoo 中更新應用程式列表或升級模組
3. 測試功能
4. 重複步驟 1-3

## 配置說明

### Odoo 配置（config/odoo.conf）

主要設定項目：
- `db_host`: 資料庫主機（預設：db）
- `db_user`: 資料庫使用者（預設：odoo）
- `db_password`: 資料庫密碼（預設：odoo）
- `http_port`: HTTP 端口（預設：8069）
- `dev_mode`: 開發模式（預設：reload）
- `addons_path`: 模組路徑（包含自訂模組目錄）

### 環境變數（.env）

可設定的環境變數：
- `POSTGRES_DB`: 資料庫名稱
- `POSTGRES_USER`: 資料庫使用者
- `POSTGRES_PASSWORD`: 資料庫密碼
- `ODOO_PORT`: Odoo 端口

## 疑難排解

### 端口已被佔用

如果端口 8069 已被佔用，可以：
1. 修改 `.env` 檔案中的 `ODOO_PORT` 設定
2. 或修改 `docker-compose.yml` 中的端口映射

### 無法連線資料庫

1. 確認資料庫容器已正常啟動：`docker-compose ps`
2. 檢查資料庫日誌：`docker-compose logs db`
3. 確認環境變數設定正確

### 模組未出現

1. 確認模組目錄在 `addons/` 下
2. 確認 `__manifest__.py` 檔案存在且格式正確
3. 在 Odoo 中更新應用程式列表
4. 檢查 Odoo 日誌是否有錯誤

### 權限問題

如果遇到權限問題，可以：
```bash
# 修改檔案權限
chmod -R 755 addons/
```

## 資料持久化

以下資料會持久化儲存：
- 資料庫資料：`odoo-db-data` 卷
- Odoo 檔案：`odoo-web-data` 卷
- 自訂模組：`./addons` 目錄（掛載到容器）

## 安全注意事項

⚠️ **重要**：此為開發環境配置，不應直接用於生產環境！

生產環境需要：
- 使用強密碼
- 設定 HTTPS
- 配置防火牆
- 定期備份資料
- 使用環境變數管理敏感資訊

## 藍新金流模組

詳細的模組說明請參考：[addons/newebpay_payment/README.md](addons/newebpay_payment/README.md)

## 授權

本專案使用 LGPL-3 授權。

## 支援

如有問題或建議，請聯繫開發團隊。

