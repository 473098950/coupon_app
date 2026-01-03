from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from coupons.models import CouponRule, MembershipCard, Redemption
from coupons.serializers import CouponRuleSerializer, RedemptionSerializer
from coupons.permissions import IsMerchant


class MerchantCouponViewSet(viewsets.ModelViewSet):
    """
    商家端优惠规则管理接口
    """
    serializer_class = CouponRuleSerializer
    permission_classes = [IsMerchant]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        merchant = getattr(self.request.user, 'merchant_profile', None)
        if not merchant:
            return CouponRule.objects.none()
        return CouponRule.objects.filter(merchant=merchant)

    @action(detail=False, methods=['post'])
    def set_first_order_rule(self, request):
        """
        设置首单优惠规则
        """
        merchant = getattr(request.user, 'merchant_profile', None)
        if not merchant:
            return Response({'error': '用户不是商家'}, status=status.HTTP_400_BAD_REQUEST)

        rule_type = request.data.get('rule_type')
        if rule_type not in ['discount_amount', 'discount_rate']:
            return Response({'error': 'rule_type 必须为 discount_amount 或 discount_rate'}, status=status.HTTP_400_BAD_REQUEST)

        # 检查是否已存在首单优惠
        existing_rule = CouponRule.objects.filter(
            merchant=merchant,
            rule_type__in=['discount_amount', 'discount_rate']
        ).first()
        if existing_rule:
            return Response({'error': '首单优惠规则已存在，只能修改'}, status=status.HTTP_400_BAD_REQUEST)

        if rule_type == 'discount_amount':
            try:
                target_price = float(request.data.get('target_price'))
                discount_amount = float(request.data.get('discount_amount'))
            except (TypeError, ValueError):
                return Response({'error': '请提供有效的 target_price 和 discount_amount'}, status=status.HTTP_400_BAD_REQUEST)

            rule = CouponRule.objects.create(
                merchant=merchant,
                rule_type='discount_amount',
                threshold=target_price,
                discount_amount=discount_amount
            )
            actual_price = max(target_price - discount_amount, 0)

        else:  # discount_rate
            try:
                discount_rate = float(request.data.get('discount_rate'))
                if not (0 < discount_rate <= 1):
                    raise ValueError
            except (TypeError, ValueError):
                return Response({'error': '折扣率必须是 0~1 之间的数字'}, status=status.HTTP_400_BAD_REQUEST)

            rule = CouponRule.objects.create(
                merchant=merchant,
                rule_type='discount_rate',
                discount_rate=discount_rate
            )
            actual_price = None  # 需要前端提供 original_price 才能计算

        serializer = self.get_serializer(rule)
        return Response({
            'rule': serializer.data,
            'actual_price': actual_price
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def apply_first_order(self, request, pk=None):
        """
        核销首单优惠
        """
        merchant = getattr(request.user, 'merchant_profile', None)
        if not merchant:
            return Response({'error': '用户不是商家'}, status=status.HTTP_400_BAD_REQUEST)

        rule = CouponRule.objects.filter(
            merchant=merchant,
            rule_type__in=['discount_amount', 'discount_rate']
        ).first()
        if not rule:
            return Response({'error': '未设置首单优惠规则'}, status=status.HTTP_400_BAD_REQUEST)

        card_id = request.data.get('membership_card_id')
        if not card_id:
            return Response({'error': '请提供 membership_card_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            card = MembershipCard.objects.get(id=card_id)
        except MembershipCard.DoesNotExist:
            return Response({'error': '会员卡不存在'}, status=status.HTTP_400_BAD_REQUEST)

        if getattr(card, 'used_first_order_rule', False):
            return Response({'error': '此会员卡首单优惠已使用'}, status=status.HTTP_400_BAD_REQUEST)

        if rule.rule_type == 'discount_amount':
            actual_price = max(rule.threshold - rule.discount_amount, 0)
        else:
            try:
                original_price = float(request.data.get('original_price'))
            except (TypeError, ValueError):
                return Response({'error': '请提供有效的 original_price'}, status=status.HTTP_400_BAD_REQUEST)
            actual_price = round(original_price * rule.discount_rate, 2)

        card.used_first_order_rule = True
        card.save()

        return Response({
            'membership_card_id': card.id,
            'actual_price': actual_price
        }, status=status.HTTP_200_OK)


class MerchantRedemptionViewSet(viewsets.ModelViewSet):
    """
    商家端核销记录管理接口
    """
    serializer_class = RedemptionSerializer
    permission_classes = [IsMerchant]
    http_method_names = ['get']

    def get_queryset(self):
        merchant = getattr(self.request.user, 'merchant_profile', None)
        if not merchant:
            return Redemption.objects.none()
        return Redemption.objects.filter(merchant=merchant)
