class Usuario:
    def __init__(self, nombre, password, presupuesto):
        self.nombre = nombre
        self.password = password
        self.presupuesto = presupuesto
        self.carros_favoritos = []
        self.preferencias = []
        self.carros_recomendados = []

    def verificar_contrasena(self, password):
        return self.password == password

    def agregar_carro_favorito(self, carro):
        self.carros_favoritos.append(carro)

    def agregar_preferencia(self, preferencia):
        self.preferencias.append(preferencia.lower())

    def __str__(self):
        favoritos = "\n".join(str(c) for c in self.carros_favoritos)
        return f"Usuario: {self.nombre}\nPreferencias: {self.preferencias}\nCarros favoritos:\n{favoritos}"
