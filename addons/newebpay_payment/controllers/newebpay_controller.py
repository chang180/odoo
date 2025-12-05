# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class NewebPayController(http.Controller):
    """ 藍新金流控制器，處理支付回調和返回頁面 """

    @http.route('/payment/newebpay/return', type='http', auth='public', csrf=False, methods=['GET', 'POST'])
    def newebpay_return(self, **post):
        """ 處理藍新金流的返回頁面 """
        _logger.info('收到藍新金流返回: %s', post)
        
        # 取得交易記錄
        tx = request.env['payment.transaction'].sudo()._get_tx_from_feedback_data('newebpay', post)
        if not tx:
            _logger.error('找不到對應的交易記錄')
            return request.redirect('/payment/process')
        
        # 處理通知資料
        tx._process_notification_data(post)
        
        # 重導向到確認頁面
        return request.redirect('/payment/status')

    @http.route('/payment/newebpay/notify', type='http', auth='public', csrf=False, methods=['POST'])
    def newebpay_notify(self, **post):
        """ 處理藍新金流的伺服器端通知（Server to Server） """
        _logger.info('收到藍新金流伺服器通知: %s', post)
        
        # 取得交易記錄
        tx = request.env['payment.transaction'].sudo()._get_tx_from_feedback_data('newebpay', post)
        if not tx:
            _logger.error('找不到對應的交易記錄')
            return '0|找不到交易記錄'
        
        # 處理通知資料
        tx._process_notification_data(post)
        
        # 回傳成功訊息給藍新金流
        return '1|OK'

