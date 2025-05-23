from rest_framework import serializers
from .models import Category, Product, Order, OrderItem, OrderHistory
from .tasks import process_order_async


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'expiry_date', 'category', 'category_id']

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product')
    product_details = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product_id', 'quantity', 'product_details']

class BulkOrderSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        orders = []
        for order_data in validated_data:
            items_data = order_data.pop('items')
            order = Order.objects.create(**order_data)

            total = 0
            for item in items_data:
                product = item['product']
                quantity = item['quantity']
                if product.stock < quantity:
                    raise serializers.ValidationError(f"Insufficient stock for {product.name}")
                product.stock -= quantity
                product.save()
                OrderItem.objects.create(order=order, product=product, quantity=quantity)
                total += product.price * quantity

            order.total_price = total
            order.save()

            process_order_async.delay(order.id)
            orders.append(order)

        return orders
    
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        list_serializer_class = BulkOrderSerializer
        fields = ['id', 'customer_name', 'customer_email', 'customer_phone', 'delivery_address',
          'status', 'status_display', 'created_at', 'updated_at', 'last_transition_time',
          'total_price', 'items']
        read_only_fields = ['status', 'created_at', 'updated_at', 'last_transition_time', 'total_price']
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        # order = Order.objects.create(**validated_data)
        order = super().create(validated_data)

        total = 0
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']

            if product.stock < quantity:
                raise serializers.ValidationError(f"Insufficient stock for product {product.name}.")

            product.stock -= quantity
            product.save()

            OrderItem.objects.create(order=order, product=product, quantity=quantity)
            total += product.price * quantity

        order.total_price = total
        order.save()

        process_order_async.delay(order.id)

        return order

class OrderHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderHistory
        fields = ['previous_status', 'new_status', 'timestamp']


