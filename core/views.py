from django.shortcuts import render
from django.http import HttpResponse

nomeLoja = "LigaSport"

def sobre(request):
    return render(request, 'core/sobre.html')

def home(request):
    return render(request, 'core/home.html')

def produtos(request):
    return render(request, 'core/produtos.html')

def contato(request):
    return render(request, 'core/contato.html')

def produto_detalhes(request):
    return render(request, 'core/produto_detalhes.html')