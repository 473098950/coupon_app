from django.db import models
from django.conf import settings
import datetime

class MembershipCard(models.Model):
    """
    会员卡模型
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    card_count = models.PositiveIntegerField(default=1, help_text="可核销次数")
    purchased_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(default=datetime.datetime(2026, 3, 3, 23, 59, 59))
    used_first_order_rule = models.BooleanField(default=False, help_text="是否已使用首单优惠规则")
