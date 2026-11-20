
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

class DatoInvalidoError(Exception):
    pass


class ServicioNoDisponibleError(Exception):
    pass


class ReservaInvalidaError(Exception):
    pass


class OperacionNoPermitidaError(Exception):
    pass


# =====================================
# CLASE ENTIDAD
# =====================================

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

        if documento == "":
            raise DatoInvalidoError("El documento es obligatorio")

        if "@" not in correo:
            raise DatoInvalidoError("El correo no es valido")

    def obtener_documento(self):
        return self.__documento

    def obtener_correo(self):
        return self.__correo

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

        if precio <= 0:
            raise DatoInvalidoError("El precio debe ser mayor que cero")

        self.precio = precio
        self.disponible = True

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


# =====================================
# CLASE RESERVA
# =====================================

class Reserva:

    def __init__(self, cliente, servicio, fecha):

        if cliente is None or servicio is None:
            raise ReservaInvalidaError(
                "El cliente y el servicio son obligatorios"
            )

        if not servicio.consultar_disponibilidad():
            raise ServicioNoDisponibleError(
                "El servicio no esta disponible"
            )

        self.cliente = cliente
        self.servicio = servicio
        self.fecha = fecha
        self.estado = "Activa"

        servicio.disponible = False

    def mostrar_reserva(self):
        print("Cliente:", self.cliente.nombre)
        print("Servicio:", self.servicio.nombre)
        print("Fecha:", self.fecha)
        print("Estado:", self.estado)

    def cancelar_reserva(self):

        if self.estado == "Cancelada":
            raise OperacionNoPermitidaError(
                "La reserva ya fue cancelada"
            )

        self.estado = "Cancelada"
        self.servicio.disponible = True

        print("La reserva fue cancelada correctamente")


# =====================================
# CLASE SISTEMA
# =====================================

class Sistema:

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    # Registrar un cliente
    def registrar_cliente(self, cliente):

        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError(
                "El dato ingresado no es un cliente"
            )

        for c in self.clientes:
            if c.obtener_documento() == cliente.obtener_documento():
                raise DatoInvalidoError(
                    "El cliente ya esta registrado"
                )

        self.clientes.append(cliente)
        print("Cliente registrado correctamente")

    # Registrar un servicio
    def registrar_servicio(self, servicio):

        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError(
                "El dato ingresado no es un servicio"
            )

        self.servicios.append(servicio)
        print("Servicio registrado correctamente")

    # Registrar una reserva
    def registrar_reserva(self, reserva):

        if not isinstance(reserva, Reserva):
            raise ReservaInvalidaError(
                "El dato ingresado no es una reserva"
            )

        self.reservas.append(reserva)
        print("Reserva registrada correctamente")

    # Mostrar los clientes
    def mostrar_clientes(self):
        for cliente in self.clientes:
            cliente.mostrar_informacion()

    # Mostrar los servicios
    def mostrar_servicios(self):
        for servicio in self.servicios:
            servicio.mostrar_informacion()

    # Mostrar las reservas
    def mostrar_reservas(self):
        for reserva in self.reservas:
            reserva.mostrar_reserva()
