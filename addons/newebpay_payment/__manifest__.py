# -*- coding: utf-8 -*-
{
    'name': '藍新金流支付模組',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Payment Providers',
    'summary': '整合藍新金流（NewebPay）支付服務',
    'description': """
藍新金流支付模組
================

此模組整合藍新金流（NewebPay）支付服務，支援：
    * 信用卡支付
    * 虛擬帳號轉帳
    * 超商代碼繳費
    * 支付回調處理
    * 交易記錄管理
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'payment',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_provider_views.xml',
        'views/payment_transaction_views.xml',
        'data/payment_provider_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

