from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from core.models import Product, ProductImage
from core.models import Cart, CartItem 
from django.shortcuts import get_object_or_404

def get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            is_active=True
        )
    else:
        if not request.session.session_key:
            request.session.create()

        cart, created = Cart.objects.get_or_create(
            session_key=request.session.session_key,
            is_active=True
        )

    return cart

nomeLoja = "LigaSport"

def sobre(request):
    return render(request, 'core/sobre.html')

def home(request):
    return render(request, 'core/home.html')

def produtos(request):
    produtos = Product.objects.all()
    # productimage = ProductImage.objects.filter(product_id=id)
    return render(request, 'core/produtos.html',{'produtos':produtos})

def contato(request):
    return render(request, 'core/contato.html')

def produto_detalhes(request,id):
    produto = Product.objects.get(id=id)
    productimage = ProductImage.objects.filter(product_id=id)
    return render(request, 'core/produto_detalhes.html', {'produto':produto, 'imagens':productimage})


def add_carrinho(request, id):
    if request.method == "POST":
        produto = get_object_or_404(Product, id=id)

        cart = get_cart(request)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=produto,
            variant=None,
            defaults={
                'price_at_time': produto.final_price
            }
        )

        if not created:
            item.quantity += 1
            item.save()

    return redirect('carrinho')

def carrinho(request):
    cart = get_cart(request)
    itens = cart.items.all

    total = sum(item.subtotal for item in itens) if itens else 0

    return render(request, 'core/carrinho.html', {
        'itens': itens,
        'total': total
    })
