# =============================================
# PROYECTO FASE 4 - SOFTWARE FJ
# Sistema integral de gestion de clientes,
# servicios y reservas
# =============================================

from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
import logging

# =============================================
# CONFIGURACION DEL REGISTRO DE EVENTOS
# =============================================

logging.basicConfig(filename="registro_eventos.log",level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")

# =============================================
# EXCEPCIONES PERSONALIZADAS
# =============================================

class DatoInvalidoError(Exception):
    """Se utiliza cuando un dato ingresado no cumple las validaciones."""
    pass
class ServicioNoDisponibleError(Exception):
    """Se utiliza cuando se intenta reservar un servicio ocupado."""
    pass
class ReservaInvalidaError(Exception):
    """Se utiliza cuando una reserva tiene datos incorrectos."""
    pass
class OperacionNoPermitidaError(Exception):
    """Se utiliza cuando se intenta realizar una operacion no permitida."""
    pass

# =============================================
# CLASE BASE ENTIDAD
# =============================================

class Entidad(ABC):
    """Clase abstracta que representa una entidad del sistema."""
    def __init__(self, nombre):
        if not isinstance(nombre, str) or not nombre.strip():
            raise DatoInvalidoError("El nombre es obligatorio")
        self.nombre = nombre.strip()
    @abstractmethod
    def mostrar_informacion(self):
        """Cada clase hija debe implementar este metodo."""
        pass

# =============================================
# CLASE CLIENTE
# =============================================

class Cliente(Entidad):
    """Almacena los datos basicos de un cliente."""
    def __init__(self, nombre, documento, correo):
        super().__init__(nombre)
        if not isinstance(documento, str) or not documento.strip():
            raise DatoInvalidoError("El documento es obligatorio")
        if not isinstance(correo, str) or "@" not in correo or not correo.strip():
            raise DatoInvalidoError("El correo no es valido")
        self.__documento = documento.strip()
        self.__correo = correo.strip()
    def obtener_documento(self):
        return self.__documento
    def obtener_correo(self):
        return self.__correo
    def mostrar_informacion(self):
        print("Nombre:", self.nombre)
        print("Documento:", self.__documento)
        print("Correo:", self.__correo)

# =============================================
# CLASE ABSTRACTA SERVICIO
# =============================================

class Servicio(Entidad):
    """Clase base para los diferentes servicios de Software FJ."""
    IVA_POR_DEFECTO = 19
    DESCUENTO_POR_DEFECTO = 10
    UNIDAD_DURACION = "horas"
    def __init__(self, nombre, precio):
        super().__init__(nombre)
        if isinstance(precio, bool) or not isinstance(precio, (int, float)):
            raise DatoInvalidoError("El precio debe ser un numero")
        if precio <= 0:
            raise DatoInvalidoError("El precio debe ser mayor que cero")
        self.precio = precio
        self.disponible = True
    def consultar_disponibilidad(self):
        return self.disponible
    @abstractmethod
    def calcular_costo(self, duracion=1, descuento=0, impuesto=0):
        """Calcula el costo segun el tipo de servicio."""
        pass
    @abstractmethod
    def describir_servicio(self):
        """Devuelve una descripcion especifica del servicio."""
        pass
    @abstractmethod
    def validar_parametros(self, duracion, **opciones):
        """Valida los datos particulares de cada servicio."""
        pass
    def mostrar_informacion(self):
        # Polimorfismo: cada servicio entrega su propia descripcion.
        print(self.describir_servicio())
    # Las siguientes variantes permiten calcular costos con diferentes
    # parametros opcionales, simulando la sobrecarga de metodos.
    def calcular_costo_con_impuesto(self, duracion=1, impuesto=None, **opciones):
        if impuesto is None:
            impuesto = self.IVA_POR_DEFECTO
        return self._calcular_con_opciones(duracion, 0, impuesto, opciones)
    def calcular_costo_con_descuento(self, duracion=1, descuento=None, **opciones):
        if descuento is None:
            descuento = self.DESCUENTO_POR_DEFECTO
        return self._calcular_con_opciones(duracion, descuento, 0, opciones)
    def calcular_costo_detallado(
        self, duracion=1, descuento=0, impuesto=0, **opciones):
        costo_base = self._calcular_con_opciones(duracion, 0, 0, opciones)
        total = self._calcular_con_opciones(duracion, descuento, impuesto, opciones)
        return {"servicio": self.nombre,
            "duracion": duracion,
            "costo_base": costo_base,
            "descuento_%": descuento,
            "impuesto_%": impuesto,
            "total": total}
    def _calcular_con_opciones(self, duracion, descuento, impuesto, opciones):
        try:
            return self.calcular_costo(duracion=duracion,descuento=descuento,impuesto=impuesto,**opciones)
        except TypeError as error:
            raise DatoInvalidoError(f"Opcion no valida para el servicio '{self.nombre}': {error}") from error
    def _validar_numero_positivo(self, valor, nombre_dato):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise DatoInvalidoError(f"{nombre_dato} debe ser un numero")
        if valor <= 0:
            raise DatoInvalidoError(f"{nombre_dato} debe ser mayor que cero")
    def _validar_booleano(self, valor, nombre_dato):
        if not isinstance(valor, bool):
            raise DatoInvalidoError(f"{nombre_dato} debe ser True o False")
    def _validar_porcentaje(self, valor, nombre_dato):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise DatoInvalidoError(f"{nombre_dato} debe ser un numero")
        if valor < 0 or valor > 100:
            raise DatoInvalidoError(f"{nombre_dato} debe estar entre 0 y 100")
    def _aplicar_descuento_e_impuesto(self, subtotal, descuento, impuesto):
        self._validar_porcentaje(descuento, "El descuento")
        self._validar_porcentaje(impuesto, "El impuesto")
        subtotal = subtotal * (1 - descuento / 100)
        total = subtotal * (1 + impuesto / 100)
        return round(total, 2)

# =============================================
# SERVICIO DE RESERVA DE SALAS
# =============================================

class ReservaSala(Servicio):
    UNIDAD_DURACION = "horas"
    MAX_HORAS = 12
    HORAS_PARA_DESCUENTO = 5
    DESCUENTO_AUTOMATICO = 10
    def __init__(self, nombre, precio, capacidad):
        super().__init__(nombre, precio)
        if isinstance(capacidad, bool) or not isinstance(capacidad, int):
            raise DatoInvalidoError("La capacidad debe ser un numero entero")
        if capacidad <= 0:
            raise DatoInvalidoError("La capacidad debe ser mayor que cero")
        self.capacidad = capacidad
    def validar_parametros(self, duracion, personas=None):
        self._validar_numero_positivo(duracion, "La duracion (horas)")
        if duracion > self.MAX_HORAS:
            raise DatoInvalidoError(f"La sala se puede reservar maximo {self.MAX_HORAS} horas")
        if personas is not None:
            if (isinstance(personas, bool)or not isinstance(personas, int)or personas <= 0):
                raise DatoInvalidoError("La cantidad de personas debe ser un entero mayor que cero")
            if personas > self.capacidad:
                raise DatoInvalidoError(f"La sala admite {self.capacidad} personas")
        return True
    def calcular_costo(self, duracion=1, descuento=0, impuesto=0, personas=None):
        self.validar_parametros(duracion, personas=personas)
        # Se valida antes de sumar el descuento automatico.
        self._validar_porcentaje(descuento, "El descuento")
        subtotal = self.precio * duracion
        if duracion >= self.HORAS_PARA_DESCUENTO:
            descuento = min(100, descuento + self.DESCUENTO_AUTOMATICO)
        return self._aplicar_descuento_e_impuesto(subtotal, descuento, impuesto)
    def describir_servicio(self):
        return (f"Sala '{self.nombre}' con capacidad para {self.capacidad} personas. "
            f"Tarifa: ${self.precio:,.0f} por hora. "
            f"Maximo {self.MAX_HORAS} horas por reserva.")

# =============================================
# SERVICIO DE ALQUILER DE EQUIPOS
# =============================================

class AlquilerEquipo(Servicio):
    UNIDAD_DURACION = "dias"
    MAX_DIAS = 30
    PORCENTAJE_SEGURO = 5
    def __init__(self, nombre, precio, tipo_equipo):
        super().__init__(nombre, precio)
        if not isinstance(tipo_equipo, str) or not tipo_equipo.strip():
            raise DatoInvalidoError("El tipo de equipo es obligatorio")
        self.tipo_equipo = tipo_equipo.strip()
    def validar_parametros(self, duracion, con_seguro=False):
        self._validar_numero_positivo(duracion, "La duracion (dias)")
        if duracion != int(duracion):
            raise DatoInvalidoError("Los equipos se alquilan por dias completos")
        if duracion > self.MAX_DIAS:
            raise DatoInvalidoError(f"El equipo se puede alquilar maximo {self.MAX_DIAS} dias")
        self._validar_booleano(con_seguro, "El seguro")
        return True
    def calcular_costo(self, duracion=1, descuento=0, impuesto=0, con_seguro=False):
        self.validar_parametros(duracion, con_seguro=con_seguro)
        subtotal = self.precio * duracion
        if con_seguro:
            subtotal *= 1 + self.PORCENTAJE_SEGURO / 100
        return self._aplicar_descuento_e_impuesto(subtotal, descuento, impuesto)
    def describir_servicio(self):
        return (f"Alquiler de '{self.nombre}' (tipo: {self.tipo_equipo}). "
            f"Tarifa: ${self.precio:,.0f} por dia. "
            f"Maximo {self.MAX_DIAS} dias.")

# =============================================
# SERVICIO DE ASESORIAS ESPECIALIZADAS
# =============================================

class AsesoriaEspecializada(Servicio):
    UNIDAD_DURACION = "horas"
    MAX_HORAS = 8
    RECARGO_URGENTE = 20
    def __init__(self, nombre, precio, especialidad):
        super().__init__(nombre, precio)
        if not isinstance(especialidad, str) or not especialidad.strip():
            raise DatoInvalidoError("La especialidad es obligatoria")
        self.especialidad = especialidad.strip()
    def validar_parametros(self, duracion, urgente=False):
        self._validar_numero_positivo(duracion, "La duracion (horas)")
        if duracion > self.MAX_HORAS:
            raise DatoInvalidoError(f"Una asesoria dura maximo {self.MAX_HORAS} horas")
        self._validar_booleano(urgente, "La urgencia")
        return True
    def calcular_costo(self, duracion=1, descuento=0, impuesto=0, urgente=False):
        self.validar_parametros(duracion, urgente=urgente)
        subtotal = self.precio * duracion
        if urgente:
            subtotal *= 1 + self.RECARGO_URGENTE / 100
        return self._aplicar_descuento_e_impuesto(subtotal, descuento, impuesto)
    def describir_servicio(self):
        return (f"Asesoria '{self.nombre}' en {self.especialidad}. "
            f"Tarifa: ${self.precio:,.0f} por hora. "
            f"Maximo {self.MAX_HORAS} horas.")

# =============================================
# CLASE RESERVA
# =============================================

class Reserva:
    """Representa una solicitud de reserva para un cliente."""
    def __init__(self, cliente, servicio, fecha, duracion=1,
        descuento=0, impuesto=0, **opciones):
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("El cliente no es valido")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("El servicio no es valido")
        try:
            fecha_reserva = datetime.strptime(fecha, "%d/%m/%Y")
        except (ValueError, TypeError) as error:
            raise ReservaInvalidaError("La fecha debe tener el formato dia/mes/año") from error
        if fecha_reserva.date() < date.today():
            raise ReservaInvalidaError("No se puede realizar una reserva para una fecha anterior")
        if not servicio.consultar_disponibilidad():
            raise ServicioNoDisponibleError("El servicio no esta disponible")
        try:
            servicio.validar_parametros(duracion, **opciones)
            costo = servicio.calcular_costo(duracion=duracion,
                descuento=descuento,
                impuesto=impuesto,
                **opciones)
        except (DatoInvalidoError, TypeError) as error:
            raise ReservaInvalidaError(f"No se pudo crear la reserva: {error}") from error
        self.fecha = fecha_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.opciones = opciones
        self.costo_total = costo
        self.estado = "Activa"
        self.registrada = False
        # El servicio NO se bloquea aqui. El bloqueo se realiza en
        # Sistema.registrar_reserva, despues de verificar los registros.
        logging.info("Solicitud de reserva creada: cliente=%s, servicio=%s, fecha=%s",
            cliente.nombre,
            servicio.nombre,
            self.fecha.strftime("%d/%m/%Y"))
    def mostrar_reserva(self):
        print("Cliente:", self.cliente.nombre)
        print("Servicio:", self.servicio.nombre)
        print("Fecha:", self.fecha.strftime("%d/%m/%Y"))
        print("Duracion:", self.duracion, self.servicio.UNIDAD_DURACION)
        print(f"Costo total: ${self.costo_total:,.2f}")
        print("Estado:", self.estado)
    def cancelar_reserva(self):
        if self.estado == "Cancelada":
            raise OperacionNoPermitidaError("La reserva ya fue cancelada")
        if not self.registrada:
            raise OperacionNoPermitidaError("No se puede cancelar una reserva que no ha sido registrada")
        self.estado = "Cancelada"
        self.servicio.disponible = True
        logging.info("Reserva cancelada: cliente=%s, servicio=%s",
            self.cliente.nombre,
            self.servicio.nombre)
        print("La reserva fue cancelada correctamente")

# =============================================
# CLASE SISTEMA
# =============================================

class Sistema:
    """Administra clientes, servicios y reservas."""
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []
    def registrar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("El dato no es un cliente")
        for cliente_registrado in self.clientes:
            if (cliente_registrado.obtener_documento()
                == cliente.obtener_documento()):
                raise DatoInvalidoError("El cliente ya esta registrado")
        self.clientes.append(cliente)
        logging.info("Se registro un cliente: %s", cliente.nombre)
        print("Cliente registrado correctamente")
    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("El dato no es un servicio")
        if servicio in self.servicios:
            raise DatoInvalidoError("El servicio ya esta registrado")
        self.servicios.append(servicio)
        logging.info("Se registro un servicio: %s", servicio.nombre)
        print("Servicio registrado correctamente")
    def registrar_reserva(self, reserva):
        if not isinstance(reserva, Reserva):
            raise ReservaInvalidaError("El dato no es una reserva")
        if reserva.cliente not in self.clientes:
            raise ReservaInvalidaError("El cliente no esta registrado")
        if reserva.servicio not in self.servicios:
            raise ReservaInvalidaError("El servicio no esta registrado")
        if not reserva.servicio.consultar_disponibilidad():
            raise ServicioNoDisponibleError("El servicio no esta disponible")
        if reserva.registrada:
            raise ReservaInvalidaError("La reserva ya fue registrada")
        # Primero se valida todo; despues se registra y se bloquea el servicio.
        self.reservas.append(reserva)
        reserva.servicio.disponible = False
        reserva.registrada = True
        logging.info("Se registro una reserva: cliente=%s, servicio=%s",
            reserva.cliente.nombre,
            reserva.servicio.nombre)
        print("Reserva registrada correctamente")
    def mostrar_clientes(self):
        for cliente in self.clientes:
            cliente.mostrar_informacion()
    def mostrar_servicios(self):
        for servicio in self.servicios:
            servicio.mostrar_informacion()
    def mostrar_reservas(self):
        for reserva in self.reservas:
            reserva.mostrar_reserva()
    def consultar_reservas(self, cliente=None, estado=None):
        """Consulta todas las reservas o filtra por cliente y/o estado."""
        resultados = []
        for reserva in self.reservas:
            if cliente is not None and reserva.cliente != cliente:
                continue
            if estado is not None and reserva.estado != estado:
                continue
            resultados.append(reserva)
        if not resultados:
            print("No se encontraron reservas")
        else:
            for reserva in resultados:
                reserva.mostrar_reserva()
        logging.info("Se realizo una consulta de reservas")
        return resultados
    def calcular_total_reservas(self, cliente=None, estado=None):
        total = 0
        for reserva in self.reservas:
            if cliente is not None and reserva.cliente != cliente:
                continue
            if estado is not None and reserva.estado != estado:
                continue
            total += reserva.costo_total
        logging.info("Se calculo el total de reservas: %s", total)
        return round(total, 2)

# =============================================
# FUNCIONES AUXILIARES PARA LAS PRUEBAS
# =============================================

def probar_costo(descripcion, servicio, metodo="calcular_costo", **parametros):
    """Ejecuta un calculo de costo y controla los errores esperados."""
    try:
        resultado = getattr(servicio, metodo)(**parametros)
    except (DatoInvalidoError, TypeError) as error:
        print(f"{descripcion} -> Error esperado: {error}")
        logging.error("Costo invalido en '%s': %s", servicio.nombre, error)
    else:
        if isinstance(resultado, dict):
            print(f"{descripcion} -> {resultado}")
        else:
            print(f"{descripcion} -> ${resultado:,.2f}")
        logging.info("Costo calculado para '%s' con %s: %s",
            servicio.nombre,
            metodo,
            resultado)

def fecha_futura(dias):
    """Devuelve una fecha futura en formato dia/mes/ano para las pruebas."""
    return (date.today() + timedelta(days=dias)).strftime("%d/%m/%Y")

def probar_reserva(descripcion, sistema, cliente, servicio, fecha, **parametros):
    """Crea y registra una reserva. Devuelve None si ocurre un error."""
    try:
        reserva = Reserva(cliente, servicio, fecha, **parametros)
        sistema.registrar_reserva(reserva)
    except (ReservaInvalidaError,
        ServicioNoDisponibleError,
        DatoInvalidoError) as error:
        print(f"{descripcion} -> Error esperado: {error}")
        logging.error("Error en reserva (%s): %s", descripcion, error)
        return None
    else:
        print(f"{descripcion} -> OK, costo ${reserva.costo_total:,.2f}")
        return reserva

# =============================================
# PRUEBAS DEL SISTEMA
# =============================================

if __name__ == "__main__":
    sistema = Sistema()
    print("\n--- PRUEBAS DEL SISTEMA SOFTWARE FJ ---")
    # ---------- PARTE 1: CLIENTES ----------
    print("\n=== PARTE 1: CLIENTES ===")
    
    # Prueba 1: Registrar un cliente con try, except, else y finally.
    try:
        cliente1 = Cliente("Carlos Perez", "123456", "carlos@gmail.com")
        sistema.registrar_cliente(cliente1)
    except DatoInvalidoError as error:
        print("Error:", error)
        logging.error("Error al registrar cliente: %s", error)
    else:
        print("Prueba 1 finalizada correctamente")
    finally:
        print("Finalizo el proceso de registro")

    # Prueba 2: Registrar otro cliente.
    try:
        cliente2 = Cliente("Maria Lopez", "789456", "maria@gmail.com"        )
        sistema.registrar_cliente(cliente2)
    except DatoInvalidoError as error:
        print("Error:", error)
        logging.error("Error al registrar cliente: %s", error)

    # Prueba 3: Intentar registrar un cliente sin documento.
    try:
        Cliente("Pedro Ruiz", "", "pedro@gmail.com")
    except DatoInvalidoError as error:
        print("Prueba 3 - Error esperado:", error)
        logging.error("Cliente invalido: %s", error)

    # Prueba 4: Intentar registrar un cliente repetido.
    try:
        cliente_repetido = Cliente("Carlos Perez", "123456", "otro@gmail.com")
        sistema.registrar_cliente(cliente_repetido)
    except DatoInvalidoError as error:
        print("Prueba 4 - Error esperado:", error)
        logging.error("Cliente repetido: %s", error)
    # Prueba adicional: rechazar un nombre compuesto por espacios.
    try:
        Cliente("   ", "555111", "espacios@gmail.com")
    except DatoInvalidoError as error:
        print("Prueba adicional - Nombre vacio:", error)
    # ---------- PARTE 2: SERVICIOS ----------
    print("\n=== PARTE 2: SERVICIOS ===")

    # Prueba 5: Registrar una sala.
    sala1 = ReservaSala("Sala principal", 50000, 10)
    sistema.registrar_servicio(sala1)

    # Prueba 6: Registrar un equipo.
    equipo1 = AlquilerEquipo("Computador", 30000, "Portatil")
    sistema.registrar_servicio(equipo1)

    # Prueba 7: Registrar una asesoria.
    asesoria1 = AsesoriaEspecializada("Asesoria tecnica", 80000, "Informatica")
    sistema.registrar_servicio(asesoria1)

    # Prueba 8: Crear servicios con parametros incorrectos.
    casos_servicios = [("Precio como texto",lambda: AlquilerEquipo("Proyector", "caro", "Video")),
        ("Capacidad cero",lambda: ReservaSala("Sala vacia", 40000, 0)),
        ("Especialidad vacia",lambda: AsesoriaEspecializada("Asesoria", 90000, "   "))]
    for nombre_caso, crear_servicio in casos_servicios:
        try:
            crear_servicio()
        except DatoInvalidoError as error:
            print(f"Prueba 8 - {nombre_caso}: {error}")
            logging.error("Servicio invalido: %s", error)

    # Prueba 9: Servicio es abstracto y no se puede instanciar.
    try:
        Servicio("Generico", 1000)
    except TypeError as error:
        print("Prueba 9 - No se puede instanciar Servicio:", error)
        logging.info("Se comprobo que Servicio es abstracta")

    # Prueba 10: Mostrar la descripcion polimorfica de los servicios.
    print("Prueba 10 - Descripcion de servicios:")
    for servicio in (sala1, equipo1, asesoria1):
        print(" *", servicio.describir_servicio())
    # ---------- PARTE 3: CALCULO DE COSTOS ----------
    print("\n=== PARTE 3: COSTOS ===")

    # Prueba 11: El mismo metodo calcula costos segun cada servicio.
    for servicio in (sala1, equipo1, asesoria1):
        probar_costo(f"Prueba 11 - {servicio.nombre}",
            servicio,
            duracion=2)

    # Prueba 12: Variantes de costo y opciones.
    probar_costo("Prueba 12 - Sala 3 horas con descuento e IVA",
        sala1,
        duracion=3,
        descuento=10,
        impuesto=19)
    probar_costo("Equipo 3 dias con seguro",
        equipo1,
        duracion=3,
        con_seguro=True)
    probar_costo("Asesoria 2 horas urgente",
        asesoria1,
        duracion=2,
        urgente=True)
    probar_costo("Sala con IVA por defecto",
        sala1,
        metodo="calcular_costo_con_impuesto",
        duracion=2)
    probar_costo("Asesoria con descuento por defecto",
        asesoria1,
        metodo="calcular_costo_con_descuento",
        duracion=2)
    probar_costo("Desglose detallado",
        sala1,
        metodo="calcular_costo_detallado",
        duracion=3,
        descuento=10,
        impuesto=19)

    # Prueba 13: Errores controlados en el calculo de costos.
    probar_costo("Sala con mas personas que su capacidad",
        sala1,
        duracion=2,
        personas=15)
    probar_costo("Equipo por 40 dias", equipo1, duracion=40)
    probar_costo("Descuento superior al 100 por ciento",
        asesoria1,
        duracion=1,
        descuento=150)
    probar_costo("Opcion que no existe para equipo",
        equipo1,
        metodo="calcular_costo_con_impuesto",
        duracion=2,
        urgente=True)

    # ---------- PARTE 4: RESERVAS ----------
    print("\n=== PARTE 4: RESERVAS ===")

    # Las fechas de prueba se calculan desde el dia actual para que
    # sigan siendo futuras cuando el programa se ejecute mas adelante.

    # Prueba 14: Reserva valida de sala.
    reserva1 = probar_reserva("Prueba 14 - Reserva de sala",
        sistema,
        cliente1,
        sala1,
        fecha_futura(4),
        duracion=3,
        impuesto=19,
        personas=8)

    # Prueba 15: Intentar reservar una sala ocupada.
    probar_reserva("Prueba 15 - Sala ocupada",
        sistema,
        cliente2,
        sala1,
        fecha_futura(5),
        duracion=2)

    # Prueba 16: Opcion no valida para el servicio de equipo.
    probar_reserva("Prueba 16 - Opcion no valida en equipo",
        sistema,
        cliente2,
        equipo1,
        fecha_futura(6),
        duracion=1,
        urgente=True)

    # Prueba 17: Reserva valida de equipo con seguro.
    probar_reserva("Prueba 17 - Equipo con seguro",
        sistema,
        cliente2,
        equipo1,
        fecha_futura(6),
        duracion=3,
        con_seguro=True)
    
    # Prueba 18: Duracion invalida; la asesoria debe seguir disponible.
    probar_reserva("Prueba 18 - Asesoria de 10 horas",
        sistema,
        cliente2,
        asesoria1,
        fecha_futura(7),
        duracion=10)
    print("Asesoria sigue disponible:",
        asesoria1.consultar_disponibilidad())

    # Prueba 19: Reserva valida de asesoria urgente.
    probar_reserva("Prueba 19 - Asesoria urgente",
        sistema,
        cliente1,
        asesoria1,
        fecha_futura(7),
        duracion=2,
        urgente=True,
        descuento=5)

    # Prueba 20: Fecha con formato incorrecto.
    probar_reserva("Prueba 20 - Fecha incorrecta",
        sistema,
        cliente2,
        equipo1,
        "fecha incorrecta",
        duracion=1)

    # Prueba 21: Fecha anterior al dia actual.
    fecha_pasada = "01/01/2020"
    probar_reserva("Prueba 21 - Fecha pasada",
        sistema,
        cliente2,
        equipo1,
        fecha_pasada,
        duracion=1)

    # Prueba 22: Intentar reservar con un cliente no registrado.
    cliente_no_registrado = Cliente("Cliente de prueba", "999999", "prueba@gmail.com"    )
    sala_no_registrada = ReservaSala("Sala sin registrar", 40000, 5)
    reserva_no_registrada = None
    try:
        reserva_no_registrada = Reserva(cliente_no_registrado,
            sala_no_registrada,
            fecha_futura(8),
            duracion=1)
        sistema.registrar_reserva(reserva_no_registrada)
    except (ReservaInvalidaError, ServicioNoDisponibleError) as error:
        print("Prueba 22 - Error esperado:", error)
        print("La sala conserva su disponibilidad:",
            sala_no_registrada.consultar_disponibilidad())
        logging.error("Reserva no registrada: %s", error)

    # Prueba 23: Cancelar una reserva registrada.
    if reserva1 is not None:
        try:
            reserva1.cancelar_reserva()
        except OperacionNoPermitidaError as error:
            print("Error al cancelar:", error)
            logging.error("Error al cancelar: %s", error)
    else:
        print("No se puede cancelar: la reserva inicial no fue creada")

    # Prueba 24: Intentar cancelar nuevamente.
    if reserva1 is not None:
        try:
            reserva1.cancelar_reserva()
        except OperacionNoPermitidaError as error:
            print("Prueba 24 - Error esperado:", error)
            logging.error("Operacion no permitida: %s", error)

    # Prueba 25: La sala liberada puede reservarse nuevamente.
    probar_reserva("Prueba 25 - Nueva reserva de sala",
        sistema,
        cliente2,
        sala1,
        fecha_futura(9),
        duracion=6)

    # ---------- PARTE 5: CONSULTAS ----------
    print("\n=== PARTE 5: CONSULTAS ===")

    print("\n--- CLIENTES REGISTRADOS ---")
    sistema.mostrar_clientes()

    print("\n--- SERVICIOS REGISTRADOS ---")
    sistema.mostrar_servicios()

    print("\n--- RESERVAS REGISTRADAS ---")
    sistema.mostrar_reservas()

    print("\n--- RESERVAS DE CARLOS ---")
    sistema.consultar_reservas(cliente=cliente1)

    print("\n--- RESERVAS CANCELADAS ---")
    sistema.consultar_reservas(estado="Cancelada")

    print("\n--- TOTALES ---")
    print("Total de reservas activas: "
        f"${sistema.calcular_total_reservas(estado='Activa'):,.2f}")
    print("Total de Maria Lopez: "
        f"${sistema.calcular_total_reservas(cliente=cliente2):,.2f}")

    print("\n--- FIN DE LAS PRUEBAS ---")
