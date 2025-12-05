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

1. 前往「會計」>「設定」>「支付提供者」
2. 建立或編輯藍新金流提供者
3. 填入以下資訊：
   - 商店代號（Merchant ID）
   - Hash Key
   - Hash IV
   - 選擇是否啟用測試模式

## 開發說明

### 模組結構

```
newebpay_payment/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── payment_provider.py
│   └── payment_transaction.py
├── controllers/
│   ├── __init__.py
│   └── newebpay_controller.py
├── views/
│   ├── payment_provider_views.xml
│   └── payment_transaction_views.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   └── payment_provider_data.xml
└── README.md
```

### 待實作功能

- [ ] 完整的加密/解密邏輯
- [ ] 簽名驗證實作
- [ ] 完整的支付流程測試
- [ ] 錯誤處理機制
- [ ] 日誌記錄完善

## 注意事項

- 此為開發版本，請勿直接使用於生產環境
- 需要向藍新金流申請正式帳號才能使用
- 測試模式使用藍新金流提供的測試環境

## 授權

LGPL-3

