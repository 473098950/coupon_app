from django.db import models
from .merchant import Merchant

class CouponRule(models.Model):
    """
    优惠规则模型
    """
    RULE_TYPE_CHOICES = [
        ('full_reduce', '满减'),
        ('discount', '折扣'),
        ('old_customer', '老客户立减'),
    ]
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPE_CHOICES)
    threshold = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
