from django.shortcuts import render, redirect, get_object_or_404
from sushiemcasa.models.produtos import Produto, Categoria
from sushiemcasa.models.horariodefuncionamento import HorarioDeFuncionamento
from sushiemcasa.models.itens_promo import BannerPromocional
from django.contrib import messages 
from django.utils import timezone  


def exibir_cardapio(request, categoria_slug=None): 
    banners = BannerPromocional.objects.filter(ativo=True).order_by('ordem')
    
    categorias = Categoria.objects.all()
    produtos = Produto.objects.filter(disponivel=True) 
    categoria_selecionada = None
    
    if categoria_slug:
        categoria = get_object_or_404(Categoria, slug=categoria_slug)
        produtos = produtos.filter(categoria=categoria)
        categoria_selecionada = categoria.nome 
    
    now = timezone.localtime(timezone.now())
    current_day_int = now.weekday() 
    current_time = now.time()
    
    is_open = False 
    try:
        today_schedule = HorarioDeFuncionamento.objects.get(day_of_week=current_day_int)
        if (today_schedule.is_open and 
            today_schedule.open_time and 
            today_schedule.close_time and
            today_schedule.open_time <= current_time < today_schedule.close_time):
            is_open = True
    except HorarioDeFuncionamento.DoesNotExist:
        is_open = False 

  
    context = {
        'banners': banners, 
        'produtos': produtos,
        'categorias': categorias, 
        'categoria_selecionada': categoria_selecionada,
        'is_open': is_open
    }
    
    return render(request, 'sushiemcasa/homepage.html', context)