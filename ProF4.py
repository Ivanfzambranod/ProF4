# =====================================
# PROYECTO FASE 4 - SOFTWARE FJ
# Sistema de clientes, servicios y reservas
# =====================================

from abc import ABC, abstractmethod
from datetime import datetime
import logging

# =====================================
# CONFIGURACION DEL REGISTRO
# =====================================

logging.basicConfig(filename="registro_eventos.log",
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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
        if nombre == "":
            raise DatoInvalidoError("El nombre es obligatorio")
        if documento == "":
            raise DatoInvalidoError("El documento es obligatorio")
        if "@" not in correo:
            raise DatoInvalidoError("El correo no es valido")
        self.__documento = documento
        self.__correo = correo
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
        if capacidad <= 0:
            raise DatoInvalidoError("La capacidad debe ser mayor que cero")
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
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("El cliente no es valido")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("El servicio no es valido")
        # Validar el formato de la fecha
        try:
            self.fecha = datetime.strptime(fecha, "%d/%m/%Y")
        except ValueError as error:
            raise ReservaInvalidaError("La fecha debe tener el formato dia/mes/año") from error
        if not servicio.consultar_disponibilidad():
            raise ServicioNoDisponibleError("El servicio no esta disponible")
        self.cliente = cliente
        self.servicio = servicio
        self.estado = "Activa"
        servicio.disponible = False
        logging.info("Se creo una reserva")
    def mostrar_reserva(self):
        print("Cliente:", self.cliente.nombre)
        print("Servicio:", self.servicio.nombre)
        print("Fecha:", self.fecha.strftime("%d/%m/%Y"))
        print("Estado:", self.estado)
    def cancelar_reserva(self):
        if self.estado == "Cancelada":
            raise OperacionNoPermitidaError("La reserva ya fue cancelada")
        self.estado = "Cancelada"
        self.servicio.disponible = True
        logging.info("Se cancelo una reserva")
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
            raise DatoInvalidoError("El dato no es un cliente")
        for c in self.clientes:
            if c.obtener_documento() == cliente.obtener_documento():
                raise DatoInvalidoError("El cliente ya esta registrado")
        self.clientes.append(cliente)
        logging.info("Se registro un cliente")
        print("Cliente registrado correctamente")
    # Registrar un servicio
    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("El dato no es un servicio")
        self.servicios.append(servicio)
        logging.info("Se registro un servicio")
        print("Servicio registrado correctamente")

    # Registrar una reserva
    def registrar_reserva(self, reserva):
        if not isinstance(reserva, Reserva):
            raise ReservaInvalidaError("El dato no es una reserva")
        if reserva.cliente not in self.clientes:
            raise ReservaInvalidaError("El cliente no esta registrado")
        if reserva.servicio not in self.servicios:
            raise ReservaInvalidaError("El servicio no esta registrado")
        self.reservas.append(reserva)
        logging.info("Se registro una reserva")
        print("Reserva registrada correctamente")

    # Mostrar clientes
    def mostrar_clientes(self):
        for cliente in self.clientes:
            cliente.mostrar_informacion()

    # Mostrar servicios
    def mostrar_servicios(self):
        for servicio in self.servicios:
            servicio.mostrar_informacion()

    # Mostrar reservas
    def mostrar_reservas(self):
        for reserva in self.reservas:
            reserva.mostrar_reserva()

    # Consultar reservas con argumentos opcionales
    def consultar_reservas(self, cliente=None, estado=None):
        resultados = []
        for reserva in self.reservas:
            if cliente is not None and reserva.cliente != cliente:
                continue
            if estado is not None and reserva.estado != estado:
                continue
            resultados.append(reserva)
        if len(resultados) == 0:
            print("No se encontraron reservas")
        else:
            for reserva in resultados:
                reserva.mostrar_reserva()
        logging.info("Se realizo una consulta de reservas")
        return resultados

# =====================================
# PRUEBAS DEL SISTEMA
# =====================================

if __name__ == "__main__":
    sistema = Sistema()
    print("\n--- PRUEBAS DEL SISTEMA SOFTWARE FJ ---")
    # Prueba 1: Registrar un cliente
    try:
        cliente1 = Cliente("Carlos Perez", "123456", "carlos@gmail.com")
        sistema.registrar_cliente(cliente1)
    except Exception as error:
        print("Error:", error)
        logging.error("Error al registrar cliente: %s", error)
    else:
        print("Prueba 1 finalizada correctamente")
    finally:
        print("Finalizo el proceso de registro")
    # Prueba 2: Registrar otro cliente
    try:
        cliente2 = Cliente("Maria Lopez", "789456", "maria@gmail.com")
        sistema.registrar_cliente(cliente2)
    except Exception as error:
        print("Error:", error)
        logging.error("Error: %s", error)
    # Prueba 3: Intentar registrar un cliente sin documento
    try:
        cliente3 = Cliente("Pedro Ruiz", "", "pedro@gmail.com")
    except DatoInvalidoError as error:
        print("Prueba 3 - Error esperado:", error)
        logging.error("Cliente invalido: %s", error)
    # Prueba 4: Intentar registrar un cliente repetido
    try:
        cliente_repetido = Cliente("Carlos Perez", "123456", "otro@gmail.com")
        sistema.registrar_cliente(cliente_repetido)
    except DatoInvalidoError as error:
        print("Prueba 4 - Error esperado:", error)
        logging.error("Cliente repetido: %s", error)
    # Prueba 5: Registrar una sala
    sala1 = ReservaSala("Sala principal", 50000, 10)
    sistema.registrar_servicio(sala1)
    # Prueba 6: Registrar un equipo
    equipo1 = AlquilerEquipo("Computador", 30000, "Portatil")
    sistema.registrar_servicio(equipo1)
    # Prueba 7: Registrar una asesoria
    asesoria1 = AsesoriaEspecializada("Asesoria tecnica", 80000, "Informatica")   
    sistema.registrar_servicio(asesoria1)
    # Prueba 8: Crear y registrar una reserva
    try:
        reserva1 = Reserva(cliente1, sala1, "25/11/2026")
        sistema.registrar_reserva(reserva1)
    except Exception as error:
        print("Error:", error)
        logging.error("Error en reserva: %s", error)
    # Prueba 9: Intentar reservar una sala ocupada
    try:
        reserva2 = Reserva(cliente2, sala1, "26/11/2026")
    except ServicioNoDisponibleError as error:
        print("Prueba 9 - Error esperado:", error)
        logging.error("Servicio no disponible: %s", error)
    # Prueba 10: Cancelar una reserva
    try:
        reserva1.cancelar_reserva()
    except OperacionNoPermitidaError as error:
        print("Error:", error)
        logging.error("Error al cancelar: %s", error)
    # Prueba 11: Intentar cancelar nuevamente
    try:
        reserva1.cancelar_reserva()
    except OperacionNoPermitidaError as error:
        print("Prueba 11 - Error esperado:", error)
        logging.error("Operacion no permitida: %s", error)
    # Prueba 12: Intentar crear una reserva con fecha incorrecta
    try:
        reserva3 = Reserva(cliente2, equipo1, "fecha incorrecta")
    except ReservaInvalidaError as error:
        print("Prueba 12 - Error esperado:", error)
        logging.error("Fecha incorrecta: %s", error)
    # Prueba 13: Mostrar los clientes
    print("\n--- CLIENTES REGISTRADOS ---")
    sistema.mostrar_clientes()
    # Prueba 14: Mostrar los servicios
    print("\n--- SERVICIOS REGISTRADOS ---")
    sistema.mostrar_servicios()
    # Prueba 15: Mostrar las reservas
    print("\n--- RESERVAS REGISTRADAS ---")
    sistema.mostrar_reservas()
    # Prueba 16: Consultar todas las reservas
    print("\n--- CONSULTAR TODAS LAS RESERVAS ---")
    sistema.consultar_reservas()
    # Prueba 17: Consultar reservas de un cliente
    print("\n--- CONSULTAR RESERVAS DE CARLOS ---")
    sistema.consultar_reservas(cliente=cliente1)
    # Prueba 18: Consultar reservas canceladas
    print("\n--- CONSULTAR RESERVAS CANCELADAS ---")
    sistema.consultar_reservas(estado="Cancelada")
    print("\n--- FIN DE LAS PRUEBAS ---")
