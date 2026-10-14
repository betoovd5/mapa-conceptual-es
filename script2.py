class Person:
    def __init__(self, name: str, nss: str, country: str, email: str):
        self.name = name
        self.nss = nss
        self.country = country
        self.email = email

    def __str__(self):
        return f"Nombre: {self.name} | Email: {self.email}"


class Client(Person):
    def __init__(self, name: str, nss: str, country: str, email: str, client_id: int):
        super().__init__(name, nss, country, email)
        self.client_id = client_id

    def __str__(self):
        return super().__str__() + f" | [ID Cliente: {self.client_id}]"


class Employee(Person):
    def __init__(self, name: str, nss: str, country: str, email: str, salary: float, employee_id: int):
        super().__init__(name, nss, country, email)
        self.salary = salary
        self.employee_id = employee_id

    def __str__(self):
        return super().__str__() + f" | [ID Empleado: {self.employee_id}] | Salario: ${self.salary:.2f}"


class Intern(Employee):  # Nueva clase: Hereda de Employee
    def __init__(self, name: str, nss: str, country: str, email: str, salary: float, employee_id: int, university: str):
        super().__init__(name, nss, country, email, salary, employee_id)
        self.university = university

    def __str__(self):
        return super().__str__() + f" | Universidad: {self.university}"


class Manager(Employee):
    def __init__(self, name: str, nss: str, country: str, email: str, salary: float, employee_id: int, budget: float):
        super().__init__(name, nss, country, email, salary, employee_id)
        self.budget = budget

    def __str__(self):
        return super().__str__() + f" | Presupuesto: ${self.budget:.2f}"


class Director(Manager):  # Nueva clase: Hereda de Manager
    def __init__(self, name: str, nss: str, country: str, email: str, salary: float, employee_id: int, budget: float, department: str):
        super().__init__(name, nss, country, email, salary, employee_id, budget)
        self.department = department

    def __str__(self):
        return super().__str__() + f" | Departamento: {self.department}"


def mostrar_herencia(obj):
    # mro() muestra el orden de resolución de métodos (la jerarquía)
    clases = [c.__name__ for c in type(obj).mro()[:-1]] # Quitamos 'object' para limpiar la vista
    print(f"   Jerarquía: {' -> '.join(clases)}")

# --- EJECUCIÓN ESTÁTICA ---
if __name__ == "__main__":
    print("=== REPORTE DE JERARQUÍA DE CLASES (ESTÁTICO) ===\n")

    # Creación de los objetos (Estatico)
    cliente = Client("Carlos Slim", "CS-999", "México", "carlos@telecom.com", 1001)
    becario = Intern("Juan Novato", "BE-123", "México", "juan@uni.edu", 800.0, 5001, "UNAM")
    empleado = Employee("Laura Soler", "LS-456", "España", "laura@empresa.com", 2500.0, 201)
    gerente = Manager("Pedro Páramo", "PP-789", "México", "pedro@empresa.com", 5000.0, 101, 20000.0)
    director = Director("Dra. Elena Poniatowska", "EP-001", "Francia", "elena@corp.com", 12000.0, 1, 100000.0, "Operaciones Globales")

    lista_objetos = [cliente, becario, empleado, gerente, director]

    for o in lista_objetos:
        print(f"DATOS: {o}")
        mostrar_herencia(o)
        print("-" * 60)