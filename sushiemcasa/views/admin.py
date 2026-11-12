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
            messages.success(request, f"Order #{order_id} status updated!")
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
def deletar_pedido(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('sushiemcasa:cardapio')
    
    pedido = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        if pedido.status in ['entregue', 'cancelado', 'Cancelled', 'Canceled', 'Delivered']:
            pedido_id = pedido.id
            pedido.delete()
            messages.success(request, f"Order #{pedido_id} was permanently deleted.")
        else:
            messages.error(request, "You can only delete orders that are Delivered or Canceled.")
        
    return redirect('sushiemcasa:painel_controle')


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
            messages.success(request, "Opening hours updated!")
            return redirect('sushiemcasa:painel_controle')
        else:
            messages.error(request, "Could not save. Please check the fields.")
            
    else:
        formset = HorarioFormSet(queryset=HorarioDeFuncionamento.objects.order_by('day_of_week'))

    context = {
        'formset': formset
    }
    return render(request, 'sushiemcasa/painel/gerenciar_horarios.html', context)