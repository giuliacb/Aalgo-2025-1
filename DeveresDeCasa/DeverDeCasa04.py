import math

def F(n):
    if n == 1: #caso base
        return 2
    return 2 * F(n - 1) + n ** 2 #chamada recursiva 

n = int(input("Digite o valor de n: "))

print(f"F({n}) = {F(n)}")


#formula fechada
#com a formula fechada, se o usuario digitar n =3 o programa vai calcular F(3) 
#diretamente pela formula fechada, evitando o uso de recursão e tornando 
#o calculo mais rapido para valores grandes de n

# def F_fechada(n):
#     return [...]???