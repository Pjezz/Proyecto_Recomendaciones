class Carro:
    def __init__(self, modelo, marca, tipo, transmision, precio):
        self.modelo = modelo
        self.marca = marca
        self.tipo = tipo
        self.transmision = transmision
        self.precio = precio

    def __str__(self):
        return f"{self.modelo} {self.marca} {self.tipo} {self.transmision} {self.precio}"
