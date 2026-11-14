"""Formulários do painel da loja (substituem as telas do Admin completo)."""
from django import forms
from django.utils.text import slugify

from sushiemcasa.models import BannerPromocional, Categoria, Produto


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'categoria', 'descricao', 'preco', 'imagem', 'disponivel', 'destaque']
        labels = {
            'destaque': 'Feature at the top of the menu',
            'nome': 'Name',
            'categoria': 'Category',
            'descricao': 'Description',
            'preco': 'Price ($)',
            'imagem': 'Photo',
            'disponivel': 'Show on the menu',
        }
        help_texts = {
            'imagem': 'Square photos look best (at least 800×800).',
            'disponivel': 'Uncheck to hide the product without deleting it.',
            'destaque': 'Shows this product\'s photo and price in the big banner at the top of the menu. '
                        'Only one product can be featured: checking this one unchecks the previous.',
        }

    def clean(self):
        dados = super().clean()
        if dados.get('destaque') and not dados.get('disponivel'):
            self.add_error('destaque', 'A featured product must also be shown on the menu.')
        return dados
        widgets = {
            'imagem': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'slug']
        labels = {'nome': 'Name', 'slug': 'Link name'}
        help_texts = {'slug': 'Used in the menu link. Leave blank to create it from the name.'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False

    def clean_slug(self):
        slug = self.cleaned_data.get('slug') or slugify(self.cleaned_data.get('nome') or '')
        if not slug:
            raise forms.ValidationError('Enter a name.')
        existe = Categoria.objects.filter(slug=slug).exclude(pk=self.instance.pk).exists()
        if existe:
            raise forms.ValidationError('Another category already uses this link name.')
        return slug


class BannerForm(forms.ModelForm):
    class Meta:
        model = BannerPromocional
        fields = ['titulo', 'descricao', 'imagem', 'produto_vinculado',
                  'preco_promocional', 'preco_antigo', 'ordem', 'ativo']
        labels = {
            'titulo': 'Title',
            'descricao': 'Short description',
            'imagem': 'Image',
            'produto_vinculado': 'Product added to the cart',
            'preco_promocional': 'Deal price ($)',
            'preco_antigo': 'Original price ($)',
            'ordem': 'Display order',
            'ativo': 'Show on the menu',
        }
        help_texts = {
            'imagem': 'Recommended: 1200×400 or larger.',
            'produto_vinculado': 'Optional. Without a product the special has no "Add" button.',
            'preco_antigo': 'Optional. Shown crossed out next to the deal price.',
            'ordem': 'Lower numbers appear first.',
        }
        widgets = {
            'imagem': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }
