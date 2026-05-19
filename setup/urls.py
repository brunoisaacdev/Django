"""
URL configuration for setup project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from core.views import (
    AddCarrinhoView,
    AdminItemCreateView,
    AdminItemDeleteView,
    AdminItemListView,
    AdminItemUpdateView,
    CarrinhoView,
    ContatoView,
    FinalizarVendaView,
    HomeView,
    LogoutView,
    MinhasComprasView,
    ProdutoDetalhesView,
    ProdutosListView,
    RemoverCarrinhoItemView,
    SobreView,
)



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('sobre/', SobreView.as_view(), name='sobre'),
    path('produtos/', ProdutosListView.as_view(), name='produtos'),
    path('administrativo/itens/', AdminItemListView.as_view(), name='admin_itens'),
    path('administrativo/itens/novo/', AdminItemCreateView.as_view(), name='admin_item_create'),
    path('administrativo/itens/<int:pk>/editar/', AdminItemUpdateView.as_view(), name='admin_item_update'),
    path('administrativo/itens/<int:pk>/excluir/', AdminItemDeleteView.as_view(), name='admin_item_delete'),
    path('contato/', ContatoView.as_view(), name='contato'),
    path('minhas-compras/', MinhasComprasView.as_view(), name='minhas_compras'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('produto_detalhes/<int:id>/', ProdutoDetalhesView.as_view(), name='produto_detalhes'),
    path('add-carrinho/<int:id>/', AddCarrinhoView.as_view(), name='add_carrinho'),
    path('remover-carrinho/<int:id>/', RemoverCarrinhoItemView.as_view(), name='remover_carrinho_item'),
    path('carrinho/', CarrinhoView.as_view(), name='carrinho'),
    path('finalizar-venda/', FinalizarVendaView.as_view(), name='finalizar_venda'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
