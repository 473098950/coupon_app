from rest_framework import serializers
from .models import User, Merchant, MembershipCard, CouponRule, Redemption, Referral

# ---------------------------
# 用户序列化器
# ---------------------------
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'wallet', 'merchant']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

# ---------------------------
# 商家序列化器
# ---------------------------
class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = [
            'id', 'name', 'address', 'bank_account', 'contact_name', 'contact_id',
            'license', 'contract', 'approved', 'created_at'
        ]
        read_only_fields = ['approved', 'created_at']

# ---------------------------
# 会员卡序列化器
# ---------------------------
class MembershipCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipCard
        fields = ['id', 'user', 'card_count', 'created_at']

# ---------------------------
# 优惠规则序列化器
# ---------------------------
class CouponRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouponRule
        fields = ['id', 'merchant', 'rule_type', 'threshold', 'discount_amount', 'discount_percent', 'created_at']

# ---------------------------
# 核销记录序列化器
# ---------------------------
class RedemptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Redemption
        fields = ['id', 'user', 'merchant', 'membership_card', 'coupon_rule', 'amount_paid', 'created_at']

# ---------------------------
# 裂变营销序列化器
# ---------------------------
class ReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referral
        fields = ['id', 'referrer', 'referred_user', 'reward_amount', 'created_at', 'rewarded']
