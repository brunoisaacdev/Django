from django.shortcuts import render
from django.http import HttpResponse

nomeLoja = "LigaSport"

def sobre(request):
    return render(request, 'core/sobre.html', {'nome_loja': nomeLoja})

def home(request):
    return render(request, 'core/home.html', {'nome_loja': nomeLoja})