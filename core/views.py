from decimal import Decimal
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout as auth_logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView, View

from core.forms import ProductForm
from core.models import Cart, CartItem, Order, OrderItem, Product, ProductVariant


nomeLoja = "LigaSport"


def get_or_create_active_user_cart(user):
    cart = Cart.objects.filter(user=user, is_active=True).order_by("-updated_at").first()
    if cart:
        return cart

    return Cart.objects.create(user=user, is_active=True)


def get_or_create_active_session_cart(session_key):
    cart = Cart.objects.filter(
        session_key=session_key,
        is_active=True,
        user__isnull=True,
    ).order_by("-updated_at").first()
    if cart:
        return cart

    return Cart.objects.create(session_key=session_key, is_active=True)


def merge_session_cart_into_user(session_key, user):
    if not session_key:
        return

    session_cart = (
        Cart.objects.filter(session_key=session_key, is_active=True, user__isnull=True)
        .prefetch_related("items")
        .first()
    )
    if not session_cart:
        return

    user_cart = get_or_create_active_user_cart(user)
    if session_cart.id == user_cart.id:
        return

    for item in session_cart.items.select_related("product", "variant"):
        cart_item, created = CartItem.objects.get_or_create(
            cart=user_cart,
            product=item.product,
            variant=item.variant,
            defaults={
                "quantity": item.quantity,
                "price_at_time": item.price_at_time,
            },
        )

        if not created:
            cart_item.quantity += item.quantity
            cart_item.price_at_time = item.price_at_time
            cart_item.save(update_fields=["quantity", "price_at_time"])

    session_cart.is_active = False
    session_cart.save(update_fields=["is_active", "updated_at"])


def get_safe_next_url(request, fallback_name="minhas_compras"):
    next_url = request.POST.get("next") or request.GET.get("next")
    fallback_url = reverse(fallback_name)

    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url

    return fallback_url


class CartMixin:
    def get_cart(self):
        request = self.request

        if request.user.is_authenticated:
            return get_or_create_active_user_cart(request.user)

        if not request.session.session_key:
            request.session.create()

        return get_or_create_active_session_cart(request.session.session_key)


class SobreView(TemplateView):
    template_name = "core/sobre.html"


class HomeView(TemplateView):
    template_name = "core/home.html"


class ProdutosListView(ListView):
    model = Product
    template_name = "core/produtos.html"
    context_object_name = "produtos"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("category")
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(category__name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "").strip()
        return context


class ContatoView(TemplateView):
    template_name = "core/contato.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next_url"] = self.request.GET.get("next", reverse("minhas_compras"))
        return context

    def post(self, request):
        action = request.POST.get("action")

        if action == "register":
            return self.register_user(request)

        if action == "login":
            return self.login_user(request)

        messages.error(request, "Escolha se deseja entrar ou criar uma conta.")
        return redirect("contato")

    def register_user(self, request):
        User = get_user_model()
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        next_url = get_safe_next_url(request)
        session_key = request.session.session_key

        if not full_name or not email or not password:
            messages.error(request, "Preencha nome, e-mail e senha para criar sua conta.")
            return redirect(f"{reverse('contato')}?{urlencode({'next': next_url})}")

        if User.objects.filter(username__iexact=email).exists() or User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Ja existe uma conta cadastrada com esse e-mail.")
            return redirect(f"{reverse('contato')}?{urlencode({'next': next_url})}")

        first_name, _, last_name = full_name.partition(" ")
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name[:150],
            last_name=last_name[:150],
        )
        login(request, user)
        merge_session_cart_into_user(session_key, user)
        messages.success(request, "Cadastro criado com sucesso. Voce ja esta logado.")

        return redirect(next_url)

    def login_user(self, request):
        User = get_user_model()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        next_url = get_safe_next_url(request)
        session_key = request.session.session_key

        if not email or not password:
            messages.error(request, "Informe e-mail e senha para entrar.")
            return redirect(f"{reverse('contato')}?{urlencode({'next': next_url})}")

        user = authenticate(request, username=email, password=password)
        if user is None:
            existing_user = User.objects.filter(email__iexact=email).first()
            if existing_user:
                user = authenticate(request, username=existing_user.get_username(), password=password)

        if user is None:
            messages.error(request, "E-mail ou senha invalidos.")
            return redirect(f"{reverse('contato')}?{urlencode({'next': next_url})}")

        login(request, user)
        merge_session_cart_into_user(session_key, user)
        messages.success(request, "Login realizado com sucesso.")

        return redirect(next_url)


class ProdutoDetalhesView(DetailView):
    model = Product
    template_name = "core/produto_detalhes.html"
    context_object_name = "produto"
    pk_url_kwarg = "id"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("images", "variants")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        variants = list(self.object.variants.all())
        sizes_order = ["XS", "S", "M", "L", "XL"]
        sizes = sorted({variant.size for variant in variants}, key=sizes_order.index)
        colors = []

        for color in {variant.color for variant in variants if variant.color}:
            colors.append(
                {
                    "name": color,
                    "style": self.get_color_style(color),
                }
            )

        context["imagens"] = self.object.images.all()
        context["variant_sizes"] = sizes
        context["variant_colors"] = sorted(colors, key=lambda color: color["name"])
        return context

    def get_color_style(self, color):
        color_map = {
            "Marfim": "#f5f1eb",
            "Ivory": "#f5f1eb",
            "Bege": "#d4c5b9",
            "Greige": "#b8ad9f",
            "Cognac": "#a66f42",
            "Cinza": "#3d3d3d",
            "Preto": "#2a2a2a",
        }

        return color_map.get(color, "#d4c5b9")


class AddCarrinhoView(CartMixin, View):
    def post(self, request, id):
        produto = get_object_or_404(Product, id=id)
        cart = self.get_cart()
        quantity = self.get_quantity()
        variant = self.get_variant(produto)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=produto,
            variant=variant,
            defaults={
                "quantity": quantity,
                "price_at_time": produto.final_price,
            },
        )

        if not created:
            item.quantity += quantity
            item.price_at_time = produto.final_price
            item.save()

        return redirect("carrinho")

    def get(self, request, id):
        return redirect("carrinho")

    def get_quantity(self):
        try:
            quantity = int(self.request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            quantity = 1

        return max(quantity, 1)

    def get_variant(self, produto):
        if not produto.variants.exists():
            return None

        return get_object_or_404(
            ProductVariant,
            product=produto,
            size=self.request.POST.get("size"),
            color=self.request.POST.get("color"),
        )


class FinalizarVendaView(CartMixin, View):
    def post(self, request):
        if not request.user.is_authenticated:
            messages.info(request, "Entre ou crie uma conta para finalizar e salvar sua compra.")
            query = urlencode({"next": reverse("carrinho")})
            return redirect(f"{reverse('contato')}?{query}")

        cart = self.get_cart()
        itens = list(cart.items.select_related("product", "product__category", "variant"))

        if not itens:
            messages.error(request, "Adicione um produto ao carrinho antes de finalizar.")
            return redirect("carrinho")

        total = sum((item.subtotal for item in itens), Decimal("0.00"))

        with transaction.atomic():
            pedido = Order.objects.create(
                user=request.user,
                full_name=request.user.get_full_name() or request.user.get_username(),
                email=request.user.email,
                total=total,
            )

            OrderItem.objects.bulk_create(
                [
                    OrderItem(
                        order=pedido,
                        product=item.product,
                        product_name=item.product.name,
                        category_name=item.product.category.name if item.product.category else "",
                        image=item.product.image,
                        variant_size=item.variant.size if item.variant else "",
                        variant_color=item.variant.color if item.variant else "",
                        quantity=item.quantity,
                        price_at_time=item.price_at_time,
                    )
                    for item in itens
                ]
            )

            cart.is_active = False
            cart.save(update_fields=["is_active", "updated_at"])

        messages.success(request, "Compra finalizada e salva no seu historico.")

        return redirect("minhas_compras")


class RemoverCarrinhoItemView(CartMixin, View):
    def post(self, request, id):
        cart = self.get_cart()
        item = get_object_or_404(CartItem, id=id, cart=cart)
        item.delete()

        return redirect("carrinho")


class CarrinhoView(CartMixin, TemplateView):
    template_name = "core/carrinho.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.get_cart()
        itens = cart.items.select_related("product", "variant").all()

        context["itens"] = itens
        context["total"] = sum(item.subtotal for item in itens)
        context["venda_finalizada"] = self.request.GET.get("finalizado") == "1"
        return context


class MinhasComprasView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "core/minhas_compras.html"
    context_object_name = "pedidos"
    login_url = "contato"

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items")
            .order_by("-created_at")
        )


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "contato"

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("Acesso permitido apenas para administradores.")

        return super().handle_no_permission()


class AdminItemListView(AdminRequiredMixin, ListView):
    model = Product
    template_name = "core/admin_item_list.html"
    context_object_name = "produtos"

    def get_queryset(self):
        queryset = Product.objects.select_related("category").order_by("name")
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(category__name__icontains=search_query)
                | Q(image__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "").strip()
        context["total_produtos"] = Product.objects.count()
        context["total_sem_estoque"] = Product.objects.filter(global_stock_quantity=0).count()
        return context


class AdminItemCreateView(AdminRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "core/admin_item_form.html"
    success_url = reverse_lazy("admin_itens")

    def form_valid(self, form):
        messages.success(self.request, "Item cadastrado com sucesso.")
        return super().form_valid(form)


class AdminItemUpdateView(AdminRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "core/admin_item_form.html"
    context_object_name = "produto"
    success_url = reverse_lazy("admin_itens")

    def form_valid(self, form):
        messages.success(self.request, "Item atualizado com sucesso.")
        return super().form_valid(form)


class AdminItemDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        produto = get_object_or_404(Product, pk=pk)
        produto.delete()
        messages.success(request, "Item excluido com sucesso.")
        return redirect("admin_itens")

    def get(self, request, pk):
        return redirect("admin_itens")


class LogoutView(View):
    def get(self, request):
        return self.logout(request)

    def post(self, request):
        return self.logout(request)

    def logout(self, request):
        auth_logout(request)
        messages.success(request, "Voce saiu da sua conta.")
        return redirect("home")
