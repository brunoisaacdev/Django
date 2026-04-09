from django.shortcuts import render
from django.http import HttpResponse

nomeLoja = "LigaSport"

def sobre(request):
    return render(request, 'core/sobre.html', {'nome_loja': nomeLoja})

def home(request):
    return render(request, 'core/home.html', {'nome_loja': nomeLoja})

def produtos(request):
    return render(request, 'core/produtos.html', {'nome_loja': nomeLoja})

def contato(request):
    return render(request, 'core/contato.html', {'nome_loja': nomeLoja})
