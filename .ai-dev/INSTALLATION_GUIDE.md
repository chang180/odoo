# 藍新金流模組安裝與使用指南

## 系統需求

- Docker 和 Docker Compose
- Odoo 19
- Python 3.12+
- pycryptodome >= 3.19.0

## 安裝步驟

### 1. 啟動 Docker 容器

```bash
cd d:\coding\odoo
docker-compose up -d
```

### 2. 檢查容器狀態

```bash
docker ps
```

應該看到兩個容器正在運行：
- `odoo-odoo-1`（Odoo 服務）
- `odoo-db-1`（PostgreSQL 資料庫）

### 3. 訪問 Odoo

開啟瀏覽器訪問：
```
http://localhost:8069
```

### 4. 建立資料庫（首次使用）

1. 在資料庫管理頁面，點擊「Create Database」
2. 填入以下資訊：
   - Database Name: `odoo`（或其他名稱）
   - Email: 管理員郵箱
   - Password: 管理員密碼
   - Language: 繁體中文
3. 點擊「Create Database」並等待建立完成

### 5. 安裝藍新金流模組

#### 方法一：透過應用程式介面

1. 登入 Odoo 後台
2. 啟用開發者模式：
   - 點擊右上角的用戶名
   - 選擇「Preferences」
   - 在「Developer Tools」區塊點擊「Activate the developer mode」
3. 前往「Apps」應用程式
4. 點擊「Update Apps List」更新應用程式列表
5. 在搜尋框輸入「newebpay」或「藍新金流」
6. 找到「藍新金流支付模組」並點擊「Install」

#### 方法二：透過命令列

```bash
docker exec -it odoo-odoo-1 odoo -d odoo -i newebpay_payment --stop-after-init
docker-compose restart odoo
```

## 設定藍新金流

### 1. 取得藍新金流測試帳號

前往藍新金流官網申請測試帳號，取得以下資訊：
- 商店代號（Merchant ID）
- Hash Key
- Hash IV

### 2. 設定支付提供者

#### 訪問支付提供者設定頁面

**方法一：直接訪問 URL**（推薦）
```
http://localhost:8069/web#action=payment.action_payment_provider&model=payment.provider
```

**方法二：透過搜尋**
1. 在 Odoo 頂部搜尋框輸入「Payment Providers」
2. 選擇「Payment Providers」選單

#### 配置藍新金流

1. 在支付提供者列表中找到「藍新金流」
2. 點擊進入編輯頁面
3. 填入以下資訊：
   - **商店代號**：填入藍新金流提供的 Merchant ID
   - **Hash Key**：填入藍新金流提供的 Hash Key
   - **Hash IV**：填入藍新金流提供的 Hash IV
   - **測試模式**：勾選（使用測試環境）
4. 點擊「Save」儲存
5. 點擊「Activate」啟用支付提供者
6. 點擊「Publish」發布（讓前台客戶可以看到此付款選項）

## 測試付款流程

### 1. 建立測試訂單

1. 前往「Sales」或「eCommerce」應用程式
2. 建立一個測試訂單
3. 選擇「藍新金流」作為付款方式
4. 確認訂單

### 2. 進行付款

1. 系統會自動導向藍新金流付款頁面
2. 在測試環境中使用測試卡號進行付款
3. 完成付款後會返回 Odoo 系統

### 3. 檢查交易記錄

1. 前往「Accounting」> 「Payment Transactions」
2. 查看交易狀態和詳細資訊

## 測試退款功能

1. 找到已完成的支付交易
2. 點擊交易記錄
3. 點擊「Refund」按鈕
4. 輸入退款金額（支援部分退款）
5. 確認退款

## 常見問題

### Q1: 容器啟動失敗

**解決方案**：
```bash
# 查看日誌
docker logs odoo-odoo-1

# 重新建置容器
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Q2: 模組安裝失敗

**解決方案**：
1. 檢查模組檔案是否完整
2. 確認 pycryptodome 已安裝：
   ```bash
   docker exec odoo-odoo-1 python3 -c "import Crypto; print(Crypto.__version__)"
   ```
3. 檢查 Odoo 日誌是否有錯誤訊息

### Q3: 付款失敗

**可能原因**：
1. Hash Key 或 Hash IV 設定錯誤
2. 商店代號錯誤
3. 測試環境設定錯誤
4. 網路連線問題

**解決方案**：
1. 確認藍新金流設定正確
2. 檢查 Odoo 日誌（`docker logs odoo-odoo-1`）
3. 確認 Return URL 和 Notify URL 可以從外部訪問

### Q4: 回調驗證失敗

**可能原因**：
- 簽名驗證失敗
- Hash Key 或 Hash IV 不正確

**解決方案**：
1. 重新確認 Hash Key 和 Hash IV
2. 檢查日誌中的詳細錯誤訊息
3. 確認使用正確的測試/正式環境設定

## 開發除錯

### 查看 Odoo 日誌

```bash
# 即時查看日誌
docker logs -f odoo-odoo-1

# 查看最近 100 行日誌
docker logs --tail 100 odoo-odoo-1

# 搜尋特定關鍵字
docker logs odoo-odoo-1 2>&1 | grep newebpay
```

### 進入容器除錯

```bash
# 進入 Odoo 容器
docker exec -it odoo-odoo-1 bash

# 檢查模組檔案
ls -la /mnt/extra-addons/newebpay_payment/

# 測試 Python 模組導入
python3 -c "from Crypto.Cipher import AES; print('OK')"
```

### 重新載入模組

```bash
# 更新模組
docker exec -it odoo-odoo-1 odoo -d odoo -u newebpay_payment --stop-after-init
docker-compose restart odoo
```

## 生產環境部署注意事項

1. **安全性**：
   - 將 Hash Key 和 Hash IV 設定為唯讀
   - 使用 HTTPS 加密連線
   - 定期更換管理員密碼
   - 限制資料庫訪問權限

2. **測試模式**：
   - 生產環境務必取消勾選「測試模式」
   - 使用正式的商店代號和金鑰

3. **回調 URL**：
   - 確保 Return URL 和 Notify URL 可從外部訪問
   - 使用固定的 IP 或域名
   - 在藍新金流後台設定白名單

4. **備份**：
   - 定期備份資料庫
   - 備份 odoo.conf 設定檔
   - 保存藍新金流設定資訊

5. **效能優化**：
   - 調整 workers 數量
   - 設定適當的 max_cron_threads
   - 監控系統資源使用

## 技術支援

如遇到問題，請檢查：
1. Odoo 日誌檔案
2. Docker 容器狀態
3. 藍新金流官方文件
4. 本專案的開發日誌（`.ai-dev/newebpay_payment_log.md`）

## 版本資訊

- Odoo 版本：19.0
- 模組版本：19.0.1.0.0
- Python 版本：3.12+
- pycryptodome 版本：3.23.0
