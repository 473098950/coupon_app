from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

# 导入模型（按你拆分后的 models 文件夹路径）
from coupons.models.user import User
from coupons.models.merchant import Merchant
from coupons.models.membership_card import MembershipCard
from coupons.models.coupon_rule import CouponRule
from coupons.models.redemption import Redemption
from coupons.models.referral import Referral

# --------------------------- 用户序列化器 ---------------------------
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'roles', 'wallet', 'merchant_profile']

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
        return User.objects.create_user(**validated_data)


# --------------------------- 商家序列化器 ---------------------------
from rest_framework import serializers
from .models.merchant import Merchant

class MerchantSerializer(serializers.ModelSerializer):
    # 模型里没有的字段用方法字段返回 None 或自定义内容
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

    # 以下方法返回可选值或 None，保证 Swagger 正常生成
    def get_contract(self, obj):
        return None

    def get_contact_id(self, obj):
        return None

    def get_qr_code(self, obj):
        return None

    def get_shop_images(self, obj):
        # 返回门店照片列表
        return obj.store_photos

    def get_first_order_enabled(self, obj):
        return obj.first_order_active

    def get_store_address(self, obj):
        return obj.address

    def get_store_hours(self, obj):
        return obj.business_hours



# --------------------------- 会员卡序列化器 ---------------------------
class MembershipCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipCard
        fields = ['id', 'user', 'card_count', 'purchased_at', 'expired_at', 'used_first_order_rule']


# --------------------------- 优惠规则序列化器 ---------------------------
class CouponRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouponRule
        fields = ['id', 'merchant', 'rule_type', 'threshold', 'discount_amount', 'discount_percent', 'created_at']


# --------------------------- 核销记录序列化器 ---------------------------
class RedemptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Redemption
        fields = ['id', 'user', 'merchant', 'membership_card', 'coupon_rule', 'amount_paid', 'created_at']


# --------------------------- 裂变营销/推荐奖励序列化器 ---------------------------
class ReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referral
        fields = ['id', 'referrer', 'referred_user', 'reward_amount', 'created_at', 'rewarded']
