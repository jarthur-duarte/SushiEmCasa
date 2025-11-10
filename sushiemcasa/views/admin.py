
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, UpdateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.forms import modelformset_factory
from sushiemcasa.models.produtos import Produto
from sushiemcasa.models import HorarioDeFuncionamento
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
    context = {
        'username': request.user.username
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