# coupons/views/admin_views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from django.utils.timezone import now
from django.http import HttpResponse
from django.db.models.functions import TruncMonth
import csv
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

from coupons.models import Merchant, MembershipCard, Redemption, User
from coupons.serializers import MerchantSerializer, MembershipCardSerializer, RedemptionSerializer, UserSerializer
from coupons.permissions import IsAdminOrSuperAdmin


# ---------------------------
# 管理员登录接口
# ---------------------------
from rest_framework.views import APIView

class AdminLoginView(APIView):
    """
    管理员 / 超级管理员 登录接口
    """
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'error': '用户名和密码不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'error': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)
        if not (user.is_admin() or user.is_superadmin()):
            return Response({'error': '用户没有管理员权限'}, status=status.HTTP_403_FORBIDDEN)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })

# ---------------------------
# 管理员商家管理
# ---------------------------
class AdminMerchantViewSet(viewsets.ModelViewSet):
    queryset = Merchant.objects.select_related('user').all()
    serializer_class = MerchantSerializer
    permission_classes = [IsAdminOrSuperAdmin]

    http_method_names = ['get', 'post']
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['approved']
    search_fields = ['name', 'phone', 'credit_code']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        merchant = self.get_object()
        merchant.approved = True
        merchant.save(update_fields=['approved'])
        return Response({'detail': '商家已审核通过'})

    @action(detail=True, methods=['post'])
    def ban(self, request, pk=None):
        merchant = self.get_object()
        merchant.approved = False
        merchant.save(update_fields=['approved'])
        return Response({'detail': '商家已封禁'})

    @action(detail=False, methods=['get'])
    def merchant_count(self, request):
        return Response({'count': Merchant.objects.count()})

    @action(detail=False, methods=['get'])
    def card_count(self, request):
        return Response({'count': MembershipCard.objects.count()})

    @action(detail=False, methods=['get'])
    def active_card_count(self, request):
        count = Redemption.objects.values('membership_card').distinct().count()
        return Response({'count': count})

    @action(detail=False, methods=['get'])
    def month_active_cards(self, request):
        today = now()
        count = Redemption.objects.filter(
            created_at__year=today.year,
            created_at__month=today.month
        ).values('membership_card').distinct().count()
        return Response({'count': count})

    @action(detail=False, methods=['get'])
    def monthly_stats(self, request):
        qs = Redemption.objects.annotate(month=TruncMonth('created_at')) \
                               .values('month') \
                               .annotate(total=Count('id')) \
                               .order_by('month')
        return Response(qs)

    @action(detail=False, methods=['get'])
    def export_cards(self, request):
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

    @action(detail=True, methods=['get'])
    def export_merchant_report(self, request, pk=None):
        merchant = self.get_object()
        qs = Redemption.objects.filter(merchant=merchant).select_related('membership_card')
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
        commission_rate = 0.10
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
