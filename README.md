# IA-Dotations-ES
Dotacion de IA y recomendaciones de uso para su maximo provecho utilizando distintos modelos, testeando distintas metodologías para un mejor resultado y lo más importante optimo y especifico a el problema u objetivo raiz.


# Modulos
Las recomendaciones y utilidades para mejorar el uso de la IA sigue la estructura dividida dependiendo sus necesidades, se encuentran divididas de la siguiente manera:
* recommended/ -> Software para poder configurar adecuadamente motores y IDE de IAs
* doc/ -> Se encuentra la documentación oficial desde 0 hasta avanzado respecto a como interactuan los motores LLM y como puedes llegar a crear tu propia IA desde 0.
* sessions/agents -> Son sesiones de ejemplo que automatizan agentes
* sessions/skills -> Son sesiones de ejemplo de distintos escenarios con distintas habilidades como coding, math, etc.
* installers/ Son scripts automatizados para instalar distintos motores u IAs LLM files para un acceso rapido a la instalacio de herramientas
* google-addons/ -> sección de información respecto a como funciona la IA en android y como aplicarla adecuadamente.
* apple-addons/ -> sección de información respecto a como funciona actualmente la IA en iOS , ya se escritorio(MAC) o iphone.

  ## Modulo Ollama Recommended
  Asistente de Configuración Ollama
Herramienta visual en Python que recomienda configuraciones óptimas para Ollama (tamaño de modelo, cuantización y contexto) basándose en los recursos de tu sistema (RAM, GPU VRAM) y el caso de uso.
¿Qué hace?
- Analiza tu hardware (RAM total, VRAM GPU opcional)
- Sugiere el mejor tamaño de modelo (3B, 4B, 7B, 8B, 13B) y nivel de cuantización (Q2_K a Q8_0) para maximizar la calidad sin exceder los límites de memoria
- Recomienda una longitud de contexto (num_ctx) adecuada
- Explica el razonamiento técnico detrás de cada recomendación
- Incluye comandos listos para usar en Ollama
Requisitos
- Python 3.6 o superior
- Tkinter (incluido con Python por defecto en Windows, Linux y macOS)
Cómo usar
1. Ejecuta el script:
python OllamaRecommender.py
2. Ingresa:
- RAM del sistema (GB): Memoria física disponible (ej: 8, 16)
- GPU VRAM (GB, opcional): Si tienes GPU dedicada (ej: 6, 8, 12); usa 0 si no
- Caso de uso principal: General, Coding, Math o Creative Writing
3. Haz clic en "Generar Recomendación"
4. Revisa la configuración sugerida y las explicaciones
Ejemplo de salida
=== RECOMENDACIÓN DE CONFIGURACIÓN OLLAMA ===

Recursos del sistema:
- RAM total: 8 GB
- GPU VRAM: 0 GB (No detectada o no utilizada)
- Caso de uso: General

Configuración recomendada:
- Tamaño de modelo: 7B parám.
- Nivel de cuantización: Q4_K_M
- Longitud de contexto (num_ctx): 4096 tokens

Explicación:
- Se usará 8GB de RAM para pesos del modelo (GPU no detectada o insuficiente: 0GB VRAM).
- Memoria estimada para pesos: 3.50GB (límite: 8.00GB).
- Para evitar sobrecarga de RAM, se mantiene contexto estándar de 4096 tokens.

Notas importantes:
- Advertencia: El modelo consume casi toda la memoria disponible. Reduce num_ctx si notas lentitud.

Próximos pasos:
1. Descarga el modelo en Ollama: 
   ollama pull <nombre-modelo>:<size>b-instruct-<quant>
   Ejemplo: ollama pull llama3:8b-instruct-q4_K_M
2. Ejecuta con:
   ollama run <nombre-modelo>:<size>b-instruct-<quant> --num-ctx 4096
3. Monitorea uso de recursos con: ollama ps
Cómo interpretar las recomendaciones
- Cuantización: Q4_K_M es un equilibrio típico entre calidad y consumo. Modelos más pequeños o cuantizaciones más agresivas (Q3_K_S, Q2_K) reducen uso de RAM pero pueden afectar la calidad.
- Contexto: Un num_ctx más alto permite procesar documentos más largos, pero consume más memoria. Si el sistema se vuelve lento, reduce este valor.
- Casos de uso: Para programación, se priorizan modelos especializados como DeepSeek-Coder. Para matemáticas, DeepSeek-Math. Para escritura creativa, modelos generales como Mistral suelen funcionar bien.
Personalización
Las reglas de recomendación están en la función generate_recommendation(). Puedes ajustar:
- quant_factors: Factores de memoria por cada tipo de cuantización
- model_sizes: Tamaños de modelo a considerar
- Lógica de selección de contexto
Notas
- Las recomendaciones son heurísticas basadas en pruebas típicas. Siempre monitorea el rendimiento real en tu equipo.
- Si experimentas lentitud o uso excesivo de memoria, reduce el num_ctx o prueba con una cuantización más agresiva.
- Para sistemas con pocos recursos (<8GB RAM), se sugiere un modelo de 3B-4B con cuantización Q3_K_S o menor.
