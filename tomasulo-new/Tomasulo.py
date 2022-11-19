from collections import deque
from ReservationStation import ReservationStation
from Register import Register
from DataMemory import DataMemory
from FunctionalUnit import FunctionalUnit
from Mostradores import Mostradores

# Arit ["ADD", "SUB", "MUL", "DIV"]
# Memoria ["LW", "SW"]

class Tomasulo(Mostradores):
    def __init__(self, instList, debug, status_avancado):
        self.debug = debug
        self.status_avancado = status_avancado
        self.arquivoSaida = open("resultados/output.txt", "w")

        self.pc = 0
        self.clock = 0
        self.instrucoes = 0
        self.lock = False
        self.rsAddI = 0
        self.rsMulI = 16
        self.rsLdI = 32
        self.instList = instList
        self.filaDespacho = deque()

        # Arquitetura Simulada.
        self.addUnit = [FunctionalUnit()
                        for i in range(3)]  # 3 Unidades funcionais
        self.mulUnit = [FunctionalUnit()
                        for i in range(3)]  # 3 Unidades de Mul
        self.ldUnit = [FunctionalUnit() for i in range(3)]  # 3 Unidades de ld
        self.memory = [DataMemory()
                       for i in range(512)]  # 512 Unidades de memória
        # 32 Unidades de registradores
        self.registerStat = [Register() for i in range(32)]
        self.RS = [ReservationStation()
                   for i in range(48)]  # 48 Reservation Stations

    # Realiza a busca da instrução na queue
    def search(self):
        if self.pc >= len(self.instList):
            return None
        if len(self.filaDespacho) < 16:
            self.filaDespacho.append(self.instList[self.pc])
            self.pc += 1

    # Faz o despacho da instrução
    def issue(self):
        if len(self.filaDespacho) < 1 or self.lock:
            return
        inst = self.filaDespacho.popleft()
        op = inst[0]
        r = 0
        if op in ["ADD", "SUB", "MUL", "DIV"]:
            if op == "MUL" or op == "DIV":
                r = 16  # Registrador de destino
                # Enquanto a RS estiver ocupada e não chegar ao limite do registrador
                while self.RS[r].busy and r < 32:
                    r += 1  # Incrementa o registrador
            else:
                # Enquanto a RS estiver ocupada e não chegar ao limite do registrador
                while self.RS[r].busy and r < 16:
                    r += 1  # Incrementa o registrador
            try:
                rd = int(inst[1][1:])
                rs = int(inst[2][1:])
                rt = int(inst[3][1:])
            except:
                raise Exception("Sintaxe invalida")
            if self.registerStat[rs].Qi != None:
                self.RS[r].Qj = self.registerStat[rs].Qi
            else:
                self.RS[r].Vj = self.registerStat[rs].value
                # self.RS[r].Qj = 0

            if self.registerStat[rt].Qi != None:
                self.RS[r].Qk = self.registerStat[rt].Qi
            else:
                self.RS[r].Vk = self.registerStat[rt].value
                # self.RS[r].Qk = 0

            self.RS[r].busy = True
            self.registerStat[rd].Qi = r
        # Se for um load ou store
        elif op in ["LW", "SW"]:
            r = 32  # Registrador de destino
            # Enquanto a RS estiver ocupada e não chegar ao limite do registrador
            while self.RS[r].busy and r < 48:
                r += 1
            #   Se for um load
            if op == "LW":
                rd = int(inst[1][1:])  # Registrador de destino
                # Valor do imediato e registrador de origem
                imm, rs = inst[2].replace("(", " ").replace(")", " ").split()
                imm = int(imm)  # Valor do imediato
                rs = int(rs[1:])  # Registrador de origem
                # Coloca o valor do registrador de origem na RS
                self.RS[r].Vj = self.memory[rs].value
                self.RS[r].A = imm  # Coloca o valor do imediato na RS
                self.RS[r].busy = True  # Marca a RS como ocupada
                # Coloca o valor da fila de prioridade do registrador de destino na RS
                self.registerStat[rd].Qi = r
            #   Se for um store
            elif op == "SW":
                rs = int(inst[1][1:])  # Registrador de origem
                # Valor do imediato e registrador de destino
                imm, rd = inst[2].replace("(", " ").replace(")", " ").split()
                imm = int(imm)  # Valor do imediato
                rd = int(rd[1:])  # Registrador de destino
                # Se o registrador de origem estiver ocupado
                if self.registerStat[rs].Qi != None:
                    # Coloca o valor da fila de prioridade do registrador de origem na RS
                    self.RS[r].Qj = self.registerStat[rs].Qi
                else:  # Se o registrador de origem não estiver ocupado
                    # Coloca o valor do registrador de origem na RS
                    self.RS[r].Vj = self.registerStat[rs].value

                self.RS[r].A = imm  # Coloca o valor do imediato na RS
                self.RS[r].busy = True  # Marca a RS como ocupada
                # Coloca o valor da fila de prioridade do registrador de destino na RS
                self.memory[rd].Qi = r
        else:
            raise Exception("Instrução não reconhecida")
        self.RS[r].exec = -1
        self.RS[r].op = op
        self.instrucoes += 1

    # Executa as instruções
    def executarInstrucoes(self):
        # Controle de tempo
        for unit in self.addUnit:
            if unit.busy:
                self.RS[unit.inst].exec -= 1
        for unit in self.mulUnit:
            if unit.busy:
                self.RS[unit.inst].exec -= 1
        for unit in self.ldUnit:
            if unit.busy:
                self.RS[unit.inst].exec -= 1

        # Enviar instruções para as unidades funcionais
        # addUnit
        for i in range(16):  # Para cada RS
            # Se a RS estiver ocupada e não estiver executando e não estiver bloqueada e não estiver no limite de instruções
            if self.RS[self.rsAddI].busy and self.RS[self.rsAddI].exec == -1 and self.RS[self.rsAddI].Vj != None and self.RS[self.rsAddI].Vk != None:
                if not self.addUnit[0].busy:
                    self.addUnit[0].inst = self.rsAddI
                    self.addUnit[0].busy = True
                elif not self.addUnit[1].busy:
                    self.addUnit[1].inst = self.rsAddI
                    self.addUnit[1].busy = True
                elif not self.addUnit[2].busy:
                    self.addUnit[2].inst = self.rsAddI
                    self.addUnit[2].busy = True
                else:
                    break
                # Setar o clock da operação todas de add levam 5 de clock para serem concluidas
                self.RS[self.rsAddI].exec = 5
            self.rsAddI = (self.rsAddI + 1) % 16

        # MulUnit
        for i in range(16):  # Para cada RS
            # Se a RS estiver ocupada e não estiver executando e não estiver bloqueada e não estiver no limite de instruções
            if self.RS[self.rsMulI].busy and self.RS[self.rsMulI].exec == -1 and self.RS[self.rsMulI].Vj != None and self.RS[self.rsMulI].Vk != None:
                if not self.mulUnit[0].busy:
                    self.mulUnit[0].inst = self.rsMulI
                    self.mulUnit[0].busy = True
                elif not self.addUnit[1].busy:
                    self.mulUnit[1].inst = self.rsMulI
                    self.mulUnit[1].busy = True
                elif not self.addUnit[2].busy:
                    self.mulUnit[2].inst = self.rsMulI
                    self.mulUnit[2].busy = True
                else:
                    break
                # setar o clock da operação
                if self.RS[self.rsMulI].op == "MUL":
                    self.RS[self.rsMulI].exec = 15
                else:
                    self.RS[self.rsMulI].exec = 25
            self.rsMulI = ((self.rsMulI + 1) % 16) + 16

        # LdUnit
        for i in range(16):  # Para cada RS
            # Se a RS estiver ocupada e não estiver executando e não estiver bloqueada e não estiver no limite de instruções
            if self.RS[self.rsLdI].busy and self.RS[self.rsLdI].exec == -1 and self.RS[self.rsLdI].Vj != None:
                if not self.ldUnit[0].busy:
                    self.ldUnit[0].inst = self.rsLdI
                    self.ldUnit[0].busy = True
                elif not self.ldUnit[1].busy:
                    self.ldUnit[1].inst = self.rsLdI
                    self.ldUnit[1].busy = True
                elif not self.ldUnit[2].busy:
                    self.ldUnit[2].inst = self.rsLdI
                    self.ldUnit[2].busy = True
                else:
                    break
                # setar o clock da operação todas levam 5 de clock para serem concluidas
                self.RS[self.rsLdI].exec = 5
            self.rsLdI = ((self.rsLdI + 1) % 16) + 32

    # Devolve o valor resultante da operação da instrução
    def simular_execucao(self, inst):
        if self.RS[inst].op == "ADD":
            return self.RS[inst].Vj + self.RS[inst].Vk
        elif self.RS[inst].op == "SUB":
            return self.RS[inst].Vj - self.RS[inst].Vk
        elif self.RS[inst].op == "MUL":
            return self.RS[inst].Vj * self.RS[inst].Vk
        elif self.RS[inst].op == "DIV":
            return self.RS[inst].Vj // self.RS[inst].Vk
        elif self.RS[inst].op == "LW":
            return self.RS[inst].Vj + self.RS[inst].A
        elif self.RS[inst].op == "SW":
            return self.RS[inst].Vj + self.RS[inst].A
        else:
            pass

    # Executa o algoritmo de Tomasulo
    def run(self):
        self.search()  # Busca instruções na memória

        if self.debug == True:
            self.mostrarStatus(self.status_avancado)
            self.mostrarOcupado(self.status_avancado)
            input("Pressione enter para o próximo passo... ")

        # Escreve o status da unidade funcional
        self.escreverSaida(self.status_avancado)
        self.clock += 1  # Próximo clock
        self.issue()  # Despacho de instruções

        while self.instrucoes > 0:  # Enquanto ainda tiverem instruções na memória
            self.write()  # Escreve o resultado da instrução
            self.executarInstrucoes()  # Executa as instruções

            if self.debug == True:
                # Mostra o status da unidade funcional
                self.mostrarStatus(self.status_avancado)
                # Mostra o status das unidades de alocação
                self.mostrarOcupado(self.status_avancado)
                # Pausa o programa
                input("Pressione enter para o próximo passo... ")

            # Escreve o status da unidade funcional
            self.escreverSaida(self.status_avancado)
            self.search()  # Busca novamente
            self.clock += 1  # Próximo clock
            self.issue()  # Instruções que podem ser executadas
        print("Arquivo de saída escrito.")
