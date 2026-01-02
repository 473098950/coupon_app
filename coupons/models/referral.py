from django.db import models
from django.conf import settings

class Referral(models.Model):
    """
    推荐奖励模型
    """
    referrer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='referrals_made', on_delete=models.CASCADE)
    referred_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='referrals_received', on_delete=models.CASCADE)
    reward_amount = models.DecimalField(max_digits=10, decimal_places=2, default=1.8)
    created_at = models.DateTimeField(auto_now_add=True)
    rewarded = models.BooleanField(default=False)
