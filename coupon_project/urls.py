from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

def home(request):
    return HttpResponse("Welcome to Coupon Backend!")
urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api/', include('coupons.urls')),  # 新增
]
