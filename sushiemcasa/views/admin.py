from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count
from django.forms import modelformset_factory
from django.views.decorators.http import require_POST
from sushiemcasa.models.produtos import Produto, Categoria
from sushiemcasa.models import BannerPromocional, HorarioDeFuncionamento, MensagemFeedback
from sushiemcasa.models.pedidos import Order
from sushiemcasa.forms.horarios import HorarioForm
from sushiemcasa.forms.painel import BannerForm, CategoriaForm, ProdutoForm


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    
    login_url = reverse_lazy('sushiemcasa:login')

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return redirect('sushiemcasa:cardapio')

# ---------------------------------------------------------------------------
# Telas de cadastro do painel (mesmas funções do Admin completo)
# ---------------------------------------------------------------------------
class PainelFormMixin(StaffRequiredMixin):
    """Usa um template de formulário comum e mostra a mensagem de sucesso."""
    template_name = 'sushiemcasa/painel/form.html'
    titulo_novo = ''
    titulo_editar = ''
    voltar_url_name = ''
    voltar_rotulo = ''
    msg_sucesso = 'Saved.'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = self.titulo_editar if getattr(self, 'object', None) else self.titulo_novo
        ctx['voltar_url'] = reverse(self.voltar_url_name)
        ctx['voltar_rotulo'] = self.voltar_rotulo
        return ctx

    def form_valid(self, form):
        resposta = super().form_valid(form)
        messages.success(self.request, self.msg_sucesso.format(obj=self.object))
        return resposta


class PainelDeleteMixin(StaffRequiredMixin):
    """Exclusão só por POST (o botão do painel já pede confirmação)."""
    http_method_names = ['post']
    msg_sucesso = 'Deleted.'

    def form_valid(self, form):
        nome = str(self.object)
        resposta = super().form_valid(form)
        messages.success(self.request, self.msg_sucesso.format(nome=nome))
        return resposta


# Produtos
class GerenciarProdutosListView(StaffRequiredMixin, ListView):
    model = Produto
    template_name = 'sushiemcasa/gerenciar_produtos_lista.html'
    context_object_name = 'produtos'

    def get_queryset(self):
        return Produto.objects.select_related('categoria').order_by('categoria__nome', 'nome')


class ProdutoCreateView(PainelFormMixin, CreateView):
    model = Produto
    form_class = ProdutoForm
    success_url = reverse_lazy('sushiemcasa:listar_produtos')
    titulo_novo = 'New product'
    voltar_url_name = 'sushiemcasa:listar_produtos'
    voltar_rotulo = 'Products'
    msg_sucesso = '"{obj.nome}" was added to the menu.'


class ProdutoUpdateView(PainelFormMixin, UpdateView):
    model = Produto
    form_class = ProdutoForm
    success_url = reverse_lazy('sushiemcasa:listar_produtos')
    titulo_editar = 'Edit product'
    voltar_url_name = 'sushiemcasa:listar_produtos'
    voltar_rotulo = 'Products'
    msg_sucesso = '"{obj.nome}" was updated.'


class ProdutoDeleteView(PainelDeleteMixin, DeleteView):
    model = Produto
    success_url = reverse_lazy('sushiemcasa:listar_produtos')
    msg_sucesso = '"{nome}" was deleted.'


# Categorias
class CategoriaListView(StaffRequiredMixin, ListView):
    model = Categoria
    template_name = 'sushiemcasa/painel/categorias.html'
    context_object_name = 'categorias'

    def get_queryset(self):
        return Categoria.objects.annotate(total_produtos=Count('produtos')).order_by('nome')


class CategoriaCreateView(PainelFormMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    success_url = reverse_lazy('sushiemcasa:listar_categorias')
    titulo_novo = 'New category'
    voltar_url_name = 'sushiemcasa:listar_categorias'
    voltar_rotulo = 'Categories'
    msg_sucesso = 'Category "{obj.nome}" was created.'


class CategoriaUpdateView(PainelFormMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    success_url = reverse_lazy('sushiemcasa:listar_categorias')
    titulo_editar = 'Edit category'
    voltar_url_name = 'sushiemcasa:listar_categorias'
    voltar_rotulo = 'Categories'
    msg_sucesso = 'Category "{obj.nome}" was updated.'


class CategoriaDeleteView(PainelDeleteMixin, DeleteView):
    model = Categoria
    success_url = reverse_lazy('sushiemcasa:listar_categorias')
    msg_sucesso = 'Category "{nome}" was deleted.'

    def form_valid(self, form):
        # Apagar a categoria apagaria os produtos dela (on_delete=CASCADE); bloqueia.
        if self.object.produtos.exists():
            messages.error(self.request, f'"{self.object.nome}" still has products. '
                                         'Move or delete them before deleting the category.')
            return redirect(self.success_url)
        return super().form_valid(form)


# Promoções (banners do carrossel)
class BannerListView(StaffRequiredMixin, ListView):
    model = BannerPromocional
    template_name = 'sushiemcasa/painel/banners.html'
    context_object_name = 'banners'

    def get_queryset(self):
        return BannerPromocional.objects.select_related('produto_vinculado').order_by('ordem', 'id')


class BannerCreateView(PainelFormMixin, CreateView):
    model = BannerPromocional
    form_class = BannerForm
    success_url = reverse_lazy('sushiemcasa:listar_banners')
    titulo_novo = 'New special'
    voltar_url_name = 'sushiemcasa:listar_banners'
    voltar_rotulo = 'Specials'
    msg_sucesso = 'Special "{obj.titulo}" was created.'


class BannerUpdateView(PainelFormMixin, UpdateView):
    model = BannerPromocional
    form_class = BannerForm
    success_url = reverse_lazy('sushiemcasa:listar_banners')
    titulo_editar = 'Edit special'
    voltar_url_name = 'sushiemcasa:listar_banners'
    voltar_rotulo = 'Specials'
    msg_sucesso = 'Special "{obj.titulo}" was updated.'


class BannerDeleteView(PainelDeleteMixin, DeleteView):
    model = BannerPromocional
    success_url = reverse_lazy('sushiemcasa:listar_banners')
    msg_sucesso = 'Special "{nome}" was deleted.'


# Mensagens do formulário de contato
class MensagemListView(StaffRequiredMixin, ListView):
    model = MensagemFeedback
    template_name = 'sushiemcasa/painel/mensagens.html'
    context_object_name = 'mensagens'

    def get_queryset(self):
        return MensagemFeedback.objects.order_by('-data_envio')


class MensagemDeleteView(PainelDeleteMixin, DeleteView):
    model = MensagemFeedback
    success_url = reverse_lazy('sushiemcasa:listar_mensagens')
    msg_sucesso = 'Message deleted.'


# Usuários
class UsuarioListView(StaffRequiredMixin, ListView):
    model = User
    template_name = 'sushiemcasa/painel/usuarios.html'
    context_object_name = 'usuarios'

    def get_queryset(self):
        return User.objects.annotate(total_pedidos=Count('order')).order_by('-date_joined')


@login_required(login_url='sushiemcasa:login')
@require_POST
def alterar_usuario(request, pk):
    """Liga/desliga o acesso ao painel (is_staff) ou a conta (is_active).
    Só superusuários podem mudar isso, e nunca a própria conta."""
    if not request.user.is_superuser:
        messages.error(request, "Only administrators can change user access.")
        return redirect('sushiemcasa:listar_usuarios')
    alvo = get_object_or_404(User, pk=pk)
    campo = request.POST.get('campo')
    if alvo.pk == request.user.pk:
        messages.error(request, "You can't change your own access.")
    elif campo not in ('is_staff', 'is_active'):
        messages.error(request, "Invalid action.")
    else:
        setattr(alvo, campo, not getattr(alvo, campo))
        alvo.save(update_fields=[campo])
        if campo == 'is_staff':
            estado = 'can now use' if alvo.is_staff else 'can no longer use'
            messages.success(request, f"{alvo.username} {estado} the store dashboard.")
        else:
            estado = 'enabled' if alvo.is_active else 'disabled'
            messages.success(request, f"{alvo.username}'s account was {estado}.")
    return redirect('sushiemcasa:listar_usuarios')

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