from django.shortcuts import render, redirect, get_object_or_404
from sushiemcasa.models import Produto, Categoria, HorarioDeFuncionamento
from django.contrib import messages 
from django.utils import timezone  

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
    
    now = timezone.localtime(timezone.now())
    current_day_int = now.weekday() # Segunda=0, Domingo=6
    current_time = now.time()
    
    is_open = False # Começa como fechado por padrão
    
    try:
        # Pega a configuração de horário para o dia de HOJE
        today_schedule = HorarioDeFuncionamento.objects.get(day_of_week=current_day_int)
        
        # Verifica se estamos dentro da janela de funcionamento
        if (today_schedule.is_open and 
            today_schedule.open_time and 
            today_schedule.close_time and
            today_schedule.open_time <= current_time < today_schedule.close_time):
            
            is_open = True
            
    except HorarioDeFuncionamento.DoesNotExist:
        is_open = False # Se não houver configuração para hoje, consideramos fechado

    if not is_open:
        # ESTA É A MENSAGEM QUE O SEU TESTE ESTÁ PROCURANDO!
        messages.warning(request, "Loja fechada. Não estamos aceitando pedidos no momento.")
        
    context = {
        'produtos': produtos,
        'categorias': categorias, 
        'categoria_selecionada': categoria_selecionada 
    }
    
   
    return render(request, 'sushiemcasa/homepage.html', context)
