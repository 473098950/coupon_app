from rest_framework import serializers
from .models import User, Merchant, MembershipCard, CouponRule, Redemption

class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = '__all__'

class MembershipCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipCard
        fields = '__all__'

class CouponRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouponRule
        fields = '__all__'

class RedemptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Redemption
        fields = '__all__'
