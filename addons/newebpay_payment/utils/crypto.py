# -*- coding: utf-8 -*-

"""
藍新金流加密/解密和簽名驗證工具

實作藍新金流的 AES-256-CBC 加密/解密和 SHA256 簽名驗證功能
"""

import hashlib
import json
import logging
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from urllib.parse import quote, unquote

_logger = logging.getLogger(__name__)


class NewebPayCrypto:
    """藍新金流加密/解密和簽名驗證類別"""

    @staticmethod
    def encrypt_trade_info(trade_info_dict, hash_key, hash_iv):
        """
        加密交易資訊

        :param trade_info_dict: 交易資訊字典
        :param hash_key: Hash Key
        :param hash_iv: Hash IV
        :return: 加密後的 TradeInfo 字串
        """
        try:
            # 將字典轉換為 query string 格式（藍新金流要求格式）
            # 根據藍新金流文件，需要使用 http_build_query 的方式（自動 URL 編碼）
            # 類似 PHP 的 http_build_query，需要對值進行 URL 編碼
            trade_info_parts = []
            for key, value in trade_info_dict.items():
                # 對值進行 URL 編碼，確保特殊字符被正確處理
                # 但不需要對 key 進行編碼
                encoded_value = quote(str(value), safe='')
                trade_info_parts.append(f"{key}={encoded_value}")
            trade_info_str = '&'.join(trade_info_parts)

            _logger.info('原始交易資訊（加密前）: %s', trade_info_str)

            # 使用 AES-256-CBC 加密
            cipher = AES.new(
                hash_key.encode('utf-8'),
                AES.MODE_CBC,
                hash_iv.encode('utf-8')
            )

            # 進行 PKCS7 padding
            padded_data = pad(trade_info_str.encode('utf-8'), AES.block_size)

            # 加密
            encrypted = cipher.encrypt(padded_data)

            # 轉換為十六進位字串並轉小寫（藍新金流要求小寫）
            trade_info = encrypted.hex()

            _logger.info('加密後的 TradeInfo: %s', trade_info)
            return trade_info

        except Exception as e:
            _logger.error('加密交易資訊失敗: %s', str(e))
            raise

    @staticmethod
    def decrypt_trade_info(trade_info, hash_key, hash_iv):
        """
        解密交易資訊

        :param trade_info: 加密後的 TradeInfo 字串
        :param hash_key: Hash Key
        :param hash_iv: Hash IV
        :return: 解密後的交易資訊字典
        """
        try:
            # 將十六進位字串轉換為 bytes
            encrypted = bytes.fromhex(trade_info)

            # 使用 AES-256-CBC 解密
            cipher = AES.new(
                hash_key.encode('utf-8'),
                AES.MODE_CBC,
                hash_iv.encode('utf-8')
            )

            # 解密
            decrypted = cipher.decrypt(encrypted)

            # 移除 PKCS7 padding
            unpadded = unpad(decrypted, AES.block_size)

            # 轉換為字串
            trade_info_str = unpadded.decode('utf-8')

            # 解析 query string 為字典
            trade_info_dict = {}
            for pair in trade_info_str.split('&'):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    trade_info_dict[key] = value

            _logger.debug('解密後的交易資訊: %s', trade_info_dict)
            return trade_info_dict

        except Exception as e:
            _logger.error('解密交易資訊失敗: %s', str(e))
            raise

    @staticmethod
    def create_trade_sha(trade_info, hash_key, hash_iv):
        """
        建立交易簽名（TradeSha）

        簽名字串 = SHA256("HashKey=" + HashKey + "&" + TradeInfo + "&HashIV=" + HashIV)

        :param trade_info: 加密後的 TradeInfo 字串
        :param hash_key: Hash Key
        :param hash_iv: Hash IV
        :return: 簽名字串（大寫）
        """
        try:
            # 組合簽名字串（根據藍新金流 PHP 範例）
            # 注意：中間是直接接加密後的 TradeInfo，沒有 "TradeInfo=" 前綴
            sign_string = f"HashKey={hash_key}&{trade_info}&HashIV={hash_iv}"

            _logger.info('簽名字串: %s', sign_string)

            # 計算 SHA256 雜湊值
            sha256_hash = hashlib.sha256(sign_string.encode('utf-8')).hexdigest()

            # 轉為大寫
            trade_sha = sha256_hash.upper()

            _logger.info('TradeSha 簽名: %s', trade_sha)
            return trade_sha

        except Exception as e:
            _logger.error('建立 TradeSha 簽名失敗: %s', str(e))
            raise

    @staticmethod
    def verify_trade_sha(trade_info, trade_sha, hash_key, hash_iv):
        """
        驗證交易簽名

        :param trade_info: 加密後的 TradeInfo 字串
        :param trade_sha: 接收到的 TradeSha 簽名
        :param hash_key: Hash Key
        :param hash_iv: Hash IV
        :return: 驗證是否成功 (True/False)
        """
        try:
            # 計算預期的簽名
            expected_sha = NewebPayCrypto.create_trade_sha(trade_info, hash_key, hash_iv)

            # 比較簽名（不區分大小寫）
            is_valid = expected_sha.upper() == trade_sha.upper()

            if not is_valid:
                _logger.warning('簽名驗證失敗 - 預期: %s, 實際: %s', expected_sha, trade_sha)

            return is_valid

        except Exception as e:
            _logger.error('驗證 TradeSha 簽名時發生錯誤: %s', str(e))
            return False
