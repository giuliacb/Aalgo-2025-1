import random
import matplotlib.pyplot as plt
import networkx as nx
#pip install matplotlib networkx


# Classe que representa um nó da árvore binária de busca (ABB)
class No:
    def __init__(self, valor):
        self.valor = valor
        self.esquerda = None
        self.direita = None

# Função para inserir um valor na ABB
# Mantém a propriedade da ABB onde valores menores ficam à esquerda e maiores à direita
def inserir_abb(raiz, valor):
    """ Insere um valor na ABB """
    if raiz is None:
        return No(valor)
    if valor < raiz.valor:
        raiz.esquerda = inserir_abb(raiz.esquerda, valor)
    else:
        raiz.direita = inserir_abb(raiz.direita, valor)
    return raiz

def buscar_abb(raiz, valor):
    """ Pesquisa um valor na ABB """
    if raiz is None or raiz.valor == valor:
        return raiz # Retorna o nó encontrado ou None se não existir
    if valor < raiz.valor:
        return buscar_abb(raiz.esquerda, valor)
    return buscar_abb(raiz.direita, valor)

def remover_abb(raiz, valor):
    """ Remove um valor da ABB """
    if raiz is None:
        return raiz
    
    # Encontrar o nó a ser removido
    if valor < raiz.valor:
        raiz.esquerda = remover_abb(raiz.esquerda, valor)
    elif valor > raiz.valor:
        raiz.direita = remover_abb(raiz.direita, valor)
    else:
       # Caso 1: Nó sem filhos ou com apenas um filho
        if raiz.esquerda is None:
            return raiz.direita
        elif raiz.direita is None:
            return raiz.esquerda
        
         # Caso 2: Nó com dois filhos - encontrar o menor nó da subárvore direita
        temp = raiz.direita
        while temp.esquerda:
            temp = temp.esquerda
        raiz.valor = temp.valor #substitui o valor
        raiz.direita = remover_abb(raiz.direita, temp.valor) #remove o sucessor
    return raiz

def imprimir_arvore(raiz, nivel=0):
    """ Imprime a árvore de forma hierárquica """
    if raiz is not None:
        imprimir_arvore(raiz.direita, nivel + 1)
        print(' ' * 4 * nivel + '->', raiz.valor)
        imprimir_arvore(raiz.esquerda, nivel + 1)

# Função para realizar a varredura pré-ordem (RED - Raiz, Esquerda, Direita)
def varredura_red(raiz):
    """ Realiza a varredura em ordem RED (pré-ordem) e retorna a lista de valores """
    if raiz is None:
        return []
    return [raiz.valor] + varredura_red(raiz.esquerda) + varredura_red(raiz.direita)

def desenhar_arvore(raiz):
    """ Gera uma representação gráfica da árvore usando NetworkX e Matplotlib """
    G = nx.DiGraph() # Criando um grafo direcionado
    pos = {}

    #Função auxiliar para adicionar nós e arestas
    def adicionar_nos(raiz, x=0, y=0, nivel=1):
        if raiz is not None:
            G.add_node(raiz.valor)
            pos[raiz.valor] = (x, -y)
            deslocamento = 2 ** (4 - nivel) # Controla o espaçamento entre nó
            if raiz.esquerda:
                G.add_edge(raiz.valor, raiz.esquerda.valor)
                adicionar_nos(raiz.esquerda, x - deslocamento, y + 1, nivel + 1)
            if raiz.direita:
                G.add_edge(raiz.valor, raiz.direita.valor)
                adicionar_nos(raiz.direita, x + deslocamento, y + 1, nivel + 1)
    
    adicionar_nos(raiz)
    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color="lightblue", edge_color="gray")
    plt.show()

# Exemplo de uso
N = 15  # Número de elementos únicos desejados
valores = sorted(set(random.randint(1, 100) for _ in range(N))) # Gerar valores únicos e ordenar
raiz = None
for valor in valores:
    raiz = inserir_abb(raiz, valor)

# Exibir a árvore
print("Árvore gerada:")
imprimir_arvore(raiz)

# Varredura RED
elementos_red = varredura_red(raiz)
print("Varredura RED:", elementos_red)

# Pesquisa
valor_pesquisa = valores[5]
print(f"Pesquisa pelo valor {valor_pesquisa}:", "Encontrado" if buscar_abb(raiz, valor_pesquisa) else "Não encontrado")

# Remoção
delecao_valor = valores[3]
print(f"Removendo o valor {delecao_valor}")
raiz = remover_abb(raiz, delecao_valor)
imprimir_arvore(raiz)

# Desenhar a árvore
desenhar_arvore(raiz)
