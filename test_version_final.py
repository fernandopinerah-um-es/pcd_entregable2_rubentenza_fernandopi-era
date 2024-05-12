import pytest
from unittest.mock import MagicMock
from io import StringIO
import sys
from rubentenza_fernandopinera_final import *
import numpy as np

def test_singleton():
    # Verificar que solo haya una instancia de Singleton
    singleton1 = Singleton.obtener_instancia()
    singleton2 = Singleton.obtener_instancia()
    assert singleton1 is singleton2

def test_observer():
    observer = GestorGlobal()

    # Simulamos la actualización del observador con un valor de temperatura
    observer.update((time.time(), 35))

    # Verificamos que la temperatura se haya agregado a la lista de temperaturas del observador
    assert observer.temperaturas == [35]

def test_estadisticos_media():
    # Verificar el cálculo de la media de las temperaturas
    media = Media()
    assert media.metodo([25, 30, 35, 40]) == np.mean([25, 30, 35, 40])

def test_estadisticos_desviacion():
    # Verifica el cálculo de la desviación estándar de las temperaturas
    desviacion = Desviacion()
    assert round(desviacion.metodo([25, 30, 35, 40]), 2) == round(np.std([25,30,35,40]), 2)

def test_estadisticos_maximo_minimo():
    # Verificar el cálculo del valor máximo y mínimo de las temperaturas
    max_min = MaximoMinimo()
    assert max_min.metodo([25, 30, 35, 40]) == (40, 25)

def test_contexto():
    contexto = Contexto(None)
    temperaturas = [25, 30, 35, 40]

    # Mock de la estrategia de cálculo de la media
    mock_media = MagicMock()
    mock_media.metodo.return_value = np.mean(temperaturas)
    
    # Mock de la estrategia de cálculo de la desviación estándar
    mock_desviacion = MagicMock()
    mock_desviacion.metodo.return_value = np.std(temperaturas)
    
    # Verifica que el contexto pueda establecer la estrategia y calcular estadísticas
    contexto.establecer_estrategia(mock_media)
    assert round(contexto.calcular_estadistico(temperaturas), 2) == round(np.mean(temperaturas), 2)

    contexto.establecer_estrategia(mock_desviacion)
    assert round(contexto.calcular_estadistico(temperaturas), 2) == round(np.std(temperaturas), 2)

def test_handler():
    # Verificar que los handlers de solicitudes pasen la solicitud al sucesor
    sucesor = Handler(None)  # Añadimos un sucesor
    assert sucesor.handle_request(Request([25, 30, 35, 40])) is None

def test_aumento_temp():
    aumento_temp = Aumento_temp()

    # Verificar que el aumento de temperatura se detecte correctamente
    request = Request([25, 30, 40, 45, 50, 60])
    assert aumento_temp.handle_request(request) is None

    request = Request([25, 30, 40, 41, 42, 43])
    assert aumento_temp.handle_request(request) is None

def test_umbral():
    # Verifica que la clase Umbral pueda ser instanciada correctamente
    sucesor = Handler(None)  # Añadimos un sucesor
    umbral = Umbral(sucesor)  # Instanciamos Umbral con un sucesor
    assert isinstance(umbral, Umbral)

if __name__ == "__main__":
    pytest.main([__file__])
