from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Order, OrderHistory
import time

def record_transition(order, new_status):
    print(f"[HISTORY] {order.id}: {order.status} → {new_status}")
    OrderHistory.objects.create(
        order=order,
        previous_status=order.status,
        new_status=new_status
    )
    order.status = new_status
    order.last_transition_time = timezone.now()
    order.save()

@shared_task
def process_order_async(order_id):
    try:
        order = Order.objects.get(id=order_id)

        time.sleep(5)
        record_transition(order, 'processing')

        time.sleep(5)
        record_transition(order, 'shipped')

        time.sleep(5)
        record_transition(order, 'delivered')

    except Order.DoesNotExist:
        pass

@shared_task
def detect_stale_orders():
    threshold = timezone.now() - timedelta(hours=1)
    stale_orders = Order.objects.filter(
        status__in=['processing', 'shipped'],
        last_transition_time__lt=threshold
    )

    for order in stale_orders:
        order.status = 'delayed'  # You can use 'failed' if preferred
        order.last_transition_time = timezone.now()
        order.save()
        print(f"Order {order.id} marked as delayed due to staleness.")

