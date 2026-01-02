from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
import random
# 导入模型
from coupons.models.membership_card import MembershipCard
from coupons.models.redemption import Redemption
from coupons.models.referral import Referral
from coupons.models.merchant import Merchant

# 导入序列化器
from coupons.serializers import (
    MerchantSerializer,
    MembershipCardSerializer,
    RedemptionSerializer,
    ReferralSerializer,
    CouponRuleSerializer,
    UserSerializer,
    UserRegisterSerializer
)

from coupons.permissions import IsAdminOrSuperAdmin, IsMerchant, IsConsumer, IsSuperAdmin

class MembershipCardViewSet(viewsets.ModelViewSet):
    queryset = MembershipCard.objects.all()
    serializer_class = MembershipCardSerializer
    permission_classes = [IsConsumer]

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

class RedemptionViewSet(viewsets.ModelViewSet):
    queryset = Redemption.objects.all()
    serializer_class = RedemptionSerializer
    permission_classes = [IsConsumer]

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

        first_use_discount = Decimal('0.0')
        if card.card_count > 0:
            first_use_discount = Decimal('1.0')
            card.card_count -= 1
            card.save()

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

class ReferralViewSet(viewsets.ModelViewSet):
    queryset = Referral.objects.all()
    serializer_class = ReferralSerializer
    permission_classes = [IsConsumer]

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

class ConsumerApplyMerchantViewSet(viewsets.ViewSet):
    """
    消费者申请成为商家接口
    """
    permission_classes = [IsConsumer]

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
        user.merchant = merchant
        user.save()

        return Response({"message": "已成为商家，等待资质上传和审核"})
