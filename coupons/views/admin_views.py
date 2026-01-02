from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from coupons.models import Merchant
from coupons.serializers import MerchantSerializer
from coupons.permissions import IsAdminOrSuperAdmin


class AdminMerchantViewSet(viewsets.ModelViewSet):
    """
    管理员/超级管理员管理商家
    """
    queryset = Merchant.objects.all()
    serializer_class = MerchantSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['approved']
    search_fields = ['name', 'address', 'contact_name']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def ban(self, request, pk=None):
        merchant = self.get_object()
        merchant.approved = False
        merchant.save()
        return Response({'status': '商家已封禁'}, status=status.HTTP_200_OK)
