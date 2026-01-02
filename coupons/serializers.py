from rest_framework import serializers
from .models import User, Merchant, MembershipCard, CouponRule, Redemption, Referral
from django.contrib.auth.password_validation import validate_password

# --------------------------- 用户序列化器 ---------------------------
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

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)

# --------------------------- 商家序列化器 ---------------------------
class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = [
            'id', 'name', 'address', 'bank_account', 'contact_name', 'contact_id',
            'license', 'contract', 'approved', 'created_at'
        ]
        read_only_fields = ['approved', 'created_at']

# --------------------------- 会员卡序列化器 ---------------------------
class MembershipCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipCard
        fields = ['id', 'user', 'card_count', 'created_at']

# --------------------------- 优惠规则 ---------------------------
class CouponRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouponRule
        fields = ['id', 'merchant', 'rule_type', 'threshold', 'discount_amount', 'discount_percent', 'created_at']

# --------------------------- 核销记录 ---------------------------
class RedemptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Redemption
        fields = ['id', 'user', 'merchant', 'membership_card', 'coupon_rule', 'amount_paid', 'created_at']

# --------------------------- 裂变营销 ---------------------------
class ReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referral
        fields = ['id', 'referrer', 'referred_user', 'reward_amount', 'created_at', 'rewarded']
