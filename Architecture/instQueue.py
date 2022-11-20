class Instructuion:

    def __init__(self, name, dest, r1, r2, imm):
        self.name = name
        self.dest = dest
        self.r1 = r1
        self.r2 = r2
        self.imm = imm

    def toString(self):
        return self.name + ' ' + self.dest + ' ' + self.r1 + ' ' + self.imm + ' ' + self.r2
