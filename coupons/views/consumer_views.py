from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from decimal import Decimal
import random

from coupons.models import MembershipCard, Redemption, Referral, Merchant, User
from coupons.serializers import (
    MembershipCardSerializer,
    RedemptionSerializer,
    ReferralSerializer,
    UserSerializer
)
from coupons.permissions import IsConsumer


# -------------------- 用户注册和登录 --------------------
class UserRegisterView(APIView):
    """
    用户注册接口（消费者）
    """
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')

        if not username or not password:
            return Response({'error': '用户名和密码必填'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': '用户名已存在'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    """
    用户登录接口（消费者）
    """
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': '用户名和密码必填'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': '用户名或密码错误'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(user)
        return Response(serializer.data)


# -------------------- 会员卡管理 --------------------
class MembershipCardViewSet(viewsets.ModelViewSet):
    """
    会员卡管理接口（消费者）
    """
    queryset = MembershipCard.objects.all()
    serializer_class = MembershipCardSerializer
    permission_classes = [IsConsumer]
    http_method_names = ['get', 'post']

    @action(detail=False, methods=['post'])
    def buy(self, request):
        user = request.user
        card = MembershipCard.objects.create(user=user, card_count=1)
        serializer = self.get_serializer(card)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        card = self.get_object()
        card.card_count += 1
        card.save()
        serializer = self.get_serializer(card)
        return Response(serializer.data)


# -------------------- 核销接口 --------------------
class RedemptionViewSet(viewsets.ModelViewSet):
    """
    核销接口（消费者）
    """
    queryset = Redemption.objects.all()
    serializer_class = RedemptionSerializer
    permission_classes = [IsConsumer]
    http_method_names = ['get', 'post']

    @action(detail=False, methods=['post'])
    def redeem(self, request):
        user = request.user
        merchant_id = request.data.get('merchant_id')
        amount = Decimal(request.data.get('amount', 0))

        try:
            merchant = Merchant.objects.get(id=merchant_id)
        except Merchant.DoesNotExist:
            return Response({'error': '商家不存在'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            card = MembershipCard.objects.filter(user=user).latest('created_at')
        except MembershipCard.DoesNotExist:
            return Response({'error': '用户没有有效会员卡'}, status=status.HTTP_400_BAD_REQUEST)

        # 首单折扣
        first_use_discount = Decimal('0.0')
        if card.card_count > 0:
            first_use_discount = Decimal('1.0')
            card.card_count -= 1
            card.save()

        # 老客户折扣
        old_customer_discount = Decimal(str(round(random.uniform(0.5, 1.0), 2)))
        actual_amount = max(amount - (first_use_discount + old_customer_discount), Decimal('0.0'))

        redemption = Redemption.objects.create(
            user=user,
            merchant=merchant,
            membership_card=card,
            amount_paid=actual_amount
        )
        serializer = self.get_serializer(redemption)
        return Response({
            'actual_amount': float(actual_amount),
            'first_use_discount': float(first_use_discount),
            'old_customer_discount': float(old_customer_discount),
            'redemption': serializer.data
        })


# -------------------- 推荐奖励接口 --------------------
class ReferralViewSet(viewsets.ModelViewSet):
    """
    推荐奖励接口（消费者）
    """
    queryset = Referral.objects.all()
    serializer_class = ReferralSerializer
    permission_classes = [IsConsumer]
    http_method_names = ['get', 'post']

    @action(detail=False, methods=['post'])
    def reward(self, request):
        referrer_id = request.data.get('referrer_id')
        referred_user_id = request.data.get('referred_user_id')

        try:
            referrer = request.user if request.user.id == int(referrer_id) else None
            referred_user = User.objects.get(id=referred_user_id)
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=status.HTTP_400_BAD_REQUEST)

        referral = Referral.objects.create(referrer=referrer, referred_user=referred_user)
        referrer.wallet += Decimal('1.8')
        referrer.save()
        referral.rewarded = True
        referral.save()
        serializer = self.get_serializer(referral)
        return Response(serializer.data)


# -------------------- 消费者申请成为商家 --------------------
class ConsumerApplyMerchantViewSet(viewsets.ViewSet):
    """
    消费者申请成为商家接口
    """
    permission_classes = [IsConsumer]
    http_method_names = ['post']

    @action(detail=False, methods=['post'])
    def apply(self, request):
        user = request.user
        if "merchant" in user.roles:
            return Response({"error": "您已经是商家"}, status=400)

        name = request.data.get("name")
        phone = request.data.get("phone")
        if not name or not phone:
            return Response({"error": "请填写店铺名称和联系方式"}, status=400)

        merchant = Merchant.objects.create(user=user, name=name, phone=phone)
        user.roles.append("merchant")
        user.merchant_profile = merchant
        user.save()

        return Response({"message": "已成为商家，等待资质上传和审核"})
