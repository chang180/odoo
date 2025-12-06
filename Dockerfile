FROM odoo:latest

# 安裝藍新金流支付模組所需的 Python 套件
USER root
RUN pip3 install --no-cache-dir --break-system-packages "pycryptodome>=3.19.0"
USER odoo
