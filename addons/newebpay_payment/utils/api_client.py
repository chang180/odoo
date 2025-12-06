# -*- coding: utf-8 -*-

"""
藍新金流 API 客戶端

用於處理退款等 API 請求
"""

import logging
import urllib.request
import urllib.parse
import urllib.error
import json
from odoo import exceptions
from .crypto import NewebPayCrypto

_logger = logging.getLogger(__name__)


class NewebPayAPIClient:
    """藍新金流 API 客戶端類別"""

    def __init__(self, merchant_id, hash_key, hash_iv, test_mode=True):
        """
        初始化 API 客戶端

        :param merchant_id: 商店代號
        :param hash_key: Hash Key
        :param hash_iv: Hash IV
        :param test_mode: 是否為測試模式
        """
        self.merchant_id = merchant_id
        self.hash_key = hash_key
        self.hash_iv = hash_iv
        self.test_mode = test_mode

        # 設定 API 端點
        if test_mode:
            self.refund_url = 'https://ccore.newebpay.com/API/CreditCard/Cancel'
        else:
            self.refund_url = 'https://core.newebpay.com/API/CreditCard/Cancel'

        _logger.debug('NewebPayAPIClient 初始化完成 - 測試模式: %s', test_mode)

    def refund(self, trade_no, refund_amount, order_no=None):
        """
        執行退款

        :param trade_no: 藍新交易序號
        :param refund_amount: 退款金額（元）
        :param order_no: 訂單編號（可選）
        :return: 退款回應字典
        """
        try:
            _logger.info('開始執行退款 - 交易序號: %s, 退款金額: %s', trade_no, refund_amount)

            # 準備退款參數
            refund_data = {
                'MerchantID': self.merchant_id,
                'TradeNo': trade_no,
                'Amt': int(refund_amount),  # 金額（元）
                'Version': '1.5',
            }

            if order_no:
                refund_data['MerchantOrderNo'] = order_no

            # 加密交易資訊
            trade_info = NewebPayCrypto.encrypt_trade_info(
                refund_data,
                self.hash_key,
                self.hash_iv
            )

            # 建立簽名
            trade_sha = NewebPayCrypto.create_trade_sha(
                trade_info,
                self.hash_key,
                self.hash_iv
            )

            # 準備請求參數
            request_data = {
                'MerchantID': self.merchant_id,
                'TradeInfo': trade_info,
                'TradeSha': trade_sha,
                'Version': '1.5',
            }

            _logger.debug('退款請求資料: MerchantID=%s, TradeNo=%s', self.merchant_id, trade_no)

            # 準備 POST 資料
            post_data = urllib.parse.urlencode(request_data).encode('utf-8')

            # 發送退款請求
            req = urllib.request.Request(
                self.refund_url,
                data=post_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            )

            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    response_text = response.read().decode('utf-8')
                    response_data = json.loads(response_text)

                    _logger.info('退款回應: %s', response_data)

                    # 驗證回應簽名
                    if 'TradeInfo' in response_data and 'TradeSha' in response_data:
                        is_valid = NewebPayCrypto.verify_trade_sha(
                            response_data['TradeInfo'],
                            response_data['TradeSha'],
                            self.hash_key,
                            self.hash_iv
                        )

                        if not is_valid:
                            _logger.error('退款回應簽名驗證失敗')
                            raise exceptions.ValidationError('退款回應簽名驗證失敗')

                        # 解密回應資料
                        trade_info_decrypted = NewebPayCrypto.decrypt_trade_info(
                            response_data['TradeInfo'],
                            self.hash_key,
                            self.hash_iv
                        )

                        _logger.info('退款成功 - 回應資料: %s', trade_info_decrypted)
                        return trade_info_decrypted
                    else:
                        _logger.error('退款回應格式錯誤: %s', response_data)
                        raise exceptions.ValidationError('退款回應格式錯誤')

            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8') if e.fp else ''
                _logger.error('退款 HTTP 錯誤: %s - %s', e.code, error_body)
                raise exceptions.ValidationError(f'退款請求失敗: HTTP {e.code}')
            except urllib.error.URLError as e:
                _logger.error('退款 URL 錯誤: %s', str(e))
                raise exceptions.ValidationError(f'退款請求失敗: {str(e)}')

        except json.JSONDecodeError as e:
            _logger.error('解析退款回應 JSON 失敗: %s', str(e))
            raise exceptions.ValidationError(f'解析退款回應失敗: {str(e)}')
        except Exception as e:
            _logger.error('退款處理發生錯誤: %s', str(e), exc_info=True)
            if isinstance(e, exceptions.ValidationError):
                raise
            raise exceptions.ValidationError(f'退款處理發生錯誤: {str(e)}')
