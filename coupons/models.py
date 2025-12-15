from django.contrib.auth.models import AbstractUser
from django.db import models

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

    def is_superadmin(self):
        return self.role == 'superadmin'

    def is_admin(self):
        return self.role == 'admin'

    def is_consumer(self):
        return self.role == 'consumer'

    def is_merchant(self):
        return self.role == 'merchant'
