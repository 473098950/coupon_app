from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from django.utils.timezone import now
from django.http import HttpResponse
from django.db.models.functions import TruncMonth

import csv

from coupons.models.merchant import Merchant
from coupons.models.membership_card import MembershipCard
from coupons.models.redemption import Redemption

# 序列化器导入
from coupons.serializers import (
    MerchantSerializer,
    MembershipCardSerializer,
    RedemptionSerializer,
    ReferralSerializer,
    CouponRuleSerializer,
    UserSerializer,
    UserRegisterSerializer
)
# 权限类导入
from coupons.permissions import IsAdminOrSuperAdmin, IsMerchant, IsConsumer, IsSuperAdmin

class AdminMerchantViewSet(viewsets.ModelViewSet):
    """
    管理员 / 超级管理员 商家管理接口

    管理员能力：
    - 商家列表 / 详情
    - 商家搜索、过滤、排序
    - 查看商家数据、统计、导出

    超级管理员额外能力：
    - 审核商家
    - 封禁 / 解封商家
    """

    queryset = Merchant.objects.select_related('user').all()
    serializer_class = MerchantSerializer
    permission_classes = [IsAdminOrSuperAdmin]

    # ===== 列表过滤 / 搜索 / 排序 =====
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # 按审核状态过滤
    filterset_fields = ['approved']

    # 搜索字段
    search_fields = [
        'name',          # 商家名称
        'phone',         # 联系电话
        'credit_code',   # 社会统一信用代码
    ]

    # 排序
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    # =========================
    # 超级管理员：审核商家
    # =========================
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        审核通过商家
        """
        merchant = self.get_object()
        merchant.approved = True
        merchant.save(update_fields=['approved'])

        return Response({'detail': '商家已审核通过'})

    # =========================
    # 超级管理员：封禁商家
    # =========================
    @action(detail=True, methods=['post'])
    def ban(self, request, pk=None):
        """
        封禁商家（停用）
        """
        merchant = self.get_object()
        merchant.approved = False
        merchant.save(update_fields=['approved'])

        return Response({'detail': '商家已封禁'})

    # =========================
    # 管理员：商家数量
    # =========================
    @action(detail=False, methods=['get'])
    def merchant_count(self, request):
        """
        返回商家总数量
        """
        return Response({
            'count': Merchant.objects.count()
        })

    # =========================
    # 管理员：会员卡总数量
    # =========================
    @action(detail=False, methods=['get'])
    def card_count(self, request):
        """
        返回会员卡总数量
        """
        return Response({
            'count': MembershipCard.objects.count()
        })

    # =========================
    # 管理员：已激活会员卡数量
    # =========================
    @action(detail=False, methods=['get'])
    def active_card_count(self, request):
        """
        有核销记录的会员卡视为已激活
        """
        count = (
            Redemption.objects
            .values('membership_card')
            .distinct()
            .count()
        )
        return Response({'count': count})

    # =========================
    # 管理员：当月激活数量
    # =========================
    @action(detail=False, methods=['get'])
    def month_active_cards(self, request):
        """
        当前月份激活的会员卡数量
        """
        today = now()
        count = (
            Redemption.objects
            .filter(
                created_at__year=today.year,
                created_at__month=today.month
            )
            .values('membership_card')
            .distinct()
            .count()
        )
        return Response({'count': count})

    # =========================
    # 管理员：按月份统计核销数
    # =========================
    @action(detail=False, methods=['get'])
    def monthly_stats(self, request):
        """
        按月份统计核销次数
        """
        qs = (
            Redemption.objects
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Count('id'))
            .order_by('month')
        )
        return Response(qs)

    # =========================
    # 管理员：导出会员卡数据
    # =========================
    @action(detail=False, methods=['get'])
    def export_cards(self, request):
        """
        导出会员卡数据 CSV
        字段：
        - 卡片ID
        - 用户ID
        - 激活时间
        - 是否已使用首单
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="membership_cards.csv"'

        writer = csv.writer(response)
        writer.writerow(['卡片ID', '用户ID', '购买时间', '首单是否已使用'])

        for card in MembershipCard.objects.select_related('user'):
            writer.writerow([
                card.id,
                card.user_id,
                card.purchased_at,
                '是' if card.used_first_order_rule else '否'
            ])

        return response

    # =========================
    # 管理员：商家经营数据报表
    # =========================
    @action(detail=True, methods=['get'])
    def export_merchant_report(self, request, pk=None):
        """
        导出指定商家的经营数据（JSON，可前端转 Excel）

        返回：
        - 消费记录
        - 汇总信息（流水、佣金）
        """
        merchant = self.get_object()
        qs = Redemption.objects.filter(
            merchant=merchant
        ).select_related('membership_card')

        records = []
        total_amount = 0

        for r in qs:
            total_amount += float(r.amount_paid)
            records.append({
                'membership_card_id': r.membership_card_id,
                'date': r.created_at,
                'amount_paid': r.amount_paid,
                'is_first_order': r.membership_card.used_first_order_rule,
            })

        commission_rate = 0.10  # 平台抽成 10%
        commission = round(total_amount * commission_rate, 2)

        return Response({
            'merchant': merchant.name,
            'records': records,
            'summary': {
                'total_amount': total_amount,
                'commission_rate': commission_rate,
                'commission': commission,
            }
        })
