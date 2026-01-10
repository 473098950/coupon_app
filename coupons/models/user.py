from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    自定义用户模型

    属性：
    - roles: 用户角色列表，一个用户可以同时是消费者和商家 ['consumer', 'merchant', 'admin', 'superadmin']
    - merchant_profile: 如果用户成为商家，则关联商家信息（可空）
    - wallet: 用户钱包余额
    - wechat_openid: 微信ID，全局唯一
    - phone: 手机号
    """
    wechat_openid = models.CharField(max_length=128, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    roles = models.JSONField(default=list)  # ['consumer'] 或 ['consumer','merchant']
    merchant_profile = models.OneToOneField(
        'Merchant',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='user_account'
    )
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    REQUIRED_FIELDS = []  # AbstractUser 默认要求 email，可留空
    USERNAME_FIELD = 'username'  # 登录用 username

    # ---------------- 角色判断属性 ----------------
    @property
    def is_superadmin(self):
        return 'superadmin' in self.roles

    @property
    def is_admin(self):
        return 'admin' in self.roles

    @property
    def is_consumer(self):
        return 'consumer' in self.roles

    @property
    def is_merchant(self):
        return 'merchant' in self.roles

    # ---------------- 角色管理方法 ----------------
    def add_role(self, role_name):
        if role_name not in self.roles:
            self.roles.append(role_name)
            self.save()

    def remove_role(self, role_name):
        if role_name in self.roles:
            self.roles.remove(role_name)
            self.save()

    # ---------------- 微信/手机号工具 ----------------
    def bind_wechat(self, openid):
        if not self.wechat_openid:
            self.wechat_openid = openid
            self.save()

    def bind_phone(self, phone):
        if not self.phone:
            self.phone = phone
            self.save()

    # ---------------- 钱包操作 ----------------
    def add_wallet(self, amount):
        self.wallet += amount
        self.save()

    def deduct_wallet(self, amount):
        if amount > self.wallet:
            raise ValueError("余额不足")
        self.wallet -= amount
        self.save()

    # ---------------- 调试显示 ----------------
    def __str__(self):
        return f"{self.username} ({', '.join(self.roles)})"
