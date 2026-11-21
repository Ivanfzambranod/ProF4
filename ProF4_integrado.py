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
# CLASE SERVICIO (ABSTRACTA)
# =====================================

class Servicio(Entidad):
    # Valores por defecto de las variantes de costo
    IVA_POR_DEFECTO = 19
    DESCUENTO_POR_DEFECTO = 10
    # Unidad en la que se mide la duracion (cada servicio la redefine)
    UNIDAD_DURACION = "horas"

    def __init__(self, nombre, precio):
        super().__init__(nombre)
        # bool es subclase de int, por eso se excluye de forma explicita
        if isinstance(precio, bool) or not isinstance(precio, (int, float)):
            raise DatoInvalidoError("El precio debe ser un numero")
        if precio <= 0:
            raise DatoInvalidoError("El precio debe ser mayor que cero")
        self.precio = precio
        self.disponible = True

    def consultar_disponibilidad(self):
        return self.disponible

    # ---- Metodos abstractos: cada servicio los sobrescribe ----

    @abstractmethod
    def calcular_costo(self, duracion=1, descuento=0, impuesto=0):
        """Calcula el costo total del servicio (polimorfismo)."""
        pass

    @abstractmethod
    def describir_servicio(self):
        """Devuelve un texto que describe el servicio."""
        pass

    @abstractmethod
    def validar_parametros(self, duracion, **opciones):
        """Valida los parametros de una reserva. Lanza DatoInvalidoError
        si algo es incorrecto y devuelve True si todo esta bien."""
        pass

    # ---- Metodo comun: usa la descripcion de cada servicio ----

    def mostrar_informacion(self):
        print(self.describir_servicio())

    # ---- Variantes de costo (simulan la sobrecarga de metodos) ----

    def calcular_costo_con_impuesto(self, duracion=1, impuesto=None, **opciones):
        """Variante 1: solo con impuesto (por defecto, el IVA de 19 %)."""
        if impuesto is None:
            impuesto = self.IVA_POR_DEFECTO
        return self._calcular_con_opciones(duracion, 0, impuesto, opciones)

    def calcular_costo_con_descuento(self, duracion=1, descuento=None, **opciones):
        """Variante 2: solo con descuento (por defecto, 10 %)."""
        if descuento is None:
            descuento = self.DESCUENTO_POR_DEFECTO
        return self._calcular_con_opciones(duracion, descuento, 0, opciones)

    def calcular_costo_detallado(self, duracion=1, descuento=0, impuesto=0, **opciones):
        """Variante 3: devuelve un diccionario con el desglose del costo."""
        base = self._calcular_con_opciones(duracion, 0, 0, opciones)
        total = self._calcular_con_opciones(duracion, descuento, impuesto, opciones)
        return {
            "servicio": self.nombre,
            "duracion": duracion,
            "costo_base": base,
            "descuento_%": descuento,
            "impuesto_%": impuesto,
            "total": total,
        }

    def _calcular_con_opciones(self, duracion, descuento, impuesto, opciones):
        """Llama a calcular_costo() con opciones variables. Si llega una
        opcion que el servicio no conoce, se lanza un error propio."""
        try:
            return self.calcular_costo(duracion=duracion, descuento=descuento,
                                       impuesto=impuesto, **opciones)
        except TypeError as error:
            raise DatoInvalidoError(
                f"Opcion no valida para '{self.nombre}': {error}") from error

    # ---- Metodos auxiliares compartidos por todos los servicios ----

    def _validar_numero_positivo(self, valor, nombre_dato):
        """Valida que un dato sea un numero mayor que cero."""
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise DatoInvalidoError(f"{nombre_dato} debe ser un numero")
        if valor <= 0:
            raise DatoInvalidoError(f"{nombre_dato} debe ser mayor que cero")

    def _validar_booleano(self, valor, nombre_dato):
        """Valida que una opcion sea True o False."""
        if not isinstance(valor, bool):
            raise DatoInvalidoError(f"{nombre_dato} debe ser True o False")

    def _validar_porcentaje(self, valor, nombre_dato):
        """Valida que un porcentaje este entre 0 y 100."""
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise DatoInvalidoError(f"{nombre_dato} debe ser un numero")
        if valor < 0 or valor > 100:
            raise DatoInvalidoError(f"{nombre_dato} debe estar entre 0 y 100")

    def _aplicar_descuento_e_impuesto(self, subtotal, descuento, impuesto):
        """Aplica primero el descuento y luego el impuesto (porcentajes)."""
        self._validar_porcentaje(descuento, "El descuento")
        self._validar_porcentaje(impuesto, "El impuesto")
        subtotal = subtotal * (1 - descuento / 100)
        total = subtotal * (1 + impuesto / 100)
        return round(total, 2)

# =====================================
# SERVICIO DE RESERVA DE SALAS
# =====================================

class ReservaSala(Servicio):
    UNIDAD_DURACION = "horas"
    MAX_HORAS = 12
    # Si la sala se reserva 5 horas o mas, se da un descuento automatico
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
        """Horas entre 0 y 12; si se indican personas, no pueden superar
        la capacidad de la sala."""
        self._validar_numero_positivo(duracion, "La duracion (horas)")
        if duracion > self.MAX_HORAS:
            raise DatoInvalidoError(
                f"La sala se puede reservar maximo {self.MAX_HORAS} horas")
        if personas is not None:
            if isinstance(personas, bool) or not isinstance(personas, int) or personas <= 0:
                raise DatoInvalidoError("Las personas deben ser un entero mayor que cero")
            if personas > self.capacidad:
                raise DatoInvalidoError(
                    f"La sala admite {self.capacidad} personas y se pidieron {personas}")
        return True

    def calcular_costo(self, duracion=1, descuento=0, impuesto=0, personas=None):
        """Costo = precio por hora x horas. Descuento automatico por
        reservas largas, que se suma al descuento recibido."""
        self.validar_parametros(duracion, personas=personas)
        subtotal = self.precio * duracion
        if duracion >= self.HORAS_PARA_DESCUENTO:
            descuento = min(100, descuento + self.DESCUENTO_AUTOMATICO)
        return self._aplicar_descuento_e_impuesto(subtotal, descuento, impuesto)

    def describir_servicio(self):
        return (f"Sala '{self.nombre}' con capacidad para {self.capacidad} personas. "
                f"Tarifa: ${self.precio:,.0f} por hora, maximo {self.MAX_HORAS} horas. "
                f"Desde {self.HORAS_PARA_DESCUENTO} horas, {self.DESCUENTO_AUTOMATICO}% "
                f"de descuento automatico.")

# =====================================
# SERVICIO DE ALQUILER DE EQUIPOS
# =====================================

class AlquilerEquipo(Servicio):
    UNIDAD_DURACION = "dias"
    MAX_DIAS = 30
    # Porcentaje del subtotal que se cobra por el seguro opcional
    PORCENTAJE_SEGURO = 5

    def __init__(self, nombre, precio, tipo_equipo):
        super().__init__(nombre, precio)
        if tipo_equipo == "":
            raise DatoInvalidoError("El tipo de equipo es obligatorio")
        self.tipo_equipo = tipo_equipo

    def validar_parametros(self, duracion, con_seguro=False):
        """Dias enteros entre 1 y 30; el seguro debe ser True o False."""
        self._validar_numero_positivo(duracion, "La duracion (dias)")
        if duracion != int(duracion):
            raise DatoInvalidoError("Los equipos se alquilan por dias completos")
        if duracion > self.MAX_DIAS:
            raise DatoInvalidoError(
                f"El equipo se puede alquilar maximo {self.MAX_DIAS} dias")
        self._validar_booleano(con_seguro, "El seguro")
        return True

    def calcular_costo(self, duracion=1, descuento=0, impuesto=0, con_seguro=False):
        """Costo = precio por dia x dias. Opcionalmente suma un seguro."""
        self.validar_parametros(duracion, con_seguro=con_seguro)
        subtotal = self.precio * duracion
        if con_seguro:
            subtotal = subtotal * (1 + self.PORCENTAJE_SEGURO / 100)
        return self._aplicar_descuento_e_impuesto(subtotal, descuento, impuesto)

    def describir_servicio(self):
        return (f"Alquiler de '{self.nombre}' (tipo: {self.tipo_equipo}). "
                f"Tarifa: ${self.precio:,.0f} por dia, maximo {self.MAX_DIAS} dias. "
                f"Seguro opcional: {self.PORCENTAJE_SEGURO}% adicional.")

# =====================================
# SERVICIO DE ASESORIAS
# =====================================

class AsesoriaEspecializada(Servicio):
    UNIDAD_DURACION = "horas"
    MAX_HORAS = 8
    # Recargo cuando la asesoria es urgente
    RECARGO_URGENTE = 20

    def __init__(self, nombre, precio, especialidad):
        super().__init__(nombre, precio)
        if especialidad == "":
            raise DatoInvalidoError("La especialidad es obligatoria")
        self.especialidad = especialidad

    def validar_parametros(self, duracion, urgente=False):
        """Horas entre 0 y 8; la urgencia debe ser True o False."""
        self._validar_numero_positivo(duracion, "La duracion (horas)")
        if duracion > self.MAX_HORAS:
            raise DatoInvalidoError(
                f"Una asesoria dura maximo {self.MAX_HORAS} horas")
        self._validar_booleano(urgente, "La urgencia")
        return True

    def calcular_costo(self, duracion=1, descuento=0, impuesto=0, urgente=False):
        """Costo = precio por hora x horas. Si es urgente, se cobra un
        recargo del 20 % antes de aplicar descuento e impuesto."""
        self.validar_parametros(duracion, urgente=urgente)
        subtotal = self.precio * duracion
        if urgente:
            subtotal = subtotal * (1 + self.RECARGO_URGENTE / 100)
        return self._aplicar_descuento_e_impuesto(subtotal, descuento, impuesto)

    def describir_servicio(self):
        return (f"Asesoria '{self.nombre}' en {self.especialidad}. "
                f"Tarifa: ${self.precio:,.0f} por hora, maximo {self.MAX_HORAS} horas. "
                f"Recargo por urgencia: {self.RECARGO_URGENTE}%.")

# =====================================
# CLASE RESERVA  (AQUI SE CONECTAN RESERVAS Y COSTOS)
# =====================================

class Reserva:
    def __init__(self, cliente, servicio, fecha, duracion=1,
                 descuento=0, impuesto=0, **opciones):
        """Crea una reserva. Los parametros nuevos son opcionales, por lo
        que Reserva(cliente, servicio, fecha) sigue funcionando como antes.
        'opciones' recibe lo propio de cada servicio: personas (sala),
        con_seguro (equipo) o urgente (asesoria)."""
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
        # Validar parametros y calcular el costo ANTES de bloquear el servicio:
        # asi, si algo falla, el servicio sigue disponible.
        try:
            servicio.validar_parametros(duracion, **opciones)
            costo = servicio.calcular_costo(duracion=duracion, descuento=descuento,
                                            impuesto=impuesto, **opciones)
        except (DatoInvalidoError, TypeError) as error:
            raise ReservaInvalidaError(
                f"No se pudo crear la reserva: {error}") from error
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.opciones = opciones
        self.costo_total = costo
        self.estado = "Activa"
        servicio.disponible = False
        logging.info("Reserva creada: cliente=%s, servicio=%s, fecha=%s, "
                     "duracion=%s %s, costo=%s", cliente.nombre, servicio.nombre,
                     self.fecha.strftime("%d/%m/%Y"), duracion,
                     servicio.UNIDAD_DURACION, costo)
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
        self.estado = "Cancelada"
        self.servicio.disponible = True
        logging.info("Reserva cancelada: cliente=%s, servicio=%s",
                     self.cliente.nombre, self.servicio.nombre)
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
        logging.info("Se registro un cliente: %s", cliente.nombre)
        print("Cliente registrado correctamente")
    # Registrar un servicio
    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("El dato no es un servicio")
        self.servicios.append(servicio)
        logging.info("Se registro un servicio: %s", servicio.nombre)
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
        logging.info("Se registro una reserva: cliente=%s, servicio=%s",
                     reserva.cliente.nombre, reserva.servicio.nombre)
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

    # NUEVO: suma el costo de las reservas (opcionalmente por cliente/estado)
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

# =====================================
# FUNCIONES AUXILIARES DE PRUEBA
# =====================================

def probar_costo(descripcion, servicio, metodo="calcular_costo", **parametros):
    """Ejecuta una variante de costo controlando los errores y
    registrando el resultado en el log."""
    try:
        resultado = getattr(servicio, metodo)(**parametros)
    except DatoInvalidoError as error:
        print(f"{descripcion} -> Error esperado: {error}")
        logging.error("Costo invalido en '%s': %s", servicio.nombre, error)
    else:
        if isinstance(resultado, dict):
            print(f"{descripcion} -> {resultado}")
        else:
            print(f"{descripcion} -> ${resultado:,.2f}")
        logging.info("Costo calculado para '%s' con %s: %s",
                     servicio.nombre, metodo, resultado)
    finally:
        pass  # Aqui podria ir una accion de cierre si hiciera falta

def probar_reserva(descripcion, sistema, cliente, servicio, fecha, **parametros):
    """Crea y registra una reserva controlando los errores. Devuelve la
    reserva, o None si hubo un error (el programa continua)."""
    try:
        reserva = Reserva(cliente, servicio, fecha, **parametros)
        sistema.registrar_reserva(reserva)
    except (ReservaInvalidaError, ServicioNoDisponibleError) as error:
        print(f"{descripcion} -> Error esperado: {error}")
        logging.error("Error en reserva (%s): %s", descripcion.strip(), error)
        return None
    else:
        print(f"{descripcion} -> OK, costo ${reserva.costo_total:,.2f}")
        return reserva

# =====================================
# PRUEBAS DEL SISTEMA
# =====================================

if __name__ == "__main__":
    sistema = Sistema()
    print("\n--- PRUEBAS DEL SISTEMA SOFTWARE FJ ---")

    # ---------- PARTE 1: CLIENTES ----------
    print("\n=== PARTE 1: CLIENTES ===")
    # Prueba 1: Registrar un cliente (try/except/else/finally)
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

    # ---------- PARTE 2: SERVICIOS ----------
    print("\n=== PARTE 2: SERVICIOS ===")
    # Prueba 5: Registrar una sala
    sala1 = ReservaSala("Sala principal", 50000, 10)
    sistema.registrar_servicio(sala1)
    # Prueba 6: Registrar un equipo
    equipo1 = AlquilerEquipo("Computador", 30000, "Portatil")
    sistema.registrar_servicio(equipo1)
    # Prueba 7: Registrar una asesoria
    asesoria1 = AsesoriaEspecializada("Asesoria tecnica", 80000, "Informatica")
    sistema.registrar_servicio(asesoria1)
    # Prueba 8: Crear servicios con parametros incorrectos
    casos = [
        ("Precio como texto", lambda: AlquilerEquipo("Proyector", "caro", "Video")),
        ("Capacidad cero", lambda: ReservaSala("Sala vacia", 40000, 0)),
        ("Especialidad vacia", lambda: AsesoriaEspecializada("Asesoria", 90000, "")),
    ]
    for nombre_caso, crear in casos:
        try:
            crear()
        except DatoInvalidoError as error:
            print(f"Prueba 8 - {nombre_caso} -> Error esperado: {error}")
            logging.error("Servicio invalido: %s", error)
    # Prueba 9: Servicio es abstracta (no se puede instanciar)
    try:
        Servicio("Generico", 1000)
    except TypeError as error:
        print("Prueba 9 - No se puede instanciar Servicio (clase abstracta)")
        logging.error("Intento de instanciar clase abstracta: %s", error)
    # Prueba 10: describir_servicio() polimorfico
    print("Prueba 10 - describir_servicio():")
    for servicio in (sala1, equipo1, asesoria1):
        print(" *", servicio.describir_servicio())

    # ---------- PARTE 3: COSTOS ----------
    print("\n=== PARTE 3: COSTOS (POLIMORFISMO Y VARIANTES) ===")
    # Prueba 11: mismo metodo, resultado distinto segun el servicio
    print("Prueba 11 - calcular_costo(duracion=2) en cada servicio:")
    for servicio in (sala1, equipo1, asesoria1):
        probar_costo(f"  {servicio.nombre}", servicio, duracion=2)
    # Prueba 12: variantes con parametros opcionales
    print("Prueba 12 - Variantes de costo:")
    probar_costo("  Sala 3 h, 10% desc., 19% IVA", sala1,
                 duracion=3, descuento=10, impuesto=19)
    probar_costo("  Equipo 3 dias con seguro", equipo1, duracion=3, con_seguro=True)
    probar_costo("  Asesoria 2 h urgente", asesoria1, duracion=2, urgente=True)
    probar_costo("  Con impuesto (IVA por defecto), sala 2 h", sala1,
                 metodo="calcular_costo_con_impuesto", duracion=2)
    probar_costo("  Con descuento (10% por defecto), asesoria 2 h", asesoria1,
                 metodo="calcular_costo_con_descuento", duracion=2)
    probar_costo("  Desglose detallado, sala 3 h", sala1,
                 metodo="calcular_costo_detallado",
                 duracion=3, descuento=10, impuesto=19)
    # Prueba 13: errores de costo controlados
    print("Prueba 13 - Errores de costo controlados:")
    probar_costo("  Sala con 15 personas", sala1, duracion=2, personas=15)
    probar_costo("  Equipo 40 dias", equipo1, duracion=40)
    probar_costo("  Descuento 150%", asesoria1, duracion=1, descuento=150)
    probar_costo("  Opcion inexistente", equipo1,
                 metodo="calcular_costo_con_impuesto", duracion=2, urgente=True)

    # ---------- PARTE 4: RESERVAS (CONEXION RESERVA <-> COSTOS) ----------
    print("\n=== PARTE 4: RESERVAS ===")
    # Prueba 14: reserva valida de sala (3 h, 8 personas, con IVA)
    reserva1 = probar_reserva("Prueba 14 - Reserva de sala 3 h", sistema,
                              cliente1, sala1, "25/11/2026",
                              duracion=3, impuesto=19, personas=8)
    # Prueba 15: intentar reservar una sala ocupada
    probar_reserva("Prueba 15 - Sala ocupada", sistema,
                   cliente2, sala1, "26/11/2026", duracion=2)
    # Prueba 16: opcion que el servicio no conoce (el equipo no tiene 'urgente')
    probar_reserva("Prueba 16 - Opcion no valida en equipo", sistema,
                   cliente2, equipo1, "27/11/2026", duracion=1, urgente=True)
    # Prueba 17: reserva valida de equipo con seguro
    probar_reserva("Prueba 17 - Equipo 3 dias con seguro", sistema,
                   cliente2, equipo1, "27/11/2026",
                   duracion=3, con_seguro=True)
    # Prueba 18: duracion invalida (el servicio NO debe quedar bloqueado)
    probar_reserva("Prueba 18 - Asesoria de 10 h (maximo 8)", sistema,
                   cliente2, asesoria1, "28/11/2026", duracion=10)
    print("  Asesoria sigue disponible:", asesoria1.consultar_disponibilidad())
    # Prueba 19: la misma asesoria, ahora con datos correctos y urgente
    probar_reserva("Prueba 19 - Asesoria 2 h urgente", sistema,
                   cliente1, asesoria1, "28/11/2026",
                   duracion=2, urgente=True, descuento=5)
    # Prueba 20: fecha incorrecta (formato)
    probar_reserva("Prueba 20 - Fecha incorrecta", sistema,
                   cliente2, equipo1, "fecha incorrecta", duracion=1)
    # Prueba 21: cancelar una reserva
    try:
        reserva1.cancelar_reserva()
    except OperacionNoPermitidaError as error:
        print("Error:", error)
        logging.error("Error al cancelar: %s", error)
    # Prueba 22: intentar cancelar nuevamente
    try:
        reserva1.cancelar_reserva()
    except OperacionNoPermitidaError as error:
        print("Prueba 22 - Error esperado:", error)
        logging.error("Operacion no permitida: %s", error)
    # Prueba 23: la sala cancelada queda libre y se puede reservar otra vez
    probar_reserva("Prueba 23 - Sala liberada, nueva reserva de 6 h", sistema,
                   cliente2, sala1, "30/11/2026", duracion=6)

    # ---------- PARTE 5: CONSULTAS ----------
    print("\n=== PARTE 5: CONSULTAS ===")
    print("\n--- CLIENTES REGISTRADOS ---")
    sistema.mostrar_clientes()
    print("\n--- SERVICIOS REGISTRADOS ---")
    sistema.mostrar_servicios()
    print("\n--- RESERVAS REGISTRADAS ---")
    sistema.mostrar_reservas()
    print("\n--- CONSULTAR RESERVAS DE CARLOS ---")
    sistema.consultar_reservas(cliente=cliente1)
    print("\n--- CONSULTAR RESERVAS CANCELADAS ---")
    sistema.consultar_reservas(estado="Cancelada")
    print("\n--- TOTALES ---")
    print(f"Total de reservas activas: ${sistema.calcular_total_reservas(estado='Activa'):,.2f}")
    print(f"Total de Maria Lopez: ${sistema.calcular_total_reservas(cliente=cliente2):,.2f}")
    print("\n--- FIN DE LAS PRUEBAS ---")
