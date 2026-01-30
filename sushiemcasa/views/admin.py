from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, UpdateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.forms import modelformset_factory
from sushiemcasa.models.produtos import Produto
from sushiemcasa.models import HorarioDeFuncionamento
from sushiemcasa.models.pedidos import Order  
from sushiemcasa.forms.horarios import HorarioForm


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    
    login_url = reverse_lazy('sushiemcasa:login')

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return redirect('sushiemcasa:cardapio')

class GerenciarProdutosListView(StaffRequiredMixin, ListView):
    model = Produto
    template_name = 'sushiemcasa/gerenciar_produtos_lista.html'
    context_object_name = 'produtos'


class ProdutoUpdateView(StaffRequiredMixin, UpdateView):
    model = Produto
    template_name = 'sushiemcasa/produto_editar_form.html'
    fields = ['nome', 'descricao', 'preco'] 
    success_url = reverse_lazy('sushiemcasa:listar_produtos')

@login_required(login_url='sushiemcasa:login') 
def painel_controle(request):
    if not request.user.is_staff:
        return redirect('sushiemcasa:cardapio')

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('new_status')
        
        if order_id and new_status:
            pedido = get_object_or_404(Order, id=order_id)
            pedido.status = new_status
            pedido.save()
            messages.success(request, f"Status do pedido #{order_id} atualizado!")
            return redirect('sushiemcasa:painel_controle')

    todos_pedidos = Order.objects.all().order_by('-created_at')
    status_choices = Order.STATUS_CHOICES

    context = {
        'username': request.user.username,
        'pedidos': todos_pedidos,        
        'status_choices': status_choices, 
    }   
    
    return render(request, 'sushiemcasa/painel/dashboard.html', context)


@login_required(login_url='sushiemcasa:login')
def gerenciar_horarios(request):
    if not request.user.is_staff:
        return redirect('sushiemcasa:cardapio')

    HorarioFormSet = modelformset_factory(
        HorarioDeFuncionamento, 
        form=HorarioForm, 
        extra=0 
    )

    if request.method == 'POST':
        formset = HorarioFormSet(request.POST, queryset=HorarioDeFuncionamento.objects.order_by('day_of_week'))
        
        if formset.is_valid():
            formset.save() 
            messages.success(request, "Horários atualizados com sucesso!")
            return redirect('sushiemcasa:painel_controle')
        else:
            messages.error(request, "Erro ao salvar. Verifique os campos.")
            
    else:
        formset = HorarioFormSet(queryset=HorarioDeFuncionamento.objects.order_by('day_of_week'))

    context = {
        'formset': formset
    }
    return render(request, 'sushiemcasa/painel/gerenciar_horarios.html', context)