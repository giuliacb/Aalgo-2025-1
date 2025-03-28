import requests
from bs4 import BeautifulSoup
import re
import time
import logging  # permite resgistrar logs no sistema, armazenando erros, avisos e ações
import csv
import os
from urllib.parse import urlparse # urlparse serve para analisar e decompor urls em seus comps (protocolo, dominio, caminho...)
from datetime import datetime

#configurando logs CSV
log_file = "monitoramento.csv"

#verifica se o arquivo monitoramento.csv ja existe para nn sobrescrever os dados
#os fornece funções para interagir com o sistema operacional
if not os.path.exists(log_file): 
  with open(log_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Data", "Hora", "Usuário", "Nível", "Mensagem"])


def registrar_log(usuario, mensagem, nivel="INFO"):
  """Registra um log personalizado em arquivo CSV com o nome do usuário, data e hora, mensagem e info."""
  now = datetime.now()
  data = now.strftime("%d-%m-%Y")
  hora = now.strftime("%H:%M:%S")
  with open(log_file, "a", newline="", encoding="utf-8") as file:
     writer = csv.writer(file)
     writer.writerow([data, hora, usuario, nivel, mensagem])


#validando se a url é valida
def validar_url(url):
  """Verifica se a URL fornecida é válida.

  Args:
    url (str): URL a ser validada.

  Returns:
    bool: True se a URL for válida, False caso contrário.
  """
  try:
    resultado = urlparse(url)
    #scheme -> verifica de a url possui um esquema (http ou https)
    #netloc -> verifica se url possui dominio (tipo exemplo.com)
    #all[] retorna True se ambos os elementos forem valores não vazios
    return all([resultado.scheme, resultado.netloc])
  except ValueError:
    return False


#solicitando nome ao usuario 
def solicitar_nome_user():
  """Solicita o nome do usuário e valida o formato.

    Returns:
        str: Nome do usuário válido.
  """
  while True:
    nome = input("Digie seu nome: ").strip() #strip remove espaços extras no inicio e final
    #[A-Za-z]{3,} garante que tenha pelo menos 3 letras
    #[A-Za-z]{3,}(\s[A-Za-z]+)* garante que seja composto apenas por letras, permite nomes compostos mas não espaços extras
    if re.fullmatch(r"[A-Za-z]{3,}(\s[A-Za-z]+)*", nome):
      return nome
    else:
      print("Nome inválido. Deve conter pelo menos 3 letras e apenas caracteres alfabéticos.")


#xpath localiza o elemento html exato que contem o numero 
def encontrar_xpath(site, numero, usuario):
  """Encontra o XPath do número dentro do HTML.

  Args:
    site (BeautifulSoup): Objeto BeautifulSoup do HTML.
    numero (str): Número a ser localizado.

  Returns:
   str: XPath do elemento contendo o número.
  """
  #busca todos os elementos de texto no ttml que correspondem a expressao regular que busca exatamente o numero esperado
  for i, tag in enumerate(site.find_all(string=re.compile(re.escape(numero)))):
    caminho = []
    while tag:
      if tag.parent is None:
         break #sai do loop se nao houver mais pai
      position = list(tag.parent.children).index(tag) + 1
      caminho.insert(0, f"{tag.parent.name}[{position}]")
      tag = tag.parent
    xpath = "/" + "/".join(caminho)
    registrar_log(usuario, f"XPath do número {numero}: {xpath}")
    return xpath
  return "XPath não encontrado."


def extrair_numero(url, posicao, usuario):
  #simula uma requisição feita por um navegador real - evita bloqueio
  """Extrai um número de uma página web na posição especificada.

    Args:
        url (str): URL da página web.
        posicao (int): Posicao do número na lista de números encontrados.

    Returns:
        tuple: (numero, contexto) onde numero é o número extraído e contexto é o trecho ao redor.
    """
  headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
  }

  try:
    #requests.get() é uma função da biblioteca requests usada para fazer uma requisição HTTP do tipo GET (solicitar dados de um servidor)
    requisicao = requests.get(url, headers=headers, timeout=10)
    requisicao.raise_for_status()  # Verifica se a resposta foi bem-sucedida (código de status HTTP 200)
  except requests.RequestException as e:
    registrar_log(usuario, f"Erro ao acessar a URL {url}: {e}", "ERROR")
    return None, None, None
    

  site = BeautifulSoup(requisicao.text, "html.parser")  # Analisa o conteúdo da página
  texto_pagina = site.get_text() # Extrai o texto da página

  # Encontra todos os números na página (inteiros e decimais)
  numeros_encontrados = re.findall(r"\d+[\.,]?\d*", texto_pagina)
  #\d+ -> procura um ou mais digitos (0-9)
    #[\.,]? -> procura opcionalmente (?) um ponto ou virgula que são usados como separadores decimais
    #\d* -> procura zero ou mais dígitos após os separador decimal (0-9)
    #re.findall() é uma função da biblioteca re que procura todas as ocorrências de um padrão (expressão regular) dentro de uma string (texto_pagina)

  if numeros_encontrados and posicao < len(numeros_encontrados):
      numero = numeros_encontrados[posicao]  # Pega o número da posição desejada
      inicio = texto_pagina.find(numero)  # Encontra o índice de onde o número aparece
      fim = inicio + len(numero)  # Índice final do número

      # Define um trecho ao redor do número para dar contexto (X caracteres antes e depois)
      inicio_contexto = max(0, inicio - 5)  # Garante que não pegue índices negativos
      fim_contexto = min(len(texto_pagina), fim + 150)  # Limita ao tamanho do texto

      #slicing (fatiamento) para extrair um trecho da string texto_pagina entre as posições indicadas por inicio_contexto e fim_contexto
      contexto = texto_pagina[inicio_contexto:fim_contexto].strip()

      xpath = encontrar_xpath(site, numero, usuario)
      registrar_log(usuario, f"Número encontrado: {numero} (posição {posicao})")
      return numero, contexto, xpath
    
  registrar_log(usuario, "Nenhum número encontrado na página.", "WARNING")
  return None, None, None


#garante que um bloco de código seja executado apenas quando o script é executado diretamente
#ou seja, quando um script é importado em outro programa, __name__ recebe o nome do arquivo
#se rodar o script diretamente, ele chama e roda todas as funções, ja se importar em outro script, 
#as funções estarão disponiveis mas não serão chamadas automaticamente
if __name__ == "__main__":
  usuario = solicitar_nome_user()
  registrar_log(usuario, "Usuário registrado e iniciou monitoramento.")

  url = input("Digite a sua URL desejada: ")
  while not validar_url(url):
    print("URL inválida. Por favor, digite novamente.")
    url = input("Digite a sua URL desejada: ").strip() #sem o strip() a validação poderia falhar por causa dos espaços

  try: # captura erros ao converter a entrada do usuario em um int
    # Solicita a posição do número ao usuário
    posicao = int(input("Digite a posição do número a ser monitorado (começando de 0): "))
  except ValueError: #se a conversao falhar um erro (ValueError) ocorre...esse bloco o captura, exibe uma mensagem de error e finaliza o programa (exit())
    registrar_log(usuario, "A posição deve ser um número inteiro.", "ERROR")
    exit()

  # Capturando o número inicial e seu contexto
  numero_inicial, contexto_inicial, xpath_inicial = extrair_numero(url, posicao, usuario)

  #verifica se o num foi encontrado na pag
  if numero_inicial:
      print(f"Monitorando... Número inicial encontrado na página: {numero_inicial}")
      print(f"Contexto: ...{contexto_inicial}...")
      print(f"XPath: {xpath_inicial}")
  else:
      print("Nenhum número encontrado na página.")
      exit()

  # Loop para monitorar mudanças no número
  while True:
      time.sleep(30)  # Espera 30 segundos antes de verificar novamente
      numero_atual, contexto_atual, xpath_atual = extrair_numero(url, posicao, usuario)

      #o primeiro numero_atual garente que a variavel nao é None ou str vazia
      #ja numero_atual != numero_inicial verifica se o num mudou
      if numero_atual and numero_atual != numero_inicial:
          print(f"🚨 Mudança detectada! Novo valor: {numero_atual} (Anterior: {numero_inicial})")
          print(f"Novo contexto: ...{contexto_atual}...")
          print(f"Novo XPath: {xpath_atual}.")
          registrar_log(usuario, f"🚨 Mudança detectada: {numero_inicial} -> {numero_atual}")
          numero_inicial = numero_atual  # Atualiza o número inicial para continuar monitorando
      else:
          print(f"Nenhuma mudança detectada. O número continua: {numero_inicial}")


# python -m pydoc Trabalho01 -- GERA DOCUMENTAÇÃO NO TERMINAL
# python -m pydoc -w Trabalho01 -- GERA ARQUIVO HTML COM A DOCUMENTAÇÃO
# python -m pydoc -p 8000 -- RODAR UM SERVIDOR DE DOCUMENTAÇÃO
