from abc import ABC, abstractmethod
from functools import reduce
import random
import time

class Singleton:
    _unicaInstancia = None

    @classmethod
    def obtener_instancia(cls):

        if not cls._unicaInstancia:
            cls._unicaInstancia = cls()

        return cls._unicaInstancia 
    
    def inicializar_sensor(self):

        gestor = GestorGlobal(Umbral(), Aumento_temp(limite=10))
        sensor = Sensor(gestor)  # Pasar el gestor como argumento al instanciar Sensor
        operador = Operator()

        while True:

            time.sleep(5)
            temperatura = obtener_temperatura_desde_sensor()
            timestamp = obtener_timestamp()
            try:
                sensor.set_value((timestamp, temperatura))
            except Exception as e:
                print(f"Error al enviar temperatura desde el sensor: {e}")


def obtener_temperatura_desde_sensor():

    # Generar temperatura aleatoria entre 10 y 35 grados
    temperatura = random.uniform(10, 35)
    return temperatura

def obtener_timestamp():
    # Obtener el timestamp actual
    return int(time.time())


class GestorGlobal:

    def __init__(self, umbral, aumento_temp):

        self.temperaturas = []
        self.umbral = umbral
        self.aumento_temp = aumento_temp

    def procesar_temperaturas(self, value):

        self.temperaturas.append(value)
        self.inicializar_salida()

    def inicializar_salida(self):

        contexto = Contexto(None)

        estadisticos = Estadisticos_H(contexto)

        request = Request(self.temperaturas)

        estadisticos.handle_request(request)
        self.umbral.handle_request(request)
        self.aumento_temp.handle_request(request)


class Observable:

    def __init__(self, gestor):

        self._gestor = gestor

    def notify_observers(self, value):

        return self._gestor.procesar_temperaturas(value)


class Observer(ABC):

    @abstractmethod
    def update(self, data):
        pass


class Sensor(Observable):

    def set_value(self, value):

        self.notify_observers(value)



class Operator(Observer):

    def update(self, data):

        print(f"Se ha recibido una alerta: {data}")


class Estadisticos(ABC):

    @abstractmethod
    def metodo(self, temperaturas):
        pass


class Media(Estadisticos):

    def metodo(self, temperaturas):
        try:
            print("Media:", reduce(lambda x, y: x + y[1], temperaturas, 0) / len(temperaturas))
        except Exception as e:
            print(f"Error al calcular la media: {e}")


class Desviacion(Estadisticos):

    def metodo(self, temperaturas):
        try:
            media_tem = sum(temp[1] for temp in temperaturas) / len(temperaturas)

            variacion = list(map(lambda x: (x[1] - media_tem) ** 2, temperaturas))

            sum_variacion = sum(variacion)

            print("Desviación estándar:", (sum_variacion / len(temperaturas)) ** 0.5)
        except Exception as e:
            print(f"Error al calcular la desviación estándar: {e}")


class MaximoMinimo(Estadisticos):

    def metodo(self, temperaturas):
        try:
            print("Máximo =", max(temperaturas, key=lambda x: x[1]), "; Mínimo =", min(temperaturas, key=lambda x: x[1]))
        except Exception as e:
            print(f"Error al calcular el máximo y el mínimo: {e}")


class MaximoMinimoPeriodo(Estadisticos):

    def metodo(self, temperaturas):
        try:
            temperaturas_ultimo_minuto = temperaturas[-12:]  # 12 valores en 60 segundos si se recibe una temperatura cada 5 segundos

            print("Máximo en el último minuto =", max(temperaturas_ultimo_minuto, key=lambda x: x[1]), "; Mínimo en el último minuto =", min(temperaturas_ultimo_minuto, key=lambda x: x[1]))
        except Exception as e:
            print(f"Error al calcular el máximo y el mínimo del último minuto: {e}")


class Contexto:

    def __init__(self, estrategia):

        self.estrategia = estrategia

    def establecer_estrategia(self, estrategia):

        self.estrategia = estrategia

    def calcular_estadistico(self, temperaturas):

        return self.estrategia.metodo(temperaturas)


class Handler:

    def __init__(self, sucesor=None):

        self.sucesor = sucesor

    @abstractmethod

    def handle_request(self, request):

        pass


class Estadisticos_H(Handler):

    def __init__(self, contexto):

        super().__init__()
        self.contexto = contexto

    def handle_request(self, request):

        media = Media()
        desviacion = Desviacion()
        max_min = MaximoMinimo()
        max_min_periodo = MaximoMinimoPeriodo()

        self.contexto.establecer_estrategia(media)
        self.contexto.calcular_estadistico(request.temperaturas)

        self.contexto.establecer_estrategia(desviacion)
        self.contexto.calcular_estadistico(request.temperaturas)

        self.contexto.establecer_estrategia(max_min)
        self.contexto.calcular_estadistico(request.temperaturas)

        self.contexto.establecer_estrategia(max_min_periodo)
        self.contexto.calcular_estadistico(request.temperaturas)

        if self.sucesor:
            self.sucesor.handle_request(request)


class Umbral(Handler):

    def __init__(self, sucesor=None, umbral=30):  # Umbral predeterminado de 30 grados

        super().__init__(sucesor)
        self.umbral = umbral

    def handle_request(self, request):

        if any(temp[1] > self.umbral for temp in request.temperaturas):

            print('Alerta: Se ha superado el umbral de temperatura')

        else:

            print('La temperatura está dentro del umbral')


class Aumento_temp(Handler):

    def __init__(self, sucesor=None, limite=10):

        super().__init__(sucesor)
        self.limite = limite

    def handle_request(self, request):

        ultima_temperatura = request.temperaturas[-1][1]
        penultima_temperatura = request.temperaturas[-2][1]

        if ultima_temperatura - penultima_temperatura > self.limite:

            print('Alerta: La temperatura ha aumentado más de 10 grados en los últimos 30 segundos')

        else:

            print('La temperatura no ha aumentado más de 10 grados en los últimos 30 segundos')


class Request:

    def __init__(self, temperaturas):

        self.temperaturas = temperaturas


# Ejemplo de uso:

if __name__ == "__main__":
    
    gestor = GestorGlobal(Umbral(), Aumento_temp())
    Singleton.obtener_instancia().inicializar_sensor()