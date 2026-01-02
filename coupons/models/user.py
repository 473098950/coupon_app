from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    自定义用户模型
    roles: 用户角色列表，一个用户可以同时是消费者和商家
    merchant_profile: 如果用户成为商家，则关联商家信息（可空）
    wallet: 用户钱包余额
    """
    roles = models.JSONField(default=list)  # ['consumer'] 或 ['consumer','merchant']
    merchant_profile = models.OneToOneField(
        'Merchant',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='user_account'
    )
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # 角色判断方法
    def is_superadmin(self):
        return 'superadmin' in self.roles

    def is_admin(self):
        return 'admin' in self.roles

    def is_consumer(self):
        return 'consumer' in self.roles

    def is_merchant(self):
        return 'merchant' in self.roles
