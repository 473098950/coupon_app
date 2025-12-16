from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, Merchant, MembershipCard, CouponRule, Redemption
from .serializers import MerchantSerializer, MembershipCardSerializer, CouponRuleSerializer, RedemptionSerializer

# 商家管理
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

# 会员卡管理
class MembershipCardViewSet(viewsets.ModelViewSet):
    queryset = MembershipCard.objects.all()
    serializer_class = MembershipCardSerializer

    @action(detail=True, methods=['get'])
    def remaining(self, request, pk=None):
        card = self.get_object()
        return Response({'remaining_count': card.card_count})

# 优惠规则管理
class CouponRuleViewSet(viewsets.ModelViewSet):
    queryset = CouponRule.objects.all()
    serializer_class = CouponRuleSerializer

# 核销接口
class RedemptionViewSet(viewsets.ModelViewSet):
    queryset = Redemption.objects.all()
    serializer_class = RedemptionSerializer

    @action(detail=False, methods=['post'])
    def redeem(self, request):
        """
        输入用户ID, 商家ID, 付款金额
        返回计算后的实际付款金额
        """
        user = request.user
        merchant_id = request.data.get('merchant_id')
        amount = float(request.data.get('amount', 0))
        # TODO: 实现首单核销和老客户立减计算
        # 示例返回
        return Response({'actual_amount': amount, 'message': '优惠逻辑待实现'})
