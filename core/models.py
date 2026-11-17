from django.db import models

# Tabela Clientes
class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    telefone = models.CharField(max_length=20)
    endereco = models.TextField()
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

# Tabela de pet
class Pet(models.Model):
    nome = models.CharField(max_length=100)
    especie = models.CharField(max_length=30)
    raca = models.CharField(max_length=30)
    data_nascimento = models.DateField()
    sexo = models.CharField(max_length=20)
    peso_atual = models.DecimalField(max_digits=5, decimal_places=2)
    anotacoes = models.TextField()
    tutor = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nome} ({self.tutor.nome})"

# Tabela Funcionarios
class Funcionario(models.Model):
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=50)
    crmv = models.CharField(max_length=20, unique=True, blank=True, null=True)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(max_length=254, unique=True)
    data_contratacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - {self.cargo}"

# Tabela Produtos
class Produto(models.Model):
    nome = models.CharField(max_length=100)
    preco_venda = models.DecimalField(max_digits=8, decimal_places=2)
    qnt_estoque = models.IntegerField()
    categoria = models.CharField(max_length=20)
    codigo_barra = models.CharField(max_length=13, unique=True)
    
    def __str__(self):
        return f"{self.nome} (R$ {self.preco_venda})"

# Tabela Agendamentos
class Agendamento(models.Model):
    data_hora = models.DateTimeField()
    motivo = models.TextField()
    status = models.CharField(max_length=30, default="Agendado")
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE)

    def __str__(self):
        return f"Agendamento: {self.pet.nome} - {self.data_hora}"

# Tabela de atendimentos
class Atendimento(models.Model):
    data_hora = models.DateTimeField(auto_now_add=True)
    sintomas = models.TextField()
    diagnostico = models.TextField()
    observacoes = models.TextField()
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    atendente = models.ForeignKey(Funcionario, on_delete=models.CASCADE)

    def __str__(self):
        return f"Atendimento: {self.pet.nome}"

# Tabela de Vendas
class Venda(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    qnt_vendida = models.IntegerField()
    preco_unit = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f"Venda: {self.produto.nome} ({self.qnt_vendida}x)"

# Tabela de financeiro
class Financeiro(models.Model):
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    forma_pagamento = models.CharField(max_length=20)
    status_pagamento = models.CharField(max_length=20, default="Pendente")
    data_hora_pagamento = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    def __str__(self):
        return f"Fatura #{self.id} - R$ {self.valor_total}"