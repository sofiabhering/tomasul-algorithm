class ReservationStation:
    def __init__(self):
        self.busy = False # Se a RS está ocupada
        self.exec = None # Instrução que está sendo executada
        self.op = None # Operação que está sendo executada
        self.Vj = None # Valor do operando Vj
        self.Vk = None # Valor do operando Vk
        self.Qj = None # Registrador de destino Qj
        self.Qk = None # Registrador de destino Qk
        self.A = None # endereço