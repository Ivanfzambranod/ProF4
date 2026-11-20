# =====================================
# PROYECTO FASE 4 - SOFTWARE FJ
# Sistema de clientes, servicios y reservas
# =====================================

# Importar librerias
from abc import ABC, abstractmethod
from datetime import datetime
import logging

# =====================================
# EXCEPCIONES PERSONALIZADAS
# =====================================

# Error cuando un dato no es valido
class DatoInvalidoError(Exception):
    pass

# Error cuando un servicio no esta disponible
class ServicioNoDisponibleError(Exception):
    pass

# Error cuando una reserva no es valida
class ReservaInvalidaError(Exception):
    pass

# Error cuando una operacion no esta permitida
class OperacionNoPermitidaError(Exception):
    pass

# =====================================
# CLASE ENTIDAD
# =====================================

# Clase abstracta que representa una entidad
class Entidad(ABC):

    def __init__(self, nombre):
        self.nombre = nombre

    @abstractmethod
    def mostrar_informacion(self):
        pass

# =====================================
# CLASE CLIENTE
# =====================================

class Cliente(Entidad):

    def __init__(self, nombre, documento, correo):
        super().__init__(nombre)

        self.__documento = documento
        self.__correo = correo

        # Validar los datos del cliente
        if documento == "":
            raise DatoInvalidoError("El documento es obligatorio")

        if "@" not in correo:
            raise DatoInvalidoError("El correo no es valido")

    # Consultar documento
    def obtener_documento(self):
        return self.__documento

    # Consultar correo
    def obtener_correo(self):
        return self.__correo

    # Mostrar informacion del cliente
    def mostrar_informacion(self):
        print("Nombre:", self.nombre)
        print("Documento:", self.__documento)
        print("Correo:", self.__correo)

# =====================================
# CLASE SERVICIO
# =====================================

class Servicio(Entidad):

    def __init__(self, nombre, precio):
        super().__init__(nombre)

        # Validar el precio
        if precio <= 0:
            raise DatoInvalidoError("El precio debe ser mayor que cero")

        self.precio = precio
        self.disponible = True

    # Consultar disponibilidad
    def consultar_disponibilidad(self):
        return self.disponible

# =====================================
# SERVICIO DE RESERVA DE SALAS
# =====================================

class ReservaSala(Servicio):

    def __init__(self, nombre, precio, capacidad):
        super().__init__(nombre, precio)
        self.capacidad = capacidad

    def mostrar_informacion(self):
        print("Servicio:", self.nombre)
        print("Precio:", self.precio)
        print("Capacidad:", self.capacidad, "personas")

# =====================================
# SERVICIO DE ALQUILER DE EQUIPOS
# =====================================

class AlquilerEquipo(Servicio):

    def __init__(self, nombre, precio, tipo_equipo):
        super().__init__(nombre, precio)
        self.tipo_equipo = tipo_equipo

    def mostrar_informacion(self):
        print("Servicio:", self.nombre)
        print("Precio:", self.precio)
        print("Tipo de equipo:", self.tipo_equipo)

# =====================================
# SERVICIO DE ASESORIAS
# =====================================

class AsesoriaEspecializada(Servicio):

    def __init__(self, nombre, precio, especialidad):
        super().__init__(nombre, precio)
        self.especialidad = especialidad

    def mostrar_informacion(self):
        print("Servicio:", self.nombre)
        print("Precio:", self.precio)
        print("Especialidad:", self.especialidad)
