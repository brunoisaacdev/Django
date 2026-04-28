from django.shortcuts import render
from django.http import HttpResponse

from core.models import Product, ProductImage

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

def carrinho(request):
    return render(request, 'core/carrinho.html')