from django.db import transaction
from .models import Produto, Venda, Financeiro, Cliente

def processar_venda(produto_id, quantidade, cliente_id):
    with transaction.atomic(): # vai ser executado por completo, ou não vai ser executado
        
        #validação do produto
        try: 
            produtoSelecionado = Produto.objects.select_for_update().get(id=produto_id) #se selecionado, travo até terminar a consulta
        except Produto.DoesNotExist: 
            raise ValueError('Produto não encontrado no sistema.')
        
        #validar o estoque
        if quantidade > produtoSelecionado.qnt_estoque:
            raise ValueError(f'Estoque insuficiente, Disponível no momento: {produtoSelecionado.qnt_estoque}, solicitado: {quantidade}')
        
        if quantidade <= 0:
            raise ValueError('A quantidade vendida deve ser maior que zero.')
        
        #buscando cliente
        try:
            clienteSelecionado = Cliente.objects.get(id=cliente_id) 
        except Cliente.DoesNotExist: 
            raise ValueError('Cliente não encontrado!')

        #dando baixa no estoque
        produtoSelecionado.qnt_estoque -= quantidade
        produtoSelecionado.save() #usando o nome correto da variável

        #registrar venda
        venda = Venda.objects.create(
            produto=produtoSelecionado, 
            qnt_vendida=quantidade, 
            preco_unit=produtoSelecionado.preco_venda
        )

        #calcular a venda total e gerar o financeiro
        valor_total = produtoSelecionado.preco_venda * quantidade 
        
        financeiro = Financeiro.objects.create(
            valor_total=valor_total, 
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
        
        #verificar se o veterinario já tem consulta marcada
        conflito = Agendamento.objects.filter(funcionario = agendamentoSelecionado.funcionario, 
        data_hora = nova_data_hora).exclude(id = agendamento_id).exclude(status = 'CANCELADO').exists() #procuro se há agendamento do mesmo funcionario, com a hora pedida do novo atendimento, e sem contar o agendamento atual, e sem considerar cancelados

        if conflito:
            raise ValueError('O veterinário já possui outra consulta marcada neste horário!')
        
        #Atualizando meu agendamento
        agendamentoSelecionado.data_hora = nova_data_hora 
        agendamentoSelecionado.save() 
    
        return agendamentoSelecionado
    
def finalizar_atendimento_e_faturar(atendimento_id, produtos_utilizados):
    with transaction.atomic(): #completa tudo, ou não faz nada
        try:
            atendimentoSelecionado = Atendimento.objects.select_for_update().get(id = atendimento_id)
        except Atendimento.DoesNotExist:
            raise ValueError('Atendimento não encontrado!')
        
        if atendimentoSelecionado.status.upper() == 'CONCLUIDO':
            raise ValueError('Este atendimento já foi finalizado.')
        
        valor_total_atendimento = 0
        vendas_realizadas = []

        for item in produtos_utilizados:
            id_prod = item['produto_id']
            qnt = item['quantidade']

            try:
                produtoSelecionado = Produto.objects.select_for_update().get(id = id_prod)
            except Produto.DoesNotExist:
                raise ValueError('O produto selecionado não existe!')
            
            if produtoSelecionado.qnt_estoque < qnt: #se caso tiver mais do que no estoque
                raise ValueError(f'Estoque insuficiente para o produto {produtoSelecionado.nome}. Disponível: {produtoSelecionado.qnt_estoque}')

            produtoSelecionado.qnt_estoque -= qnt
            produtoSelecionado.save() #save é tipo um UPDATE, já o create é o INSERT

            #registando minha venda
            venda = Venda.objects.create(produto=produtoSelecionado, qnt_vendida=qnt, preco_unit=produtoSelecionado.preco_venda)
            vendas_realizadas.append(venda)
            
            #acumulando no valor
            valor_total_atendimento += produtoSelecionado.preco_venda * qnt

        # Finaliza o atendimento após processar todos os produtos do loop
        atendimentoSelecionado.status = 'CONCLUIDO'
        atendimentoSelecionado.save()

        #buscar o animal
        clienteSelecionado = atendimentoSelecionado.pet.cliente #vou na tabelça de atendimento, pego a foreign ket e ligo o nome do cliente

        #criando a aba de financeiro
        financeiro = Financeiro.objects.create(valor_total=valor_total_atendimento, forma_pagamento='Pendente', status_pagamento='Pendente', cliente=clienteSelecionado)
        
        return atendimentoSelecionado, vendas_realizadas, financeiro
    
def processar_pagamento(financeiro_id, forma_pagamento_escolhida):
    with transaction.atomic():
        try:
            financeiroSelecionado = Financeiro.objects.select_for_update().get(id = financeiro_id)
        except Financeiro.DoesNotExist:
            raise ValueError('Financeiro não encontrado!')
        
        if financeiroSelecionado.status_pagamento.upper() == 'PAGO':
            raise ValueError('O financeiro selecionado já foi pago')

        #atualizando as variaveis de financeiro
        financeiroSelecionado.forma_pagamento = forma_pagamento_escolhida.upper()
        financeiroSelecionado.status_pagamento = 'PAGO'
        financeiroSelecionado.save() #UPDATE na minha tabela
        return financeiroSelecionado




        



    


        


        

    
        





