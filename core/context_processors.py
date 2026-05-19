from django.db.models import Sum

from core.models import Cart


def cart_item_count(request):
    cart = None

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
    elif request.session.session_key:
        cart = Cart.objects.filter(session_key=request.session.session_key, is_active=True).first()

    count = 0
    if cart:
        count = cart.items.aggregate(total=Sum("quantity"))["total"] or 0

    return {"cart_item_count": count}
