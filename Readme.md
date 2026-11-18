# 🐾 Sistema de Gerenciamento para Clínica Veterinária (Back-end)

Sistema de back-end robusto desenvolvido em **Django** para o gerenciamento completo de uma clínica veterinária. O projeto foca em regras de negócios complexas, integridade de dados através de transações atômicas (`atomic transactions`), controle de estoque em tempo real, agendamentos e faturamento automatizado.

---

## 🚀 Tecnologias e Ferramentas Utilizadas

* **Python 3.10+**
* **Django** (Models, ORM, Migrations)
* **Pytest** & **pytest-django** (Suíte de testes automatizados)
* **SQLite** (Banco de dados para desenvolvimento e testes)

---

## 🛠️ Arquitetura e Regras de Negócio

O projeto adota uma arquitetura em camadas, isolando a lógica de negócio em uma camada de **Services** (`services.py`), mantendo as *views* e o ecossistema limpos e testáveis. 

### Principais Módulos do Sistema:
1. **Gestão de Clientes e Pets:** Cadastro de tutores e seus respectivos animais com validações de dados (como peso e data de nascimento).
2. **Controle de Estoque e Vendas:** Processamento de vendas de produtos com baixa automática de estoque, validação de itens esgotados e prevenção de concorrência com bloqueio de linhas (`select_for_update`).
3. **Atendimentos Médicos:** Registro de sintomas, diagnósticos e observações vinculados a veterinários e pets.
4. **Agendamentos:** Marcação, reagendamento e cancelamento de consultas com checagem automática de conflitos de horário para os profissionais.
5. **Módulo Financeiro e Faturamento:** Geração automática de faturas ao concluir atendimentos, associando produtos utilizados e calculando o valor total de forma transacional.

---

## 🧪 Testes Automatizados (Quality Assurance)

O projeto possui uma suíte de testes de integração e lógica de negócio cobrindo cenários de sucesso, exceções e reversões de banco de dados (`rollback`).

Para rodar os testes utilizando o `pytest`:

```bash
# Instale as dependências do projeto
pip install -r requirements.txt

# Execute a suíte de testes
pytest