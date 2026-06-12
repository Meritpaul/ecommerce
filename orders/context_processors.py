from .models import OrderItem
from django.db.models import Sum
from django.utils.timezone import now


def sales_data(request):
    today_items = OrderItem.objects.filter(
        order__created_at__date=now().date(),
        order__status='paid',
    ).select_related('order')

    total_sales    = sum(item.price * item.quantity for item in today_items)
    total_quantity = today_items.aggregate(Sum('quantity'))['quantity__sum'] or 0

    return {
        'today_sales':    total_sales,
        'today_quantity': total_quantity,
    }