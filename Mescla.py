# Copyright (c) 2025 José Miguel Vargas Alvarez
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import json
import os
import re
import math
import random
import collections
import urllib.request
import urllib.error
import sys

=====================================================================
COM2 (Hebbiano, fuerza configurable, generales a partir del 4%)
=====================================================================
class CerebroPosicionalAlma:
def init(self):
self.pesos = {}
self.info_posicion = {}
self.vocabulario_q = set()
self.coocurrencias_q = {}
self.umbral_general = 0.04 # 4%
self.fuerza_minima = 2.0 # fuerza mínima configurable
self._cache_generales = None

def limpiar_texto(self, text):
return re.sub(r'[.,/#!$%^&*;:{}=-_`~()?¿¡]', '', str(text).lower()).split()

def entrenar_con_dataset(self, dataset_json):
for par in dataset_json:
palabras_q = self.limpiar_texto(par["user"])
palabras_a = self.limpiar_texto(par["alma"])
longitud_a = len(palabras_a)
if longitud_a == 0: continue

for pq in palabras_q:
self.vocabulario_q.add(pq)

for idx, pa in enumerate(palabras_a):
if pa not in self.info_posicion:
self.info_posicion[pa] = {
"total": 0,
"suma_pos_relativa": 0.0,
"veces_inicio": 0,
"veces_final": 0
}
self.info_posicion[pa]["total"] += 1
pos_relativa = idx / (longitud_a - 1) if longitud_a > 1 else 0.0
self.info_posicion[pa]["suma_pos_relativa"] += pos_relativa
if idx == 0:
self.info_posicion[pa]["veces_inicio"] += 1
if idx == longitud_a - 1:
self.info_posicion[pa]["veces_final"] += 1

for pq in palabras_q:
if pq not in self.pesos:
self.pesos[pq] = {}
for pa in palabras_a:
if pa not in self.pesos[pq]:
self.pesos[pq][pa] = 0.0
self.pesos[pq][pa] += 2.0
palabras_viejas = list(self.pesos[pq].keys())
for pv in palabras_viejas:
if pv not in palabras_a:
self.pesos[pq][pv] -= 1.0

self._recalcular_coocurrencias()
self._cache_generales = None

def _recalcular_coocurrencias(self):
self.coocurrencias_q = {}
for pa in self.info_posicion:
self.coocurrencias_q[pa] = set()
for pq, dict_pa in self.pesos.items():
for pa, puntaje in dict_pa.items():
if puntaje >= self.fuerza_minima:
self.coocurrencias_q[pa].add(pq)

def _obtener_palabras_generales(self):
if self._cache_generales is not None:
return self._cache_generales
total_preguntas = len(self.vocabulario_q)
if total_preguntas == 0:
self._cache_generales = set()
return self._cache_generales
generales = set()
for pa, preguntas_asociadas in self.coocurrencias_q.items():
if len(preguntas_asociadas) / total_preguntas >= self.umbral_general:
generales.add(pa)
self._cache_generales = generales
return generales

def set_umbral(self, porcentaje):
if 0.0 <= porcentaje <= 1.0:
self.umbral_general = porcentaje
self._cache_generales = None
print(f"✅ Umbral de generalización actualizado a {porcentaje*100:.0f}%")
else:
print("❌ El porcentaje debe estar entre 0 y 1 (ej: 0.04 para 4%).")

def set_fuerza_minima(self, valor):
if valor >= 0:
self.fuerza_minima = valor
self._recalcular_coocurrencias()
self._cache_generales = None
print(f"✅ Fuerza mínima actualizada a {valor} (palabras con fuerza < {valor} serán ignoradas)")
else:
print("❌ La fuerza mínima debe ser >= 0.")

def generales(self):
return self._obtener_palabras_generales()

def posicion_promedio(self, palabra):
info = self.info_posicion.get(palabra)
if not info: return 0.5
return info["suma_pos_relativa"] / info["total"]

def fuerza_con_pregunta(self, palabra_q, palabra_a):
return self.pesos.get(palabra_q, {}).get(palabra_a, 0.0)

def palabras_activadas_por(self, palabra):
if palabra not in self.pesos:
return set()
generales = self.generales()
return {pa for pa, score in self.pesos[palabra].items()
if score >= self.fuerza_minima and pa not in generales}

def obtener_ruta_com2(self, tokens_pregunta, top=6):
generales = self.generales()
acum = collections.Counter()
for p in tokens_pregunta:
if p not in self.pesos: continue
for a, score in self.pesos[p].items():
if score >= self.fuerza_minima and a not in generales:
acum[a] += score
if not acum:
return []
candidatas = [a for a, _ in acum.most_common(top*2)]
candidatas.sort(key=lambda a: self.posicion_promedio(a))
return candidatas[:top]

def mostrar_conexiones(self, palabra_q, solo_contenido=True):
palabra_q = palabra_q.lower().strip()
if palabra_q not in self.pesos:
print(f"La palabra '{palabra_q}' no está en el vocabulario de pregunta.")
return
generales = self.generales()
conexiones = []
for pa, fuerza in self.pesos[palabra_q].items():
if fuerza >= self.fuerza_minima:
if solo_contenido and pa in generales:
continue
pos = self.posicion_promedio(pa)
es_general = pa in generales
conexiones.append((pa, fuerza, pos, es_general))
if not conexiones:
print(f"No hay conexiones (de contenido) con fuerza >= {self.fuerza_minima} para '{palabra_q}'.")
return
conexiones.sort(key=lambda x: x[1], reverse=True)
tipo = " (solo contenido)" if solo_contenido else " (incluyendo generales)"
print(f"\nConexiones de '{palabra_q}'{tipo} [umbral general {self.umbral_general*100:.0f}%, fuerza mínima {self.fuerza_minima}]:")
print(f"{'Palabra Alma':<16} | {'Fuerza':<8} | {'Posición':<10} | {'General':<8}")
print("-" * 55)
for pa, fuerza, pos, gen in conexiones:
marca = "Sí" if gen else "No"
print(f" {pa:<15} | {fuerza:<8.1f} | {pos:.2f} ({int(pos*100):>2}%) | {marca}")

def mostrar_todas_palabras(self):
total_preguntas = len(self.vocabulario_q)
if total_preguntas == 0:
print("No hay palabras de pregunta registradas.")
return
print(f"\n=== TODAS LAS PALABRAS DEL ALMA (total preguntas únicas: {total_preguntas}) ===")
print(f"{'Palabra':<16} | {'% Preguntas':<12} | {'Fuerza media':<12} | {'Posición':<10} | {'Ubicación'}")
print("-" * 75)
for pa in sorted(self.coocurrencias_q.keys()):
info = self.info_posicion[pa]
pos_prom = info["suma_pos_relativa"] / info["total"]
porcentaje = len(self.coocurrencias_q[pa]) / total_preguntas * 100
fuerza_media = sum(self.pesos[pq].get(pa,0) for pq in self.coocurrencias_q[pa]) / len(self.coocurrencias_q[pa])
if info["veces_inicio"] > info["total"] * 0.5:
etiqueta = "Inicio Fijo"
elif info["veces_final"] > info["total"] * 0.5:
etiqueta = "Final Fijo"
elif pos_prom < 0.35:
etiqueta = "Zona Temprana"
elif pos_prom > 0.65:
etiqueta = "Zona Tardía"
else:
etiqueta = "Intermedio"
print(f" {pa:<15} | {porcentaje:>5.1f}% | {fuerza_media:>8.1f} | {pos_prom:.2f} ({int(pos_prom*100):>2}%) | {etiqueta}")
print()

def mostrar_palabra(self, palabra):
total_preguntas = len(self.vocabulario_q)
if total_preguntas == 0:
print("No hay palabras de pregunta registradas.")
return
if palabra not in self.coocurrencias_q:
print(f"La palabra '{palabra}' no está en el alma o no alcanza fuerza mínima ({self.fuerza_minima}).")
return
info = self.info_posicion[palabra]
apariciones = len(self.coocurrencias_q[palabra])
porcentaje = apariciones / total_preguntas * 100
pos_prom = info["suma_pos_relativa"] / info["total"]
fuerza_media = sum(self.pesos[pq].get(palabra,0) for pq in self.coocurrencias_q[palabra]) / apariciones
if info["veces_inicio"] > info["total"] * 0.5:
etiqueta = "Inicio Fijo"
elif info["veces_final"] > info["total"] * 0.5:
etiqueta = "Final Fijo"
elif pos_prom < 0.35:
etiqueta = "Zona Temprana"
elif pos_prom > 0.65:
etiqueta = "Zona Tardía"
else:
etiqueta = "Intermedio"
print(f"\nPalabra del alma: '{palabra}'")
print(f" Total palabras de pregunta registradas: {total_preguntas}")
print(f" Activada (fuerza ≥ {self.fuerza_minima}) en {apariciones} → {porcentaje:.1f}%")
print(f" Fuerza media: {fuerza_media:.2f}")
print(f" Posición promedio: {pos_prom:.2f} ({int(pos_prom100)}%) – {etiqueta}")
if porcentaje >= self.umbral_general * 100:
print(f" ⚠️ Es considerada GENERAL (umbral {self.umbral_general100:.0f}%).")
else:
print(f" ℹ️ No alcanza el umbral de generalización actual ({self.umbral_general*100:.0f}%).")

=====================================================================
CEREBRO HÍBRIDO (COM2 + PRE2) – Puentes obligatorios, COM2 opcional
=====================================================================
class CerebroPlanificadorHibrido:
def init(self, debug=True):
self.com2 = CerebroPosicionalAlma()
self.base_3 = collections.defaultdict(collections.Counter)
self.base_2 = collections.defaultdict(collections.Counter)
self.base_1 = collections.defaultdict(collections.Counter)
self.debug = debug
self.cantidad_predicciones = 20

def log(self, *args):
if self.debug:
print(" [DEBUG]", *args)

def limpiar(self, texto):
return re.sub(r'[^\w\s]', '', str(texto).lower()).split()

def entrenar_local(self, ruta="aprender.json"):
if not os.path.exists(ruta):
print("No se encontró", ruta); return False
with open(ruta, encoding="utf-8") as f:
dataset = json.load(f)
self.com2.entrenar_con_dataset(dataset)
for par in dataset:
if "user" not in par or "alma" not in par: continue
pa = self.limpiar(par["alma"])
for i in range(len(pa)):
if i>=1: self.base_1[pa[i-1]][pa[i]] += 100
if i>=2: self.base_2[(pa[i-2], pa[i-1])][pa[i]] += 100
if i>=3: self.base_3[(pa[i-3], pa[i-2], pa[i-1])][pa[i]] += 100
return True

def bigrama_prob(self, a, b):
if a in self.base_1:
total = sum(self.base_1[a].values())
return self.base_1[a].get(b,0)/total if total>0 else 0.0
return 0.0

def existe_bigrama(self, a, b):
return self.bigrama_prob(a,b) > 0

def candidatos_pre2(self, contexto):
c = collections.Counter()
if len(contexto)>=3:
t = tuple(contexto[-3:])
if t in self.base_3: c.update(self.base_3[t])
if len(contexto)>=2:
t = tuple(contexto[-2:])
if t in self.base_2: c.update(self.base_2[t])
if len(contexto)>=1:
if contexto[-1] in self.base_1: c.update(self.base_1[contexto[-1]])
return [p for p,_ in c.most_common(30)]

# ------------------------------------------------------------
# EXPANSIÓN DE CONTENIDO
# ------------------------------------------------------------
def expandir_contenido(self, palabra_origen, n=None):
if n is None:
n = self.cantidad_predicciones
generales = self.com2.generales()
resultados = set()
intentos = n * 5
for _ in range(intentos):
actual = palabra_origen
contenido_recogido = []
pasos = 0
while len(contenido_recogido) < n and pasos < 6:
if actual not in self.base_1:
break
siguientes = self.base_1[actual].most_common(10)
random.shuffle(siguientes)
elegido = None
for cand, _ in siguientes:
if cand == actual: continue
if cand in generales:
elegido = cand
break
elif self.com2.fuerza_con_pregunta(palabra_origen, cand) >= self.com2.fuerza_minima:
elegido = cand
break
if elegido is None: break
if elegido not in generales:
contenido_recogido.append(elegido)
actual = elegido
pasos += 1
for w in contenido_recogido:
if w in self.com2.info_posicion and w not in generales:
resultados.add(w)
if len(resultados) >= n: break
if len(resultados) >= n: break
return list(resultados)

# ------------------------------------------------------------
# EXTRACCIÓN DE PUENTES, NÚCLEOS Y TIPO3
# ------------------------------------------------------------
def extraer_puentes_y_nucleos(self, tokens_pregunta):
generales = self.com2.generales()
palabras_validas = [p for p in tokens_pregunta
if p not in generales and any(self.com2.fuerza_con_pregunta(p, a) >= self.com2.fuerza_minima
for a in self.com2.pesos.get(p, {}))]
self.log(f"Palabras de pregunta con activaciones: {palabras_validas}")

mapa = {}
for p in palabras_validas:
representantes = self.expandir_contenido(p)
palabras = set(representantes)
palabras = {w for w in palabras if w in self.com2.info_posicion and w not in generales}
mapa[p] = palabras
self.log(f" {p}: {len(palabras)} predicciones -> {palabras}")

conteo = collections.Counter()
for pal_set in mapa.values():
conteo.update(pal_set)
self.log(f"Intersecciones: {dict(conteo)}")

t1 = {w for w, c in conteo.items() if c >= 2}
t3 = {w for w, c in conteo.items() if c == 1 and w not in t1}
self.log(f"Tipo 1: {t1} Tipo 3: {t3}")

origen_t3 = {w: set() for w in t3}
for p, palabras in mapa.items():
for w in palabras:
if w in origen_t3:
origen_t3[w].add(p)

t2 = set()
for w in t3:
representantes_w = self.expandir_contenido(w, n=self.cantidad_predicciones//2)
nuevas = set(representantes_w)
nuevas = {x for x in nuevas if x in t3 and x != w}
for otra in nuevas:
if origen_t3[w].isdisjoint(origen_t3[otra]):
t2.add(w)
t2.add(otra)
self.log(f" T3 '{w}' ↔ '{otra}' → T2")
self.log(f"Tipo 2: {t2}")

# Núcleos reales: palabras de pregunta que tienen predicciones no vacías
nucleos = [p for p in palabras_validas if len(mapa[p]) > 0]
self.log(f"Núcleos reales: {nucleos}")

return t1, t2, t3, nucleos

# ------------------------------------------------------------
# CONEXIÓN
# ------------------------------------------------------------
def conectar_con_puente(self, a, puente, b, max_pasos=3):
for pasos1 in range(0, max_pasos+1):
tramo1 = self._buscar_ruta(a, puente, pasos1)
if not tramo1 and pasos1 > 0: continue
if pasos1 == 0:
tramo1 = [a, puente] if self.existe_bigrama(a, puente) else None
if not tramo1: continue
for pasos2 in range(0, max_pasos+1):
tramo2 = self._buscar_ruta(puente, b, pasos2)
if pasos2 == 0:
tramo2 = [puente, b] if self.existe_bigrama(puente, b) else None
if tramo2:
return tramo1[:-1] + tramo2
return None

def _buscar_ruta(self, a, b, intermedios):
if intermedios == 0:
return [a, b] if self.existe_bigrama(a, b) else None
for _ in range(20):
ruta = [a]
for i in range(intermedios):
ctx = ruta if len(ruta) < 3 else ruta[-3:]
cands = self.candidatos_pre2(ctx)
if len(ruta)>=1 and cands and ruta[-1] in cands:
cands.remove(ruta[-1])
if not cands: break
elegido = random.choice(cands[:5])
ruta.append(elegido)
else:
ruta.append(b)
if all(self.existe_bigrama(ruta[i], ruta[i+1]) for i in range(len(ruta)-1)):
return ruta
return None

def conexion_directa(self, a, b, max_pasos=4):
for pasos in range(1, max_pasos+1):
ruta = self._buscar_ruta(a, b, pasos)
if ruta:
return ruta
return None

def _ruta_emergencia(self, a, b):
"""Inserta la palabra 'de' entre a y b si existe el bigrama, si no, inserta 'y'."""
if self.existe_bigrama(a, "de") and self.existe_bigrama("de", b):
return [a, "de", b]
if self.existe_bigrama(a, "y") and self.existe_bigrama("y", b):
return [a, "y", b]
return None

def afinidad(self, puente, palabra):
prob1 = self.bigrama_prob(puente, palabra)
prob2 = self.bigrama_prob(palabra, puente)
return max(prob1, prob2)

# ============================================================
# RESPUESTA PRINCIPAL (Puentes obligatorios, COM2 opcional)
# ============================================================
def responder(self, pregunta):
tokens = self.limpiar(pregunta)
if not tokens:
return "Escribe algo válido."

self.log("="*60)
self.log(f"Pregunta: '{pregunta}'")
self.log(f"Tokens: {tokens}")

# --- 1. Obtener puentes, t3 y núcleos ---
t1, t2, t3, nucleos = self.extraer_puentes_y_nucleos(tokens)
puentes_todos = t1.union(t2)
puentes_puros = [p for p in puentes_todos if p not in nucleos]
generales = self.com2.generales()
self.log(f"Núcleos: {nucleos}")
self.log(f"Puentes (T1 U T2): {puentes_todos}")
self.log(f"Puentes puros (no núcleos): {puentes_puros}")
self.log(f"Tipo 3: {t3}")

if not nucleos and not puentes_todos:
return "No tengo suficientes referencias para responder."

# --- 2. Ruta COM2 original ---
ruta_com2 = self.com2.obtener_ruta_com2(tokens, top=6)
self.log(f"Ruta COM2 original: {ruta_com2}")

# --- 3. Selección de palabras COM2 (opcionales) ---
palabras_com2_validas = set()
# 3a. Palabras de COM2 que están en Tipo3 se incluyen automáticamente
for palabra in ruta_com2:
if palabra in t3:
palabras_com2_validas.add(palabra)
self.log(f" '{palabra}' está en Tipo3 → incluida como COM2 opcional.")
# 3b. Doble filtro para el resto
for palabra in ruta_com2:
if palabra in palabras_com2_validas or palabra in nucleos or palabra in puentes_todos:
continue
conecta_nucleo = False
conecta_puente_puro = False
for nuc in nucleos:
if (self.conexion_directa(palabra, nuc, max_pasos=2) or
self.conexion_directa(nuc, palabra, max_pasos=2)):
conecta_nucleo = True
break
if not conecta_nucleo:
self.log(f" '{palabra}' NO conecta con núcleo → descartada.")
continue
for puente in puentes_puros:
if (self.conexion_directa(palabra, puente, max_pasos=2) or
self.conexion_directa(puente, palabra, max_pasos=2)):
conecta_puente_puro = True
break
if conecta_puente_puro:
palabras_com2_validas.add(palabra)
self.log(f" '{palabra}' conecta con núcleo Y puente puro → incluida (opcional).")
else:
self.log(f" '{palabra}' NO conecta con puente puro → descartada.")

self.log(f"Palabras COM2 opcionales: {palabras_com2_validas}")

# --- 4. Secuencia obligatoria: núcleos + puentes (ordenados) ---
obligatorios = list(set(nucleos).union(puentes_todos))
obligatorios.sort(key=lambda p: self.com2.posicion_promedio(p))
self.log(f"Secuencia obligatoria (núcleos+puentes): {obligatorios}")

# --- 5. Construcción de frase (primero obligatorios, luego opcionales) ---
primera = obligatorios[0]
pos_primera = self.com2.posicion_promedio(primera)
frase = []
if pos_primera > 0.0:
iniciadores = [g for g in generales if self.com2.posicion_promedio(g) < 0.05]
conectado = False
for ini in iniciadores:
if self.existe_bigrama(ini, primera):
frase = [ini, primera]
conectado = True
self.log(f"Inicio con general 0.0: '{ini}'")
break
if not conectado:
frase = [primera]
self.log(f"Inicio directo (sin general 0.0)")
else:
frase = [primera]

puentes_usados = set()
# Función para conectar un tramo (obligatorio)
def conectar_tramo(actual, objetivo, es_obligatorio=False):
# Primero intentar con puente
mejor_puente = None
mejor_afinidad = 0
for puente in puentes_todos:
if puente in puentes_usados:
continue
af1 = self.afinidad(puente, actual)
af2 = self.afinidad(puente, objetivo)
if af1 > 0 and af2 > 0:
af_combinada = af1 + af2
if af_combinada > mejor_afinidad:
mejor_afinidad = af_combinada
mejor_puente = puente
if mejor_puente:
ruta = self.conectar_con_puente(actual, mejor_puente, objetivo, max_pasos=3)
if ruta and len(ruta) <= 8:
self.log(f" ✔ Puente '{mejor_puente}': {ruta}")
puentes_usados.add(mejor_puente)
return ruta[1:] # devolver solo las palabras nuevas
# Conexión directa
ruta = self.conexion_directa(actual, objetivo, max_pasos=4)
if ruta and len(ruta) <= 8:
self.log(f" ✔ Directa: {ruta}")
return ruta[1:]
# Si es obligatorio, forzar con emergencia
if es_obligatorio:
emerg = self._ruta_emergencia(actual, objetivo)
if emerg:
self.log(f" ⚠ Emergencia: {emerg}")
return emerg[1:]
else:
# Último recurso: insertar la palabra tal cual
self.log(f" ⚠ Insertando '{objetivo}' sin conector conocido.")
return [objetivo]
return None

# Recorrer obligatorios
idx = 1
while idx < len(obligatorios):
actual = frase[-1]
objetivo = obligatorios[idx]
self.log(f"\n→ Obligatorio {idx}: parado='{actual}', objetivo='{objetivo}'")
nuevas = conectar_tramo(actual, objetivo, es_obligatorio=True)
if nuevas:
frase.extend(nuevas)
else:
self.log(f" ✘ No se pudo conectar obligatorio '{objetivo}' (inesperado).")
idx += 1

# --- 6. Intentar añadir palabras COM2 opcionales ---
for palabra in palabras_com2_validas:
if palabra in frase: # ya está
continue
# Buscar la mejor posición para insertarla (antes de la primera palabra con posición mayor)
pos_palabra = self.com2.posicion_promedio(palabra)
insert_index = len(frase)
for i, p in enumerate(frase):
if self.com2.posicion_promedio(p) > pos_palabra:
insert_index = i
break
# Intentar conectar con el contexto
anterior = frase[insert_index-1] if insert_index > 0 else None
siguiente = frase[insert_index] if insert_index < len(frase) else None
exito = False
if anterior and self.conexion_directa(anterior, palabra, max_pasos=2):
ruta = self.conexion_directa(anterior, palabra, max_pasos=2)
frase.insert(insert_index, palabra)
self.log(f" Añadida opcional '{palabra}' entre '{anterior}' y '{siguiente}'.")
exito = True
elif siguiente and self.conexion_directa(palabra, siguiente, max_pasos=2):
ruta = self.conexion_directa(palabra, siguiente, max_pasos=2)
frase.insert(insert_index, palabra)
self.log(f" Añadida opcional '{palabra}' entre '{anterior}' y '{siguiente}'.")
exito = True
if not exito:
self.log(f" Opcional '{palabra}' no se pudo insertar, omitiendo.")

# Cierre
if frase:
ultima_pos = self.com2.posicion_promedio(frase[-1])
if ultima_pos < 0.95:
finalistas = [g for g in generales if self.com2.posicion_promedio(g) >= 0.95]
finalistas.extend([p for p in obligatorios if self.com2.posicion_promedio(p) >= 0.95])
for fin in finalistas:
ruta = self.conexion_directa(frase[-1], fin, max_pasos=2)
if ruta and len(ruta) <= 5:
self.log(f" Cierre con '{fin}': {ruta}")
frase.extend(ruta[1:])
break

if len(frase) > 20:
frase = frase[:20]

self.log(f"FRASE FINAL: {frase}")
return ' '.join(frase)

=====================================================================
INTERFAZ
=====================================================================
if name == "main":
if not os.path.exists("aprender.json"):
print("Error: Necesitas el archivo 'aprender.json' en esta carpeta.")
sys.exit()

with open("aprender.json", "r", encoding="utf-8") as f:
dataset = json.load(f)

cerebro = CerebroPlanificadorHibrido(debug=True)
print("=" * 60)
print(" CEREBRO HÍBRIDO – Puentes obligatorios, COM2 opcional")
print("=" * 60)
print("[1] Entrenar con aprender.json")
print("[2] Solo PRE2")
op = input("Opción: ").strip()

if op == "1":
if not cerebro.entrenar_local("aprender.json"):
sys.exit()
else:
cerebro.com2.entrenar_con_dataset(dataset)
for par in dataset:
if "user" not in par or "alma" not in par: continue
pa = cerebro.limpiar(par["alma"])
for i in range(len(pa)):
if i >= 1: cerebro.base_1[pa[i - 1]][pa[i]] += 100
if i >= 2: cerebro.base_2[(pa[i - 2], pa[i - 1])][pa[i]] += 100
if i >= 3: cerebro.base_3[(pa[i - 3], pa[i - 2], pa[i - 1])][pa[i]] += 100
print("PRE2 entrenado.")

print("\nComandos:")
print(" /top <num>% → umbral de generales")
print(" /fuerza <num> → fuerza mínima")
print(" /cantidad <num> → predicciones por palabra (defecto 20)")
print(" /general → mostrar generales")
print(" /mostrar <p> → detalles de una palabra del alma")
print(" /mostrar → todas las palabras del alma")
print(" /conector <p> → conexiones de una palabra de pregunta")
print(" 'salir' → terminar\n")

while True:
try:
entrada = input("Tú: ").strip()
if not entrada or entrada.lower() == "salir":
print("Sesión finalizada.")
break
elif entrada.lower() == "/general":
generales = cerebro.com2.generales()
if generales:
print(f"Generales (umbral {cerebro.com2.umbral_general*100:.0f}%, fuerza mínima {cerebro.com2.fuerza_minima}):")
for g in sorted(generales):
print(f" {g}")
else:
print("No hay palabras generales con los parámetros actuales.")
elif entrada.lower().startswith("/top"):
partes = entrada.split()
if len(partes) >= 2:
valor_str = partes[1].replace("%", "").strip()
try:
valor = float(valor_str)
if valor > 1:
valor = valor / 100.0
cerebro.com2.set_umbral(valor)
except ValueError:
print("Formato inválido. Usa /top 4 o /top 0.04")
else:
print("Debes especificar un porcentaje. Ej: /top 4")
elif entrada.lower().startswith("/fuerza"):
partes = entrada.split()
if len(partes) >= 2:
try:
valor = float(partes[1])
cerebro.com2.set_fuerza_minima(valor)
except ValueError:
print("Formato inválido. Usa /fuerza 2.5")
else:
print("Debes especificar un valor numérico. Ej: /fuerza 3")
elif entrada.lower().startswith("/cantidad"):
partes = entrada.split()
if len(partes) >= 2:
try:
valor = int(partes[1])
if valor >= 1:
cerebro.cantidad_predicciones = valor
print(f"✅ Cantidad de predicciones por palabra: {valor}")
else:
print("Debe ser un entero positivo.")
except ValueError:
print("Formato inválido. Usa /cantidad 20")
else:
print("Debes especificar un número. Ej: /cantidad 20")
elif entrada.lower().startswith("/mostrar"):
partes = entrada.split(maxsplit=1)
if len(partes) == 1:
cerebro.com2.mostrar_todas_palabras()
else:
palabra = partes[1].strip().lower()
cerebro.com2.mostrar_palabra(palabra)
elif entrada.lower().startswith("/conector"):
partes = entrada.split(maxsplit=2)
if len(partes) >= 2:
palabra = partes[1].strip().lower()
solo_contenido = True
if len(partes) >= 3 and partes[2].strip() == "--todas":
solo_contenido = False
cerebro.com2.mostrar_conexiones(palabra, solo_contenido)
else:
print("Debes especificar una palabra. Ej: /conector color")
else:
respuesta = cerebro.responder(entrada)
print(f"🔵 RESPUESTA: {respuesta}\n")
except KeyboardInterrupt:
print("\nInterrupción detectada.")
break
