from django.db import transaction
from .models import Produto, Venda, Financeiro, Cliente

def processar_venda(produto_id, quantidade, cliente_id):
    with transaction.atomic(): # Vai ser executado por completo, ou não vai ser executado
        
        # 1. Validação do produto
        try: 
            produtoSelecionado = Produto.objects.select_for_update().get(id=produto_id) #se selecionado, travo até terminar a consulta
        except Produto.DoesNotExist: 
            raise ValueError('Produto não encontrado no sistema.')
        
        # 2. Validar o estoque
        if quantidade > produtoSelecionado.qnt_estoque:
            raise ValueError(f'Estoque insuficiente, Disponível no momento: {produtoSelecionado.qnt_estoque}, solicitado: {quantidade}')
        
        if quantidade <= 0:
            raise ValueError('A quantidade vendida deve ser maior que zero.')
        
        # 3. Buscar Cliente
        try:
            clienteSelecionado = Cliente.objects.get(id=cliente_id) 
        except Cliente.DoesNotExist: 
            raise ValueError('Cliente não encontrado!')

        # 4. Dar baixa no estoque
        produtoSelecionado.qnt_estoque -= quantidade
        produtoSelecionado.save() #usando o nome correto da variável

        # 5. Registrar venda
        venda = Venda.objects.create(
            produto=produtoSelecionado, 
            qnt_vendida=quantidade, 
            preco_unit=produtoSelecionado.preco_venda
        )

        # 6. Calcular a venda total e gerar o financeiro
        valor_total = produtoSelecionado.preco_venda * quantidade # Usando padrão snake_case
        
        financeiro = Financeiro.objects.create(
            valor_total=valor_total, # Correção: Nome do campo igual ao model (valor_total)
            forma_pagamento='Pendente', 
            status_pagamento='Pendente', 
            cliente=clienteSelecionado # Passando o objeto do cliente inteiro
        )

        return venda, financeiro

def registrar_atendimento(pet_id, funcionario_id, sintomas, diagnostico, observacoes):
    with transaction.atomic(): #vai ser executado por completo, ou não vai ser executado
        try: #verificando se o pet existe
            petSelecionado = Pet.objects.get(id = pet_id)
        except Pet.DoesNotExist:
            raise ValueError('Pet selecionado não existe')
        
        try: #verifincando funcionário
            funcionarioSelecionado = Funcionario.objects.get(id = funcionario_id)
        except Funcionario.DoesNotExist:
            raise ValueError('Funcionário não existente!')
        
        atendimento = Atendimento.objects.create(sistemas = sintomas,
         diagnostico = diagnostico, 
         observacoes = observacoes, 
         pet = petSelecionado, 
         atendente = funcionarioSelecionado)
        
        return atendimento
    
def agendar_consulta(pet_id, funcionario_id, data_hora, motivo):
    with transaction.atomic():
        try: #verificando o pet existe
            petSelecionado = Pet.objects.select_for_update().get(id = pet_id)
        except Pet.DoesNotExist:
            raise ValueError('Pet não encontrado!')
        
        try: #verificando se funcionario existe
            funcionarioSelecionado = Funcionario.objects.get(id = funcionario_id)
        except Funcionario.DoesNotExist:
            raise ValueError('Funcionario não encontrado!')
        
        
        agendamento = Agendamento.objects.create(motivo = motivo,
            data_hora = data_hora, 
            pet = petSelecionado,
            funcionario = funcionarioSelecionado
        )

        return agendamento

def processar_pagamento(financeiro_id, forma_pagamento):
    with transaction.atomic(): #só completa se tudo for correto, caso contrario nao faz nada na tabela
        try:
            financeiroSelecionado = Financeiro.objects.get(id = financeiro_id)
        except Financeiro.DoesNotExist:
            raise ValueError('Erro: financeiro não encontrada')
        
        if financeiroSelecionado.status_pagamento.upper() == 'PAGO':
            raise ValueError('Pagemento já realizado!')

        financeiroSelecionado.status_pagamento = 'PAGO'
        financeiroSelecionado.forma_pagamento = forma_pagamento
        financeiroSelecionado.save() #salvando no BD

        return financeiroSelecionado

def cancelar_agendamento(agendamento_id):
    with transaction.atomic():
        try:
            agendamentoSelecionado = Agendamento.objects.select_for_update().get(id = agendamento_id) #paralisei enquanto seleciono
        except Agendamento.DoesNotExist:
            raise ValueError('Erro: agendamento não encontrado!')
        
        if agendamentoSelecionado.status.upper() == 'CANCELADO': #se caso já estiver cancelado
            raise ValueError('Erro: Agendamento já cancelado!')

        #Atualizando o meu agendamento
        agendamentoSelecionado.status = 'CANCELADO'
        agendamentoSelecionado.save()

        return agendamentoSelecionado

def adicionar_estoque(produto_id, quantidade):
    with transaction.atomic():
        #buscando produto
        try:
            produtoSelecionado = Produto.objects.select_for_update().get(id = produto_id)
        except Produto.DoesNotExist:
            raise ValueError('Erro: Produto não encontrado!')
        
        if quantidade <= 0:
            raise ValueError('Erro: A quantidade escolhida de reposição deve ser maior que zero')

        produtoSelecionado.qnt_estoque += quantidade
        produtoSelecionado.save()

        return produtoSelecionado

def listar_estoque_critico(limite_minimo=5):
    if limite_minimo < 0:
        raise ValueError('O limite mínimo não pode ser negativo')
    

    #__gt = >, __gte >=, __lt = <, __lte = <=, ou seja, o L significa que tá apontado pra Left
    produtos_criticos = Produto.objects.filter(qnt_estoque__lte = limite_minimo).order_by('qnt_estoque') #qnt_estoque <= limite_minimo
    return produtos_criticos

def reagendar_consulta(agendamento_id, nova_data_hora):
    with transaction.atomic():
        try:
            agendamentoSelecionado = Agendamento.objects.select_for_update().get(id = agendamento_id) #busquei meu agendamento
        except Agendamento.DoesNotExist:
            raise ValueError('O agendamento não existe!')
        
        if agendamentoSelecionado.status.upper() in ['CANCELADO', 'CONCLUIDO']:
            raise ValueError('Seu agendamento já está concluido/cancelado')
        
        #falta mais
        
        



    


        


        

    
        





