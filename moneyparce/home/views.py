from django.shortcuts import render

def home_view(request):
    template_data = {
        'title': 'Home - MoneyParce'
    }
    return render(request, 'home/index.html', {'template_data': template_data})