import threading
import time
import random

# ---------------- SUBJECT ----------------
class Carrera:
    def __init__(self, num_autos):
        self.barrera = threading.Barrier(num_autos)
        self.evento_inicio = threading.Event()
        self.autos = []

    def registrar_auto(self, auto):
        self.autos.append(auto)

    def iniciar(self):
        # Método que ejecutan los autos internamente
        pass


# ---------------- OBSERVER ----------------
class Auto(threading.Thread):
    def __init__(self, id_auto, carrera):
        super().__init__()
        self.id_auto = id_auto
        self.carrera = carrera

    def run(self):
        # Simula llegada
        time.sleep(random.uniform(0.5, 2))
        print(f"Auto {self.id_auto} llegó a la salida y está esperando.")

        # Espera en la barrera
        posicion = self.carrera.barrera.wait()

        # Solo uno anuncia
        if posicion == 0:
            print("\n--- ¡CARRERA! ---")
            self.carrera.evento_inicio.set()

        # Espera señal del sujeto (Observer pattern)
        self.carrera.evento_inicio.wait()

        print(f"Auto {self.id_auto} inició la carrera.")


# ---------------- MAIN ----------------
if __name__ == "__main__":
    num_autos = 5
    carrera = Carrera(num_autos)

    autos = []

    for i in range(1, num_autos + 1):
        auto = Auto(i, carrera)
        carrera.registrar_auto(auto)
        autos.append(auto)
        auto.start()

    for auto in autos:
        auto.join()