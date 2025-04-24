import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
from calcula_criterios_riesgos import *

class InterfazDecision:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Criterios de Decision - Agustin Weisbek")

        self.resultados_labels = {}
        self.create_widgets()
        # Hacer que la ventana sea más grande
        # self.root.geometry("770x1000")
        self.root.geometry("1100x890")

        # Hacer que las columnas sean expandibles
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=2)

        # Hacer la fila del Treeview expandible
        self.root.grid_rowconfigure(10, weight=1)

    def create_widgets(self):
        row = 0
        campos = [
            ("Alternativas (filas):", 'alt_entry'),
            ("Estados (columnas):", 'est_entry'),
            ("Probabilidades (Una por columna, separada por espacios):", 'prob_entry'),
            ("Nombres columnas:", 'cols_entry'),
            ("Nombres filas:", 'rows_entry'),
            ("Coef. Hurwicz (0-1):", 'omega_entry')
        ]

        for label, attr in campos:
            tk.Label(self.root, text=label).grid(row=row, column=0, sticky="w")
            setattr(self, attr, tk.Entry(self.root))
            getattr(self, attr).grid(row=row, column=1)
            row += 1

        tk.Label(self.root, text="Valores (una fila por línea):").grid(row=row, column=0, sticky="nw")
        self.vals_text = scrolledtext.ScrolledText(self.root, height=5, width=30)
        self.vals_text.grid(row=row, column=1)
        row += 1

        tk.Button(self.root, text="Calcular", command=self.calcular).grid(row=row, column=0, columnspan=2)
        row += 1

        tk.Label(self.root, text="Matriz ingresada:").grid(row=row, column=0, columnspan=2, pady=(10, 0))
        row += 1
        # Matriz principal
        self.tree = ttk.Treeview(self.root)
        self.tree.grid(row=row, column=0, columnspan=2, sticky="nsew")
        row += 1

        self.result_frame = tk.LabelFrame(self.root, text="Resultados", padx=10, pady=10)
        self.result_frame.grid(row=row, column=0, columnspan=2, pady=10, sticky="ew")
        self.crear_resultados_labels()

    def crear_resultados_labels(self):
        etiquetas = [
            "Wald (Maximin)", "Optimista (Maximax)", "Hurwicz",
            "Savage", "Esperanza Matemática", "BEIP", "VEIP"
        ]
        for i, nombre in enumerate(etiquetas):
            label = tk.Label(self.result_frame, text=f"{nombre}: ", anchor="w", width=50)
            label.grid(row=i, column=0, sticky="w")
            self.resultados_labels[nombre] = label
        
    
    def obtener_matriz_arrepentimiento(self, matriz, columnas, filas, m):
        max_beneficio = np.max(matriz, axis=0)
        matriz_arrepentimiento = max_beneficio - matriz
        matriz_resultado = []
        for i in range(m):
            matriz_resultado.append([filas[i]] + list(np.round(matriz_arrepentimiento[i], 2)))
        return matriz_resultado

    def mostrar_matriz_arrepentimiento(self, matriz_arrep, columnas):
        if hasattr(self, "tree_arrep"):
            for item in self.tree_arrep.get_children():
                self.tree_arrep.delete(item)
        else:
            self.tree_arrep = ttk.Treeview(self.root, columns=["Alternativa [Matriz de Arrepentimiento]"] + columnas, show="headings", height=5)
            # self.tree_arrep.grid(row=self.result_frame.grid_info()["row"] + 2, column=0, columnspan=2, pady=(5, 10), sticky="nsew")
            self.tree_arrep.grid(row=20, column=1, sticky="nsew", padx=(5, 10), pady=(5, 10))
            self.tree_arrep.heading("Alternativa [Matriz de Arrepentimiento]", text="Alternativa [Matriz de Arrepentimiento]")
            for col in columnas:
                self.tree_arrep.heading(col, text=col)

        for fila in matriz_arrep:
            self.tree_arrep.insert("", "end", values=fila)


    def mostrar_resultados_integrados(self, matriz, omega, m, n, columnas, filas):
        matriz_sin_prob = matriz[1:]

        # Criterios sin riesgo
        wald_val = criterio_wald(matriz_sin_prob)
        wald_alt = devolver_valor_accion(matriz_sin_prob, filas)

        optim_val = criterio_optimista(matriz_sin_prob)
        optim_alt = devolver_valor_accion_maximax(matriz_sin_prob, filas)

        hurwicz_val = criterio_hurwicz(matriz_sin_prob, omega)
        hurwicz_alt = devolver_alternativa_hurwicz(matriz_sin_prob, filas)

        savage_val = criterio_savage(matriz_sin_prob)
        savage_alt = devolver_alternativa_arrepentimiento(matriz_sin_prob, columnas, filas, m)

        # Criterios con riesgo
        # Obtener y guardar la esperanza matemática por alternativa
        esperanza_matematica = []
        for i in range(m):
            sumatoria = sum(matriz[1 + i, j] * matriz[0, j] for j in range(n))
            esperanza_matematica.append((filas[i], round(sumatoria, 4)))

        max_esperanza = max(x[1] for x in esperanza_matematica)
        beip_val = calcular_BEIP(matriz, m, n)
        veip_val = beip_val - max_esperanza

        # Mostrar criterios en etiquetas
        self.resultados_labels["Wald (Maximin)"].config(text=f"Wald (Maximin): {wald_alt} → {wald_val:.2f}")
        self.resultados_labels["Optimista (Maximax)"].config(text=f"Optimista (Maximax): {optim_alt} → {optim_val:.2f}")
        self.resultados_labels["Hurwicz"].config(text=f"Hurwicz (ω={omega}): {hurwicz_alt} → {hurwicz_val:.2f}")
        self.resultados_labels["Savage"].config(text=f"Savage: {savage_alt} → {savage_val:.2f}")
        self.resultados_labels["Esperanza Matemática"].config(text=f"E(B) = {max_esperanza:.2f}")
        self.resultados_labels["BEIP"].config(text=f"BEIP: {beip_val:.2f}")
        self.resultados_labels["VEIP"].config(text=f"VEIP: {veip_val:.2f}")

        self.mostrar_matriz_esperanza(esperanza_matematica)
        matriz_arrep = self.obtener_matriz_arrepentimiento(matriz_sin_prob, columnas, filas, m)
        self.mostrar_matriz_arrepentimiento(matriz_arrep, columnas)

        
    def mostrar_matriz_esperanza(self, esperanza_data):
        if hasattr(self, "tree_esperanza"):
            for item in self.tree_esperanza.get_children():
                self.tree_esperanza.delete(item)
        else:
            self.tree_esperanza = ttk.Treeview(self.root, columns=["Alternativa [E(B)]", "E(B)"], show="headings", height=5)
            # self.tree_esperanza.grid(row=self.result_frame.grid_info()["row"] + 1, column=0, columnspan=2, pady=(5, 10))
            self.tree_esperanza.grid(row=20, column=0, sticky="nsew", padx=(10, 5), pady=(5, 10))
            self.tree_esperanza.heading("Alternativa [E(B)]", text="Alternativa [E(B)]")
            self.tree_esperanza.heading("E(B)", text="Esperanza")

        for alt, val in esperanza_data:
            self.tree_esperanza.insert("", "end", values=(alt, val))

    def mostrar_matriz(self, matriz, filas, columnas, m):
        for item in self.tree.get_children():
            self.tree.delete(item)

        headers = ["Alternativa"] + columnas
        self.tree["columns"] = headers
        self.tree["show"] = "headings"
        for col in headers:
            self.tree.heading(col, text=col)

        self.tree.insert("", "end", values=["P(x)"] + list(matriz[0]))
        for i in range(1, m + 1):
            self.tree.insert("", "end", values=[filas[i - 1]] + list(matriz[i]))

    def calcular(self):
        try:
            m = int(self.alt_entry.get())
            n = int(self.est_entry.get())
            probabilidades = list(map(float, self.prob_entry.get().split()))
            if len(probabilidades) != n or not np.isclose(sum(probabilidades), 1.0):
                raise ValueError("Las probabilidades deben sumar 1 y coincidir con las columnas.")

            nombreColumnas = self.cols_entry.get().split()
            nombreFilas = self.rows_entry.get().split()
            if len(nombreColumnas) != n or len(nombreFilas) != m:
                raise ValueError("Cantidad de nombres incorrecta.")

            valores = self.vals_text.get("1.0", tk.END).strip().split("\n")
            matriz = [probabilidades]
            for i in range(m):
                fila = list(map(float, valores[i].split()))
                if len(fila) != n:
                    raise ValueError(f"La fila {i+1} no tiene {n} valores.")
                matriz.append(fila)

            omega = float(self.omega_entry.get())
            if not (0 <= omega <= 1):
                raise ValueError("ω debe estar entre 0 y 1.")

            matriz_np = np.array(matriz)
            self.mostrar_matriz(matriz_np, nombreFilas, nombreColumnas, m)
            self.mostrar_resultados_integrados(matriz_np, omega, m, n, nombreColumnas, nombreFilas)

        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazDecision(root)
    root.mainloop()