from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, filters, generics, status
from .models import Category, Product, Order, OrderHistory
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer, OrderHistorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['status', 'customer_name', 'customer_email']

class DelayedOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(status='delayed').order_by('-last_transition_time')

class OrderHistoryView(generics.ListAPIView):
    serializer_class = OrderHistorySerializer

    def get_queryset(self):
        order_id = self.kwargs['order_id']
        return OrderHistory.objects.filter(order_id=order_id).order_by('timestamp')

class BulkOrderCreateView(APIView):
    def post(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response({"detail": "Expected a list of orders."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = OrderSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
print("SERIALIZERS LOADED OK ✅")