import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
from calcula_criterios_riesgos import *

class InterfazDecision:
    def __init__(self, root):
        self.root = root
        self.root.title("Calculadora de Criterios de Decisión :: Agustin Weisbek")

        self.resultados_labels = {}
        self.root.geometry("1100x800")
        self.root.minsize(900, 700)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        self.create_widgets()

    def create_widgets(self):
        # ======== FRAME SUPERIOR: Inputs =========
        top_frame = tk.Frame(self.root)
        top_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        for i in range(2):
            top_frame.columnconfigure(i, weight=1)

        campos = [
            ("Alternativas (filas):", 'alt_entry'),
            ("Estados (columnas):", 'est_entry'),
            ("Probabilidades (separadas por espacios):", 'prob_entry'),
            ("Nombres columnas:", 'cols_entry'),
            ("Nombres filas:", 'rows_entry'),
            ("Coef. Hurwicz (0-1):", 'omega_entry')
        ]

        for i, (label, attr) in enumerate(campos):
            tk.Label(top_frame, text=label).grid(row=i, column=0, sticky="w")
            setattr(self, attr, tk.Entry(top_frame))
            getattr(self, attr).grid(row=i, column=1, sticky="ew", padx=5, pady=2)

        tk.Label(top_frame, text="Valores (una fila por línea):").grid(row=len(campos), column=0, sticky="nw")
        self.vals_text = scrolledtext.ScrolledText(top_frame, height=4)
        self.vals_text.grid(row=len(campos), column=1, sticky="ew")

        tk.Button(top_frame, text="Calcular", command=self.calcular).grid(row=len(campos)+1, column=0, columnspan=2, pady=5)

        # ======== FRAME CENTRAL: Matriz cargada =========
        self.matriz_frame = tk.LabelFrame(self.root, text="Matriz Ingresada")
        self.matriz_frame.grid(row=1, column=0, sticky="nsew", padx=10)
        self.matriz_frame.rowconfigure(0, weight=1)
        self.matriz_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(self.matriz_frame, height=6)
        self.tree.grid(row=0, column=0, sticky="nsew")

        # ======== FRAME INFERIOR: Resultados y Matrices =========
        bottom_frame = tk.Frame(self.root)
        bottom_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=1)

        # Resultados a la izquierda
        self.result_frame = tk.LabelFrame(bottom_frame, text="Resultados (Riesgos e incertidumbres)", padx=10, pady=10)
        self.result_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.result_frame.columnconfigure(0, weight=1)
        for i in range(10):
            self.result_frame.rowconfigure(i, weight=1)

        self.crear_resultados_labels()

        # Matrices a la derecha (esperanza y arrepentimiento)
        self.matrices_frame = tk.Frame(bottom_frame)
        self.matrices_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.matrices_frame.columnconfigure(0, weight=1)
        self.matrices_frame.rowconfigure(0, weight=1)
        self.matrices_frame.rowconfigure(1, weight=1)

        self.tree_esperanza = None
        self.tree_arrep = None

    def crear_resultados_labels(self):
        etiquetas = [
            "Wald (Maximin)", "Optimista (Maximax)", "Hurwicz",
            "Savage", "Esperanza Matemática","--RIESGOS--", "BEIP", "VEIP"
        ]
        for i, nombre in enumerate(etiquetas):
            label = tk.Label(self.result_frame, text=f"{nombre}: ", anchor="w")
            label.grid(row=i, column=0, sticky="ew")
            self.resultados_labels[nombre] = label

    def mostrar_matriz_esperanza(self, esperanza_data):
        if self.tree_esperanza is not None:
            for item in self.tree_esperanza.get_children():
                self.tree_esperanza.delete(item)
        else:
            self.tree_esperanza = ttk.Treeview(self.matrices_frame, columns=["Alternativa", "E(B)"], show="headings", height=5)
            self.tree_esperanza.grid(row=0, column=0, sticky="nsew", pady=5)
            self.tree_esperanza.heading("Alternativa", text="Alternativa [E(B)]")
            self.tree_esperanza.heading("E(B)", text="Esperanza")

        for alt, val in esperanza_data:
            self.tree_esperanza.insert("", "end", values=(alt, val))

    def mostrar_matriz_arrepentimiento(self, matriz, filas, columnas):
        maximos = np.max(matriz, axis=0)
        matriz_arrep = maximos - matriz
        matriz_resultado = [[filas[i]] + list(np.round(matriz_arrep[i], 2)) for i in range(len(filas))]

        if self.tree_arrep is not None:
            for item in self.tree_arrep.get_children():
                self.tree_arrep.delete(item)
        else:
            self.tree_arrep = ttk.Treeview(self.matrices_frame, columns=["Alternativa"] + columnas, show="headings", height=5)
            self.tree_arrep.grid(row=1, column=0, sticky="nsew", pady=5)
            self.tree_arrep.heading("Alternativa", text="Alternativa [Matriz de Arrepentimiento]")
            for col in columnas:
                self.tree_arrep.heading(col, text=col)

        for fila in matriz_resultado:
            self.tree_arrep.insert("", "end", values=fila)

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

    def mostrar_resultados_integrados(self, matriz, omega, m, n, columnas, filas):
        matriz_sin_prob = matriz[1:]

        wald_val = criterio_wald(matriz_sin_prob)
        wald_alt = devolver_valor_accion(matriz_sin_prob, filas)

        optim_val = criterio_optimista(matriz_sin_prob)
        optim_alt = devolver_valor_accion_maximax(matriz_sin_prob, filas)

        hurwicz_val, hurwicz_alt = criterio_hurwicz(matriz_sin_prob, omega, filas)

        savage_val = criterio_savage(matriz_sin_prob)
        savage_alt = devolver_alternativa_arrepentimiento(matriz_sin_prob, columnas, filas, m)

        esperanza_matematica = []
        for i in range(m):
            sumatoria = sum(matriz[1 + i, j] * matriz[0, j] for j in range(n))
            esperanza_matematica.append((filas[i], round(sumatoria, 4)))

        max_esperanza = max(x[1] for x in esperanza_matematica)
        beip_val = calcular_BEIP(matriz, m, n)
        veip_val = beip_val - max_esperanza

        self.resultados_labels["Wald (Maximin)"].config(text=f"Wald (Maximin): {wald_alt} → {wald_val:.2f}")
        self.resultados_labels["Optimista (Maximax)"].config(text=f"Optimista (Maximax): {optim_alt} → {optim_val:.2f}")
        self.resultados_labels["Hurwicz"].config(text=f"Hurwicz (ω={omega}): {hurwicz_alt} → {hurwicz_val:.2f}")
        self.resultados_labels["Savage"].config(text=f"Savage: {savage_alt} → {savage_val:.2f}")
        self.resultados_labels["Esperanza Matemática"].config(text=f"E(B) = {max_esperanza:.2f}")
        self.resultados_labels["BEIP"].config(text=f"BEIP: {beip_val:.2f}")
        self.resultados_labels["VEIP"].config(text=f"VEIP: {veip_val:.2f}")

        self.mostrar_matriz_esperanza(esperanza_matematica)
        self.mostrar_matriz_arrepentimiento(matriz_sin_prob, filas, columnas)

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
