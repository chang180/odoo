# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
import re
from urllib.parse import urlparse, urlunparse
from ..utils.crypto import NewebPayCrypto

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
    newebpay_refund_trade_no = fields.Char(
        string='退款交易序號',
        readonly=True,
        help='藍新金流回傳的退款交易序號'
    )
    newebpay_refund_status = fields.Char(
        string='退款狀態',
        readonly=True,
        help='退款處理狀態'
    )

    def _get_specific_rendering_values(self, processing_values):
        """ 覆寫以產生藍新金流的支付表單值 """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'newebpay':
            return res

        try:
            provider = self.provider_id

            # 驗證必要設定
            if not provider.newebpay_merchant_id or not provider.newebpay_hash_key or not provider.newebpay_hash_iv:
                raise ValidationError(_('藍新金流設定不完整，請檢查商店代號、Hash Key 和 Hash IV'))

            # 建立返回和通知 URL
            # 藍新金流要求：ReturnURL 和 NotifyURL 的埠號只能是 80（HTTP）或 443（HTTPS）
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            
            # 解析 URL 並確保埠號符合要求
            parsed_url = urlparse(base_url)
            scheme = parsed_url.scheme.lower()  # http 或 https
            hostname = parsed_url.hostname or parsed_url.netloc.split(':')[0]  # 取得主機名
            
            # 根據協定設定正確的埠號（HTTP=80, HTTPS=443）
            # 藍新金流要求埠號必須明確為 80 或 443
            if scheme == 'https':
                # HTTPS 使用 443
                port = 443
            else:
                # HTTP 使用 80（預設也是 80）
                port = 80
            
            # 重新組裝 base URL，確保使用正確的埠號
            # 如果主機名已包含埠號資訊，先移除
            if ':' in hostname:
                hostname = hostname.split(':')[0]
            
            new_netloc = f"{hostname}:{port}"
            adjusted_base_url = urlunparse((
                scheme,
                new_netloc,
                parsed_url.path.rstrip('/'),  # 移除尾部斜線
                parsed_url.params,
                parsed_url.query,
                parsed_url.fragment
            ))
            
            return_url = f"{adjusted_base_url}/payment/newebpay/return"
            notify_url = f"{adjusted_base_url}/payment/newebpay/notify"
            
            _logger.debug('URL 調整 - 原始: %s, 調整後: %s (埠號: %s)', base_url, adjusted_base_url, port)

            # 準備交易資訊
            # 處理商店訂單編號：藍新金流限制最多 20 個字元，且只能包含英數字
            merchant_order_no = str(self.reference)
            # 只保留英文字母和數字，移除特殊字符
            merchant_order_no = re.sub(r'[^a-zA-Z0-9]', '', merchant_order_no)
            # 如果過濾後為空，使用時間戳作為備用
            if not merchant_order_no:
                merchant_order_no = str(int(self.create_date.timestamp()))
                _logger.warning('交易編號過濾後為空，使用時間戳作為備用: %s', merchant_order_no)
            # 限制長度為 20 字元
            if len(merchant_order_no) > 20:
                merchant_order_no = merchant_order_no[:20]
                _logger.warning(
                    '交易編號超過 20 字元，已截斷 - 原始: %s, 處理後: %s',
                    self.reference, merchant_order_no
                )
            
            # 處理商品描述：限制為 50 字元（藍新金流限制）
            item_desc = str(self.reference)
            if len(item_desc) > 50:
                item_desc = item_desc[:50]
            
            trade_info_dict = {
                'MerchantID': provider.newebpay_merchant_id,
                'RespondType': 'JSON',
                'TimeStamp': str(int(self.create_date.timestamp())),
                'Version': '2.0',
                'MerchantOrderNo': merchant_order_no,
                'Amt': int(self.amount),  # 金額（元）
                'ItemDesc': item_desc,  # 商品描述
                'ReturnURL': return_url,
                'NotifyURL': notify_url,
            }

            # 設定啟用的付款方式
            if provider.newebpay_credit_card:
                trade_info_dict['CREDIT'] = '1'
            if provider.newebpay_webatm:
                trade_info_dict['WEBATM'] = '1'
            if provider.newebpay_vacc:
                trade_info_dict['VACC'] = '1'
            if provider.newebpay_cvs:
                trade_info_dict['CVS'] = '1'
            if provider.newebpay_barcode:
                trade_info_dict['BARCODE'] = '1'

            # 如果有客戶資訊，加入交易資訊
            if self.partner_id:
                trade_info_dict['Email'] = self.partner_id.email or ''
                trade_info_dict['LoginType'] = '0'

            _logger.debug('準備交易資訊: %s', trade_info_dict)

            # 加密交易資訊
            trade_info = NewebPayCrypto.encrypt_trade_info(
                trade_info_dict,
                provider.newebpay_hash_key,
                provider.newebpay_hash_iv
            )

            # 建立簽名
            trade_sha = NewebPayCrypto.create_trade_sha(
                trade_info,
                provider.newebpay_hash_key,
                provider.newebpay_hash_iv
            )

            _logger.info('藍新金流付款表單已產生 - 交易編號: %s', self.reference)

            return {
                'api_url': self._get_newebpay_api_url(),
                'MerchantID': provider.newebpay_merchant_id,
                'TradeInfo': trade_info,
                'TradeSha': trade_sha,
                'Version': '2.0',
            }

        except Exception as e:
            _logger.error('產生藍新金流付款表單失敗: %s', str(e), exc_info=True)
            raise ValidationError(_('產生付款表單失敗: %s') % str(e))

    def _get_newebpay_api_url(self):
        """ 取得藍新金流 API URL """
        if self.provider_id.newebpay_test_mode:
            return 'https://ccore.newebpay.com/MPG/mpg_gateway'
        return 'https://core.newebpay.com/MPG/mpg_gateway'

    @api.model
    def _get_tx_from_feedback_data(self, provider_code, notification_data):
        """ 從回調資料中找出對應的交易記錄 """
        if provider_code != 'newebpay':
            return super()._get_tx_from_feedback_data(provider_code, notification_data)

        try:
            # 取得 TradeInfo（加密的回調資料）
            trade_info_encrypted = notification_data.get('TradeInfo')
            if not trade_info_encrypted:
                _logger.error('回調資料中缺少 TradeInfo')
                return None

            # 取得提供者
            provider = self.env['payment.provider']._get_provider(
                provider_code,
                raise_if_not_found=False
            )
            if not provider:
                _logger.error('找不到藍新金流提供者')
                return None

            # 解密回調資料
            try:
                trade_info = NewebPayCrypto.decrypt_trade_info(
                    trade_info_encrypted,
                    provider.newebpay_hash_key,
                    provider.newebpay_hash_iv
                )
            except Exception as e:
                _logger.error('解密回調資料失敗: %s', str(e))
                return None

            # 從解密後的資料中取得訂單編號
            merchant_order_no = trade_info.get('MerchantOrderNo')
            if not merchant_order_no:
                _logger.error('回調資料中缺少 MerchantOrderNo')
                return None

            # 尋找對應的交易記錄
            tx = self.search([
                ('reference', '=', merchant_order_no),
                ('provider_code', '=', 'newebpay'),
            ], limit=1)

            if not tx:
                _logger.warning('找不到對應的交易記錄: %s', merchant_order_no)

            return tx

        except Exception as e:
            _logger.error('處理回調資料時發生錯誤: %s', str(e), exc_info=True)
            return None

    def _process_notification_data(self, notification_data):
        """ 處理藍新金流的回調通知 """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'newebpay':
            return

        try:
            # 驗證回調資料的簽名
            if not self._verify_newebpay_notification(notification_data):
                _logger.warning('藍新金流回調驗證失敗 - 交易: %s', self.reference)
                self._set_error(_('回調驗證失敗'))
                return

            # 解密回調資料
            trade_info_encrypted = notification_data.get('TradeInfo')
            if not trade_info_encrypted:
                _logger.error('回調資料中缺少 TradeInfo')
                self._set_error(_('回調資料不完整'))
                return

            provider = self.provider_id
            trade_info = NewebPayCrypto.decrypt_trade_info(
                trade_info_encrypted,
                provider.newebpay_hash_key,
                provider.newebpay_hash_iv
            )

            _logger.info('處理藍新金流回調 - 交易: %s, 資料: %s', self.reference, trade_info)

            # 儲存藍新交易序號和支付方式
            self.newebpay_trade_no = trade_info.get('TradeNo')
            self.newebpay_payment_type = trade_info.get('PaymentType')

            # 處理支付結果
            status = trade_info.get('Status')
            message = trade_info.get('Message', '')

            if status == 'SUCCESS':
                # 驗證金額是否一致
                response_amt = float(trade_info.get('Amt', 0))  # 金額（元）
                if abs(response_amt - self.amount) > 0.01:  # 允許小數點誤差
                    _logger.warning(
                        '金額不符 - 交易: %s, 期望: %s, 實際: %s',
                        self.reference, self.amount, response_amt
                    )
                    self._set_error(_('金額驗證失敗'))
                    return

                self._set_done()
                _logger.info('藍新金流付款成功 - 交易: %s', self.reference)
            elif status == 'FAIL':
                error_msg = message or '支付失敗'
                self._set_error(error_msg)
                _logger.warning('藍新金流付款失敗 - 交易: %s, 訊息: %s', self.reference, error_msg)
            else:
                # 其他狀態（如處理中等）
                self._set_pending(message or _('付款處理中'))
                _logger.info('藍新金流付款處理中 - 交易: %s, 狀態: %s', self.reference, status)

        except Exception as e:
            _logger.error('處理藍新金流回調時發生錯誤: %s', str(e), exc_info=True)
            self._set_error(_('處理回調時發生錯誤: %s') % str(e))

    def _verify_newebpay_notification(self, notification_data):
        """ 驗證藍新金流回調通知的簽名 """
        try:
            trade_info = notification_data.get('TradeInfo')
            trade_sha = notification_data.get('TradeSha')

            if not trade_info or not trade_sha:
                _logger.error('回調資料中缺少 TradeInfo 或 TradeSha')
                return False

            provider = self.provider_id
            if not provider.newebpay_hash_key or not provider.newebpay_hash_iv:
                _logger.error('藍新金流設定不完整')
                return False

            # 驗證簽名
            is_valid = NewebPayCrypto.verify_trade_sha(
                trade_info,
                trade_sha,
                provider.newebpay_hash_key,
                provider.newebpay_hash_iv
            )

            if is_valid:
                _logger.debug('藍新金流回調簽名驗證成功')
            else:
                _logger.warning('藍新金流回調簽名驗證失敗')

            return is_valid

        except Exception as e:
            _logger.error('驗證藍新金流回調簽名時發生錯誤: %s', str(e), exc_info=True)
            return False

    def _send_refund_request(self, amount_to_refund=None):
        """ 發送退款請求到藍新金流 """
        self.ensure_one()
        if self.provider_code != 'newebpay':
            return super()._send_refund_request(amount_to_refund=amount_to_refund)

        try:
            if not self.newebpay_trade_no:
                raise ValidationError(_('找不到藍新交易序號，無法執行退款'))

            provider = self.provider_id
            if not provider.newebpay_merchant_id or not provider.newebpay_hash_key or not provider.newebpay_hash_iv:
                raise ValidationError(_('藍新金流設定不完整，無法執行退款'))

            # 決定退款金額
            refund_amount = amount_to_refund if amount_to_refund else self.amount
            if refund_amount > self.amount:
                raise ValidationError(_('退款金額不能超過原始交易金額'))

            _logger.info('準備執行退款 - 交易: %s, 退款金額: %s', self.reference, refund_amount)

            # 使用 API 客戶端執行退款
            from ..utils.api_client import NewebPayAPIClient

            api_client = NewebPayAPIClient(
                merchant_id=provider.newebpay_merchant_id,
                hash_key=provider.newebpay_hash_key,
                hash_iv=provider.newebpay_hash_iv,
                test_mode=provider.newebpay_test_mode
            )

            # 執行退款
            refund_response = api_client.refund(
                trade_no=self.newebpay_trade_no,
                refund_amount=refund_amount,
                order_no=self.reference
            )

            # 處理退款回應
            if refund_response:
                status = refund_response.get('Status', '')
                message = refund_response.get('Message', '')

                # 儲存退款交易序號和狀態
                self.newebpay_refund_trade_no = refund_response.get('TradeNo', '')
                self.newebpay_refund_status = status

                if status == 'SUCCESS':
                    _logger.info('退款成功 - 交易: %s, 退款金額: %s', self.reference, refund_amount)
                    return True
                else:
                    error_msg = message or '退款失敗'
                    _logger.warning('退款失敗 - 交易: %s, 訊息: %s', self.reference, error_msg)
                    raise ValidationError(_('退款失敗: %s') % error_msg)

            return False

        except ValidationError:
            raise
        except Exception as e:
            _logger.error('執行退款時發生錯誤: %s', str(e), exc_info=True)
            raise ValidationError(_('執行退款時發生錯誤: %s') % str(e))

