# Modelos, Simulación y Teoría de la Decisión

> [!IMPORTANT]
> **DATOS DEL ALUMNO**  
> Nombre y Apellido: Agustín Weisbek  
> Legajo: 190179

> [!NOTE]
> Si quiere armar un archivo .exe, debe instalar 'pyinstaller' con el siguiente comando:
> ```bash
>  pip install pyinstaller
>  pyinstaller --onefile {path/to/file/}  
> ```
> Debe compilarse el archivo 'interfazGrafica.py' !! 

## Funcionamiento

Para correr el programa hay que cargar primero una matriz **m x n**.

```bash
  Ingrese cantidad de alternativas (filas):
  Ingrese cantidad de estados de la naturaleza (columnas):
```
Luego, se indican las probabilidades a cada estado de la naturaleza (la suma de ellas debe ser 1):  

```bash
  Ingrese la probabilidad asociada para el estado de naturaleza Ni (separado por espacios):
```

A continuación se escriben los nombres tanto para las filas como para las columnas (separado por espacios).
```bash
  Ingrese los nombres de columnas: 
  Ingrese los nombres de filas:
```

Por último, se escriben las alternativas para cada estado de naturaleza (cada alternativa corresponde a una fila).
```bash
  Ingrese Alternativa An: 
```

