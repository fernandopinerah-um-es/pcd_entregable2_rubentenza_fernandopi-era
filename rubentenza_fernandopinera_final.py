from abc import ABC, abstractmethod  # Importamos las clases ABC y abstractmethod del módulo abc para definir clases y métodos abstractos
from functools import reduce  # Importamos reduce del módulo functools para reducir secuencias de valores a un solo valor
import time  # Importamos el módulo time para trabajar con el tiempo
import random  # Importamos el módulo random para generar números aleatorios
import asyncio  # Importamos asyncio para la programación asíncrona
from datetime import datetime  # Importamos datetime para trabajar con fechas y horas

# Definimos la clase Singleton para garantizar que solo exista una instancia de ciertas clases en todo el programa
class Singleton:
    _unicaInstancia = None  # Variable que almacenará la única instancia de la clase

    def __init__(self):
        # Creamos instancias de otras clases relacionadas con el monitoreo de temperatura
        self.contexto = Contexto(None)
        self.media = Media()
        self.desviacion = Desviacion()
        self.max_min = MaximoMinimo()
        self.sensor = Sensor ()
        self.operador = GestorGlobal()

    @classmethod
    def obtener_instancia(cls):
        # Método estático para obtener la única instancia de la clase Singleton
        if not cls._unicaInstancia:
            cls._unicaInstancia = cls()  # Si no hay una instancia, creamos una
        return cls._unicaInstancia  # Devolvemos la instancia existente o recién creada
    
    def inicializar_sensor(self):
        # Método para inicializar el sensor y comenzar a generar valores de temperatura aleatorios
        self.sensor.register_observer(self.operador)  # Registramos al gestor global como observador del sensor
        asyncio.run(self.sensor.valor_aleatorio())  # Ejecutamos el método valor_aleatorio del sensor de forma asíncrona, el cual generará valores aleatorios.

# Definimos la clase Observable (Sujeto)
class Observable:
    def __init__(self):
        self._observers = []  # Lista para almacenar los observadores registrados

    def register_observer(self, observer):
        # Método para registrar un observador
        self._observers.append(observer)

    def remove_observer(self, observer):
        # Método para eliminar un observador
        self._observers.remove(observer)

    def notify_observers(self, value):
        # Método para notificar a todos los observadores con un valor dado (fecha y temperatura)
        for observer in self._observers:
            observer.update(value)

# Definimos la clase Observer (Observador)
class Observer(ABC):
    @abstractmethod
    def update(self, data):
        # Método abstracto para actualizar el observador con nuevos datos
        pass

# Definimos la clase Sensor (Sujeto observable)
class Sensor(Observable):
    def __init__(self):
        super().__init__()
        self.run = True  # Variable para controlar la ejecución del sensor

    async def valor_aleatorio(self):
        # Método para generar valores de temperatura aleatorios de forma asíncrona
        while self.run:
            timestamp = int(time.time())  # Obtenemos el timestamp actual
            temperatura = random.uniform(25, 40)  # Generamos una temperatura aleatoria entre 30 y 40
            self.set_value((timestamp,temperatura))  # Notificamos a los observadores con el valor generado
            await asyncio.sleep(5)  # Esperamos 5 segundos antes de generar otro valor

    def set_value(self, value):
        # Método para notificar a los observadores con un nuevo valor
        self.notify_observers(value)

    def stop(self):
        # Método para detener la generación de valores por parte del sensor
        self.run = False

# Definimos la clase Operador (Observador)
class GestorGlobal(Observer):
    def __init__(self):
        self.temperaturas = []  # Lista para almacenar las temperaturas recibidas

    def update(self,value):
        # Método para actualizar el observador con un nuevo valor de temperatura
        self.temperaturas.append(value[1])  # Agregamos la temperatura a la lista de temperaturas
        self.inicializar_salida(value[0],value[1])  # Inicializamos la salida con la fecha y temperatura recibidas

    def inicializar_salida(self,fecha,valor):
        # Método para inicializar la salida con la fecha y temperatura recibidas
        fecha_hora = datetime.fromtimestamp(fecha)  # Convertimos el timestamp a un objeto datetime
        fecha_legible = fecha_hora.strftime('%Y-%m-%d %H:%M:%S')  # Formateamos la fecha y hora como cadena legible
        print('\nSe ha recibido una alerta de temperatura: ',valor)
        print('Fecha : ', fecha_legible)

        # Creamos instancias de clases relacionadas con el cálculo de estadísticas y las manejamos
        aumento = Aumento_temp()
        umbral = Umbral(aumento)
        estadisticos = Estadisticos_H(umbral)
        request = Request(self.temperaturas[-12:])  # Creamos una solicitud con las últimas 12 temperaturas recibidas (60 segundos->60/5=12)
        return estadisticos.handle_request(request)  # Manejamos la solicitud de estadísticas, inicializando la cadena de responsabilidad

# Definimos la clase abstracta Estadisticos para calcular estadísticas de temperaturas
class Estadisticos(ABC):
    @abstractmethod
    def metodo(self,temperaturas):
        # Método abstracto para calcular estadísticas de temperaturas
        pass

# Definimos la clase Media para calcular la media de las temperaturas
class Media(Estadisticos):
    def metodo(self,temperaturas):
        # Método para calcular la media de las temperaturas
        return (reduce(lambda x, y: x+y, temperaturas)/len(temperaturas))

# Definimos la clase Desviacion para calcular la desviación estándar de las temperaturas
class Desviacion(Estadisticos):
     def metodo(self,temperaturas):
        # Método para calcular la desviación estándar de las temperaturas
        media_tem = Media().metodo(temperaturas)
        variacion = list(map(lambda x: (x-media_tem)**2, temperaturas))
        sum_variacion = sum(variacion)
        promedio_sum = sum_variacion/len(temperaturas)
        return (promedio_sum)**0.5

# Definimos la clase MaximoMinimo para calcular el valor máximo y mínimo de las temperaturas
class MaximoMinimo(Estadisticos):
    def metodo(self,temperaturas):
        # Método para calcular el valor máximo y mínimo de las temperaturas
        return (reduce(lambda x,y: x if(x>y) else y,temperaturas), reduce(lambda x,y: x if(x<y) else y,temperaturas))

# Definimos la clase Contexto para establecer la estrategia de cálculo de estadísticas
class Contexto:
    def __init__(self,estrategia):
        self.estrategia = estrategia  # Estrategia de cálculo de estadísticas

    def establecer_estrategia(self,estrategia):
        # Método para establecer la estrategia de cálculo de estadísticas
        self.estrategia = estrategia

    def calcular_estadistico(self, temperaturas):
        # Método para calcular estadísticas de temperaturas según la estrategia establecida
        return self.estrategia.metodo(temperaturas)

# Definimos la clase Handler como la clase base abstracta para los manejadores de solicitudes
# En este caso, puesto que cada handler tiene que manejar la solicitud sí o sí y después pasar
# la solicitud a su sucesor, no realizaremos ninguna comprobación sobre si la petición es igual a ese handler
# ya que la petición requiere del resultado de todos los handler de la cadena de responsabilidad.
class Handler:
    def __init__(self,sucesor):
        self.sucesor = sucesor  # Sucesor en la cadena de responsabilidad

    def handle_request(self,request):
        # Método abstracto para manejar una solicitud
        pass

# Definimos la clase Estadisticos_H para manejar solicitudes relacionadas con las estadísticas de temperaturas
class Estadisticos_H(Handler):
    def handle_request(self,request):
        # Método para manejar una solicitud de estadísticas de temperaturas
        singleton = Singleton.obtener_instancia()  # Obtenemos la instancia del Singleton
        # Establecemos la estrategia de cálculo de estadísticas y las calculamos
        # En este caso, como la petición requiere el resultado de todos los estadísticos, iremos cambiando
        # manualmente la estrategia para obtener todos los estadísticos.
        singleton.contexto.establecer_estrategia(singleton.media)
        media_calculada = singleton.contexto.calcular_estadistico(request.temperaturas)
        singleton.contexto.establecer_estrategia(singleton.desviacion)
        desviacion_calculada = singleton.contexto.calcular_estadistico(request.temperaturas)
        singleton.contexto.establecer_estrategia(singleton.max_min)
        max_min_calculado = singleton.contexto.calcular_estadistico(request.temperaturas)
        # Mostramos las estadísticas calculadas
        print('Media = ',media_calculada, ' ; Desviacion = ', desviacion_calculada, ' ; Máximo = ',max_min_calculado[0], ' ; Mínimo = ',max_min_calculado[1])
        # Pasamos la solicitud al sucesor si existe
        if self.sucesor:
            self.sucesor.handle_request(request)

# Definimos la clase Umbral para manejar solicitudes relacionadas con el umbral de temperaturas
class Umbral(Handler):
    def handle_request(self,request):
        # Método para manejar una solicitud de umbral de temperaturas
        limite = 35  # Umbral de temperatura
        temperaturas = request.temperaturas[-6:]  # Últimas 6 temperaturas recibidas(30 segundos -> 30/5=6)
        umbral = temperaturas[-1] # Verificamos si alguna temperatura supera el umbral
        if umbral>=limite:
            print ('Se ha superado el umbral de ', limite,'ºC')  # Mostramos un mensaje si se supera el umbral
        else:
            print ('No se ha superado el umbral')  # Mostramos un mensaje si no se supera el umbral
        # Pasamos la solicitud al sucesor si existe
        if self.sucesor:
            self.sucesor.handle_request(request)

# Definimos la clase Aumento_temp para manejar solicitudes relacionadas con el aumento de temperaturas
class Aumento_temp(Handler):
    def __init__(self):
        super().__init__(sucesor=None)

    def handle_request(self,request):
        # Método para manejar una solicitud de aumento de temperaturas
        limite = 10  # Límite de aumento de temperatura
        temperaturas = request.temperaturas[-6:]  # Últimas 6 temperaturas recibidas (30 segundos)
        aumento=any(map(lambda x: any(map(lambda y: abs(x - y) >= limite, temperaturas)), temperaturas))  # Verificamos si hay una diferencia de 10 grados de temperatura
        if aumento:
            print ('Ha habido una diferencia de temperatura de', limite, 'ºC en los últimos 30 segundos')  # Mostramos un mensaje si se sobrepasa la temperatura
        else:
            print ('No ha habido una diferencia de temperatura de', limite, 'ºC en los últimos 30 segundos')  # Mostramos un mensaje si no se sobrepasa la temperatura
        # Pasamos la solicitud al sucesor si existe
        if self.sucesor:
            self.sucesor.handle_request(request)

# Definimos la clase Request para representar una solicitud relacionada con las temperaturas
class Request:
    def __init__(self,temperaturas):
        self.temperaturas = temperaturas  # Lista de temperaturas de la solicitud

# Función principal
if __name__ == '__main__':
    # Creamos una instancia del Singleton y inicializamos el sensor para comenzar a generar valores de temperatura aleatorios
    singleton = Singleton.obtener_instancia()
    singleton.inicializar_sensor()
