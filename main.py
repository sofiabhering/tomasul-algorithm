import sys
from Architecture.instQueue import Instructuion

def createInstructionQueue(arq):
    queue = []
    for line in arq:
        aux = line.split()
        name = aux[0]
        aux = aux[1].split(',')
        if len(aux) > 2:
            x = Instructuion(name, aux[0],aux[1],aux[2])
            queue.append(x)
        elif len(aux) == 2:
            x = Instructuion(name, aux[0], aux[1], '')
            queue.append(x)
    return queue


def main():
    print("Implementação do Algoritmo de Tomasulo")
    arq = open("in.txt")
    iq = createInstructionQueue(arq)
    
    for i in iq:
        print(i.toString()) 

main()