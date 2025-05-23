from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, OrderViewSet, DelayedOrderListView, OrderHistoryView, BulkOrderCreateView

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('orders/bulk/', BulkOrderCreateView.as_view(), name='bulk-order-create'),
    path('orders/delayed/', DelayedOrderListView.as_view(), name='delayed-orders'),
    path('orders/<int:order_id>/history/', OrderHistoryView.as_view(), name='order-history'),
    path('', include(router.urls)),
]
