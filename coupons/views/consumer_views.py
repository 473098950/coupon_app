# coupons/views/consumer_views.py

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
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
    UserSerializer,
    MerchantSerializer
)
from coupons.permissions import IsConsumer


# -------------------- 用户注册和登录 --------------------
class UserRegisterView(APIView):
    permission_classes = []

    @swagger_auto_schema(
        operation_summary="用户注册",
        operation_description="创建新用户，返回用户信息",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='用户名'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='密码'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='邮箱，可选')
            }
        ),
        responses={
            201: openapi.Response(
                description="注册成功",
                schema=UserSerializer()
            ),
            400: openapi.Response(
                description="注册失败，例如用户名已存在",
                examples={"application/json": {"error": "用户名已存在"}}
            )
        }
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')

        if not username or not password:
            return Response({'error': '用户名和密码必填'}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({'error': '用户名已存在'}, status=400)

        user = User.objects.create_user(username=username, password=password, email=email)
        return Response(UserSerializer(user).data, status=201)


class UserLoginView(APIView):
    permission_classes = []

    @swagger_auto_schema(
        operation_summary="用户登录",
        operation_description="用户名 + 密码登录，返回用户信息",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='用户名'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='密码')
            }
        ),
        responses={
            200: openapi.Response(
                description="登录成功",
                schema=UserSerializer()
            ),
            400: openapi.Response(
                description="用户名或密码错误",
                examples={"application/json": {"error": "用户名或密码错误"}}
            )
        }
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': '用户名或密码错误'}, status=400)
        return Response(UserSerializer(user).data)


# -------------------- 会员卡管理 --------------------
class MembershipCardViewSet(viewsets.ModelViewSet):
    serializer_class = MembershipCardSerializer
    permission_classes = [IsConsumer]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user = getattr(self.request, 'user', None)
        if user and user.is_authenticated:
            return MembershipCard.objects.filter(user=user)
        return MembershipCard.objects.none()

    @swagger_auto_schema(
        operation_summary="购买会员卡",
        operation_description="消费者购买一张会员卡",
        responses={
            201: openapi.Response(description="购买成功", schema=MembershipCardSerializer()),
            401: openapi.Response(description="未登录", examples={"application/json": {"error": "未登录"}})
        }
    )
    @action(detail=False, methods=['post'])
    def buy(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({'error': '未登录'}, status=401)

        card = MembershipCard.objects.create(user=user, card_count=1)
        serializer = self.get_serializer(card)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary="续费会员卡",
        operation_description="增加会员卡数量",
        responses={
            200: openapi.Response(description="续费成功", schema=MembershipCardSerializer())
        }
    )
    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        card = self.get_object()
        card.card_count += 1
        card.save()
        serializer = self.get_serializer(card)
        return Response(serializer.data)


# -------------------- 核销接口 --------------------
class RedemptionViewSet(viewsets.ModelViewSet):
    serializer_class = RedemptionSerializer
    permission_classes = [IsConsumer]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user = getattr(self.request, 'user', None)
        if user and user.is_authenticated:
            return Redemption.objects.filter(user=user)
        return Redemption.objects.none()

    @swagger_auto_schema(
        operation_summary="核销会员卡",
        operation_description="用户在商家处使用会员卡进行消费",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['merchant_id', 'amount'],
            properties={
                'merchant_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='商家ID'),
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='消费金额')
            }
        ),
        responses={
            200: openapi.Response(
                description="核销成功",
                examples={
                    "application/json": {
                        "actual_amount": 5.0,
                        "first_use_discount": 1.0,
                        "old_customer_discount": 1.2,
                        "redemption": {
                            "id": 1,
                            "user": 2,
                            "merchant": 1,
                            "membership_card": 1,
                            "amount_paid": 5.0,
                            "created_at": "2026-01-10T00:00:00Z"
                        }
                    }
                }
            ),
            401: openapi.Response(description="未登录", examples={"application/json": {"error": "未登录"}})
        }
    )
    @action(detail=False, methods=['post'])
    def redeem(self, request):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return Response({'error': '未登录'}, status=401)

        try:
            merchant_id = int(request.data.get('merchant_id'))
            amount = Decimal(request.data.get('amount', 0))
        except Exception:
            return Response({'error': '参数格式错误'}, status=400)

        try:
            merchant = Merchant.objects.get(id=merchant_id)
        except Merchant.DoesNotExist:
            return Response({'error': '商家不存在'}, status=400)

        try:
            card = MembershipCard.objects.filter(user=user).latest('created_at')
        except MembershipCard.DoesNotExist:
            return Response({'error': '用户没有有效会员卡'}, status=400)

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


# -------------------- 推荐奖励接口 --------------------
class ReferralViewSet(viewsets.ModelViewSet):
    serializer_class = ReferralSerializer
    permission_classes = [IsConsumer]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user = getattr(self.request, 'user', None)
        if user and user.is_authenticated:
            return Referral.objects.filter(referrer=user)
        return Referral.objects.none()

    @action(detail=False, methods=['post'])
    def reward(self, request):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return Response({'error': '未登录'}, status=401)

        try:
            referrer_id = int(request.data.get('referrer_id'))
            referred_user_id = int(request.data.get('referred_user_id'))
        except Exception:
            return Response({'error': '参数格式错误'}, status=400)

        try:
            referrer = user if user.id == referrer_id else None
            referred_user = User.objects.get(id=referred_user_id)
        except User.DoesNotExist:
            return Response({'error': '用户不存在'}, status=400)

        referral = Referral.objects.create(referrer=referrer, referred_user=referred_user)
        if referrer:
            referrer.wallet += Decimal('1.8')
            referrer.save()
        referral.rewarded = True
        referral.save()
        serializer = self.get_serializer(referral)
        return Response(serializer.data)


# -------------------- 消费者申请商家 --------------------
class ConsumerApplyMerchantViewSet(viewsets.ModelViewSet):
    serializer_class = MerchantSerializer
    permission_classes = [IsConsumer]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user = getattr(self.request, 'user', None)
        if user and user.is_authenticated:
            return Merchant.objects.filter(applicants=user)
        return Merchant.objects.none()

    @swagger_auto_schema(
        operation_summary="申请商家",
        operation_description="消费者申请加入商家",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['merchant_id'],
            properties={
                'merchant_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='商家ID')
            }
        ),
        responses={
            200: openapi.Response(description="申请成功", schema=MerchantSerializer()),
            401: openapi.Response(description="未登录", examples={"application/json": {"error": "未登录"}}),
            400: openapi.Response(description="商家不存在", examples={"application/json": {"error": "商家不存在"}})
        }
    )
    @action(detail=False, methods=['post'])
    def apply(self, request):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return Response({'error': '未登录'}, status=401)

        merchant_id = request.data.get('merchant_id')
        try:
            merchant = Merchant.objects.get(id=merchant_id)
        except Merchant.DoesNotExist:
            return Response({'error': '商家不存在'}, status=400)

        # 假设 Merchant 模型有 ManyToManyField applicants
        merchant.applicants.add(user)
        merchant.save()
        serializer = self.get_serializer(merchant)
        return Response(serializer.data)
