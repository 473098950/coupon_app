from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime

# 用户角色
ROLE_CHOICES = [
    ('superadmin', '超级管理员'),
    ('admin', '管理员'),
    ('consumer', '消费者'),
    ('merchant', '商家用户'),
]

class User(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='consumer')
    merchant = models.ForeignKey('Merchant', null=True, blank=True, on_delete=models.SET_NULL)
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def is_superadmin(self):
        return self.role == 'superadmin'

    def is_admin(self):
        return self.role == 'admin'

    def is_consumer(self):
        return self.role == 'consumer'

    def is_merchant(self):
        return self.role == 'merchant'

class Merchant(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    bank_account = models.CharField(max_length=50, blank=True, null=True)
    contact_name = models.CharField(max_length=50, blank=True, null=True)
    contact_id = models.CharField(max_length=50, blank=True, null=True)
    license = models.CharField(max_length=100, blank=True, null=True)
    contract = models.CharField(max_length=100, blank=True, null=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class MembershipCard(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    card_count = models.PositiveIntegerField(default=1)  # 首单核销次数
    purchased_at = models.DateTimeField(auto_now_add=True)  # 购买时间
    expired_at = models.DateTimeField(default=datetime.datetime(2026, 3, 3, 23, 59, 59))  # 过期时间

class CouponRule(models.Model):
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

class Redemption(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE)
    membership_card = models.ForeignKey(MembershipCard, on_delete=models.CASCADE)
    coupon_rule = models.ForeignKey(CouponRule, null=True, blank=True, on_delete=models.SET_NULL)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class Referral(models.Model):
    referrer = models.ForeignKey(User, related_name='referrals_made', on_delete=models.CASCADE)
    referred_user = models.ForeignKey(User, related_name='referrals_received', on_delete=models.CASCADE)
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2, default=1.8)
    created_at = models.DateTimeField(auto_now_add=True)
    rewarded = models.BooleanField(default=False)
