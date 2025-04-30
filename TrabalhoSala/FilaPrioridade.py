from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import heapq
from typing import List, Tuple
from plyer import notification
from enum import Enum
from starlette.responses import EventSourceResponse
import asyncio
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

# Mapeamentos de prioridade
# Enum para tipos de chamados com níveis de prioridade (menor valor = mais urgente)
class PrioridadeChamadoEnum(Enum):
    SERVER_DOWN = 1
    IMPACTA_PRODUCAO = 2
    SEM_IMPACTO = 3
    DUVIDA = 4

# Enum para tipos de cliente com níveis de prioridade (menor valor = mais prioritário)
class PrioridadeClienteEnum(Enum):
    PRIORITARIO = 1
    SEM_PRIORIDADE = 2
    DEMONSTRACAO = 3

#Tempo estimado para resolver cada chamado
TEMPO_RESOLUCAO_ESTIMADO = {
    "SERVER_DOWN": 60,
    "IMPACTA_PRODUCAO": 45,
    "SEM_IMPACTO": 30,
    "DUVIDA": 15
}

# --- Função para calcular prioridade combinada ---
def calcular_prioridade_combinada(tipo_chamado, tipo_cliente):
    """
    Retorna uma tupla com a prioridade combinada:
    (prioridade do chamado, prioridade do cliente)
    """
    try:
        # Converte entrada em letras maiúsculas e formata para usar com Enum
        prioridade_chamado = PrioridadeChamadoEnum[tipo_chamado.upper().replace(" ", "_")].value
        prioridade_cliente = PrioridadeClienteEnum[tipo_cliente.upper().replace(" ", "_")].value
        #Use .upper().replace(" ", "_") para tornar a entrada do usuário compatível com o Enum
        return (prioridade_chamado, prioridade_cliente)
    except KeyError:
        raise ValueError("Tipo de chamado ou cliente inválido.")

# Modelo de entrada de dados via JSON com validação (FastAPI)
class ChamadoInput(BaseModel):
    id_chamado: str
    cliente_nome: str
    tipo_cliente: str
    tipo_chamado: str
    descricao: str

# Representa um chamado com os dados completos (interno do sistema)
class ChamadoSuporte:
    def __init__(self, id_chamado, cliente_nome, tipo_cliente, tipo_chamado, descricao):
        self.id_chamado = id_chamado
        self.cliente_nome = cliente_nome
        self.tipo_cliente = tipo_cliente.upper().replace(" ", "_")
        self.tipo_chamado = tipo_chamado.upper().replace(" ", "_")
        self.descricao = descricao
        self.agente = None  # Novo atributo
        self.tempo_estimado = TEMPO_RESOLUCAO_ESTIMADO.get(self.tipo_chamado, 30)
        self.timestamp = datetime.now()

# --- Função de notificação ---
def enviar_notificacao_desktop(titulo: str, mensagem: str):
    """
    Envia uma notificação no desktop com o título e a mensagem fornecidos.
    """
    notification.notify(
        title=titulo,
        message=mensagem,
        timeout=10  # O tempo que a notificação fica visível (em segundos)
    )

# --- Gerenciador de Fila de Chamados ---

class GerenciadorFilaChamados:
    def __init__(self):
        # Fila de prioridade usando heapq (menor valor = maior prioridade)
        self.fila_heap: List[Tuple[Tuple[int, int], datetime, ChamadoSuporte]] = []

    def adicionar_chamado(self, chamado: ChamadoSuporte):
        # Calcula a prioridade combinada
        prioridade = calcular_prioridade_combinada(chamado.tipo_chamado, chamado.tipo_cliente)
        print(f"[LOG] Chamado {chamado.id_chamado} adicionado com prioridade {prioridade}")
        
        # Adiciona na heap com a tupla (prioridade, timestamp, objeto)
        heapq.heappush(self.fila_heap, (prioridade, chamado.timestamp, chamado))
        
        # Notifica imediatamente se for chamado crítico 
        if chamado.tipo_chamado in ["SERVER_DOWN", "IMPACTA_PRODUCAO"]:
            enviar_notificacao_desktop(
                f"Novo chamado: {chamado.tipo_chamado.replace('_', ' ').title()}",
                f"Cliente: {chamado.cliente_nome}\nDescrição: {chamado.descricao}"
            )

    def listar_fila(self):
        """
        Retorna a lista atual de chamados na fila.
        """
        return [
            {
                "id": ch.id_chamado,
                "cliente": ch.cliente_nome,
                "tipo_chamado": ch.tipo_chamado,
                "tipo_cliente": ch.tipo_cliente,
                "timestamp": ch.timestamp.isoformat()
            }
            for _, _, ch in self.fila_heap
        ]

    def processar_proximo(self):
        """
        Processa o próximo chamado na fila (maior prioridade).
        Envia notificação se for chamado urgente.
        """
        if not self.fila_heap:
            return None # Retorna None se a fila estiver vazia

        # Remove o próximo item da fila (o de maior prioridade)
        prioridade_tuple, timestamp, chamado = heapq.heappop(self.fila_heap)

        # Verifica se o chamado exige notificação
        if prioridade_tuple[0] in [1, 2]:  # Alta prioridade 1: Server down, 2: Impacta produção
            enviar_notificacao_desktop(
                "Chamado Urgente na Fila!",
                f"Cliente: {chamado.cliente_nome} ({chamado.tipo_cliente})\n"
                f"Tipo: {chamado.tipo_chamado}\n"
                f"Descrição: {chamado.descricao[:50]}..."
            )

        # Imprime no console
        print(f"[{timestamp}] Processado chamado {chamado.id_chamado} | "
              f"Cliente: {chamado.cliente_nome} | Tipo: {chamado.tipo_chamado}")

        return chamado # Retorna o chamado processado

# -------------------------- FASTAPI - ROTAS --------------------------

# Cria a instância da aplicação FastAPI

app = FastAPI()

# Instancia o gerenciador de chamados (fila compartilhada entre rotas)
gerenciador = GerenciadorFilaChamados()

@app.get("/")
def read_root():
    return {"mensagem": "API de Fila de Prioridade funcionando!"}

@app.post("/chamado")
def adicionar_chamado(dados: ChamadoInput):
    """
    Rota para adicionar um novo chamado.
    Recebe os dados como JSON e adiciona na fila.
    """
    chamado = ChamadoSuporte(
        id_chamado=dados.id_chamado,
        cliente_nome=dados.cliente_nome,
        tipo_cliente=dados.tipo_cliente,
        tipo_chamado=dados.tipo_chamado,
        descricao=dados.descricao
    )
    try:
        gerenciador.adicionar_chamado(chamado)
        return {"mensagem": "Chamado adicionado com sucesso", "id": chamado.id_chamado}
    except ValueError as e:
        return {"erro": str(e)}

@app.get("/fila")
def listar_fila():
    """
    Rota que retorna a lista atual de chamados aguardando na fila.
    """
    return gerenciador.listar_fila()

@app.get("/proximo_chamado")
def proximo_chamado():
    """
    Rota que processa o próximo chamado da fila (maior prioridade).
    Envia notificação se for urgente.
    """
    chamado = gerenciador.processar_proximo()
    if not chamado:
        return {"mensagem": "Fila de chamados vazia."}

    return {
        "mensagem": "Chamado processado com sucesso",
        "id": chamado.id_chamado,
        "cliente": chamado.cliente_nome,
        "tipo_chamado": chamado.tipo_chamado,
        "tipo_cliente": chamado.tipo_cliente,
        "descricao": chamado.descricao,
        "timestamp": chamado.timestamp.isoformat()
    }


@app.post("/escalar/{id_chamado}")
def escalar_chamado(id_chamado: str):
    """
    Endpoint para escalar a prioridade de um chamado.
    A prioridade do chamado é aumentada (diminuída numericamente), garantindo que
    ela não seja inferior a 1 (prioridade máxima).
    """
    for i, (prioridade, timestamp, chamado) in enumerate(gerenciador.fila_heap):
        # Procurar o chamado com o id fornecido
        if chamado.id_chamado == id_chamado:
            # Ajustar a prioridade do chamado, diminuindo a prioridade (aumentando a urgência)
            # Não permitimos que a prioridade seja menor que 1
            nova_prioridade = (max(prioridade[0] - 1, 1), prioridade[1])  # reduz tipo_chamado, não menor que 1
            # Atualizar a fila com a nova prioridade
            gerenciador.fila_heap[i] = (nova_prioridade, timestamp, chamado)
            # Reorganizar a heap para manter a propriedade da fila de prioridade
            heapq.heapify(gerenciador.fila_heap)
            return {"mensagem": f"Chamado {id_chamado} escalado com sucesso."}
    return {"erro": "Chamado não encontrado na fila."}


@app.post("/atribuir/{id_chamado}")
def atribuir_agente(id_chamado: str, agente: str):
    """
    Endpoint para atribuir um agente a um chamado específico.
    O id do chamado é passado na URL, e o agente é passado no corpo da requisição.
    """
    for _, _, chamado in gerenciador.fila_heap:
        # Procurar o chamado pelo id
        if chamado.id_chamado == id_chamado:
            # Atribuir o agente ao chamado
            chamado.agente = agente
            return {"mensagem": f"Chamado {id_chamado} atribuído a {agente}."}
    return {"erro": "Chamado não encontrado."}


@app.get("/stream")
async def stream_fila():
    """
    Endpoint para transmitir as atualizações da fila de chamados em tempo real
    utilizando Server-Sent Events (SSE).
    O SSE permite que o navegador receba atualizações contínuas do servidor sem a necessidade de re-carregar a página.
    """
    async def event_generator():
        # Função geradora assíncrona que envia os dados da fila em intervalos de 2 segundos
        while True:
            # Obter a lista atualizada da fila de chamados
            fila = gerenciador.listar_fila()
            # Enviar os dados para o cliente via SSE
            yield f"data: {fila}\n\n"
            # Esperar 2 segundos antes de enviar a próxima atualização
            await asyncio.sleep(2)

    return EventSourceResponse(event_generator())


templates = Jinja2Templates(directory="TrabalhoSala")

@app.get("/web", response_class=HTMLResponse)
def web_interface(request: Request):
    """
    Endpoint que serve a interface web da fila de chamados.
    A página HTML será renderizada utilizando o Jinja2.
    """
    return templates.TemplateResponse("fila.html", {"request": request})

