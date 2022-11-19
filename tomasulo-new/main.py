from typing import List, TextIO
import sys
from Tomasulo import Tomasulo
from Color import COLOR

# Função que interpreta o arquivo de entrada
# Separa as intruções em uma lista
def interpretador(file):
    instrucoes = []
    for line in file:
        instrucoes.append(line.replace(',', '').split())
    return instrucoes

def menu():
    print(COLOR.HEADER+"=== Algoritmo de Tomasulo ==="+COLOR.ENDC)
    print("- Gustavo Torres Bretas Alves")
    print("- Maria Fernanda Oliveira Guimarães")
    print("- Maria Luiza Raso")
    print("- Rafael Lopes Murta")
    print("- Yan Silva Dumont")
    print(COLOR.OKBLUE+"=========== Configurações: ============"+COLOR.ENDC)
    
    debug = input("- Debug? (s/n) - Enter para não: ")
    status_avancado = input("- Status avançado? [Mostrar Registradores e Celulas de Memoria] (s/n) - Enter para não: ")
    arquivo = input("- Arquivo de entrada? - Enter para o testes/input.txt: ")

    debug = debug.lower()
    status_avancado = status_avancado.lower()
    yes = ["s", "y", "sim", "yes"]

    if debug in yes:
        debug = True
    else:
        debug = False

    if status_avancado in yes:
        status_avancado = True
    else:
        status_avancado = False

    if(arquivo == ""):
        arquivo = "testes/input.txt"


    try:
        inputFile = open(arquivo)
    except:
        print(COLOR.FAIL+"Arquivo de leitura não encontrado"+COLOR.ENDC)
        sys.exit()

    instrucoes = interpretador(inputFile)
    Tomasulo(instrucoes, debug, status_avancado).run()



# Função Main
def main():
    menu()

if __name__ == "__main__":
    main()