# 藍新金流支付模組

## 簡介

此模組整合藍新金流（NewebPay）支付服務到 Odoo 系統中，支援多種支付方式。

## 功能特色

- 信用卡支付
- 網路 ATM 轉帳
- 虛擬帳號轉帳
- 超商代碼繳費
- 條碼繳費
- 支付回調處理
- 交易記錄管理

## 安裝說明

1. 將此模組放置在 `addons` 目錄下
2. 在 Odoo 中啟用開發者模式
3. 更新應用程式列表
4. 安裝「藍新金流支付模組」

## 設定說明

### 訪問支付提供者設定（Odoo 19）

在 Odoo 19 中，可以透過以下方式訪問支付提供者設定：

1. **直接訪問 URL**（推薦）：
   ```
   http://localhost:8069/web#action=payment.action_payment_provider&model=payment.provider
   ```

2. **使用搜尋功能**：
   - 在 Odoo 頂部搜尋框輸入「Payment Providers」或「支付提供者」

3. **透過應用程式選單**：
   - 前往「應用程式」> 搜尋「Payment Providers」模組

### 設定步驟

1. 開啟支付提供者設定頁面
2. 找到或建立「藍新金流」提供者
3. 點擊「編輯」並填入以下資訊：
   - **商店代號（Merchant ID）**：藍新金流提供的商店代號
   - **Hash Key**：藍新金流提供的 Hash Key（密碼欄位）
   - **Hash IV**：藍新金流提供的 Hash IV（密碼欄位）
   - **測試模式**：勾選表示使用測試環境
4. 點擊「啟用」按鈕啟用提供者
5. 點擊「發布」按鈕發布提供者（讓客戶可以看到此付款選項）

## 開發說明

### 模組結構

```
newebpay_payment/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── payment_provider.py       # 支付提供者模型擴充
│   └── payment_transaction.py    # 支付交易模型擴充
├── controllers/
│   ├── __init__.py
│   └── newebpay_controller.py    # 回調處理控制器
├── utils/
│   ├── __init__.py
│   ├── crypto.py                 # 加密/解密工具
│   └── api_client.py             # API 客戶端（退款）
├── views/
│   ├── payment_provider_views.xml
│   └── payment_transaction_views.xml
├── templates/
│   └── payment_newebpay_form.xml # 付款表單模板
├── security/
│   └── ir.model.access.csv
├── data/
│   └── payment_provider_data.xml
└── README.md
```

### 已實作功能

- [x] 完整的加密/解密邏輯（AES-256-CBC）
- [x] SHA256 簽名驗證實作
- [x] 錯誤處理機制
- [x] 日誌記錄完善
- [x] MPG 付款功能（支援多種支付方式）
- [x] API 退款功能（支援部分退款）
- [x] 回調處理機制（return 和 notify）
- [x] 付款表單自動提交
- [x] Docker 環境配置
- [x] URL 編碼處理（符合藍新金流 http_build_query 要求）
- [x] 商店訂單編號格式驗證（長度限制 20 字元，僅英數字）
- [x] ReturnURL/NotifyURL 埠號處理（強制使用 80/443）

### 待實作功能

- [ ] 完整的支付流程測試（需要藍新金流測試帳號）
- [ ] 退款功能測試

## 注意事項

- 此為開發版本，請勿直接使用於生產環境
- 需要向藍新金流申請正式帳號才能使用
- 測試模式使用藍新金流提供的測試環境
- **重要**：ReturnURL 和 NotifyURL 必須使用埠號 80（HTTP）或 443（HTTPS）
  - 如果 Odoo 運行在其他埠號（如 8069），需要使用反向代理（如 nginx）將請求轉發到 Odoo

## 授權

LGPL-3

