import sys
from Architecture.instQueue import Instructuion
from Architecture.ReservationStation import ReservationStation
from Architecture.Register import Register
from Architecture.DataMemory import DataMemory
from Architecture.FunctionalUnit import FunctionalUnit

global clock, instrucoes, rsAddI, rsMulI, rsLdI, addUnit, mulUnit, ldUnit, memory, register, reservationStation, arquivoSaida

clock = 0
instrucoes = 0
rsAddI = 0  
rsMulI = 16  
rsLdI = 32
arquivoSaida = open("output.txt", "w")
addUnit = [FunctionalUnit() for i in range(3)]
mulUnit = [FunctionalUnit() for i in range(3)]
ldUnit = [FunctionalUnit() for i in range(3)]
memory = [DataMemory() for i in range(512)]
register = [Register() for i in range(32)]
reservationStation = [ReservationStation() for i in range(48)]


def createInstructionQueue(arq):
    queue = []
    for line in arq:
        aux = line.replace(",", '').split(' ')
        name = aux[0]
        if len(aux) > 3:
            x = Instructuion(name, int(aux[1][1:]), int(
                aux[2][1:]), int(aux[3][1:]), '')
            queue.append(x)
        elif len(aux) == 3:
            imm, rs = aux[2].replace("(", " ").replace(")", " ").split()
            x = Instructuion(name, int(aux[1][1:]), int(rs[1:]), '', int(imm))
            queue.append(x)
    return queue


def issue(instruction):
    global instrucoes
    op = instruction.name
    r = 0
    if op in ["ADD", "SUB", "MUL", "DIV"]:
        if op == "MUL" or op == "DIV":
            r = 16
            while reservationStation[r].busy and r < 32:
                r += 1
        else:
            while reservationStation[r].busy and r < 16:
                r += 1
        try:
            rd = instruction.dest
            rs = instruction.r1
            rt = instruction.r2
        except:
            raise Exception("Sintaxe invalida")

        if register[rs].Qi != None:
            reservationStation[r].Qj = register[rs].Qi
        else:
            reservationStation[r].Vj = register[rs].value

        if register[rt].Qi != None:
            reservationStation[r].Qk = register[rt].Qi
        else:
            reservationStation[r].Vk = register[rt].value

        reservationStation[r].busy = True
        register[rd].Qi = r

    elif op in ["LW", "SW"]:
        r = 32
        while reservationStation[r].busy and r < 48:
            r += 1

        if op == "LW":
            rd = instruction.dest
            imm = instruction.imm
            rs = instruction.r1

            reservationStation[r].Vj = memory[rs].value
            reservationStation[r].A = imm
            reservationStation[r].busy = True

            register[rd].Qi = r

        elif op == "SW":
            rd = instruction.dest
            imm = instruction.imm
            rs = instruction.r1

            if register[rs].Qi != None:
                reservationStation[r].Qj = register[rs].Qi
            else:
                reservationStation[r].Vj = register[rs].value

            reservationStation[r].A = imm
            reservationStation[r].busy = True

            memory[rd].Qi = r
    else:
        raise Exception("Instrução não reconhecida")

    reservationStation[r].exec = -1
    reservationStation[r].op = op
    instrucoes += 1


def simular_execucao(inst):
    if reservationStation[inst].op == "ADD":
        return reservationStation[inst].Vj + reservationStation[inst].Vk
    elif reservationStation[inst].op == "SUB":
        return reservationStation[inst].Vj - reservationStation[inst].Vk
    elif reservationStation[inst].op == "MUL":
        return reservationStation[inst].Vj * reservationStation[inst].Vk
    elif reservationStation[inst].op == "DIV":
        return reservationStation[inst].Vj // reservationStation[inst].Vk
    elif reservationStation[inst].op == "LW":
        return reservationStation[inst].Vj + reservationStation[inst].A
    elif reservationStation[inst].op == "SW":
        return reservationStation[inst].Vj + reservationStation[inst].A
    else:
        pass


def write():
    global instrucoes, register
    for unit in addUnit:
        if unit.busy and reservationStation[unit.inst].exec == 0:
            v = simular_execucao(unit.inst)
            for reg in register:
                if reg.Qi == unit.inst:
                    reg.Qi = None
                    reg.value = v
            for rs in reservationStation:
                if rs.Qj == unit.inst:
                    rs.Vj = v
                    rs.Qj = None
                if rs.Qk == unit.inst:
                    rs.Vk = v
                    rs.Qk = None
            instrucoes -= 1
            reservationStation[unit.inst] = ReservationStation()
            unit.busy = False
    # mulUnit
    for unit in mulUnit:  # Se ocupado e não está executando
        if unit.busy and reservationStation[unit.inst].exec == 0:
            v = simular_execucao(unit.inst)
            for reg in register:
                if reg.Qi == unit.inst:
                    reg.Qi = None
                    reg.value = v
            for rs in reservationStation:
                if rs.Qj == unit.inst:
                    rs.Vj = v
                    rs.Qj = None
                if rs.Qk == unit.inst:
                    rs.Vk = v
                    rs.Qk = None
            instrucoes -= 1
            # Limpa a estação de reserva
            reservationStation[unit.inst] = ReservationStation()
            unit.busy = False
    # ldUnit
    for unit in ldUnit:
        # Se ocupado e não está executando
        if unit.busy and reservationStation[unit.inst].exec == 0:
            v = simular_execucao(unit.inst)
            if reservationStation[unit.inst].op == "SW":
                for memory in memory:
                    if memory.Qi == unit.inst:
                        memory.Qi = None
                        memory.value = v
            else:
                for reg in register:
                    if reg.Qi == unit.inst:
                        reg.Qi = None
                        reg.value = v
            for rs in reservationStation:
                if rs.Qj == unit.inst:
                    rs.Vj = v
                    rs.Qj = None
                if rs.Qk == unit.inst:
                    rs.Vk = v
                    rs.Qk = None
            instrucoes -= 1
            reservationStation[unit.inst] = ReservationStation()
            unit.busy = False


def executarInstrucoes():
    global rsAddI, rsLdI, rsMulI
    for unit in addUnit:
        if unit.busy:
            reservationStation[unit.inst].exec -= 1
    for unit in mulUnit:
        if unit.busy:
            reservationStation[unit.inst].exec -= 1
    for unit in ldUnit:
        if unit.busy:
            reservationStation[unit.inst].exec -= 1

    for i in range(16):
        if reservationStation[rsAddI].busy and reservationStation[rsAddI].exec == -1 and reservationStation[rsAddI].Vj != None and reservationStation[rsAddI].Vk != None:
            if not addUnit[0].busy:
                addUnit[0].inst = rsAddI
                addUnit[0].busy = True
            elif not addUnit[1].busy:
                addUnit[1].inst = rsAddI
                addUnit[1].busy = True
            elif not addUnit[2].busy:
                addUnit[2].inst = rsAddI
                addUnit[2].busy = True
            else:
                break

            reservationStation[rsAddI].exec = 5
        rsAddI = (rsAddI + 1) % 16

        if reservationStation[rsMulI].busy and reservationStation[rsMulI].exec == -1 and reservationStation[rsMulI].Vj != None and reservationStation[rsMulI].Vk != None:
            if not mulUnit[0].busy:
                mulUnit[0].inst = rsMulI
                mulUnit[0].busy = True
            elif not addUnit[1].busy:
                mulUnit[1].inst = rsMulI
                mulUnit[1].busy = True
            elif not addUnit[2].busy:
                mulUnit[2].inst = rsMulI
                mulUnit[2].busy = True
            else:
                break

            if reservationStation[rsMulI].op == "MUL":
                reservationStation[rsMulI].exec = 15
            else:
                reservationStation[rsMulI].exec = 25
        rsMulI = ((rsMulI + 1) % 16) + 16

        if reservationStation[rsLdI].busy and reservationStation[rsLdI].exec == -1 and reservationStation[rsLdI].Vj != None:
            if not ldUnit[0].busy:
                ldUnit[0].inst = rsLdI
                ldUnit[0].busy = True
            elif not ldUnit[1].busy:
                ldUnit[1].inst = rsLdI
                ldUnit[1].busy = True
            elif not ldUnit[2].busy:
                ldUnit[2].inst = rsLdI
                ldUnit[2].busy = True
            else:
                break
            # setar o clock da operação todas levam 5 de clock para serem concluidas
            reservationStation[rsLdI].exec = 5
        rsLdI = ((rsLdI + 1) % 16) + 32


def escreverSaida():
    global arquivoSaida
    arquivoSaida.write("="*80)
    arquivoSaida.write("\n")
    arquivoSaida.write("Clock: {}\n".format(clock))
    arquivoSaida.write(
        " Name  | BUSY  | Clock |   OP   |   Vj  |   Vk  |   Qj  |   Qk  |   A   |\n")
    for i in range(16):
        if reservationStation[i].busy:
            arquivoSaida.write("ADD {:2d} | {!r:5} | {!r:5} | {!r:6s} | {!r:5} | {!r:5} | {!r:5} | {!r:5} | {!r:5} |\n".format(
                i, reservationStation[i].busy, reservationStation[i].exec, reservationStation[i].op, reservationStation[i].Vj, reservationStation[i].Vk, reservationStation[i].Qj, reservationStation[i].Qk, reservationStation[i].A))
    for i in range(16, 32):
        if reservationStation[i].busy:
            arquivoSaida.write("MUL {:2d} | {!r:5} | {!r:5} | {!r:6s} | {!r:5} | {!r:5} | {!r:5} | {!r:5} | {!r:5} |\n".format(
                i, reservationStation[i].busy, reservationStation[i].exec, reservationStation[i].op, reservationStation[i].Vj, reservationStation[i].Vk, reservationStation[i].Qj, reservationStation[i].Qk, reservationStation[i].A))
    for i in range(32, 48):
        if reservationStation[i].busy:
            arquivoSaida.write("LOA {:2d} | {!r:5} | {!r:5} | {!r:6s} | {!r:5} | {!r:5} | {!r:5} | {!r:5} | {!r:5} |\n".format(
                i, reservationStation[i].busy, reservationStation[i].exec, reservationStation[i].op, reservationStation[i].Vj, reservationStation[i].Vk, reservationStation[i].Qj, reservationStation[i].Qk, reservationStation[i].A))
    
    arquivoSaida.write("\nRegistradores:\n")
    arquivoSaida.write("Reg | Qi | Value\n")
    for i in range(len(register)):
        arquivoSaida.write("{:3d} | {!r:5} | {:3d} \n".format(i, register[i].Qi, register[i].value))
    

def menu():
    global clock, instrucoes
    print("Implementação do Algoritmo de Tomasulo")
    arq = open("in.txt")
    iq = createInstructionQueue(arq)
    issue(iq.pop(0))
    while instrucoes > 0:
        write()
        executarInstrucoes()
        escreverSaida()
        clock += 1
        if iq != []:
            issue(iq.pop(0))



menu()