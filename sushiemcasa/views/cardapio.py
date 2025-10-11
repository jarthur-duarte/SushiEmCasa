from django.shortcuts import render, redirect, get_object_or_404
from sushiemcasa.models import Produto, Categoria

# =========================================================================
# FUNÇÃO 1: CARDÁPIO (Homepage e Filtro)
# =========================================================================
def exibir_cardapio(request, categoria_slug=None): 
    # Busca todas as categorias (para exibir o menu de filtro)
    categorias = Categoria.objects.all()
    # Começa com todos os produtos
    produtos = Produto.objects.all() 
    categoria_selecionada = None
    
    # Lógica de Filtragem: Se um slug for fornecido na URL
    if categoria_slug:
        # Pega a categoria pelo slug (ou retorna 404)
        categoria = get_object_or_404(Categoria, slug=categoria_slug)
        
        # Filtra os produtos
        produtos = produtos.filter(categoria=categoria)
        categoria_selecionada = categoria.nome # Salva o nome para exibição
        
    context = {
        'produtos': produtos,
        'categorias': categorias, # Passa todas as categorias para o menu
        'categoria_selecionada': categoria_selecionada # Para destacar o filtro ativo
    }
    
    # Renderiza o seu template existente da homepage
    return render(request, 'sushiemcasa/homepage.html', context)
