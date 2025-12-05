# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    newebpay_trade_no = fields.Char(
        string='藍新交易序號',
        readonly=True,
        help='藍新金流回傳的交易序號'
    )
    newebpay_payment_type = fields.Selection(
        [
            ('CREDIT', '信用卡'),
            ('WEBATM', '網路 ATM'),
            ('VACC', '虛擬帳號'),
            ('CVS', '超商代碼'),
            ('BARCODE', '條碼繳費'),
        ],
        string='支付方式',
        readonly=True
    )

    def _get_specific_rendering_values(self, processing_values):
        """ 覆寫以產生藍新金流的支付表單值 """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'newebpay':
            return res

        # 這裡應該實作藍新金流的表單產生邏輯
        # 包含加密、簽名等處理
        return {
            'api_url': self._get_newebpay_api_url(),
            'merchant_id': self.provider_id.newebpay_merchant_id,
            'amount': int(self.amount * 100),  # 轉換為分
            'order_no': self.reference,
            # ... 其他必要參數
        }

    def _get_newebpay_api_url(self):
        """ 取得藍新金流 API URL """
        if self.provider_id.newebpay_test_mode:
            return 'https://ccore.newebpay.com/MPG/mpg_gateway'
        return 'https://core.newebpay.com/MPG/mpg_gateway'

    def _process_notification_data(self, notification_data):
        """ 處理藍新金流的回調通知 """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'newebpay':
            return

        # 驗證回調資料的簽名
        if not self._verify_newebpay_notification(notification_data):
            _logger.warning('藍新金流回調驗證失敗: %s', notification_data)
            self._set_error('回調驗證失敗')
            return

        # 處理支付結果
        status = notification_data.get('Status')
        if status == 'SUCCESS':
            self._set_done()
        elif status == 'FAIL':
            self._set_error('支付失敗')
        else:
            self._set_pending()

        # 儲存藍新交易序號
        self.newebpay_trade_no = notification_data.get('TradeNo')
        self.newebpay_payment_type = notification_data.get('PaymentType')

    def _verify_newebpay_notification(self, notification_data):
        """ 驗證藍新金流回調通知的簽名 """
        # 這裡應該實作簽名驗證邏輯
        # 使用 Hash Key 和 Hash IV 進行驗證
        return True  # 暫時回傳 True，實際應實作驗證邏輯

