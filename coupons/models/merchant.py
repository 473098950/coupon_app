from django.db import models
from django.conf import settings


class Merchant(models.Model):
    """
    商家模型（核心业务模型）
    支持营业执照、法人身份证、门店照片、店铺类型、抽成比例、二维码、售卡统计、流水统计
    """
    STORE_TYPE_CHOICES = [
        ('clothing', '服装鞋饰'),
        ('food', '餐饮美食'),
        ('entertainment', '休闲娱乐'),
        ('supermarket', '商超便利'),
        ('digital', '数码家电'),
        ('beauty', '美妆个护'),
        ('home', '家居生活'),
        ('baby', '母婴亲子'),
        ('sports', '运动户外'),
        ('health', '健康医药'),
        ('auto', '汽车出行'),
        ('education', '教育培训'),
        ('pet', '宠物生活'),
        ('hardware', '建筑五金'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='merchant_info'
    )
    name = models.CharField(max_length=100, help_text="商家名称")
    phone = models.CharField(max_length=20, default='00000000000', help_text="联系电话")
    credit_code = models.CharField(max_length=50, blank=True, null=True, help_text="社会统一信用代码")

    # 上传文件
    license = models.FileField(upload_to='licenses/', blank=True, null=True, help_text="营业执照（图片或PDF，不超过20M）")
    id_card = models.FileField(upload_to='id_cards/', blank=True, null=True, help_text="法人身份证（图片，不超过2M）")
    store_photos = models.JSONField(default=list, blank=True, help_text="门店照片列表（图片）")
    logo = models.FileField(upload_to='logos/', blank=True, null=True, help_text="LOGO图片")
    promo_images = models.JSONField(default=list, blank=True, help_text="宣传图片列表")

    # 店铺信息
    contact_name = models.CharField(max_length=50, blank=True, null=True, help_text="联系人姓名")
    business_hours = models.CharField(max_length=50, blank=True, null=True, help_text="营业时间")
    address = models.CharField(max_length=200, blank=True, null=True, help_text="店铺地址")
    store_type = models.CharField(max_length=20, choices=STORE_TYPE_CHOICES, blank=True, null=True,
                                  help_text="店铺类型")

    # 核心业务统计
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.08, help_text="抽成比例，默认8%")
    total_card_sold = models.PositiveIntegerField(default=0, help_text="售卡数量")
    total_card_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="售卡收入")
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="总流水金额")
    total_redemptions = models.PositiveIntegerField(default=0, help_text="总核销次数")
    avg_order_value = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="平均客单价")

    # 当日营业数据
    today_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="今日营业额")
    today_orders = models.PositiveIntegerField(default=0, help_text="今日客单量")
    today_avg_order_value = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="今日客单价")

    # 活动开关
    first_order_active = models.BooleanField(default=True, help_text="首单优惠是否开启")

    approved = models.BooleanField(default=False, help_text="是否审核通过")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
