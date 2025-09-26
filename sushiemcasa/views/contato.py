from django.shortcuts import render

def pagina_de_contato(request):
    # sua lógica de contato aqui
    return render(request, 'contato.html')