from django.views.generic import ListView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from ..models.produtos import Produto 

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):

        return self.request.user.is_staff

    def handle_no_permission(self):
        return super().handle_no_permission()



class GerenciarProdutosListView(StaffRequiredMixin, ListView):
    model = Produto
    template_name = 'sushiemcasa/gerenciar_produtos_lista.html'
    context_object_name = 'produtos'


class ProdutoUpdateView(StaffRequiredMixin, UpdateView):
    model = Produto
    template_name = 'sushiemcasa/produto_editar_form.html'
    
    fields = ['nome', 'descricao', 'preco'] 

    success_url = reverse_lazy('sushiemcasa:listar_produtos')