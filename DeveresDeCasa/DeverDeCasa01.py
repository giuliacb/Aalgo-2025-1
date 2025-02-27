# Importar os módulos do sistema operacional
import locale
import pytz # type: ignore // pip install pytz (p usar no vs code)
from datetime import datetime
import random

# Ajustar a localidade para en_US.UTF-8
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Definir o fuso horário para o Brasil (Brasília)
con_fuso_horario = pytz.timezone("America/Sao_Paulo")

# Separador de seções no código
conSeparador = "\nXXXXXXXXXXXXX---XXXXXXXXXXXXX\n"

# Função para formatar tempo de execução (dado tempo de início e fim, retorna h:m:milisegundos formatado)
def formata_tempo_execucao(dttInicio, dttFim):
    strTempo = dttFim - dttInicio
    str_tempo_execucao_formatado = "{:02d}:{:02d}.{:06d}".format(
        strTempo.seconds // 60,  # Minutos
        strTempo.seconds % 60,  # Segundos
        strTempo.microseconds  # Microsegundos
    )
    return str_tempo_execucao_formatado

# Função para formatar a data e hora
def formata_data(dttParametro):
    return dttParametro.strftime("%d/%m/%Y - %H:%M:%S.%f")

# Função para formatar números com separadores de milhar
def formata_numero(numero):
    return locale.format_string("%d", numero, grouping=True)

# Função para criar um array de números inteiros entre intMin e intMax
def montar_array(intElementosArray, intMin, intMax):
    x = 0
    array = []
    while x < intElementosArray:
        numero = random.randint(intMin, intMax)
        array.append(numero)
        x += 1
    return array

# Função para ler um número inteiro do usuário
def ler_inteiro(strMensagem):
    while True:
        try:
            tamanho = int(input(strMensagem))
            break  # Se a entrada for válida, sai do loop e finaliza o programa
        except ValueError:
            print("Erro: Por favor, digite um número inteiro válido.")
    return tamanho

# Função para marcar o início de um processo e exibir a data e hora
def marcar_inicio(strMensagem):
    dttInicio = datetime.now(con_fuso_horario)
    dttInicioFormatado = formata_data(dttInicio)
    print(f"Iniciando {strMensagem} as : " + str(dttInicioFormatado))
    return dttInicio

# Função para marcar o fim de um processo e exibir a data e hora
def marcar_fim(strMensagem):
    dttFim = datetime.now(con_fuso_horario)
    dttFimFormatado = formata_data(dttFim)
    print(f"Finalizando {strMensagem} as : " + str(dttFimFormatado))
    return dttFim

# -------------------------------------------------------------------------------------------------------------#

# Função de ordenação Bubble Sort
def bubble_sort(arr):
    """
    Função que implementa o algoritmo de ordenação Bubble Sort.
    A ideia é comparar elementos adjacentes e trocá-los de lugar se estiverem fora de ordem.
    A cada iteração do laço externo, o maior elemento "borbulha" para o final da lista.
    """
    num_elementos = len(arr)  # comprimento da lista arr
    for i in range(num_elementos): # Cada iteração do laço externo representa uma "passagem" pelo vetor, onde comparamos os elementos e trocamos se necessário. A cada passada, o maior elemento já vai "borbulhando" para o final da lista.
        trocou = False  #  verificar se houve alguma troca na iteração. Se não houver troca, significa que a lista já está ordenada e o algoritmo pode ser interrompido precocemente.
        for j in range(0, num_elementos-i-1):  # O laço interno... Percorre a lista e compara elementos adjacentes. O laço vai até n-i-1 porque após cada passagem, o maior elemento já foi "colocado" no final da lista, evitando comparação com os elementos já ordenados.
            if arr[j] > arr[j+1]:  # Se o elemento atual for maior que o próximo
                arr[j], arr[j+1] = arr[j+1], arr[j]  # Troca os dois elementos
                trocou = True
        if not trocou:  # Se não houve troca, a lista já está ordenada
            break
    return arr

# Função principal para executar e medir o tempo de ordenação
def executar_algoritmo():
    # Solicitar ao usuário o tamanho da lista
    tamanho_lista = ler_inteiro("Digite o tamanho da lista para ordenação: ")

    # Gerar um array aleatório com os números
    lista = montar_array(tamanho_lista, 1, 1000)

    # Marcar o início da execução
    dttInicio = marcar_inicio("algoritmo de ordenação Bubble Sort")

    # Ordenar a lista usando Bubble Sort
    bubble_sort(lista)

    # Marcar o fim da execução
    dttFim = marcar_fim("algoritmo de ordenação Bubble Sort")

    # Calcular o tempo de execução
    tempo_execucao = formata_tempo_execucao(dttInicio, dttFim)

    # Exibir o tempo de execução
    print(f"Tempo de execução para ordenar uma lista de tamanho {formata_numero(tamanho_lista)}: {tempo_execucao}.")

# Executando a função principal
executar_algoritmo()


# Digite o tamanho da lista para ordenação: 100
# Iniciando algoritmo de ordenação Bubble Sort as : 27/02/2025 - 10:56:27.696012  
# Finalizando algoritmo de ordenação Bubble Sort as : 27/02/2025 - 10:56:27.696648
# Tempo de execução para ordenar uma lista de tamanho 100: 00:00.000636.

# Digite o tamanho da lista para ordenação: 1000
# Iniciando algoritmo de ordenação Bubble Sort as : 27/02/2025 - 10:57:24.530688
# Finalizando algoritmo de ordenação Bubble Sort as : 27/02/2025 - 10:57:24.583240
# Tempo de execução para ordenar uma lista de tamanho 1,000: 00:00.052552.

# Digite o tamanho da lista para ordenação: 10000
# Iniciando algoritmo de ordenação Bubble Sort as : 27/02/2025 - 10:58:06.289671
# Finalizando algoritmo de ordenação Bubble Sort as : 27/02/2025 - 10:58:12.124258
# Tempo de execução para ordenar uma lista de tamanho 10,000: 00:05.834587.

# Digite o tamanho da lista para ordenação: 100000
# Iniciando algoritmo de ordenação Bubble Sort as : 27/02/2025 - 10:58:42.788161
# Finalizando algoritmo de ordenação Bubble Sort as : 27/02/2025 - 11:08:18.318667
# Tempo de execução para ordenar uma lista de tamanho 100,000: 09:35.530506.

#A complexidade do Bubble Sort é O(n²) no pior e no caso médio, o que o torna um algoritmo ineficiente para listas grandes.
#Embora o melhor caso seja linear (O(n)), a complexidade quadrática no pior caso faz com que, em muitas situações, algoritmos
#mais eficientes como Quick Sort ou Merge Sort (com complexidade média de O(n log n)) sejam preferidos para grandes volumes de dados.
