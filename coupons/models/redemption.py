from django.db import models
from django.conf import settings
from .merchant import Merchant
from .membership_card import MembershipCard
from .coupon_rule import CouponRule

class Redemption(models.Model):
    """
    核销记录模型
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    membership_card = models.ForeignKey(MembershipCard, on_delete=models.CASCADE)
    coupon_rule = models.ForeignKey(CouponRule, null=True, blank=True, on_delete=models.SET_NULL)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
