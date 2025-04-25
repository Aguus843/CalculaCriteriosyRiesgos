import numpy as np
from tabulate import tabulate
#axis = 0 rows
#axis = 1 columns
# numpy.min/max(matriz, AXIS = 1/0)
# numpy.argmax() devuelve la primera aparicion del maximo valor (indice)

def criterio_wald(matriz):
    # este criterio agarra los maximos de la matriz y se queda con el minimo de todos
    return np.max(np.min(matriz, 1))

def devolver_valor_accion(matriz, nombreFilas):
    # esta funcion devuelve el indice de la alternativa a tomar
    indice = np.argmax(np.min(matriz, 1))
    if nombreFilas is not None:
        return nombreFilas[indice]
    return indice

#Criterio Optimista (Lo contrario al Pesimista)
def criterio_optimista(matriz):
    #agarro los maximos de la matriz y me quedo con el maximo de todos
    return np.max(np.max(matriz, 1))

def devolver_valor_accion_maximax(matriz, nombreFilas):
    indice = np.argmax(np.max(matriz, 1))
    if nombreFilas is not None:
        return nombreFilas[indice]
    return indice

# para el criterio de Hurwicz tengo una funcion
# Hi = ωMAX + (1 - ω)MIN
# ω se establece arbitrariamente al cargar el archivo
def criterio_hurwicz(matriz, omega, nombreFilas):
    vectorHurwicz = []
    # Calculo los minimos y maximos
    minimo = np.min(matriz, 1)
    maximo = np.max(matriz, 1)
    funcion = (omega*maximo) + ((1-omega)*minimo)
    vectorHurwicz = funcion.tolist()
    
    
    # y de esa funcion saco el maximo
    return np.max(funcion), nombreFilas[np.argmax(vectorHurwicz)]

def devolver_alternativa_hurwicz(matriz, nombreFilas):
    indice = np.argmax(np.max(matriz, 1))
    
    if nombreFilas is not None:
        return nombreFilas[indice]
    return indice
    
def criterio_savage(matriz):
    # aca tengo que crear una matriz de arrepentimiento
    # Yo se que : 
    # Arrepentimiento: (max beneficio posible - beneficio obtenido por la acción tomada)
    # Busco el maximo beneficio posible
    
    maximo_beneficio_columna = np.max(matriz, 0) # 0 para que busque en las filas
    matriz_arrepentimiento = maximo_beneficio_columna - matriz
    
    # y elijo el minimo de los maximos
    maximos_columna = np.max(matriz_arrepentimiento, 1) # maximo arrepentimiento de todas las columnas.
    return np.min(maximos_columna) # saco el minimo de todas las columnas

def devolver_alternativa_arrepentimiento(matriz, nombreColumnas, nombreFilas, filas):
    maximo_beneficio_columna = np.max(matriz, 0) # 0 para que busque en las filas
    matriz_arrepentimiento = maximo_beneficio_columna - matriz
    maximos_columna = np.max(matriz_arrepentimiento, 1)
    maximos_columna = np.array(maximos_columna)
    MatrizFilas = cargar_nombres_filas_sin_probabilidades(matriz_arrepentimiento, nombreFilas, filas)
    #print(f"DEBUG : MINIMO DE ARGMAX = {np.argmin(np.min(matriz_arrepentimiento, 1))}")
    columnas = ["N1", "N2", "N3", "N4"]
    print("MATRIZ DE ARREPENTIMIENTO: ")
    print(tabulate(MatrizFilas, headers=["Alternativas"] + nombreColumnas, tablefmt="fancy_grid"))
    indice = np.argmin(maximos_columna)
    if nombreFilas is not None:
        return nombreFilas[indice]
    return indice
    # return np.argmin(maximos_columna) # busco el indice del MINIMO de las columnas de los maximos


#------------------ Funciones para calcular modelos con riesgos -------------------

def calcular_BEIP_Esperanza_Matematica(matriz, filas, columnas, nombreFilas, imprimirMatrizEsperanza):
    mascara = np.ones(len(matriz), dtype=bool) # Me saco la fila de probabilidades ya que sino se utiliza para calcular el valor buscado Y NO SE QUIERE ESO
    mascara[0] = False
    matriz_sin_probabilidades = matriz[mascara]
    
    # Hay que conocer las probabilidades asociadas a cada Ni
    # Usamos el "Maximo beneficio esperado" calculando la Esperanza Matematica
    # es la sumatoria (P(Xj) Bij)
    # Omega = MAX E(Bij)
    # Si se trabaja con arrepentimientos se calcula el MINIMO (Omega)
    # Las probabilidades se ubican SIEMPRE en la fila 0 de la matriz original.
    
    vector_de_esperanzas = []
    for i in range(filas):
        sumatoria = 0
        for j in range(columnas):
            sumatoria += matriz_sin_probabilidades[i,j] * matriz[0,j]
        # print(f'Fila {i+1} = {sumatoria}')
        vector_de_esperanzas.append(sumatoria)
        
    matriz_resultado = []
    if imprimirMatrizEsperanza:
        for i in range(filas):
            matriz_resultado.append([nombreFilas[i], round(vector_de_esperanzas[i], 4)])
        print(tabulate(matriz_resultado, headers=["Alternativa", "E(B)"], tablefmt="grid"))
    
    vector_de_esperanzas = np.array(vector_de_esperanzas)
    return np.max(vector_de_esperanzas, 0) # devuelvo el OMEGA MAYOR (Ω)
    
def calcular_BEIP(matriz, filas, columnas):
    mascara = np.ones(len(matriz), dtype=bool) # Me saco la fila de probabilidades ya que sino se utiliza para calcular el valor buscado Y NO SE QUIERE ESO
    mascara[0] = False
    matriz_sin_probabilidades = matriz[mascara]
    valor_BEIP = 0
    # El BEIP es la Sumatoria de las probabilidades P(Xj)*max Bij
    maximo_columna = np.max(matriz_sin_probabilidades, 0)
    maximo_columna = np.array(maximo_columna).tolist()
    for j in range(columnas):
        valor_BEIP += maximo_columna[j] * matriz[0][j]
    # print(f"DEBUG: {maximo_columna}")
    return valor_BEIP
    
    
def calcular_VEIP(matriz, filas, columnas, nombreFilas):
    # El VEIP es el Valor Esperado con la Informacion Perfecta
    # Por lo que, se puede calcular como BEIP - maxE(Bij) = VEIP
    # Como ya tenemos la funcion de la esperanza matematica entonces:
    esperanza_matematica_beneficio = calcular_BEIP_Esperanza_Matematica(matriz, filas, columnas, nombreFilas, False)
    valor_BEIP = calcular_BEIP(matriz, filas, columnas)
    
    return (valor_BEIP - esperanza_matematica_beneficio)

def mostrar_criterios(matriz, omega, filas, columnas, nombreColumnas, nombreFilas):
    mascara = np.ones(len(matriz), dtype=bool) # Me saco la fila de probabilidades ya que sino se utiliza para calcular el valor buscado Y NO SE QUIERE ESO
    mascara[0] = False
    matriz_sin_probabilidades = matriz[mascara] # paso a dicha variable la matriz sin probabilidades, luego se utiliza en modelos con riesgos
    print("==============================================\n")
    print("Criterio de Wald (MAXIMIN): ")
    valor = criterio_wald(matriz_sin_probabilidades)
    accion = devolver_valor_accion(matriz_sin_probabilidades, nombreFilas)
    print(f'Mejor alternativa: {accion} --> {valor}')
    
    print("Criterio Optimista (MAXIMAX): ")
    valor = criterio_optimista(matriz_sin_probabilidades)
    accion = devolver_valor_accion_maximax(matriz_sin_probabilidades, nombreFilas)
    print(f"Mejor alternativa: {accion} --> {valor}")
    
    print("Criterio de Hurwicz: ")
    valor, accion = criterio_hurwicz(matriz_sin_probabilidades, omega, nombreFilas)
    # accion = devolver_alternativa_hurwicz(matriz_sin_probabilidades, nombreFilas)
    print(f'Mejor alternativa: {accion} --> {valor}')
    
    print("Criterio de Savage: ")
    valor = criterio_savage(matriz_sin_probabilidades)
    accion = devolver_alternativa_arrepentimiento(matriz_sin_probabilidades, nombreColumnas, nombreFilas, filas)
    print(f'Mejor alternativa: {accion} --> {valor}')
    
    print("--------------------Riesgos---------------------\n")
    # print("BEIP: E(B)")
    print("Esperanza Matemática del Beneficio: ")
    valor = calcular_BEIP_Esperanza_Matematica(matriz, filas, columnas, nombreFilas, imprimirMatrizEsperanza=True)
    print(f'Ω = MAX E(B) : {valor}')
    print("Valor BEIP: ")
    valor = calcular_BEIP(matriz, filas, columnas)
    print(f"BEIP: {valor}")
    
    valor = calcular_VEIP(matriz, filas, columnas, nombreFilas)
    print(f"VEIP: {valor}\n")
    print("==============================================\n")
    # matriz_tabla = tabulate(guardar_nombresfilas(matriz), headers=["Alternativa"] + nombreColumnas, tablefmt="grid")
    return 0
    
def main():
    salir = ""
    while (salir != '0'):
        # Defino matriz n x m para cargar los datos
        m = int(input("Ingrese cantidad de alternativas (filas): "))
        n = int(input("Ingrese cantidad de estados de la naturaleza (columnas): "))
        matriz = []
        print("Ingrese las probabilidades asociadas a cada estado de naturaleza \n[!] Ingreselo como si fuese una lista, separado por espacios: ")

        probabilidades = list(map(float,input(f'Ingrese la probabilidad asociada para el estado de naturaleza Ni: ').split()))
        if len(probabilidades) != n:
                print(f"La cantidad de probabilidades ingresadas no es igual a las columnas disponibles, debe ser {n} columnas")
                return
        # if contador_probabilidades < 0 or contador_probabilidades > 1:
        #     print(f"[!] La suma de las probabilidades debe ser 1! => Pi = {contador_probabilidades}")
        #     return -1
        matriz.append(probabilidades)
        # print(f"DEBUG: LA SUMA DE LAS PROBABILIDADES ES {np.sum(matriz)}")
        if np.sum(matriz) != 1:
            print(f'La suma de las probabilidades debe ser 1. ({np.sum(matriz)})')
            return

        # Ingreso de nombres de columnas
        print("Ingrese el nombre de las columnas (Debe respetar la cantidad de columnas, separado por espacio)")
        nombreColumna = list(map(str,input("Ingrese los nombres de columnas: ").split()))
        if (len(nombreColumna) != n):
            print("Debe ingresar la cantidad de columnas ingresadas.")
            return

        # ingreso de nombres de filas
        print("Ingrese el nombre de las filas (Debe respetar la cantidad de filas, separado por espacio)")
        nombreFila = list((input("Ingrese los nombres de filas: ").split()))
        if (len(nombreFila) != m):
            print("Debe ingresar la cantidad de filas ingresadas.")
            return

        print("Ingrese los valores correspondientes a cada alternativa segun su estado de naturaleza:")
        nombresColumnas = []
        nombresColumnas.append(nombreColumna)
        for i in range(m):
            # hago un ciclo for de m veces (m filas) para cargar las respectivas filas segun la cantidad de columnas
            # el formato a utilizar es A1 = N1 N2 ... Nn (Escrito en consola)
            fila = list(map(float,input(f"Ingrese Alternativa A{i+1}: ").split()))
            # verifico que la cantidad de columnas ingresadas en el prompt sean correctas

            if len(fila) != n:
                print(f"La cantidad de columnas ingresadas no es correcta, debe ser {n} columnas")
                return
            matriz.append(fila) # agrego a la matriz creada la fila creada

        # creo mi coeficiente ω de optimismo
        ω = float(input("Ingrese el coeficiente de optimismo | ∃ω ∈ ℝ, ω ∈ [0,1]] : "))
        while (ω < 0 or ω > 1):
            print("ω está fuera del rango.")
            ω = float(input("Ingrese el coeficiente de optimismo | ∃ω ∈ ℝ, ω ∈ [0,1] : "))

        matriz = np.array(matriz) # crea un array (matriz)
        MatrizFilas = cargar_nombres_filas(matriz, nombreFila, m)
        nombresColumnas = nombreColumna
        # Mostrar tabla
        matriz_tabla = tabulate(MatrizFilas, headers=["Alternativa"] + nombresColumnas, tablefmt="grid")
        print(matriz_tabla)

        mostrar_criterios(matriz, ω, m, n, nombresColumnas, nombreFila)
        salir = input("Aprete Enter para continuar... (0 para salir): ")
    return 0

# ============================================================================================================

def cargar_nombres_filas(matriz, fila_nombres, filas):        
    # NOMBRES
    # nombresFilas = ['P(x)'] + fila_nombres  # concateno la probabilidad con los nombres
    MatrizFilas = []
    # Primera fila (probabilidades)
    MatrizFilas.append(['P(x)'] + list(matriz[0]))
    # Filas de alternativas
    for i in range(1, filas+1):
        MatrizFilas.append([fila_nombres[i-1]] + list(matriz[i]))
    return MatrizFilas


def cargar_nombres_filas_sin_probabilidades(matriz, fila_nombres, filas):        
    # NOMBRES
    # nombresFilas = ['P(x)'] + fila_nombres  # concateno la probabilidad con los nombres
    MatrizFilas = []
    # Filas de alternativas
    for i in range(filas):
        MatrizFilas.append([fila_nombres[i]] + list(matriz[i]))
    return MatrizFilas

if __name__ == "__main__":
    main()