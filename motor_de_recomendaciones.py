from abc import ABC, abstractmethod

class MotorDeRecomendaciones(ABC):

    @abstractmethod
    def crear_usuario(self, usuario): pass

    @abstractmethod
    def iniciar_sesion(self, nombre, password): pass

    @abstractmethod
    def obtener_nombre_usuario(self, nombre): pass

    @abstractmethod
    def eliminar_usuario(self, nombre): pass

    @abstractmethod
    def actualizar_contrasena(self, nombre, nueva_password): pass

    @abstractmethod
    def cambiar_presupuesto(self, nombre, nuevo_presupuesto): pass

    @abstractmethod
    def crear_carro(self, carro): pass

    @abstractmethod
    def filtrar_carros_por_preferencias(self, nombre): pass

    @abstractmethod
    def filtrar_carros_por_presupuesto(self, nombre): pass

    @abstractmethod
    def agregar_carro_favorito(self, nombre, modelo): pass

    @abstractmethod
    def eliminar_carro_favorito(self, nombre, modelo): pass

    @abstractmethod
    def obtener_carros_favoritos(self, nombre): pass

    @abstractmethod
    def agregar_preferencia(self, nombre, tipo_preferencia, valor_preferencia): pass

    @abstractmethod
    def eliminar_preferencia(self, nombre, tipo_preferencia, valor_preferencia): pass

    @abstractmethod
    def obtener_preferencias(self, nombre, tipo_preferencia): pass

    @abstractmethod
    def generar_recomendaciones(self, nombre): pass

    @abstractmethod
    def agregar_recomendacion(self, nombre, modelo): pass

    @abstractmethod
    def obtener_recomendaciones_guardadas(self, nombre): pass

    @abstractmethod
    def limpiar_recomendaciones_de_usuario(self, nombre): pass
