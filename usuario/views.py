from django.shortcuts import render

def home_view(request):
    # O caminho precisa ser exatamente 'usuario/pages/home.html'
    return render(request, 'usuario/pages/home.html') 