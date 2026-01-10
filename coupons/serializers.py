from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from decimal import Decimal

from coupons.models.user import User
from coupons.models.merchant import Merchant
from coupons.models.membership_card import MembershipCard
from coupons.models.coupon_rule import CouponRule
from coupons.models.redemption import Redemption
from coupons.models.referral import Referral

# ---------------------------
# 用户序列化器
# ---------------------------
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    merchant_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'roles', 'wallet', 'merchant_profile']
        read_only_fields = ['wallet', 'merchant_profile']

    def get_merchant_profile(self, obj):
        if hasattr(obj, 'merchant_profile') and obj.merchant_profile:
            return {
                'id': obj.merchant_profile.id,
                'name': obj.merchant_profile.name,
                'phone': getattr(obj.merchant_profile, 'phone', '')
            }
        return None

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
            raise serializers.ValidationError({"password": "两次输入密码不一致"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )


# ---------------------------
# 商家序列化器
# ---------------------------
class MerchantSerializer(serializers.ModelSerializer):
    contract = serializers.SerializerMethodField()
    contact_id = serializers.SerializerMethodField()
    qr_code = serializers.SerializerMethodField()
    shop_images = serializers.SerializerMethodField()
    first_order_enabled = serializers.SerializerMethodField()
    store_address = serializers.SerializerMethodField()
    store_hours = serializers.SerializerMethodField()

    class Meta:
        model = Merchant
        fields = [
            'id', 'user', 'name', 'phone', 'credit_code', 'license', 'contract',
            'approved', 'created_at', 'store_address', 'contact_name', 'contact_id',
            'store_hours', 'store_type', 'logo', 'shop_images', 'first_order_enabled',
            'commission_rate', 'qr_code'
        ]
        read_only_fields = ['approved', 'created_at', 'qr_code']

    def get_contract(self, obj):
        return None

    def get_contact_id(self, obj):
        return None

    def get_qr_code(self, obj):
        return None

    def get_shop_images(self, obj):
        return getattr(obj, 'store_photos', [])

    def get_first_order_enabled(self, obj):
        return getattr(obj, 'first_order_active', False)

    def get_store_address(self, obj):
        return getattr(obj, 'address', '')

    def get_store_hours(self, obj):
        return getattr(obj, 'business_hours', '')


# ---------------------------
# 会员卡序列化器
# ---------------------------
class MembershipCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipCard
        fields = ['id', 'user', 'card_count', 'purchased_at', 'expired_at', 'used_first_order_rule']


# ---------------------------
# 优惠规则序列化器
# ---------------------------
class CouponRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouponRule
        fields = ['id', 'merchant', 'rule_type', 'threshold', 'discount_amount', 'discount_rate', 'created_at']


# ---------------------------
# 核销记录序列化器
# ---------------------------
class RedemptionSerializer(serializers.ModelSerializer):
    membership_card = serializers.SerializerMethodField()
    coupon_rule = serializers.SerializerMethodField()

    class Meta:
        model = Redemption
        fields = ['id', 'user', 'merchant', 'membership_card', 'coupon_rule', 'amount_paid', 'created_at']

    def get_membership_card(self, obj):
        if obj.membership_card:
            return {
                'id': obj.membership_card.id,
                'card_count': obj.membership_card.card_count
            }
        return None

    def get_coupon_rule(self, obj):
        if obj.coupon_rule:
            return {
                'id': obj.coupon_rule.id,
                'rule_type': obj.coupon_rule.rule_type,
                'discount_amount': float(getattr(obj.coupon_rule, 'discount_amount', 0)),
                'discount_rate': float(getattr(obj.coupon_rule, 'discount_rate', 0))
            }
        return None


# ---------------------------
# 裂变营销 / 推荐奖励序列化器
# ---------------------------
class ReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referral
        fields = ['id', 'referrer', 'referred_user', 'reward_amount', 'created_at', 'rewarded']


# ---------------------------
# JWT 自定义序列化器
# ---------------------------
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    支持两种登录方式：
    1. username + password（网页端 / API 通用）
    2. wechat_openid（小程序登录）
    登录返回 token 的同时，返回 roles 和默认角色
    """
    openid = serializers.CharField(write_only=True, required=False)

    def validate(self, attrs):
        openid = attrs.pop('openid', None)
        if openid:
            # 微信登录
            try:
                user = User.objects.get(wechat_openid=openid)
            except User.DoesNotExist:
                raise serializers.ValidationError("微信用户不存在，请先注册")
            self.user = user
        else:
            # 用户名 + 密码登录
            return super().validate(attrs)

        # 生成 token
        refresh = self.get_token(self.user)
        access = refresh.access_token

        # 默认角色选择逻辑
        roles = self.user.roles
        default_role = 'consumer' if 'consumer' in roles else roles[0]

        return {
            'refresh': str(refresh),
            'access': str(access),
            'username': self.user.username,
            'roles': roles,
            'default_role': default_role,
        }
