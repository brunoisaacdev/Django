from django.contrib import admin

from .models import Cart, CartItem, Category, Order, OrderItem, Product, ProductImage, ProductVariant


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price_brl",
        "discount_percentage",
        "global_stock_quantity",
    )
    list_filter = ("category",)
    search_fields = ("name", "description", "sku")
    readonly_fields = ("sku",)
    inlines = [ProductImageInline, ProductVariantInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image", "is_main", "order")
    list_filter = ("is_main",)
    search_fields = ("product__name", "image", "alt_text")


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "size", "color", "stock_quantity")
    list_filter = ("size", "color")
    search_fields = ("product__name", "color")


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("added_at",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("user__username", "session_key")
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "variant", "quantity", "price_at_time", "subtotal")
    list_filter = ("added_at",)
    search_fields = ("product__name", "cart__session_key", "cart__user__username")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product",
        "product_name",
        "category_name",
        "image",
        "variant_size",
        "variant_color",
        "quantity",
        "price_at_time",
        "subtotal",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "email", "total", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "email", "full_name", "items__product_name")
    readonly_fields = ("created_at",)
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product_name", "quantity", "price_at_time", "subtotal")
    search_fields = ("product_name", "category_name", "order__user__username")
