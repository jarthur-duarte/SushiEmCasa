# sushiemcasa/views/contato.py

from django.shortcuts import render, redirect
from django.contrib import messages
from sushiemcasa.forms.contato import FeedbackForm

def pagina_contato(request):

    print(f"MÉTODO DA REQUISIÇÃO: {request.method}")

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
            messages.success(request, 'Your feedback was sent. Thank you!')
            return redirect('sushiemcasa:contato')
        else:
            messages.error(request, 'We could not send your feedback. Please correct the errors below.')
            print("ERROS DE VALIDAÇÃO DO FORMULÁRIO:", form.errors)
    else:
        form = FeedbackForm()

    context = {
        'form': form,
        'info_contato': info_contato
    }

    return render(request, 'sushiemcasa/contato.html', context)