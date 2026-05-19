from decimal import Decimal

from django.core.management.base import BaseCommand

from core.models import Category, Product, ProductImage, ProductVariant


class Command(BaseCommand):
    help = "Cadastra categorias, produtos, imagens estaticas e variacoes iniciais."

    def handle(self, *args, **options):
        categories = {
            "mulher": "Mulher",
            "masculino": "Masculino",
            "acessorios": "Acessorios",
        }

        category_objects = {}
        for slug, name in categories.items():
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name},
            )
            category_objects[slug] = category

        products = [
            {
                "name": "Blazer Oversize Marfim",
                "category": "mulher",
                "description": "Blazer oversize em alfaiataria leve, pensado para compor looks elegantes e confortaveis.",
                "price_brl": Decimal("5450.00"),
                "discount_percentage": 10,
                "rating_average": 4.9,
                "rating_count": 127,
                "material": "Linho belga com forro em algodao.",
                "care_instructions": "Lavar a mao em agua fria e nao usar alvejante.",
                "origin": "Brasil",
                "global_stock_quantity": 8,
                "image": "imagens/Blazer.webp",
                "color": "Marfim",
                "sizes": ["XS", "S", "M", "L", "XL"],
            },
            {
                "name": "Terno Greige Estruturado",
                "category": "masculino",
                "description": "Terno estruturado de caimento classico, ideal para ocasioes formais e producoes refinadas.",
                "price_brl": Decimal("6200.00"),
                "discount_percentage": 0,
                "rating_average": 4.8,
                "rating_count": 89,
                "material": "La fria com acabamento premium.",
                "care_instructions": "Lavagem a seco profissional.",
                "origin": "Brasil",
                "global_stock_quantity": 6,
                "image": "imagens/Terno.webp",
                "color": "Greige",
                "sizes": ["S", "M", "L", "XL"],
            },
            {
                "name": "Vestido Drapeado Ivory",
                "category": "mulher",
                "description": "Vestido drapeado com silhueta fluida e acabamento delicado para eventos especiais.",
                "price_brl": Decimal("5450.00"),
                "discount_percentage": 5,
                "rating_average": 4.9,
                "rating_count": 103,
                "material": "Viscose acetinada com toque macio.",
                "care_instructions": "Lavar a mao pelo avesso e secar a sombra.",
                "origin": "Brasil",
                "global_stock_quantity": 10,
                "image": "imagens/Vestido.webp",
                "color": "Ivory",
                "sizes": ["XS", "S", "M", "L"],
            },
            {
                "name": "Kit Acessorios Cognac",
                "category": "acessorios",
                "description": "Kit de acessorios em tom cognac para finalizar producoes com textura e personalidade.",
                "price_brl": Decimal("3100.00"),
                "discount_percentage": 0,
                "rating_average": 4.7,
                "rating_count": 64,
                "material": "Couro com ferragens metalicas.",
                "care_instructions": "Limpar com pano seco e guardar em local arejado.",
                "origin": "Brasil",
                "global_stock_quantity": 15,
                "image": "imagens/Kit.webp",
                "color": "",
                "sizes": [],
            },
        ]

        created_count = 0
        updated_count = 0

        for product_data in products:
            sizes = product_data.pop("sizes")
            color = product_data.pop("color")
            category_slug = product_data.pop("category")

            product, created = Product.objects.update_or_create(
                name=product_data["name"],
                defaults={
                    **product_data,
                    "category": category_objects[category_slug],
                },
            )

            ProductImage.objects.update_or_create(
                product=product,
                image=product.image,
                defaults={
                    "alt_text": product.name,
                    "is_main": True,
                    "order": 0,
                },
            )

            for size in sizes:
                ProductVariant.objects.update_or_create(
                    product=product,
                    size=size,
                    color=color,
                    defaults={
                        "stock_quantity": max(product.global_stock_quantity // len(sizes), 1),
                    },
                )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed concluido: {created_count} produtos criados e {updated_count} atualizados."
            )
        )
