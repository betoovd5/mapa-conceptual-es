#CREAR UNA LISTA DE 5 COLORES NOMBRAR LA LISTA COMO COLORS
#1MOSTRAR TODA LA LISTA
#2MODIFICAR LA LISTA PARA QUE ESTA MISMA MUESTRE EL SEGUNDO ELEMENTO
#3CAMBIA EL PRIMER ELEMTO POR OTRO COLOR
#4ELIMINA LA TERCERA ENTRADA DE LA LISTA
#4AÑADE UN ELEMENTO MAS AL FINAL DE LA LISTA
#5AGREGA EL COLOR VIOLETA A LA POSICION 0

def mostrar_lista(lista, paso):
    print(f"\n--- {paso} ---")
    print(f"Lista actual: {lista}")

# 0. CREAR UNA LISTA DE 5 COLORES (Dinámica)
print("Ingresa 5 colores iniciales para tu lista:")
colors = []
for i in range(5):
    color = input(f"Color {i+1}: ")
    colors.append(color)

# 1. MOSTRAR TODA LA LISTA
mostrar_lista(colors, "1. MOSTRAR TODA LA LISTA")

# 2. MOSTRAR EL SEGUNDO ELEMENTO
# Nota: En Python los índices empiezan en 0, el segundo es [1]
print(f"\n--- 2. SEGUNDO ELEMENTO ---")
print(f"El segundo elemento es: {colors[1]}")

# 3. CAMBIA EL PRIMER ELEMENTO POR OTRO COLOR
nuevo_color = input("\nIngresa un nuevo color para sustituir al primero: ")
colors[0] = nuevo_color
mostrar_lista(colors, "3. PRIMER ELEMENTO CAMBIADO")

# 4. ELIMINA LA TERCERA ENTRADA DE LA LISTA
# El tercer elemento es el índice [2]
if len(colors) >= 3:
    eliminado = colors.pop(2)
    print(f"\nElemento eliminado: {eliminado}")
mostrar_lista(colors, "4. TERCERA ENTRADA ELIMINADA")

# 4. (Bis) AÑADE UN ELEMENTO MAS AL FINAL DE LA LISTA
extra_color = input("\nIngresa un color para añadir al final: ")
colors.append(extra_color)
mostrar_lista(colors, "4-BIS. ELEMENTO AÑADIDO AL FINAL")

# 5. AGREGA EL COLOR VIOLETA A LA POSICIÓN 0
colors.insert(0, "Violeta")
mostrar_lista(colors, "5. COLOR VIOLETA AGREGADO A LA POSICIÓN 0")

print("\n¡Proceso finalizado con éxito!")


