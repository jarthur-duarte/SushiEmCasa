
# sushiemcasa/views/contato.py

from django.shortcuts import render, redirect
from django.contrib import messages
# Lembre-se que o caminho deste import depende de onde você criou seus formulários
from sushiemcasa.forms.contato import FeedbackForm 

# ATENÇÃO: Verifique se o nome da função é o mesmo que você usa no seu urls.py
def pagina_contato(request):
    # Dicionário com as informações estáticas de contato
    info_contato = {
        'telefone': '+1(239)7719811',
        'instagram': '@sushiemcasausa',
        'email': 'sushiemacasausa@gmail.com',
        'whatsapp': '+1 (239) 771-9811'
    }

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Seu feedback foi enviado com sucesso!')
            return redirect('sushiemcasa:contato')
    else:
        form = FeedbackForm()

    # Este 'context' envia o formulário e as infos para o template
    context = {
        'form': form,
        'info_contato': info_contato
    }

    return render(request, 'sushiemcasa/contato.html', context)