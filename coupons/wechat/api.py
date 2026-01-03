import requests
from .config import WECHAT_APPID, WECHAT_SECRET, WECHAT_MCH_ID, WECHAT_API_KEY

class WeChatAPI:
    """微信接口类"""

    @staticmethod
    def get_session(js_code):
        """用前端传来的 code 换取 openid 和 session_key"""
        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            "appid": WECHAT_APPID,
            "secret": WECHAT_SECRET,
            "js_code": js_code,
            "grant_type": "authorization_code"
        }
        resp = requests.get(url, params=params)
        return resp.json()  # 包含 openid, session_key

    @staticmethod
    def send_payment(openid, amount, out_trade_no):
        """调用微信支付下单接口（示意）"""
        # 实际使用需要签名和 xml 封装
        return {"status": "ok", "openid": openid, "amount": amount, "out_trade_no": out_trade_no}
