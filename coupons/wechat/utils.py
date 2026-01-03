import qrcode
import random
import string

def generate_qrcode(data, filename=None):
    """生成二维码，保存为文件或返回 qrcode 对象"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    if filename:
        img.save(filename)
    return img

def random_string(length=12):
    """生成随机字符串"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))
