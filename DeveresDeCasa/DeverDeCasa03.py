def eh_palindromo(arr, esquerda=0, direita=None):
    # provavel questao de prova
    # Não foi pedido, no entanto gostaria de testar para strings também
    # Se a entrada for uma string, converte para uma lista de caracteres
    if isinstance(arr, str):
      # isinstance é uma função embutida do Python que verifica se um objeto pertence a uma determinada classe ou a uma tupla de classes.
      # isinstance(obj, classinfo) obj: O objeto que você quer verificar/classinfo: A classe (ou tupla de classes) contra a qual você quer testar o objeto.
      # neste caso verifica se arr é str, se for, converte para uma lista de caracteres para que a função trate como um array
        arr = list(arr)

    # Se direita for None, define como o índice do último elemento
    if direita is None:
        direita = len(arr) - 1

    # Caso base: se os índices se cruzarem ou forem iguais, é um palíndromo
    if esquerda >= direita:
        return True

    # Se os elementos nas posições esquerda e direita forem diferentes, não é um palíndromo
    if arr[esquerda] != arr[direita]:
        return False

    # Chamada recursiva, avançando left e reduzindo right
    return eh_palindromo(arr, esquerda + 1, direita - 1)

arrayX = input("Digite um array: ")
arrayX = list(arrayX)
print(eh_palindromo(arrayX))


# Exemplos de uso
#array1 = [0, 1, 2, 3, 2, 1, 0]  # Palíndromo
#array2 = ['a', 'b', 'c', 'f', 'b', 'a']  # Não é palíndromo
#array3 = "giulia"

# Testando a função
#print(eh_palindromo(array1))  # True
#print(eh_palindromo(array2))  # False
#print(eh_palindromo(array3))  # False