# Cerebro Híbrido 🧠

Generador de lenguaje natural que imita la forma en que las palabras se asocian en la mente: aprende con refuerzo hebbiano, recuerda en qué posición suele aparecer cada palabra y planifica las frases usando **puentes conceptuales**.

No es un clon de GPT: es **ligero, interpretable y se entrena con pocos ejemplos**. Pensado para funcionar en dispositivos pequeños, experimentos de IA creativa y asistentes sin conexión.

---

## ✨ Características

- 🔁 **Aprendizaje Hebbiano (COM2):** refuerza las conexiones entre palabras de pregunta y respuesta, y olvida las que dejan de aparecer.
- 📍 **Conciencia posicional:** cada palabra del "alma" recuerda en qué lugar de la frase suele aparecer (inicio, mitad, final).
- 🌉 **Puentes conceptuales:** detecta palabras que conectan varios conceptos de la pregunta y las convierte en obligatorias en la respuesta.
- 🧩 **Planificador híbrido (PRE2):** usa bigramas/trigramas para unir las palabras obligatorias con fluidez, sin necesidad de un modelo masivo.
- 🗂️ **Umbral de generalización:** separa automáticamente palabras funcionales (artículos, conectores) de palabras de contenido.
- 💬 **Respuesta en tiempo real:** desde terminal, sin GPU, sin Internet.

---

## 🚀 Cómo funciona (en 3 pasos)

1. **Asociación:** cuando entrenas con pares `pregunta → respuesta`, las palabras de la pregunta fortalecen sus lazos con las palabras de la respuesta.
2. **Selección:** ante una nueva pregunta, el sistema extrae las palabras del alma más activadas y las clasifica en **núcleos**, **puentes** y **opcionales**.
3. **Construcción:** un planificador coloca primero los puentes (lo obligatorio), los une con un modelo de bigramas y añade las palabras opcionales en el orden natural que aprendieron.

---

## 📦 Requisitos

Solo necesitas Python 3.7 o superior. No hay dependencias externas (solo `json`, `os`, `re`, `math`, `random`, `collections`, `urllib`, `sys`, todas estándar).
