from django.urls import path
from .views import StockViewSet

# Make sure to add this viewset to your router in urls.py
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'stocks', StockViewSet, basename='stock')
urlpatterns = router.urls
