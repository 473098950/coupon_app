from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from coupons.models import CouponRule, Redemption
from coupons.serializers import CouponRuleSerializer, RedemptionSerializer
from coupons.permissions import IsMerchant

class MerchantCouponViewSet(viewsets.ModelViewSet):
    queryset = CouponRule.objects.all()
    serializer_class = CouponRuleSerializer
    permission_classes = [IsMerchant]

class MerchantRedemptionViewSet(viewsets.ModelViewSet):
    queryset = Redemption.objects.all()
    serializer_class = RedemptionSerializer
    permission_classes = [IsMerchant]
