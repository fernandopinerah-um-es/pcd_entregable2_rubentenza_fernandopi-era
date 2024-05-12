from abc import ABC, abstractmethod
from functools import reduce
import time
import random
import asyncio
from datetime import datetime

class Singleton:
    _unicaInstancia = None

    def __init__(self):
        self.contexto = Contexto(None)
        self.media = Media()
        self.desviacion = Desviacion()
        self.max_min = MaximoMinimo()
        self.sensor = Sensor ()
        self.operador = GestorGlobal()


    @classmethod
    def obtener_instancia(cls):
        if not cls._unicaInstancia :
            cls._unicaInstancia = cls()
        return cls._unicaInstancia 
    
    def inicializar_sensor(self):
        self.sensor.register_observer(self.operador)
        asyncio.run(self.sensor.valor_aleatorio())



# Definición de la clase Observable (Sujeto)
class Observable:
    def __init__(self):
        self._observers = []

    def register_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def notify_observers(self, value):
        for observer in self._observers:
            observer.update(value)

# Definición de la clase Observer
class Observer(ABC):
    @abstractmethod
    def update(self, data):
        pass

# Definición de la clase Sensor (Sujeto observable)
class Sensor(Observable):
    def __init__(self):
        super().__init__()
        self.run = True

    async def valor_aleatorio(self):
        while self.run:
            timestamp = int(time.time())
            temperatura = random.uniform(0, 40)  # Temperaturas aleatorias entre 20°C y 40°C
            self.set_value((timestamp,temperatura))
            await asyncio.sleep(5)

    def set_value(self, value):
        self.notify_observers(value)

    def stop(self):
        self.run = False

# Definición de la clase Operador (Observador)
class GestorGlobal(Observer):
    def __init__(self):
        self.temperaturas = []

    def update(self,value):
        self.temperaturas.append(value[1])
        self.inicializar_salida(value[0],value[1])

    def inicializar_salida(self,fecha,valor):

        # Convertir el tiempo actual a un objeto datetime
        fecha_hora = datetime.fromtimestamp(fecha)

        # Formatear la fecha y hora como una cadena legible
        fecha_legible = fecha_hora.strftime('%Y-%m-%d %H:%M:%S')

        print('\nSe ha recibido una alerta de temperautura: ',valor)
        print('Fecha : ', fecha_legible)


        aumento = Aumento_temp()
        umbral = Umbral(aumento)
        estadisticos = Estadisticos_H(umbral)

        request = Request(self.temperaturas[-12:])
        return estadisticos.handle_request(request)