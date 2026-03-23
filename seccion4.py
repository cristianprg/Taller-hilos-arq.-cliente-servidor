"""Procesos e hilos - Taller

Sección 4

"""

import threading
import time
import random
from collections import deque

# --- 1. CLASE DEL MONITOR DE LA COLA (Patrón Productor-Consumidor) ---
class PrioritizedJobQueue:
    def __init__(self, limite_premium_consecutivos=3):
        self.cola_premium = deque()
        self.cola_gratis = deque()
        self.lock = threading.Lock()
        self.condicion = threading.Condition(self.lock)
        
        # Variables para manejar la inanición
        self.premium_consecutivos = 0
        self.limite_premium_consecutivos = limite_premium_consecutivos
        self.sistema_activo = True # Bandera para apagar los workers al final

    def agregar_trabajo(self, trabajo, tipo_cliente):
        with self.condicion: # Adquiere el lock automáticamente
            if tipo_cliente == "Premium":
                self.cola_premium.append(trabajo)
            else:
                self.cola_gratis.append(trabajo)
            
            # Despierta a un worker que esté durmiendo esperando trabajo
            self.condicion.notify()

    def obtener_trabajo(self):
        with self.condicion:
            # Mientras no haya trabajos y el sistema siga activo, el worker duerme
            while not self.cola_premium and not self.cola_gratis and self.sistema_activo:
                self.condicion.wait()
            
            # Si el sistema se apaga y no hay trabajos, el worker termina
            if not self.sistema_activo and not self.cola_premium and not self.cola_gratis:
                return None, None

            # LÓGICA DE PRIORIDAD Y ANTI-INANICIÓN
            if self.cola_premium and self.cola_gratis:
                if self.premium_consecutivos >= self.limite_premium_consecutivos:
                    # Forzamos uno gratis para evitar inanición
                    trabajo = self.cola_gratis.popleft()
                    self.premium_consecutivos = 0
                    return trabajo, "Gratis"
                else:
                    # Damos prioridad al Premium
                    trabajo = self.cola_premium.popleft()
                    self.premium_consecutivos += 1
                    return trabajo, "Premium"
            
            elif self.cola_premium: # Solo hay premium
                trabajo = self.cola_premium.popleft()
                self.premium_consecutivos += 1
                return trabajo, "Premium"
            
            else: # Solo hay gratis
                trabajo = self.cola_gratis.popleft()
                self.premium_consecutivos = 0
                return trabajo, "Gratis"

    def apagar_sistema(self):
        with self.condicion:
            self.sistema_activo = False
            self.condicion.notify_all() # Despierta a todos los workers para que mueran pacíficamente

# --- 2. HILOS CLIENTE (Productores) ---
def cliente(id_cliente, tipo_cliente, cola_trabajos):
    num_trabajos = random.randint(5, 10)
    for i in range(num_trabajos):
        nombre_video = f"[VIDEO-{tipo_cliente[0]}{id_cliente}-{i+1}]"
        print(f"Cliente-{tipo_cliente}-{id_cliente}: Envió trabajo {nombre_video}")
        cola_trabajos.agregar_trabajo(nombre_video, tipo_cliente)
        
        # Simula tiempo entre envíos
        time.sleep(random.uniform(0.1, 0.5))

# --- 3. HILOS WORKER (Consumidores) ---
def worker(id_worker, cola_trabajos):
    while True:
        trabajo, tipo = cola_trabajos.obtener_trabajo()
        
        if trabajo is None: # Señal de apagado
            break
            
        motivo = ""
        # Pequeño hack para la salida: si es gratis y acabamos de reiniciar el contador premium
        if tipo == "Gratis" and cola_trabajos.cola_premium: 
             motivo = " (Se procesa uno gratis por anti-inanición)"
             
        print(f"Worker-{id_worker}: Procesando trabajo {trabajo} de Cliente-{tipo}{motivo}")
        
        # Simula el procesamiento de video
        time.sleep(random.uniform(0.5, 1.0))

# --- 4. EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    cola = PrioritizedJobQueue(limite_premium_consecutivos=3)
    
    hilos = []
    
    # Crear 3 Workers
    for i in range(1, 4):
        w = threading.Thread(target=worker, args=(i, cola))
        w.start()
        hilos.append(w)
        
    # Crear 3 Clientes Premium y 5 Gratuitos
    for i in range(1, 4):
        c = threading.Thread(target=cliente, args=(i, "Premium", cola))
        c.start()
        hilos.append(c)
        
    for i in range(1, 6):
        c = threading.Thread(target=cliente, args=(i, "Gratis", cola))
        c.start()
        hilos.append(c)

    # Esperar a que todos los clientes terminen de enviar
    for t in hilos[3:]: # Ignoramos los primeros 3 (workers)
        t.join()
        
    # Apagar la cola y esperar a que los workers terminen lo que queda
    cola.apagar_sistema()
    for w in hilos[:3]:
        w.join()

    print("--- Sistema finalizado ---")