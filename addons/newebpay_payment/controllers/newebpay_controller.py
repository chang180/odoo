# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

# 導入支付後處理控制器以設置交易監控
try:
    from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing
except ImportError:
    PaymentPostProcessing = None
    _logger.warning('無法導入 PaymentPostProcessing，支付狀態監控可能無法正常工作')


class NewebPayController(http.Controller):
    """ 藍新金流控制器，處理支付回調和返回頁面 """

    @http.route('/payment/newebpay/return', type='http', auth='none', csrf=False, methods=['GET', 'POST'], website=True)
    def newebpay_return(self, **post):
        """ 處理藍新金流的返回頁面 """
        try:
            _logger.info('===== 收到藍新金流返回請求 =====')
            _logger.info('POST 資料: %s', post)
            _logger.info('GET 參數: %s', request.httprequest.args)
            
            # 取得交易記錄
            tx = request.env['payment.transaction'].sudo()._get_tx_from_feedback_data('newebpay', post)
            if not tx:
                _logger.error('找不到對應的交易記錄 - 回調資料: %s', post)
                # 重定向到支付狀態頁面（顯示支付未找到）
                return request.redirect('/payment/status')
            
            _logger.info('找到交易記錄 - 交易編號: %s', tx.reference)
            
            # 處理通知資料
            try:
                tx._process_notification_data(post)
                _logger.info('交易通知處理完成 - 交易編號: %s, 狀態: %s', tx.reference, tx.state)
            except Exception as e:
                _logger.error('處理交易通知時發生錯誤 - 交易編號: %s, 錯誤: %s', tx.reference, str(e), exc_info=True)
            
            # 設置交易監控，以便支付狀態頁面可以找到交易
            if PaymentPostProcessing:
                try:
                    PaymentPostProcessing.monitor_transaction(tx)
                    _logger.info('交易已設置監控 - 交易編號: %s', tx.reference)
                except Exception as e:
                    _logger.warning('設置交易監控時發生錯誤: %s', str(e))
            
            # 重導向到確認頁面
            return request.redirect('/payment/status')
            
        except Exception as e:
            _logger.error('處理藍新金流返回時發生錯誤: %s', str(e), exc_info=True)
            # 發生錯誤時重定向到支付狀態頁面
            return request.redirect('/payment/status')

    @http.route('/payment/newebpay/notify', type='http', auth='none', csrf=False, methods=['POST'], save_session=False)
    def newebpay_notify(self, **post):
        """ 處理藍新金流的伺服器端通知（Server to Server） """
        try:
            _logger.info('===== 收到藍新金流伺服器通知 =====')
            _logger.info('POST 資料: %s', post)
            
            # 取得交易記錄
            tx = request.env['payment.transaction'].sudo()._get_tx_from_feedback_data('newebpay', post)
            if not tx:
                _logger.error('找不到對應的交易記錄 - 回調資料: %s', post)
                return '0|找不到交易記錄'
            
            _logger.info('找到交易記錄 - 交易編號: %s', tx.reference)
            
            # 處理通知資料
            try:
                tx._process_notification_data(post)
                _logger.info('交易通知處理完成 - 交易編號: %s, 狀態: %s', tx.reference, tx.state)
                
                # 回傳成功訊息給藍新金流（格式：1|OK）
                return '1|OK'
                
            except Exception as e:
                _logger.error('處理交易通知時發生錯誤 - 交易編號: %s, 錯誤: %s', tx.reference, str(e), exc_info=True)
                # 即使處理失敗，也要回傳失敗訊息給藍新金流（格式：0|錯誤訊息）
                return f'0|處理錯誤: {str(e)}'
                
        except Exception as e:
            _logger.error('處理藍新金流伺服器通知時發生錯誤: %s', str(e), exc_info=True)
            return f'0|系統錯誤: {str(e)}'

