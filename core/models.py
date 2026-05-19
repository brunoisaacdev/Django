import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "categoria"
        verbose_name_plural = "categorias"

    def __str__(self):
        return self.name


class Product(models.Model):
    sku = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price_brl = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    rating_average = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    material = models.TextField(blank=True)
    care_instructions = models.TextField(blank=True)
    origin = models.CharField(max_length=100, blank=True)
    global_stock_quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "produto"
        verbose_name_plural = "produtos"

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        if self.discount_percentage > 0:
            discount = Decimal(self.discount_percentage) / Decimal("100")
            return self.price_brl * (Decimal("1") - discount)
        return self.price_brl


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Caminho da imagem em static. Ex: imagens/Blazer.webp",
    )
    alt_text = models.CharField(max_length=255, blank=True)
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "imagem do produto"
        verbose_name_plural = "imagens dos produtos"

    def __str__(self):
        return self.alt_text or self.image


class ProductVariant(models.Model):
    SIZE_CHOICES = [("XS", "XS"), ("S", "S"), ("M", "M"), ("L", "L"), ("XL", "XL")]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    size = models.CharField(max_length=10, choices=SIZE_CHOICES)
    color = models.CharField(max_length=50)
    stock_quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("product", "size", "color")
        verbose_name = "variacao do produto"
        verbose_name_plural = "variacoes dos produtos"

    def __str__(self):
        return f"{self.product.name} - {self.size} - {self.color}"


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "carrinho"
        verbose_name_plural = "carrinhos"

    def __str__(self):
        if self.user:
            return f"Carrinho de {self.user}"
        return f"Carrinho sessao {self.session_key}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "product", "variant")
        verbose_name = "item do carrinho"
        verbose_name_plural = "itens do carrinho"

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    @property
    def subtotal(self):
        return self.quantity * self.price_at_time


class Order(models.Model):
    STATUS_CHOICES = [
        ("finalizado", "Finalizado"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="finalizado")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"

    def __str__(self):
        return f"Pedido #{self.id} - {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=255)
    category_name = models.CharField(max_length=100, blank=True)
    image = models.CharField(max_length=255, blank=True)
    variant_size = models.CharField(max_length=10, blank=True)
    variant_color = models.CharField(max_length=50, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "item do pedido"
        verbose_name_plural = "itens do pedido"

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    @property
    def subtotal(self):
        return self.quantity * self.price_at_time
