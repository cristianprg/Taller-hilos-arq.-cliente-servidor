import threading
import time
import random
from datetime import datetime


class BufferCompartido:
    _instancia = None
    _lock_instancia = threading.Lock()

    def __new__(cls, capacidad):
        with cls._lock_instancia:
            if cls._instancia is None:
                cls._instancia = super(BufferCompartido, cls).__new__(cls)
        return cls._instancia

    def __init__(self, capacidad):
        # Evitar reinicialización en múltiples llamadas
        if hasattr(self, "inicializado"):
            return

        self.buffer = []
        self.capacidad = capacidad

        self.vacios = threading.Semaphore(capacidad)
        self.llenos = threading.Semaphore(0)
        self.mutex = threading.Lock()
        self.print_lock = threading.Lock()

        self.inicializado = True

    def _get_timestamp(self):
        return datetime.now().strftime('%H:%M:%S.%f')[:-3]

    def producir(self, item):
        self.vacios.acquire()

        with self.mutex:
            self.buffer.append(item)
            with self.print_lock:
                print(f"[{self._get_timestamp()}] 📤 Productor: Tarea {item} añadida | Buffer: {self.buffer} (Tamaño: {len(self.buffer)}/{self.capacidad})")

        self.llenos.release()

    def consumir(self, nombre):
        self.llenos.acquire()

        with self.mutex:
            item = self.buffer.pop(0)
            with self.print_lock:
                print(f"[{self._get_timestamp()}] 📥 {nombre}: Tomó tarea {item} | Buffer: {self.buffer} (Tamaño: {len(self.buffer)}/{self.capacidad})")

        self.vacios.release()
        return item


def productor(buffer):
    for i in range(1, 16):
        time.sleep(random.uniform(0.01, 0.1))
        buffer.producir(i)

    buffer.producir(None)
    buffer.producir(None)

    with buffer.print_lock:
        print(f"[{buffer._get_timestamp()}] ✅ Productor: Finalizó la producción\n")


def consumidor(buffer, nombre):
    while True:
        item = buffer.consumir(nombre)

        if item is None:
            with buffer.print_lock:
                print(f"[{buffer._get_timestamp()}] 🛑 {nombre}: Recibió señal de terminación\n")
            break

        time.sleep(random.uniform(0.2, 0.5))
        with buffer.print_lock:
            print(f"[{buffer._get_timestamp()}] ⚙️  {nombre}: Finalizó procesamiento de tarea {item}")


if __name__ == "__main__":
    buffer = BufferCompartido(10)

    prod = threading.Thread(target=productor, args=(buffer,), name="Productor")
    cons1 = threading.Thread(target=consumidor, args=(buffer, "Consumidor-1"), name="Cons-1")
    cons2 = threading.Thread(target=consumidor, args=(buffer, "Consumidor-2"), name="Cons-2")

    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   SISTEMA PRODUCTOR-CONSUMIDOR CON BUFFER COMPARTIDO          ║")
    print("║   Capacidad del Buffer: 10   |   Tareas: 15                   ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")

    prod.start()
    cons1.start()
    cons2.start()

    prod.join()
    cons1.join()
    cons2.join()

    print("╔════════════════════════════════════════════════════════════════╗")
    print("║              ✅ PROCESO COMPLETADO EXITOSAMENTE ✅             ║")
    print("╚════════════════════════════════════════════════════════════════╝")