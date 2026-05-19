from django import forms

from core.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "category",
            "description",
            "price_brl",
            "discount_percentage",
            "global_stock_quantity",
            "rating_average",
            "rating_count",
            "material",
            "care_instructions",
            "origin",
            "image",
        ]
        labels = {
            "name": "Nome",
            "category": "Categoria",
            "description": "Descricao",
            "price_brl": "Preco",
            "discount_percentage": "Desconto (%)",
            "global_stock_quantity": "Estoque",
            "rating_average": "Avaliacao media",
            "rating_count": "Quantidade de avaliacoes",
            "material": "Material",
            "care_instructions": "Cuidados",
            "origin": "Origem",
            "image": "Imagem static",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "admin-input"}),
            "category": forms.Select(attrs={"class": "admin-input"}),
            "description": forms.Textarea(attrs={"class": "admin-input", "rows": 5}),
            "price_brl": forms.NumberInput(attrs={"class": "admin-input", "step": "0.01", "min": "0"}),
            "discount_percentage": forms.NumberInput(attrs={"class": "admin-input", "min": "0", "max": "100"}),
            "global_stock_quantity": forms.NumberInput(attrs={"class": "admin-input", "min": "0"}),
            "rating_average": forms.NumberInput(attrs={"class": "admin-input", "step": "0.1", "min": "0", "max": "5"}),
            "rating_count": forms.NumberInput(attrs={"class": "admin-input", "min": "0"}),
            "material": forms.Textarea(attrs={"class": "admin-input", "rows": 3}),
            "care_instructions": forms.Textarea(attrs={"class": "admin-input", "rows": 3}),
            "origin": forms.TextInput(attrs={"class": "admin-input"}),
            "image": forms.TextInput(attrs={"class": "admin-input", "placeholder": "imagens/Blazer.webp"}),
        }
