# 📞 Gerenciador de Chamados com Prioridade (FastAPI + Notificações)
Este projeto implementa uma API REST com FastAPI para gerenciamento de chamados de suporte técnico, utilizando uma **fila de prioridade** com `heapq`. Chamados urgentes geram **notificações no desktop** com a biblioteca `plyer`.


## 🚀 Funcionalidades

- ✅ Adicionar chamados com informações de cliente e tipo de problema  
- ✅ Fila ordenada por **prioridade combinada** (tipo de chamado + tipo de cliente)  
- ✅ Processar o próximo chamado da fila  
- ✅ Listar chamados pendentes  
- ✅ Notificações visuais para chamados urgentes (ex: SERVER_DOWN)  
- ✅ **Escalonamento manual de chamados**
- ✅ **Atribuição de agentes aos chamados**
- ✅ **Interface Web com atualizações em tempo real (SSE)**
- ✅ **Tempo estimado de resolução por tipo de chamado**


## 🔧 Funcionalidades Extras Implementadas

### 🚨 Escalonar Chamado
Aumenta manualmente a prioridade de um chamado específico, tornando-o mais urgente na fila.

**Exemplo de uso via API**:
curl -X POST http://localhost:8000/escalar/C123

> Esse endpoint reduz numericamente o valor da prioridade do chamado, garantindo que não fique abaixo de 1.


### 👩‍💻 Atribuir Agente ao Chamado
Permite designar um agente de suporte a um chamado específico.

**Exemplo de uso via API**:
curl -X POST "http://localhost:8000/atribuir/C123?agente=Joao"

> O `id_chamado` é passado na URL, e o nome do agente no parâmetro `agente`.


### ⏱️ Tempo Estimado por Tipo de Chamado

Cada chamado agora inclui um tempo estimado com base em seu tipo:

| Tipo de Chamado     | Tempo Estimado |
|---------------------|----------------|
| SERVER_DOWN         | 60 minutos     |
| IMPACTA_PRODUCAO    | 45 minutos     |
| SEM_IMPACTO         | 30 minutos     |
| DUVIDA              | 15 minutos     |

Esse valor é exibido na fila e na interface web.


### 🌐 Interface Web em Tempo Real

Foi criada uma interface HTML simples para visualizar a fila em tempo real:

- Caminho: `TrabalhoSala/fila.html`
- Endpoint: [http://localhost:8000/web](http://localhost:8000/web)
- Atualizações via **Server-Sent Events (SSE)** sem precisar recarregar a página.

Utiliza:

- `Jinja2` para renderização HTML
- `sse-starlette` para SSE


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


## 🔁 Exemplos de Uso via `curl`

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


> Os campos `tipo_cliente` e `tipo_chamado` devem coincidir com os valores dos Enums não contendo acentuação ou caracteres especiais:
- tipo_cliente: PRIORITARIO, SEM_PRIORIDADE, DEMONSTRACAO  
- tipo_chamado: SERVER_DOWN, IMPACTA_PRODUCAO, SEM_IMPACTO, DUVIDA

### 📋 Listar fila
curl http://localhost:8000/fila


### ⏭️ Processar próximo chamado
curl http://localhost:8000/proximo_chamado


## 📦 Dependências
As principais bibliotecas utilizadas:

- [`fastapi`](https://fastapi.tiangolo.com/)
- [`uvicorn`](https://www.uvicorn.org/)
- [`plyer`](https://github.com/kivy/plyer)
- `jinja2`
- `sse-starlette`
- `pydantic`
- `heapq`

> ⚠️ Obs: A `plyer` pode exigir bibliotecas extras no sistema (ex: `libnotify` no Linux).


## 📎 Observações Técnicas

- A **prioridade** é uma tupla: `(tipo_chamado, tipo_cliente)`
- A fila é uma min-heap (`heapq`) — quanto menor a tupla, maior a urgência
- A interface Web usa `SSE` para atualização da fila sem recarregamento
- O HTML da interface está em `TrabalhoSala/fila.html`


## ⚙️ Análise de Complexidade – heapq

| Operação             | Complexidade |
|----------------------|--------------|
| Inserção (heappush)  | O(log n)     |
| Remoção (heappop)    | O(log n)     |

> `heapq` é eficiente mesmo com milhares de elementos, ideal para cenários com alta carga.


## Comparação com Alternativas

| Estrutura         | Inserção | Remoção (prioritário)  | Comentário                        |
|-------------------|----------|------------------------|-----------------------------------|
| `heapq` (min-heap)| O(log n) | O(log n)               | ✅ Ideal para prioridade dinâmica|
| Lista ordenada    | O(n)     | O(1)                   | ❌ Inserção lenta                |
| Lista não ordenada| O(1)     | O(n)                   | ❌ Busca/remoção lenta           |
| Árvore balanceada | O(log n) | O(log n)               | ⚠️ Mais complexa de implementar  |


## 📈 Escalabilidade

- Boa performance com milhares de chamados simultâneos
- Pode ser estendido com:
  - Banco de dados (Redis, SQLite, etc)
  - Filas distribuídas
  - Balanceamento por tipo de chamado


## 📧 Autor

Desenvolvido por **Giulia Campelo Bezerra**  
Projeto acadêmico – *Gerenciamento de chamados com priorização e resposta em tempo real*
