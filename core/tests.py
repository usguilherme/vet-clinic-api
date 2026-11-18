import pytest
from datetime import timedelta
from django.utils import timezone
from .models import Cliente, Pet, Funcionario, Produto, Venda, Atendimento, Agendamento, Financeiro
from .services import (
    processar_venda,
    registrar_atendimento,
    agendar_consulta,
    processar_pagamento,
    cancelar_agendamento,
    adicionar_estoque,
    listar_estoque_critico,
    reagendar_consulta,
    finalizar_atendimento_e_faturar,
)

@pytest.mark.django_db
class TestVeterinariaServices:

    def test_processar_venda_sucesso(self):
        cliente = Cliente.objects.create(nome="Carlos Silva", telefone="83999999999")
        produto = Produto.objects.create(nome="Antipulgas", preco_venda=50.00, qnt_estoque=10, codigo_barra="7891001")
        venda, financeiro = processar_venda(produto_id=produto.id, quantidade=2, cliente_id=cliente.id)
        produto.refresh_from_db()
        assert produto.qnt_estoque == 8
        assert venda.qnt_vendida == 2
        assert venda.preco_unit == 50.00
        assert financeiro.valor_total == 100.00
        assert financeiro.status_pagamento == "Pendente"
        assert financeiro.forma_pagamento == "Pendente"
        assert financeiro.cliente == cliente

    def test_processar_venda_produto_nao_encontrado(self):
        cliente = Cliente.objects.create(nome="Carlos Silva", telefone="83999999999")
        with pytest.raises(ValueError, match="Produto não encontrado no sistema."):
            processar_venda(produto_id=9999, quantidade=1, cliente_id=cliente.id)

    def test_processar_venda_estoque_insuficiente(self):
        cliente = Cliente.objects.create(nome="Ana", telefone="83988888888")
        produto = Produto.objects.create(nome="Vacina", preco_venda=120.00, qnt_estoque=1, codigo_barra="7891002")
        with pytest.raises(ValueError, match="Estoque insuficiente"):
            processar_venda(produto_id=produto.id, quantidade=5, cliente_id=cliente.id)

    def test_processar_venda_quantidade_zero_ou_negativa(self):
        cliente = Cliente.objects.create(nome="Ana", telefone="83988888888")
        produto = Produto.objects.create(nome="Vacina", preco_venda=120.00, qnt_estoque=10, codigo_barra="7891003")
        with pytest.raises(ValueError, match="A quantidade vendida deve ser maior que zero."):
            processar_venda(produto_id=produto.id, quantidade=0, cliente_id=cliente.id)
        with pytest.raises(ValueError, match="A quantidade vendida deve ser maior que zero."):
            processar_venda(produto_id=produto.id, quantidade=-3, cliente_id=cliente.id)

    def test_processar_venda_cliente_nao_encontrado(self):
        produto = Produto.objects.create(nome="Vacina", preco_venda=120.00, qnt_estoque=10, codigo_barra="7891004")
        with pytest.raises(ValueError, match="Cliente não encontrado!"):
            processar_venda(produto_id=produto.id, quantidade=1, cliente_id=9999)

    def test_registrar_atendimento_sucesso(self):
        cliente = Cliente.objects.create(nome="Mariana", telefone="83977777777")
        pet = Pet.objects.create(nome="Thor", especie="Cachorro", tutor=cliente, data_nascimento="2023-01-01", peso_atual=10.5)
        funcionario = Funcionario.objects.create(nome="Dr. Roberto", cargo="Veterinário")
        atendimento = registrar_atendimento(
            pet_id=pet.id,
            funcionario_id=funcionario.id,
            sintomas="Apatia",
            diagnostico="Virose",
            observacoes="Hidratação"
        )
        assert atendimento.pet == pet
        assert atendimento.atendente == funcionario
        assert atendimento.diagnostico == "Virose"

    def test_registrar_atendimento_pet_inexistente(self):
        funcionario = Funcionario.objects.create(nome="Dr. Roberto", cargo="Veterinário")
        with pytest.raises(ValueError, match="Pet selecionado não existe"):
            registrar_atendimento(
                pet_id=9999,
                funcionario_id=funcionario.id,
                sintomas="Apatia",
                diagnostico="Virose",
                observacoes="Hidratação"
            )

    def test_registrar_atendimento_funcionario_inexistente(self):
        cliente = Cliente.objects.create(nome="Mariana", telefone="83977777777")
        pet = Pet.objects.create(nome="Thor", especie="Cachorro", tutor=cliente, data_nascimento="2023-01-01", peso_atual=10.5)
        with pytest.raises(ValueError, match="Funcionário não existente!"):
            registrar_atendimento(
                pet_id=pet.id,
                funcionario_id=9999,
                sintomas="Apatia",
                diagnostico="Virose",
                observacoes="Hidratação"
            )

    def test_agendar_consulta_sucesso(self):
        cliente = Cliente.objects.create(nome="Mariana", telefone="83977777777")
        pet = Pet.objects.create(nome="Thor", especie="Cachorro", tutor=cliente, data_nascimento="2023-01-01", peso_atual=10.5)
        funcionario = Funcionario.objects.create(nome="Dr. Roberto", cargo="Veterinário")
        data_consulta = timezone.now() + timedelta(days=1)
        agendamento = agendar_consulta(
            pet_id=pet.id,
            funcionario_id=funcionario.id,
            data_hora=data_consulta,
            motivo="Check-up"
        )
        assert agendamento.pet == pet
        assert agendamento.funcionario == funcionario
        assert agendamento.data_hora == data_consulta
        assert agendamento.motivo == "Check-up"

    def test_agendar_consulta_pet_nao_encontrado(self):
        funcionario = Funcionario.objects.create(nome="Dr. Roberto", cargo="Veterinário")
        with pytest.raises(ValueError, match="Pet não encontrado!"):
            agendar_consulta(
                pet_id=9999,
                funcionario_id=funcionario.id,
                data_hora=timezone.now() + timedelta(days=1),
                motivo="Check-up"
            )

    def test_agendar_consulta_funcionario_nao_encontrado(self):
        cliente = Cliente.objects.create(nome="Mariana", telefone="83977777777")
        pet = Pet.objects.create(nome="Thor", especie="Cachorro", tutor=cliente, data_nascimento="2023-01-01", peso_atual=10.5)
        with pytest.raises(ValueError, match="Funcionario não encontrado!"):
            agendar_consulta(
                pet_id=pet.id,
                funcionario_id=9999,
                data_hora=timezone.now() + timedelta(days=1),
                motivo="Check-up"
            )

    def test_cancelar_agendamento_sucesso(self):
        cliente = Cliente.objects.create(nome="Mariana", telefone="83977777777")
        pet = Pet.objects.create(nome="Thor", especie="Cachorro", tutor=cliente, data_nascimento="2023-01-01", peso_atual=10.5)
        funcionario = Funcionario.objects.create(nome="Dr. Roberto", cargo="Veterinário")
        agendamento = Agendamento.objects.create(
            pet=pet,
            funcionario=funcionario,
            data_hora=timezone.now() + timedelta(days=1),
            motivo="Rotina"
        )
        cancelado = cancelar_agendamento(agendamento_id=agendamento.id)
        assert cancelado.status == "CANCELADO"

    def test_cancelar_agendamento_nao_encontrado(self):
        with pytest.raises(ValueError, match="Erro: agendamento não encontrado!"):
            cancelar_agendamento(agendamento_id=9999)

    def test_cancelar_agendamento_ja_cancelado(self):
        cliente = Cliente.objects.create(nome="Mariana", telefone="83977777777")
        pet = Pet.objects.create(nome="Thor", especie="Cachorro", tutor=cliente, data_nascimento="2023-01-01", peso_atual=10.5)
        funcionario = Funcionario.objects.create(nome="Dr. Roberto", cargo="Veterinário")
        agendamento = Agendamento.objects.create(
            pet=pet,
            funcionario=funcionario,
            data_hora=timezone.now() + timedelta(days=1),
            motivo="Rotina",
            status="CANCELADO"
        )
        with pytest.raises(ValueError, match="Erro: Agendamento já cancelado!"):
            cancelar_agendamento(agendamento_id=agendamento.id)

    def test_reagendar_consulta_sucesso(self):
        cliente = Cliente.objects.create(nome="Mariana", telefone="83977777777")
        pet = Pet.objects.create(nome="Thor", especie="Cachorro", tutor=cliente, data_nascimento="2023-01-01", peso_atual=10.5)
        funcionario = Funcionario.objects.create(nome="Dr. Roberto", cargo="Veterinário")
        data_inicial = timezone.now() + timedelta(days=1)
        nova_data = timezone.now() + timedelta(days=2)
        agendamento = Agendamento.objects.create(
            pet=pet,
            funcionario=funcionario,
            data_hora=data_inicial,
            motivo="Rotina"
        )
        agendamento_alterado = reagendar_consulta(agendamento_id=agendamento.id, nova_data_hora=nova_data)
        assert agendamento_alterado.data_hora == nova_data

    def test_reagendar_consulta_inexistente(self):
        with pytest.raises(ValueError, match="O agendamento não existe!"):
            reagendar_consulta(agendamento_id=9999, nova_data_hora=timezone.now() + timedelta(days=2))

    def test_reagendar_consulta_ja_concluida_ou_cancelada(self):
        cliente = Cliente.objects.create(nome="Mariana", telefone="83977777777")
        pet = Pet.objects.create(nome="Thor", especie="Cachorro", tutor=cliente, data_nascimento="2023-01-01", peso_atual=10.5)
        funcionario = Funcionario.objects.create(nome="Dr. Roberto", cargo="Veterinário")
        agendamento_cancelado = Agendamento.objects.create(
            pet=pet,
            funcionario=funcionario,
            data_hora=timezone.now() + timedelta(days=1),
            motivo="Rotina",
            status="CANCELADO"
        )
        agendamento_concluido = Agendamento.objects.create(
            pet=pet,
            funcionario=funcionario,
            data_hora=timezone.now() + timedelta(days=2),
            motivo="Retorno",
            status="CONCLUIDO"
        )
        with pytest.raises(ValueError, match="Seu agendamento já está concluido/cancelado"):
            reagendar_consulta(agendamento_id=agendamento_cancelado.id, nova_data_hora=timezone.now() + timedelta(days=3))
        with pytest.raises(ValueError, match="Seu agendamento já está concluido/cancelado"):
            reagendar_consulta(agendamento_id=agendamento_concluido.id, nova_data_hora=timezone.now() + timedelta(days=4))

    def test_reagendar_consulta_conflito_horario(self):
        funcionario = Funcionario.objects.create(nome="Dra. Fernanda", cargo="Veterinária")
        cliente = Cliente.objects.create(nome="Pedro", telefone="83966666666")
        pet1 = Pet.objects.create(nome="Mel", especie="Gato", tutor=cliente, data_nascimento="2023-01-01", peso_atual=4.0)
        pet2 = Pet.objects.create(nome="Bob", especie="Cachorro", tutor=cliente, data_nascimento="2023-01-01", peso_atual=12.0)
        horario_fixo = timezone.now() + timedelta(days=5)
        Agendamento.objects.create(pet=pet1, funcionario=funcionario, data_hora=horario_fixo, motivo="Consulta 1")
        agendamento_2 = Agendamento.objects.create(pet=pet2, funcionario=funcionario, data_hora=timezone.now() + timedelta(days=10), motivo="Consulta 2")
        with pytest.raises(ValueError, match="O veterinário já possui outra consulta marcada neste horário!"):
            reagendar_consulta(agendamento_id=agendamento_2.id, nova_data_hora=horario_fixo)

    def test_reagendar_consulta_ignora_horario_cancelado(self):
        funcionario = Funcionario.objects.create(nome="Dra. Fernanda", cargo="Veterinária")
        cliente = Cliente.objects.create(nome="Pedro", telefone="83966666666")
        pet1 = Pet.objects.create(nome="Mel", especie="Gato", tutor=cliente, data_nascimento="2023-01-01", peso_atual=4.0)
        pet2 = Pet.objects.create(nome="Bob", especie="Cachorro", tutor=cliente, data_nascimento="2023-01-01", peso_atual=12.0)
        horario_fixo = timezone.now() + timedelta(days=5)
        Agendamento.objects.create(pet=pet1, funcionario=funcionario, data_hora=horario_fixo, motivo="Consulta 1", status="CANCELADO")
        agendamento_2 = Agendamento.objects.create(pet=pet2, funcionario=funcionario, data_hora=timezone.now() + timedelta(days=10), motivo="Consulta 2")
        reagendado = reagendar_consulta(agendamento_id=agendamento_2.id, nova_data_hora=horario_fixo)
        assert reagendado.data_hora == horario_fixo

    def test_adicionar_estoque_sucesso(self):
        produto = Produto.objects.create(nome="Ração Gatos", preco_venda=80.00, qnt_estoque=5, codigo_barra="7891005")
        produto_atualizado = adicionar_estoque(produto_id=produto.id, quantidade=10)
        assert produto_atualizado.qnt_estoque == 15

    def test_adicionar_estoque_produto_inexistente(self):
        with pytest.raises(ValueError, match="Erro: Produto não encontrado!"):
            adicionar_estoque(produto_id=9999, quantidade=10)

    def test_adicionar_estoque_quantidade_invalida(self):
        produto = Produto.objects.create(nome="Ração Gatos", preco_venda=80.00, qnt_estoque=5, codigo_barra="7891006")
        with pytest.raises(ValueError, match="Erro: A quantidade escolhida de reposição deve ser maior que zero"):
            adicionar_estoque(produto_id=produto.id, quantidade=0)
        with pytest.raises(ValueError, match="Erro: A quantidade escolhida de reposição deve ser maior que zero"):
            adicionar_estoque(produto_id=produto.id, quantidade=-5)

    def test_listar_estoque_critico_sucesso(self):
        p1 = Produto.objects.create(nome="Prod 1", preco_venda=10.00, qnt_estoque=2, codigo_barra="7891007")
        p2 = Produto.objects.create(nome="Prod 2", preco_venda=10.00, qnt_estoque=5, codigo_barra="7891008")
        p3 = Produto.objects.create(nome="Prod 3", preco_venda=10.00, qnt_estoque=10, codigo_barra="7891009")
        criticos = list(listar_estoque_critico(limite_minimo=5))
        assert criticos == [p1, p2]
        assert p3 not in criticos

    def test_listar_estoque_critico_limite_negativo(self):
        with pytest.raises(ValueError, match="O limite mínimo não pode ser negativo"):
            listar_estoque_critico(limite_minimo=-1)

    def test_finalizar_atendimento_e_faturar_sucesso(self):
        cliente = Cliente.objects.create(nome="João", telefone="83955555555")
        pet = Pet.objects.create(nome="Rex", especie="Cachorro", tutor=cliente, data_nascimento="2023-01-01", peso_atual=15.0)
        funcionario = Funcionario.objects.create(nome="Dr. Marcos", cargo="Veterinário")
        produto1 = Produto.objects.create(nome="Antibiótico", preco_venda=40.00, qnt_estoque=10, codigo_barra="7891010")
        produto2 = Produto.objects.create(nome="Seringa", preco_venda=5.00, qnt_estoque=20, codigo_barra="7891011")
        atendimento = Atendimento.objects.create(
            sintomas="Febre",
            diagnostico="Infecção",
            observacoes="Repouso",
            pet=pet,
            atendente=funcionario
        )
        produtos_utilizados = [
            {"produto_id": produto1.id, "quantidade": 2},
            {"produto_id": produto2.id, "quantidade": 4}
        ]
        atendimento_finalizado, vendas, financeiro = finalizar_atendimento_e_faturar(
            atendimento_id=atendimento.id,
            produtos_utilizados=produtos_utilizados
        )
        produto1.refresh_from_db()
        produto2.refresh_from_db()
        assert atendimento_finalizado.status == "CONCLUIDO"
        assert len(vendas) == 2
        assert produto1.qnt_estoque == 8
        assert produto2.qnt_estoque == 16
        assert financeiro.valor_total == 100.00
        assert financeiro.cliente == cliente
        assert financeiro.status_pagamento == "Pendente"
        assert financeiro.forma_pagamento == "Pendente"

    def test_finalizar_atendimento_inexistente(self):
        with pytest.raises(ValueError, match="Atendimento não encontrado!"):
            finalizar_atendimento_e_faturar(atendimento_id=9999, produtos_utilizados=[])

    def test_finalizar_atendimento_ja_concluido(self):
        cliente = Cliente.objects.create(nome="João", telefone="83955555555")
        pet = Pet.objects.create(nome="Rex", especie="Cachorro", tutor=cliente, data_nascimento="2023-01-01", peso_atual=15.0)
        funcionario = Funcionario.objects.create(nome="Dr. Marcos", cargo="Veterinário")
        atendimento = Atendimento.objects.create(
            sintomas="Febre",
            diagnostico="Infecção",
            observacoes="Repouso",
            pet=pet,
            atendente=funcionario,
            status="CONCLUIDO"
        )
        with pytest.raises(ValueError, match="Este atendimento já foi finalizado."):
            finalizar_atendimento_e_faturar(atendimento_id=atendimento.id, produtos_utilizados=[])

    def test_finalizar_atendimento_produto_inexistente_rollback(self):
        cliente = Cliente.objects.create(nome="João", telefone="83955555555")
        pet = Pet.objects.create(nome="Rex", especie="Cachorro", tutor=cliente, data_nascimento="2023-01-01", peso_atual=15.0)
        funcionario = Funcionario.objects.create(nome="Dr. Marcos", cargo="Veterinário")
        produto_valido = Produto.objects.create(nome="Antibiótico", preco_venda=40.00, qnt_estoque=10, codigo_barra="7891012")
        atendimento = Atendimento.objects.create(
            sintomas="Febre",
            diagnostico="Infecção",
            observacoes="Repouso",
            pet=pet,
            atendente=funcionario
        )
        produtos_utilizados = [
            {"produto_id": produto_valido.id, "quantidade": 2},
            {"produto_id": 9999, "quantidade": 1}
        ]
        with pytest.raises(ValueError, match="O produto selecionado não existe!"):
            finalizar_atendimento_e_faturar(atendimento_id=atendimento.id, produtos_utilizados=produtos_utilizados)
        produto_valido.refresh_from_db()
        atendimento.refresh_from_db()
        assert produto_valido.qnt_estoque == 10
        assert atendimento.status != "CONCLUIDO"
        assert Venda.objects.count() == 0
        assert Financeiro.objects.count() == 0

    def test_finalizar_atendimento_estoque_insuficiente_rollback(self):
        cliente = Cliente.objects.create(nome="João", telefone="83955555555")
        pet = Pet.objects.create(nome="Rex", especie="Cachorro", tutor=cliente, data_nascimento="2023-01-01", peso_atual=15.0)
        funcionario = Funcionario.objects.create(nome="Dr. Marcos", cargo="Veterinário")
        produto1 = Produto.objects.create(nome="Antibiótico", preco_venda=40.00, qnt_estoque=10, codigo_barra="7891013")
        produto2 = Produto.objects.create(nome="Seringa", preco_venda=5.00, qnt_estoque=1, codigo_barra="7891014")
        atendimento = Atendimento.objects.create(
            sintomas="Febre",
            diagnostico="Infecção",
            observacoes="Repouso",
            pet=pet,
            atendente=funcionario
        )
        produtos_utilizados = [
            {"produto_id": produto1.id, "quantidade": 2},
            {"produto_id": produto2.id, "quantidade": 5}
        ]
        with pytest.raises(ValueError, match="Estoque insuficiente"):
            finalizar_atendimento_e_faturar(atendimento_id=atendimento.id, produtos_utilizados=produtos_utilizados)
        produto1.refresh_from_db()
        produto2.refresh_from_db()
        atendimento.refresh_from_db()
        assert produto1.qnt_estoque == 10
        assert produto2.qnt_estoque == 1
        assert atendimento.status != "CONCLUIDO"
        assert Venda.objects.count() == 0
        assert Financeiro.objects.count() == 0

    def test_processar_pagamento_sucesso(self):
        cliente = Cliente.objects.create(nome="João", telefone="83955555555")
        financeiro = Financeiro.objects.create(
            valor_total=150.00,
            forma_pagamento="Pendente",
            status_pagamento="Pendente",
            cliente=cliente
        )
        financeiro_pago = processar_pagamento(financeiro_id=financeiro.id, forma_pagamento_escolhida="pix")
        assert financeiro_pago.status_pagamento == "PAGO"
        assert financeiro_pago.forma_pagamento == "PIX"

    def test_processar_pagamento_nao_encontrado(self):
        with pytest.raises(ValueError, match="Financeiro não encontrado!"):
            processar_pagamento(financeiro_id=9999, forma_pagamento_escolhida="pix")

    def test_processar_pagamento_ja_pago(self):
        cliente = Cliente.objects.create(nome="João", telefone="83955555555")
        financeiro = Financeiro.objects.create(
            valor_total=150.00,
            forma_pagamento="PIX",
            status_pagamento="PAGO",
            cliente=cliente
        )
        with pytest.raises(ValueError, match="O financeiro selecionado já foi pago"):
            processar_pagamento(financeiro_id=financeiro.id, forma_pagamento_escolhida="cartao")