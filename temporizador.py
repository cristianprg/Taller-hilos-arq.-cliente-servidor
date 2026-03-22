import threading
import time
import random

# ---------------- STRATEGY ----------------
class EstrategiaConexion:
    def ejecutar(self) -> str:
        return ""


class ConexionReal(EstrategiaConexion):
    def ejecutar(self) -> str:
        tiempo = random.randint(1, 5)
        time.sleep(tiempo)
        return "Conectado"


# ---------------- CONTEXTO ----------------
class Cliente:
    def __init__(self, estrategia):
        self.estrategia = estrategia

    def conectar(self):
        return self.estrategia.ejecutar()


# ---------------- TIMEOUT ----------------
def timeout_expirado(evento_cancelacion):
    print("Timeout: La conexión tardó demasiado. Operación cancelada.")
    evento_cancelacion.set()


# ---------------- MAIN ----------------
if __name__ == "__main__":
    evento_cancelacion = threading.Event()

    # Timer de 2 segundos
    timer = threading.Timer(2, timeout_expirado, args=(evento_cancelacion,))
    timer.start()

    cliente = Cliente(ConexionReal())

    resultado = [None]

    # Ejecutar conexión
    def ejecutar_conexion():
        resultado[0] = cliente.conectar()

    hilo_conexion = threading.Thread(target=ejecutar_conexion)
    hilo_conexion.start()

    # Esperar a que termine o que ocurra timeout
    hilo_conexion.join()

    # Cancelar timer si terminó antes
    if not evento_cancelacion.is_set():
        timer.cancel()
        print(f"Conexión exitosa: {resultado[0]}")