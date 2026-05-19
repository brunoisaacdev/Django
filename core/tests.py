from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from core.models import Cart, Category, Order, Product, ProductVariant


@override_settings(ALLOWED_HOSTS=["localhost"])
class AccountAndOrderFlowTests(TestCase):
    def setUp(self):
        self.client.defaults["HTTP_HOST"] = "localhost"
        self.category = Category.objects.create(name="Mulher", slug="mulher")
        self.product = Product.objects.create(
            name="Blazer Teste",
            description="Produto para teste",
            price_brl=Decimal("299.90"),
            category=self.category,
            image="imagens/Blazer.webp",
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            size="M",
            color="Preto",
            stock_quantity=5,
        )

    def test_register_logs_user_in_and_opens_purchase_history(self):
        response = self.client.post(
            reverse("contato"),
            {
                "action": "register",
                "full_name": "Cliente Teste",
                "email": "cliente@example.com",
                "password": "senha12345",
            },
        )

        self.assertRedirects(response, reverse("minhas_compras"))
        self.assertTrue(get_user_model().objects.filter(email="cliente@example.com").exists())

        history_response = self.client.get(reverse("minhas_compras"))
        self.assertEqual(history_response.status_code, 200)

    def test_checkout_creates_order_and_order_items_for_logged_user(self):
        user = get_user_model().objects.create_user(
            username="comprador@example.com",
            email="comprador@example.com",
            password="senha12345",
            first_name="Comprador",
        )
        self.client.login(username="comprador@example.com", password="senha12345")

        self.client.post(
            reverse("add_carrinho", args=[self.product.id]),
            {"quantity": 2, "size": self.variant.size, "color": self.variant.color},
        )
        response = self.client.post(reverse("finalizar_venda"))

        self.assertRedirects(response, reverse("minhas_compras"))
        order = Order.objects.get(user=user)
        self.assertEqual(order.total, Decimal("599.80"))
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().product_name, "Blazer Teste")
        self.assertFalse(Cart.objects.get(user=user).is_active)

    def test_anonymous_checkout_redirects_to_login(self):
        response = self.client.post(reverse("finalizar_venda"))

        self.assertRedirects(response, f"{reverse('contato')}?next={reverse('carrinho')}")
        self.assertEqual(Order.objects.count(), 0)

    def test_product_search_filters_by_query(self):
        Product.objects.create(
            name="Bolsa Cognac",
            description="Acessorio em couro",
            price_brl=Decimal("499.90"),
            category=self.category,
        )

        response = self.client.get(reverse("produtos"), {"q": "blazer"})

        self.assertContains(response, "Blazer Teste")
        self.assertNotContains(response, "Bolsa Cognac")
        self.assertEqual(response.context["search_query"], "blazer")


@override_settings(ALLOWED_HOSTS=["localhost"])
class AdminItemManagementTests(TestCase):
    def setUp(self):
        self.client.defaults["HTTP_HOST"] = "localhost"
        self.category = Category.objects.create(name="Admin", slug="admin")
        self.product = Product.objects.create(
            name="Item Original",
            description="Descricao original",
            price_brl=Decimal("120.00"),
            category=self.category,
            global_stock_quantity=3,
            image="imagens/Blazer.webp",
        )
        User = get_user_model()
        self.admin_user = User.objects.create_user(
            username="admin@example.com",
            email="admin@example.com",
            password="senha12345",
            is_staff=True,
        )
        self.common_user = User.objects.create_user(
            username="cliente2@example.com",
            email="cliente2@example.com",
            password="senha12345",
        )

    def get_form_data(self, **overrides):
        data = {
            "name": "Item Novo",
            "category": self.category.id,
            "description": "Item cadastrado pela tela administrativa",
            "price_brl": "199.90",
            "discount_percentage": "10",
            "global_stock_quantity": "7",
            "rating_average": "4.5",
            "rating_count": "8",
            "material": "Algodao",
            "care_instructions": "Lavar a mao",
            "origin": "Brasil",
            "image": "imagens/Kit.webp",
        }
        data.update(overrides)
        return data

    def test_anonymous_user_is_redirected_from_admin_items(self):
        response = self.client.get(reverse("admin_itens"))

        self.assertRedirects(response, f"{reverse('contato')}?next={reverse('admin_itens')}")

    def test_common_user_cannot_view_or_create_admin_items(self):
        self.client.login(username="cliente2@example.com", password="senha12345")

        list_response = self.client.get(reverse("admin_itens"))
        create_response = self.client.post(reverse("admin_item_create"), self.get_form_data())

        self.assertEqual(list_response.status_code, 403)
        self.assertEqual(create_response.status_code, 403)
        self.assertFalse(Product.objects.filter(name="Item Novo").exists())

    def test_admin_can_create_update_and_delete_item(self):
        self.client.login(username="admin@example.com", password="senha12345")

        list_response = self.client.get(reverse("admin_itens"))
        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, "Item Original")

        create_response = self.client.post(reverse("admin_item_create"), self.get_form_data())
        self.assertRedirects(create_response, reverse("admin_itens"))
        created_product = Product.objects.get(name="Item Novo")
        self.assertEqual(created_product.global_stock_quantity, 7)

        update_response = self.client.post(
            reverse("admin_item_update", args=[created_product.id]),
            self.get_form_data(name="Item Atualizado", price_brl="249.90"),
        )
        self.assertRedirects(update_response, reverse("admin_itens"))
        created_product.refresh_from_db()
        self.assertEqual(created_product.name, "Item Atualizado")
        self.assertEqual(created_product.price_brl, Decimal("249.90"))

        delete_response = self.client.post(reverse("admin_item_delete", args=[created_product.id]))
        self.assertRedirects(delete_response, reverse("admin_itens"))
        self.assertFalse(Product.objects.filter(id=created_product.id).exists())

    def test_delete_route_has_no_confirmation_screen(self):
        self.client.login(username="admin@example.com", password="senha12345")

        response = self.client.get(reverse("admin_item_delete", args=[self.product.id]))

        self.assertRedirects(response, reverse("admin_itens"))
        self.assertTrue(Product.objects.filter(id=self.product.id).exists())
