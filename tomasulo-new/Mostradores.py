from collections import deque
from ReservationStation import ReservationStation

class Mostradores:
    #variable

    def write(self):
        for unit in self.addUnit:
            # Se ocupado e não está executando
            if unit.busy and self.RS[unit.inst].exec == 0:
                v  = self.simular_execucao(unit.inst)
                for register in self.registerStat:
                    if register.Qi == unit.inst:
                        register.Qi = None
                        register.value = v
                for rs in self.RS:
                    if rs.Qj == unit.inst:
                        rs.Vj = v
                        rs.Qj = None
                    if rs.Qk == unit.inst:
                        rs.Vk = v
                        rs.Qk = None
                self.instrucoes -= 1
                self.RS[unit.inst] = ReservationStation()
                unit.busy = False

        # mulUnit
        for unit in self.mulUnit: # Se ocupado e não está executando
            if unit.busy and self.RS[unit.inst].exec == 0:
                v = self.simular_execucao(unit.inst)

                for register in self.registerStat:
                    if register.Qi == unit.inst:
                        register.Qi = None
                        register.value = v
                for rs in self.RS:
                    if rs.Qj == unit.inst:
                        rs.Vj = v
                        rs.Qj = None
                    if rs.Qk == unit.inst:
                        rs.Vk = v
                        rs.Qk = None
                self.instrucoes -= 1
                self.RS[unit.inst] = ReservationStation() # Limpa a estação de reserva
                unit.busy = False
        # ldUnit
        for unit in self.ldUnit:
            if unit.busy and self.RS[unit.inst].exec == 0: # Se ocupado e não está executando
                v = self.simular_execucao(unit.inst)
                if self.RS[unit.inst].op == "SW":
                    for memory in self.memory:
                        if memory.Qi == unit.inst:
                            memory.Qi = None
                            memory.value = v
                else:
                    for register in self.registerStat:
                        if register.Qi == unit.inst:
                            register.Qi = None
                            register.value = v
                for rs in self.RS:
                    if rs.Qj == unit.inst:
                        rs.Vj = v
                        rs.Qj = None
                    if rs.Qk == unit.inst:
                        rs.Vk = v
                        rs.Qk = None
                self.instrucoes -= 1
                self.RS[unit.inst] = ReservationStation()
                unit.busy = False

    # Escreve na tela o status das Estações de Reserva, dos Registradores e da Memoria
    def mostrarStatus(self, status_avancado):
        print("\n")
        print("="*25)
        print("\n")
        print("Clock: ", self.clock)
        print("    Name    | Busy  | Clock |   Op   |   Vj  |   Vk  |   Qj  |   Qk  |   A   |")
        for i in range(16):
            print("ADD  | {:2d} | {!r:5} | {!r:5} | {!r:6s} | {!r:5} | {!r:5} | {!r:5} | {!r:5} | {!r:5} |".format(i, self.RS[i].busy, self.RS[i].exec, self.RS[i].op, self.RS[i].Vj, self.RS[i].Vk, self.RS[i].Qj, self.RS[i].Qk, self.RS[i].A))
        for i in range(16, 32):
            print("MUL  | {:2d} | {!r:5} | {!r:5} | {!r:6s} | {!r:5} | {!r:5} | {!r:5} | {!r:5} | {!r:5} |".format(i, self.RS[i].busy, self.RS[i].exec, self.RS[i].op, self.RS[i].Vj, self.RS[i].Vk, self.RS[i].Qj, self.RS[i].Qk, self.RS[i].A))
        for i in range(32, 48):
            print("LOAD | {:2d} | {!r:5} | {!r:5} | {!r:6s} | {!r:5} | {!r:5} | {!r:5} | {!r:5} | {!r:5} |".format(i, self.RS[i].busy, self.RS[i].exec, self.RS[i].op, self.RS[i].Vj, self.RS[i].Vk, self.RS[i].Qj, self.RS[i].Qk, self.RS[i].A))
        
        if status_avancado == True:
            print("\nRegistradores:")
            print("Reg | Qi | Value")
            for i in range(len(self.registerStat)):
                print("{:3d} | {!r:5} | {:3d} ".format(i, self.registerStat[i].Qi, self.registerStat[i].value))
        
            print("\nMemoria:")
            print("Mem | Qi | Value")
            for i in range(len(self.memory)):
                print("{:3d} | {!r:5} | {:3d} ".format(i, self.memory[i].Qi, self.memory[i].value))

    # Escreve na tela o status das Estações de Reserva ocupadas, 
    # dos 16 Primeiros Registradores e das 16 Primeiras Celulas de Memoria
    def mostrarOcupado(self, status_avancado):
        print("\n")
        print("="*10)
        print("\n")
        print("Clock: ", self.clock)
        print("    RS    | BUSY  | Clock |   OP   |   Vj  |   Vk  |   Qj  |   Qk  |   A   |")
        for i in range(16):
            if self.RS[i].busy:
                print("ADD  | {:2d} | {!r:5} | {!r:5} | {!r:6s} | {!r:5} | {!r:5} | {!r:5} | {!r:5} | {!r:5} |".format(i, self.RS[i].busy, self.RS[i].exec, self.RS[i].op, self.RS[i].Vj, self.RS[i].Vk, self.RS[i].Qj, self.RS[i].Qk, self.RS[i].A))
        for i in range(16, 32):
            if self.RS[i].busy:
                print("MUL  | {:2d} | {!r:5} | {!r:5} | {!r:6s} | {!r:5} | {!r:5} | {!r:5} | {!r:5} | {!r:5} |".format(i, self.RS[i].busy, self.RS[i].exec, self.RS[i].op, self.RS[i].Vj, self.RS[i].Vk, self.RS[i].Qj, self.RS[i].Qk, self.RS[i].A))
        for i in range(32, 48):
            if self.RS[i].busy:
                print("LOAD | {:2d} | {!r:5} | {!r:5} | {!r:6s} | {!r:5} | {!r:5} | {!r:5} | {!r:5} | {!r:5} |".format(i, self.RS[i].busy, self.RS[i].exec, self.RS[i].op, self.RS[i].Vj, self.RS[i].Vk, self.RS[i].Qj, self.RS[i].Qk, self.RS[i].A))
        
        if status_avancado == True:
            print("\n16 Primeiros Registradores:")
            print("Reg | Qi | Value")
            for i in range(16):
                print("{:3d} | {!r:5} | {:3d} ".format(i, self.registerStat[i].Qi, self.registerStat[i].value))
        
            print("\n16 Primeiras Celulas de Memoria:")
            print("Mem | Qi | Value")
            for i in range(16):
                print("{:3d} | {!r:5} | {:3d} ".format(i, self.memory[i].Qi, self.memory[i].value))
    
    # Escreve no arquivo "output.txt" o status das Estações de Reserva ocupadas, 
    # dos 16 Primeiros Registradores e das 16 Primeiras Celulas de Memoria
    def escreverSaida(self, status_avancado):   
        # self.arquivoSaida.write("\n")
        self.arquivoSaida.write("="*80)
        self.arquivoSaida.write("\n")
        self.arquivoSaida.write("Clock: {}\n".format(self.clock))
        self.arquivoSaida.write(" Name  | BUSY  | Clock |   OP   |   Vj  |   Vk  |   Qj  |   Qk  |   A   |\n")
        for i in range(16):
            if self.RS[i].busy:
                self.arquivoSaida.write("ADD {:2d} | {!r:5} | {!r:5} | {!r:6s} | {!r:5} | {!r:5} | {!r:5} | {!r:5} | {!r:5} |\n".format(i, self.RS[i].busy, self.RS[i].exec, self.RS[i].op, self.RS[i].Vj, self.RS[i].Vk, self.RS[i].Qj, self.RS[i].Qk, self.RS[i].A))
        for i in range(16, 32):
            if self.RS[i].busy:
                self.arquivoSaida.write("MUL {:2d} | {!r:5} | {!r:5} | {!r:6s} | {!r:5} | {!r:5} | {!r:5} | {!r:5} | {!r:5} |\n".format(i, self.RS[i].busy, self.RS[i].exec, self.RS[i].op, self.RS[i].Vj, self.RS[i].Vk, self.RS[i].Qj, self.RS[i].Qk, self.RS[i].A))
        for i in range(32, 48):
            if self.RS[i].busy:
                self.arquivoSaida.write("LOA {:2d} | {!r:5} | {!r:5} | {!r:6s} | {!r:5} | {!r:5} | {!r:5} | {!r:5} | {!r:5} |\n".format(i, self.RS[i].busy, self.RS[i].exec, self.RS[i].op, self.RS[i].Vj, self.RS[i].Vk, self.RS[i].Qj, self.RS[i].Qk, self.RS[i].A))
        
        if status_avancado == True:
            self.arquivoSaida.write("\nRegistradores:\n")
            self.arquivoSaida.write("Reg | Qi | Valor\n")
            for i in range(16):
                self.arquivoSaida.write("{:3d} | {!r:5} | {:3d} \n".format(i, self.registerStat[i].Qi, self.registerStat[i].value))
            
            self.arquivoSaida.write("\nCélulas de Memoria:\n")
            self.arquivoSaida.write("Mem | Qi | Valor\n")
            for i in range(16):
                self.arquivoSaida.write("{:3d} | {!r:5} | {:3d} \n".format(i, self.memory[i].Qi, self.memory[i].value))
            self.arquivoSaida.write("\n")
