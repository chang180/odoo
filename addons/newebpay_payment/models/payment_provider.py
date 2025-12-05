# -*- coding: utf-8 -*-

from odoo import models, fields, api


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

    @api.model
    def _get_compatible_providers(self, *args, currency_id=None, **kwargs):
        """ 覆寫以支援藍新金流 """
        providers = super()._get_compatible_providers(
            *args, currency_id=currency_id, **kwargs
        )
        return providers

