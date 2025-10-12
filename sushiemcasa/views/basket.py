from django.shortcuts import render

def pagina_basket(request):
    return render(request, 'sushiemcasa/basket.html')