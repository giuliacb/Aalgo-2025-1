import re
import time
import csv
import os
from urllib.parse import urlparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#para executar o código precisa instalar a biblioteca do selenium, as outras já vem instaladas com o Python
#pip install selenium

# Configuração do log CSV
log_file = "monitoramento.csv"

#se o arquivo não existe, ele entra no bloco e executa
if not os.path.exists(log_file):
    with open(log_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Data", "Hora", "Usuário", "Nível", "Mensagem"])

def registrar_log(usuario, mensagem, nivel="INFO"):
    """
    Registra uma entrada de log no arquivo CSV de monitoramento.

    Args:
        usuario (str): Nome do usuário que está utilizando o sistema.
        mensagem (str): Mensagem a ser registrada no log.
        nivel (str): Nível do log (ex: INFO, WARNING, ERROR). Padrão é "INFO".
    """
    now = datetime.now()
    data = now.strftime("%d-%m-%Y")
    hora = now.strftime("%H:%M:%S")
    with open(log_file, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([data, hora, usuario, nivel, mensagem])

def validar_url(url):
    """
    Valida se uma string é uma URL válida.

    Args:
        url (str): URL a ser validada.

    Returns:
        bool: True se a URL for válida, False caso contrário.
    """
    try:
        resultado = urlparse(url)
        return all([resultado.scheme, resultado.netloc])
    except ValueError:
        return False

def solicitar_nome_user():
    """
    Solicita o nome do usuário e valida se é composto por pelo menos 3 letras e apenas caracteres alfabéticos.

    Returns:
        str: Nome válido do usuário.
    """
    while True:
        nome = input("Digite seu nome: ").strip()
        if re.fullmatch(r"[A-Za-z]{3,}(\s[A-Za-z]+)*", nome): #expressão regular para verificar nome
            return nome
        else:
            print("Nome inválido. Deve conter pelo menos 3 letras e apenas caracteres alfabéticos.")

def configurar_driver():
    """
    Configura e retorna um driver do Selenium com Firefox em modo privado.

    Returns:
        webdriver.Firefox: Driver do Firefox configurado.
    """
    #options = webdriver.ChromeOptions()
    #options.add_argument("--headless")  # Roda sem abrir o navegador (remova para visualizar)
    #options.add_argument("--disable-gpu")
    #options.add_argument("--no-sandbox")
    #options.add_argument("--disable-extensions")
    #options.add_argument("--disable-blink-features=AutomationControlled")
    #options.add_argument("--incognito")  # Modo anônimo
    #options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    #options.add_argument(r"--user-data-dir=C:\Users\Giulia\AppData\Local\Google\Chrome\User Data\Profile 1")
    #options.add_experimental_option("excludeSwitches", ["enable-automation"])
    #options.add_experimental_option("useAutomationExtension", False)
    options = Options()
    options.add_argument("--private")
    options.binary_location = (r"C:\Users\Giulia\AppData\Local\Mozilla Firefox\firefox.exe") #mudar para path do seu respectivo browser
    service = Service(executable_path=r"C:\Program Files\geckodriver-v0.36.0-win64\geckodriver.exe") #mesma coisa, precisa mudar
    return webdriver.Firefox(service=service, options=options)

def encontrar_numero_e_xpath(driver, numero, usuario):
    """
    Procura um número em uma página carregada no Selenium e retorna seu XPath.

    Args:
        driver (webdriver): Driver do Selenium com a página carregada.
        numero (str): Número a ser encontrado na página.
        usuario (str): Nome do usuário para fins de log.

    Returns:
        tuple: Número encontrado e XPath correspondente. Se não encontrado, retorna (None, None).
    """
    try:
        # Espera até que algum texto da página contenha o número (tempo limite: 10s)
        elementos = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, f"//*[contains(text(), '{numero}')]"))
        )
        for elemento in elementos:
            try:
                texto = elemento.text.strip()
                if numero in texto:
                    # Constrói o XPath absoluto do elemento encontrado
                    xpath = driver.execute_script("""
                        function absoluteXPath(element) {
                            var comp, comps = [];
                            var parent = null;
                            var xpath = '';
                            var getPos = function(element) {
                                var position = 1, curNode;
                                if (element.nodeType == Node.ATTRIBUTE_NODE) {
                                    return null;
                                }
                                for (curNode = element.previousSibling; curNode; curNode = curNode.previousSibling){
                                    if (curNode.nodeName == element.nodeName)
                                        ++position;
                                }
                                return position;
                            }

                            if (element instanceof Document) {
                                return '/';
                            }

                            for (; element && !(element instanceof Document); element = element.nodeType ==Node.ATTRIBUTE_NODE ? element.ownerElement : element.parentNode) {
                                comp = {};
                                switch (element.nodeType) {
                                    case Node.TEXT_NODE:
                                        comp.name = 'text()';
                                        break;
                                    case Node.ATTRIBUTE_NODE:
                                        comp.name = '@' + element.nodeName;
                                        break;
                                    case Node.PROCESSING_INSTRUCTION_NODE:
                                        comp.name = 'processing-instruction()';
                                        break;
                                    case Node.COMMENT_NODE:
                                        comp.name = 'comment()';
                                        break;
                                    case Node.ELEMENT_NODE:
                                        comp.name = element.nodeName;
                                        break;
                                }
                                comp.position = getPos(element);
                                comps.push(comp);
                            }

                            for (var i = comps.length - 1; i >= 0; i--) {
                                comp = comps[i];
                                xpath += '/' + comp.name.toLowerCase();
                                if (comp.position !== null) {
                                    xpath += '[' + comp.position + ']';
                                }
                            }

                            return xpath;
                        }
                        return absoluteXPath(arguments[0]);
                    """, elemento)

                    registrar_log(usuario, f"XPath do número {numero}: {xpath}")
                    return numero, xpath
            except Exception:
                continue

    except Exception:
        pass

    return None, None

def extrair_valor_por_xpath(driver, xpath):
    """
    Extrai o texto de um elemento localizado por um XPath na página carregada pelo Selenium.

    Args:
        driver (webdriver): Driver do Selenium com a página carregada.
        xpath (str): Caminho XPath do elemento.

    Returns:
        str: Texto extraído do elemento ou None se não encontrado.
    """
    try:
        elemento = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return elemento.text.strip()
    except Exception:
        return None
    
if __name__ == "__main__":
    usuario = solicitar_nome_user()
    registrar_log(usuario, "Usuário registrado e iniciou monitoramento.")

    url = input("Digite a sua URL desejada: ")
    while not validar_url(url):
        print("URL inválida. Por favor, digite novamente.")
        url = input("Digite a sua URL desejada: ").strip()

    numero_monitorado = input("Digite o número específico que deseja monitorar: ").strip()

    driver = configurar_driver()
    driver.get(url)
    WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")

    numero_inicial, xpath_inicial = encontrar_numero_e_xpath(driver, numero_monitorado, usuario)
    if numero_inicial:
        print(f"Monitorando... Número inicial encontrado na página: {numero_inicial}")
        print(f"XPath: {xpath_inicial}")
    else:
        print("❌ Número não encontrado na página.")
        registrar_log(usuario, f"Número {numero_monitorado} não encontrado.", "WARNING")
        driver.quit()
        exit()

    try:
        while True:
            WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")

            novo_valor = extrair_valor_por_xpath(driver, xpath_inicial)

            if novo_valor is None:
                time.sleep(1)
                novo_valor = extrair_valor_por_xpath(driver, xpath_inicial)

            if novo_valor is None:
                numero_reencontrado, novo_xpath = encontrar_numero_e_xpath(driver, numero_monitorado, usuario)
                if numero_reencontrado and novo_xpath != xpath_inicial:
                    print(f"⚠️ Valor mudou de lugar. Novo XPath encontrado: {novo_xpath}")
                    registrar_log(usuario, f"Valor realocado. Novo XPath: {novo_xpath}")
                    xpath_inicial = novo_xpath
                elif numero_reencontrado:
                    if numero_reencontrado == numero_inicial:
                        print(f"ℹ️  Valor reapareceu no mesmo XPath e continua {numero_inicial}.")
                    else:
                        print(f"ℹ️  Valor reapareceu no mesmo XPath e foi alterado para {numero_reencontrado}.")
                        registrar_log(usuario, f"ℹ️  Valor alterado no mesmo XPath: {numero_inicial} -> {numero_reencontrado}")
                        numero_inicial = numero_reencontrado
                else:
                    print(f"🚨 Alerta! O valor no XPath {xpath_inicial} desapareceu da página!")
                    registrar_log(usuario, f"🚨 Valor sumiu no XPath {xpath_inicial}.", "WARNING")
            elif novo_valor != numero_inicial:
                print(f"🚨 Mudança detectada! {numero_inicial} foi alterado para {novo_valor}.")
                registrar_log(usuario, f"🚨 Mudança detectada: {numero_inicial} -> {novo_valor}")
                numero_inicial = novo_valor
            else:
                print(f"Nenhuma mudança detectada. O número continua: {numero_inicial}")

            time.sleep(30)  # intervalo entre checagens

    except KeyboardInterrupt:
        print("\nMonitoramento encerrado pelo usuário.")
        registrar_log(usuario, "Monitoramento encerrado manualmente.", "INFO")
        driver.quit()
    except Exception as e:
        registrar_log(usuario, f"Erro inesperado: {e}", "ERROR")
        print(f"Erro inesperado: {e}")
        driver.quit()

# python -m pydoc TrabalhoOficial (nome_arquivo) -- GERA DOCUMENTAÇÃO NO TERMINAL
# python -m pydoc -w TrabalhoOficial -- GERA ARQUIVO HTML COM A DOCUMENTAÇÃO
# python -m pydoc -p 8000 -- RODAR UM SERVIDOR DE DOCUMENTAÇÃO
