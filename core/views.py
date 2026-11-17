from django.http import HttpResponse

def fn_home(request):  # <-- Olha o 'def' aqui na frente!
    return HttpResponse("<h1>Tudo pronto, mano! Projeto rodando.</h1>")