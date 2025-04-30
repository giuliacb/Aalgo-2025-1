# 📞 Gerenciador de Chamados com Prioridade (FastAPI + Notificações)
Este projeto implementa uma API REST com FastAPI para gerenciamento de chamados de suporte técnico, utilizando uma **fila de prioridade** com `heapq`. Chamados urgentes geram **notificações no desktop** com a biblioteca `plyer`.


## 🚀 Funcionalidades

- ✅ Adicionar chamados com informações de cliente e tipo de problema
- ✅ Fila ordenada por **prioridade combinada** (tipo de chamado + tipo de cliente)
- ✅ Processar o próximo chamado da fila
- ✅ Listar chamados pendentes
- ✅ Notificações visuais para chamados urgentes (ex: SERVER_DOWN)


## ⚙️ Instalação e Execução

### 1. Clone o repositório
git clone https://github.com/giuliacb/Aalgo-2025-1
cd TrabalhoSala


### 2. Crie e ative um ambiente virtual (opcional, mas recomendado)
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate


### 3. Instale as dependências
pip install -r requirements.txt


### 4. Execute a API
python -m uvicorn FilaPrioridade:app --reload
> A API estará disponível em: [http://127.0.0.1:8000](http://127.0.0.1:8000)
> Obs: FilaPrioridade é o nome do arquivo. Se o nome do seu arquivo for diferente, substitua.


### ✅ Adicionar um chamado
curl -X POST http://localhost:8000/chamado \
 -H "Content-Type: application/json" \
 -d '{
        "id_chamado": "C123",
        "cliente_nome": "Empresa X",
        "tipo_cliente": "PRIORITARIO",
        "tipo_chamado": "SERVER_DOWN",
        "descricao": "Servidor caiu"
      }'

> Obs: Os campos tipo_cliente e tipo_chamado devem ser informados sem acentos ou caracteres especiais. Eles devem coincidir exatamente com os valores dos Enums, como:
    - tipo_cliente: PRIORITARIO, SEM_PRIORIDADE, DEMONSTRACAO
    - tipo_chamado: SERVER_DOWN, IMPACTA_PRODUCAO, SEM_IMPACTO, DUVIDA


### 📋 Listar fila
curl http://localhost:8000/fila


### ⏭️ Processar próximo chamado
curl http://localhost:8000/proximo_chamado


## 📦 Dependências

As principais bibliotecas utilizadas:

- [`fastapi`](https://fastapi.tiangolo.com/)
- [`uvicorn`](https://www.uvicorn.org/) – servidor ASGI para rodar a API
- [`plyer`](https://github.com/kivy/plyer) – envio de notificações no desktop
- `pydantic` – validação de dados
- `heapq` – fila de prioridade nativa do Python

> Obs: A `plyer` pode exigir dependências de notificação específicas para cada sistema operacional. Em alguns ambientes Linux, pode ser necessário instalar `libnotify` ou ferramentas equivalentes.


## 📎 Observações

- O sistema usa a **prioridade combinada** como uma tupla `(prioridade_chamado, prioridade_cliente)` onde     menor valor = maior prioridade.
- Tipos de chamados e clientes são padronizados com Enums.
- As notificações são disparadas em dois momentos:
  - Ao adicionar chamados críticos (`SERVER_DOWN`, `IMPACTA_PRODUCAO`)
  - Ao processar o próximo chamado, se for urgente.


## ⚙️ Análise de Complexidade – heapq

- `heapq.heappush()` – **Inserção de chamado**  
  ⏱️ Complexidade: **O(log n)**  
  Cada inserção reorganiza parcialmente a heap para manter a propriedade de min-heap.

- `heapq.heappop()` – **Remoção do chamado mais prioritário**  
  ⏱️ Complexidade: **O(log n)**  
  Remove o menor elemento (maior prioridade), reordenando a heap.


## Comparação com Alternativas

| Estrutura       > Inserção   > Remoção do mais prioritário > Comentário          

| Heap (heapq)    >   O(log n)   > O(log n)     > Ideal para fila de prioridades.    
| Lista Ordenada  >      O(n)    > O(1)         > Inserção lenta, mas remoção rápida.
| Lista Não Ordenada >   O(1)    > O(n)         > Inserção rápida, mas busca/remoção lenta.       
| Árvore Balanceada  > O(log n)  > O(log n)     > Mais flexível, mas mais complexa de implementar.

> Conclusão: A `heapq` oferece o melhor custo-benefício em Python puro, especialmente considerando o volume crescente de chamados.


## Escalabilidade do Sistema

> Comportamento com volume crescente de chamados:
- A estrutura heap é eficiente mesmo com milhares de elementos.
- Operações de push/pop mantêm desempenho consistente (O(log n)), diferente de listas que degradam para O(n).

> Pontos de atenção com escalabilidade:
- Se houver centenas de milhares de chamados simultâneos, pode valer a pena:
  - Persistir os dados em um banco (Redis, SQLite, PostgreSQL).
  - Usar tarefas assíncronas/processamento em lote.
  - Aplicar sharding por cliente/tipo de chamado para balanceamento.


## Resumo Final

| Aspecto                       | Resultado |
|-------------------------------|-----------|
| Inserção (heappush)           | O(log n)  |
| Remoção (heappop)             | O(log n)  |
| Ideal para grande volume?     | ✅ Sim    |
| Melhor que listas simples?    | ✅ Muito mais eficiente |


## 📧 Autor

Desenvolvido por Giulia Campelo Bezerra
Projeto acadêmico para gerenciamento de chamados de suporte técnico.
