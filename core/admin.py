from django.contrib import admin
from .models import Cliente, Pet, Funcionario, Produto, Agendamento, Atendimento,Venda, Financeiro

# Register your models here.
admin.site.register(Cliente)
admin.site.register(Pet)
admin.site.register(Funcionario)
admin.site.register(Produto)
admin.site.register(Agendamento)
admin.site.register(Atendimento)
admin.site.register(Venda)
admin.site.register(Financeiro)

