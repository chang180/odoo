# -*- coding: utf-8 -*-

from odoo import models, fields

from odoo.addons.newebpay_payment import const


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(
        selection_add=[('newebpay', '藍新金流')],
        ondelete={'newebpay': 'set default'}
    )
    newebpay_merchant_id = fields.Char(
        string='商店代號',
        required_if_provider='newebpay',
        help='藍新金流提供的商店代號'
    )
    newebpay_hash_key = fields.Char(
        string='Hash Key',
        required_if_provider='newebpay',
        help='藍新金流的 Hash Key（用於資料加密）'
    )
    newebpay_hash_iv = fields.Char(
        string='Hash IV',
        required_if_provider='newebpay',
        help='藍新金流的 Hash IV（用於資料加密）'
    )
    newebpay_test_mode = fields.Boolean(
        string='測試模式',
        default=True,
        help='啟用測試模式時，將使用藍新金流的測試環境'
    )

    # 支援的付款方式
    newebpay_credit_card = fields.Boolean(
        string='信用卡',
        default=True,
        help='啟用信用卡付款'
    )
    newebpay_webatm = fields.Boolean(
        string='網路 ATM',
        default=False,
        help='啟用網路 ATM 付款'
    )
    newebpay_vacc = fields.Boolean(
        string='虛擬帳號',
        default=False,
        help='啟用虛擬帳號付款'
    )
    newebpay_cvs = fields.Boolean(
        string='超商代碼',
        default=False,
        help='啟用超商代碼繳費'
    )
    newebpay_barcode = fields.Boolean(
        string='條碼繳費',
        default=False,
        help='啟用條碼繳費'
    )

    def _compute_feature_support_fields(self):
        """ Override of `payment` to enable additional features. """
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == 'newebpay').update({
            'support_manual_capture': False,
            'support_refund': 'partial',
            'support_tokenization': False,
        })

    def _get_default_payment_method_codes(self):
        """ Override of `payment` to return the default payment method codes. """
        self.ensure_one()
        if self.code != 'newebpay':
            return super()._get_default_payment_method_codes()
        return const.DEFAULT_PAYMENT_METHOD_CODES

    def _is_compatible_with_currency(self, currency):
        """ 檢查是否與指定貨幣相容 """
        res = super()._is_compatible_with_currency(currency)
        if self.code != 'newebpay':
            return res
        # 藍新金流支援新台幣 (TWD)
        # 暫時也支援 USD 用於測試（實際上藍新金流主要支援 TWD）
        return currency.name in ['TWD', 'USD']
