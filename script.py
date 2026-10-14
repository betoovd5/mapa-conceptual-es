import threading
import time

# Función para el primer hilo
def tarea_a():
    for i in range(5):
        print(f"--- Hilo A en ejecución (paso {i+1}) ---")
        time.sleep(1)  # Simula una tarea que toma tiempo

# Función para el segundo hilo
def tarea_b():
    for i in range(5):
        print(f"*** Hilo B en ejecución (paso {i+1}) ***")
        time.sleep(0.8) # Un intervalo diferente para notar la concurrencia

if __name__ == "__main__":
    # 1. Crear los hilos definiendo la función 'target'
    hilo1 = threading.Thread(target=tarea_a)
    hilo2 = threading.Thread(target=tarea_b)

    # 2. Iniciar la ejecución de los hilos
    hilo1.start()
    hilo2.start()

    # 3. El hilo principal espera a que ambos terminen
    hilo1.join()
    hilo2.join()

    print("¡Ambos hilos han terminado su ejecución!")