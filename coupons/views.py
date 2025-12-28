from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from decimal import Decimal
import random

from .models import User, Merchant, MembershipCard, CouponRule, Redemption, Referral
from .serializers import UserSerializer, MerchantSerializer, MembershipCardSerializer, CouponRuleSerializer, RedemptionSerializer, ReferralSerializer

# ---------------------------
# 用户管理
# ---------------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# ---------------------------
# 商家管理
# ---------------------------
class MerchantViewSet(viewsets.ModelViewSet):
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superadmin() or user.is_admin():
            return Merchant.objects.all()
        if user.is_merchant():
            return Merchant.objects.filter(id=user.merchant.id)
        return Merchant.objects.none()

# ---------------------------
# 会员卡管理
# ---------------------------
class MembershipCardViewSet(viewsets.ModelViewSet):
    queryset = MembershipCard.objects.all()
    serializer_class = MembershipCardSerializer

    @action(detail=False, methods=['post'])
    def buy(self, request):
        user = request.user
        expired_at = timezone.datetime(2026, 3, 3, 23, 59, 59)
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

# ---------------------------
# 优惠规则管理
# ---------------------------
class CouponRuleViewSet(viewsets.ModelViewSet):
    queryset = CouponRule.objects.all()
    serializer_class = CouponRuleSerializer

# ---------------------------
# 核销管理
# ---------------------------
class RedemptionViewSet(viewsets.ModelViewSet):
    queryset = Redemption.objects.all()
    serializer_class = RedemptionSerializer

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

        # 首单核销逻辑
        first_use_discount = Decimal('0.0')
        if card.card_count > 0:
            first_use_discount = Decimal('1.0')
            card.card_count -= 1
            card.save()

        # 老客户随机优惠
        old_customer_discount = Decimal(str(round(random.uniform(0.5, 1.0), 2)))

        total_discount = first_use_discount + old_customer_discount
        actual_amount = max(amount - total_discount, Decimal('0.0'))

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

# ---------------------------
# 裂变营销
# ---------------------------
class ReferralViewSet(viewsets.ModelViewSet):
    queryset = Referral.objects.all()
    serializer_class = ReferralSerializer

    @action(detail=False, methods=['post'])
    def reward(self, request):
        referrer_id = request.data.get('referrer_id')
        referred_user_id = request.data.get('referred_user_id')
        try:
            referrer = User.objects.get(id=referrer_id)
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
