import tkinter as tk
from tkinter import ttk, scrolledtext

def generate_recommendation():
    try:
        ram = float(ram_var.get())
        gpu_vram = float(gpu_var.get()) if gpu_var.get() else 0.0
        use_case = use_case_var.get()
    except ValueError:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "Error: Ingresa valores numéricos válidos para RAM y GPU VRAM.")
        return

    explanation = []
    model_size = "N/A"
    quantization = "N/A"
    num_ctx = "N/A"
    notes = []

    if gpu_vram >= 4.0:
        weight_mem_limit = gpu_vram
        explanation.append(f"Se detectó {gpu_vram}GB de VRAM GPU. Se priorizará carga en GPU (menos carga en RAM).")
    else:
        weight_mem_limit = ram
        explanation.append(f"Se usará {ram}GB de RAM para pesos del modelo (GPU no detectada o insuficiente: {gpu_vram}GB VRAM).")

    quant_factors = {
        "Q8_0": 1.0,
        "Q6_K": 0.75, 
        "Q5_K_S": 0.625,
        "Q5_K_M": 0.625,
        "Q4_K_M": 0.5,
        "Q3_K_S": 0.375,
        "Q3_K_M": 0.375,
        "Q2_K": 0.25
    }
    
    model_sizes = [3, 4, 7, 8, 13]
    
    best_fit = None
    for size in reversed(model_sizes):
        for quant_name, factor in quant_factors.items():
            mem_needed = size * factor
            if mem_needed <= weight_mem_limit:
                best_fit = (size, quant_name, mem_needed)
                break
        if best_fit:
            break
    
    if not best_fit:
        model_size = "3B"
        quantization = "Q2_K"
        num_ctx = "1024"
        explanation.append("Recursos muy limitados: se recomienda el modelo más pequeño posible.")
        notes.append("Advertencia: La calidad será baja debido a cuantización agresiva.")
    else:
        size, quant_name, mem_used = best_fit
        model_size = f"{size}B"
        quantization = quant_name
        
        if use_case == "Coding":
            explanation.append("Para tareas de código, se priorizan modelos especializados (ej: deepseek-coder-v2, codellama).")
            notes.append("Si el modelo recomendado no es específico para código, busca variantes como *-code* o *-instruct* en Ollama.")
        elif use_case == "Math":
            explanation.append("Para razonamiento matemático, modelos como deepseek-math suelen ser más eficaces.")
        elif use_case == "Creative Writing":
            explanation.append("Para escritura creativa, modelos como mistral o llamma3 ofrecen buen equilibrio.")
        
        base_ctx = 4096
        if ram >= 16 or gpu_vram >= 8:
            suggested_ctx = 8192
            if ram >= 32 or gpu_vram >= 16:
                suggested_ctx = 16384
            num_ctx = str(suggested_ctx)
            explanation.append(f"Con {ram}GB RAM/{gpu_vram}GB VRAM, se sugiere contexto de {num_ctx} tokens para documentos largos o conversaciones extensas.")
        else:
            num_ctx = str(base_ctx)
            explanation.append(f"Para evitar sobrecarga de RAM, se mantiene contexto estándar de {num_ctx} tokens.")
            if mem_used > weight_mem_limit * 0.9:
                notes.append("Advertencia: El modelo consume casi toda la memoria disponible. Reduce num_ctx si notas lentitud.")
        
        explanation.append(f"Memoria estimada para pesos: {mem_used:.2f}GB (límite: {weight_mem_limit:.2f}GB).")

    result = f"""
=== RECOMENDACIÓN DE CONFIGURACIÓN OLLAMA ===

Recursos del sistema:
- RAM total: {ram} GB
- GPU VRAM: {gpu_vram} GB ({"Detectada" if gpu_vram > 0 else "No detectada o no utilizada"})
- Caso de uso: {use_case}

Configuración recomendada:
- Tamaño de modelo: {model_size} parám.
- Nivel de cuantización: {quantization}
- Longitud de contexto (num_ctx): {num_ctx} tokens

Explicación:
{chr(10).join("- " + line for line in explanation)}

{"Notas importantes:" if notes else ""}
{chr(10).join("- " + note for note in notes)}

Próximos pasos:
1. Descarga el modelo en Ollama: 
   ollama pull <nombre-modelo>:<size>b-instruct-<quant>
   Ejemplo: ollama pull llama3:8b-instruct-q4_K_M
2. Ejecuta con:
   ollama run <nombre-modelo>:<size>b-instruct-<quant> --num-ctx {num_ctx}
3. Monitorea uso de recursos con: ollama ps (o administrador de tareas)
"""
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, result)

root = tk.Tk()
root.title("Asistente de Configuración Ollama")
root.geometry("650x500")
root.resizable(False, False)

main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

ttk.Label(main_frame, text="RAM del sistema (GB):", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
ram_var = tk.StringVar(value="8")
ttk.Entry(main_frame, textvariable=ram_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=2)

ttk.Label(main_frame, text="GPU VRAM (GB, opcional):", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=2)
gpu_var = tk.StringVar(value="0")
ttk.Entry(main_frame, textvariable=gpu_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=2)

ttk.Label(main_frame, text="Caso de uso principal:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=2)
use_case_var = tk.StringVar(value="General")
use_case_options = ["General", "Coding", "Math", "Creative Writing"]
ttk.Combobox(main_frame, textvariable=use_case_var, values=use_case_options, state="readonly", width=15).grid(row=2, column=1, sticky=tk.W, pady=2)

ttk.Button(main_frame, text="Generar Recomendación", command=generate_recommendation).grid(row=3, column=0, columnspan=2, pady=15)

result_text = scrolledtext.ScrolledText(main_frame, width=70, height=20, wrap=tk.WORD, font=("Consolas", 9))
result_text.grid(row=4, column=0, columnspan=2, pady=10, padx=5, sticky=tk.N+tk.S+tk.E+tk.W)

main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(4, weight=1)

result_text.insert(tk.END, "Ingresa tus especificaciones de sistema y haz clic en 'Generar Recomendación' para obtener configuraciones óptimas de Ollama.\n\n"
                         "Esta herramienta sugiere tamaños de modelo, niveles de cuantización y longitudes de contexto basadas en:\n"
                         "- Memoria disponible para pesos del modelo (RAM o VRAM GPU)\n"
                         "- Trade-off entre calidad y consumo de recursos\n"
                         "- Ajustes específicos según el caso de uso (programación, matemáticas, etc.)\n\n"
                         "Nota: Las recomendaciones son heurísticas basadas en pruebas típicas. Siempre monitorea el rendimiento real en tu equipo.")

root.mainloop()
