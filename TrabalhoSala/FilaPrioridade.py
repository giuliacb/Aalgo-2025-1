from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import heapq
from typing import List, Tuple
from plyer import notification
from enum import Enum

# Mapeamentos de prioridade
class PrioridadeChamadoEnum(Enum):
    SERVER_DOWN = 1
    IMPACTA_PRODUCAO = 2
    SEM_IMPACTO = 3
    DUVIDA = 4

class PrioridadeClienteEnum(Enum):
    PRIORITARIO = 1
    SEM_PRIORIDADE = 2
    DEMONSTRACAO = 3

# --- Função para calcular prioridade combinada ---
def calcular_prioridade_combinada(tipo_chamado, tipo_cliente):
    """
    Retorna a prioridade combinada (menor valor = maior prioridade).
    """
    try:
        prioridade_chamado = PrioridadeChamadoEnum[tipo_chamado.upper().replace(" ", "_")].value
        prioridade_cliente = PrioridadeClienteEnum[tipo_cliente.upper().replace(" ", "_")].value
        #Use .upper().replace(" ", "_") para tornar a entrada do usuário compatível com o Enum
        return (prioridade_chamado, prioridade_cliente)
    except KeyError:
        raise ValueError("Tipo de chamado ou cliente inválido.")

# --- MODELO Pydantic para recebimento de dados via JSON ---
class ChamadoInput(BaseModel):
    id_chamado: str
    cliente_nome: str
    tipo_cliente: str
    tipo_chamado: str
    descricao: str

# --- OBJETO Chamado Interno ---
class ChamadoSuporte:
    def __init__(self, id_chamado, cliente_nome, tipo_cliente, tipo_chamado, descricao):
        self.id_chamado = id_chamado
        self.cliente_nome = cliente_nome
        self.tipo_cliente = tipo_cliente.upper().replace(" ", "_")
        self.tipo_chamado = tipo_chamado.upper().replace(" ", "_")
        self.descricao = descricao
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
        self.fila_heap: List[Tuple[Tuple[int, int], datetime, ChamadoSuporte]] = []

    def adicionar_chamado(self, chamado: ChamadoSuporte):
        prioridade = calcular_prioridade_combinada(chamado.tipo_chamado, chamado.tipo_cliente)
        print(f"[LOG] Chamado {chamado.id_chamado} adicionado com prioridade {prioridade}")
        heapq.heappush(self.fila_heap, (prioridade, chamado.timestamp, chamado))
        

        if chamado.tipo_chamado in ["SERVER_DOWN", "IMPACTA_PRODUCAO"]:
            enviar_notificacao_desktop(
                f"Novo chamado: {chamado.tipo_chamado.replace('_', ' ').title()}",
                f"Cliente: {chamado.cliente_nome}\nDescrição: {chamado.descricao}"
            )

    def listar_fila(self):
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

# --- Inicialização da API e da fila ---

app = FastAPI()
gerenciador = GerenciadorFilaChamados()

@app.get("/")
def read_root():
    return {"mensagem": "API de Fila de Prioridade funcionando!"}

@app.post("/chamado")
def adicionar_chamado(dados: ChamadoInput):
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
    return gerenciador.listar_fila()

@app.get("/proximo_chamado")
def proximo_chamado():
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
