from django.shortcuts import render, redirect, get_object_or_404
from sushiemcasa.models import Produto, Categoria

# =========================================================================
# FUNÇÃO 1: CARDÁPIO (Homepage e Filtro)
# =========================================================================
def exibir_cardapio(request, categoria_slug=None): 
   
    categorias = Categoria.objects.all()
    
    produtos = Produto.objects.all() 
    categoria_selecionada = None
    
  
    if categoria_slug:
        
        categoria = get_object_or_404(Categoria, slug=categoria_slug)
        
        produtos = produtos.filter(categoria=categoria)
        categoria_selecionada = categoria.nome 
        
    context = {
        'produtos': produtos,
        'categorias': categorias, 
        'categoria_selecionada': categoria_selecionada 
    }
    
   
    return render(request, 'sushiemcasa/homepage.html', context)
