# Documento de diseño — Observatorio de Turismo Sostenible (Guatemala)

**Laboratorio 10 · Visualización Interactiva · CC3066 Data Science · UVG · Semestre II 2026**

**Integrantes del grupo — Proyecto 1 · Grupo 4**

- Hansel André López Montenegro — GitHub: [HanseLopez99](https://github.com/HanseLopez99)
- María José Yee Vidal — GitHub: [Yee404](https://github.com/Yee404)
- Pablo Andrés Cabrera Argüello — GitHub: [pablouwunya2021](https://github.com/pablouwunya2021)
- Pablo José Méndez Alvarado — GitHub: [Paul-1511](https://github.com/Paul-1511)

**Repositorio del código:** https://github.com/pablouwunya2021/lab10-ds.git

Tablero dirigido a **directivos y tomadores de decisiones del sector turístico** sin formación
estadística. Permite explorar el ingreso de visitantes no residentes a Guatemala (2009–2026),
comparar los pronósticos de tres modelos y comprender sus limitaciones. Reutiliza datos, modelos
y resultados de evaluación del **Laboratorio 2** (series de tiempo + redes LSTM). No se
construyeron modelos nuevos.

---

## 4.5 Alcance del tablero

**Qué incluye**

- Exploración del ingreso mensual de visitantes no residentes (turistas y excursionistas),
  enero 2009 – junio 2026, por **vía de ingreso** (aérea, terrestre, marítima) y por **origen**
  (regiones del mundo y principales países).
- Comparación del desempeño de **tres modelos de pronóstico** reutilizados del Laboratorio 2
  (LSTM simple, LSTM apilado y LSTM global con características catch22) sobre la ventana de
  prueba abril 2021 – junio 2026.
- Análisis del **perfil de las series** (qué mercados/vías se comportan parecido) con catch22.

**Qué NO incluye (límites explícitos)**

- No entrena ni ajusta modelos nuevos: solo muestra resultados ya calculados.
- No incorpora variables de gasto, empleo, ocupación hotelera ni sostenibilidad ambiental (no
  están en la fuente disponible); el "turismo sostenible" se aborda aquí desde el volumen y la
  composición de la demanda.
- Los pronósticos cubren únicamente las series con modelo entrenado (Total y Vía aérea).
- La ventana de prueba abarca la pandemia y la recuperación, por lo que los errores son altos;
  el tablero lo advierte y recomienda leer los pronósticos como **tendencia**, no como cifra exacta.

**Fuente de datos:** `Base_Migracion_2009-2026jun.xlsx` (registros mensuales de ingreso de
viajeros). Población de referencia y partición 70/30 heredadas del Laboratorio 1/2.

---

## 4.4 Preguntas exploratorias que guiaron el diseño

El diseño de las visualizaciones y de la navegación partió de preguntas de **gestión**:

1. ¿El destino crece, se estanca o se recupera? ¿A qué ritmo? → *panorama y serie mensual*.
2. ¿En qué meses llega más gente? ¿Cómo planifico capacidad y campañas por temporada? →
   *mapa de calor de estacionalidad*.
3. ¿Por qué vía entran los visitantes y cómo ha cambiado ese peso (p. ej. tras la pandemia)? →
   *composición por vía de ingreso*.
4. ¿De dónde vienen? ¿Qué mercados concentran la demanda y cómo evoluciona cada uno? →
   *ranking de origen enlazado con su serie temporal; drill-down región → país*.
5. ¿Qué tan confiables son los pronósticos? ¿Qué modelo es mejor y en qué meses falla? →
   *comparación de modelos, pronóstico vs. observado, error en el tiempo*.
6. ¿Qué mercados/vías se comportan parecido y podrían gestionarse con una misma estrategia? →
   *perfil de series (catch22)*.

La navegación se organizó siguiendo el recorrido mental del directivo: **entender el panorama →
explorar el detalle → consultar pronósticos → comparar perfiles**.

---

## 4.3 Framework, lenguaje y herramienta — justificación

**Lenguaje: Python.** Los modelos del Laboratorio 2 (Keras/TensorFlow) y el preprocesamiento
están en Python; reutilizarlos desde el mismo lenguaje evita reimplementar la carga de datos y
las predicciones.

**Herramienta: Streamlit + Plotly.**

| Criterio | Por qué Streamlit/Plotly | Por qué no las alternativas |
|---|---|---|
| Reúso del Lab 2 | Importa directamente `lstm_lab2` y lee `outputs/` | R Shiny obligaría a reescribir todo en R |
| Rapidez de desarrollo | Tablero multipágina con poco código; ideal para el plazo | Dash exige más *boilerplate* (callbacks, layout) |
| Interactividad | Plotly da zoom, *hover*, leyendas conmutables y selección de puntos listos | Voilà/Panel tienen menos ejemplos y comunidad para este caso |
| Público directivo | Interfaz limpia, textos explicativos y vistas coordinadas fáciles de leer | — |
| Costo | 100 % libre y de código abierto | — |

Para un tablero **centrado en datos y modelos ya calculados**, con énfasis en claridad para
directivos y plazo corto, Streamlit es la opción más adecuada: menos código que Dash, mismo
lenguaje que los modelos, y Plotly aporta la interacción (zoom, filtros, vistas enlazadas) que
pide el laboratorio.

> Nota técnica: se fijó **Plotly 5.24.1** con **Streamlit 1.66.1** por ser una combinación estable
> para los eventos de selección de los gráficos.

---

## 4.1 Paleta de colores, tipografía, bosquejo e interfaz

### Paleta de colores (teoría del color)

Principios aplicados: **un significado por color, mantenido en toda la app**; contraste suficiente
para legibilidad (texto AA); y distinción también para daltonismo rojo-verde.

- **Color de marca — turquesa `#0F766E`:** evoca los lagos y costas de Guatemala; se usa para el
  encabezado, los acentos y el total agregado. Transmite confianza y es sobrio para un público
  directivo.
- **Categóricos con significado fijo (vías de ingreso):**
  - Aérea `#1B6FB3` (azul cielo), Terrestre `#E08A1E` (ámbar, carretera/tierra),
    Marítima `#2BA6A4` (turquesa, mar). Son colores intuitivos respecto a lo que representan.
- **Categóricos de origen (regiones):** azul, turquesa, púrpura, ámbar, rojo, verde, marrón y gris,
  elegidos para ser distinguibles entre sí; cada región conserva su color en todas las vistas.
- **Modelos:** Observado en **gris oscuro `#2F3B44`** (el dato real, referencia neutra) y cada
  modelo con su color vivo fijo; el modelo resaltado se dibuja sólido y los demás atenuados.
- **Escala secuencial turquesa** (claro→oscuro) para mapas de calor: un solo tono porque
  representa "más vs. menos".
- **Escala divergente** (azul↔rojo con centro neutro) solo para el error de pronóstico, donde el
  **signo** (sobrestima vs. subestima) importa.

Regla de consistencia: el gris siempre es "dato observado"; los colores vivos siempre son
"estimaciones/categorías". El usuario no necesita releer leyendas.

### Tipografía

**Inter** (con alternativas del sistema: Segoe UI, Helvetica). Es una fuente *sans-serif*
humanista, de alta legibilidad en pantalla, neutra y profesional. Jerarquía: títulos en negrita,
subtítulos por sección, textos explicativos cortos en gris secundario.

### Bosquejo de la interfaz y navegación

```
┌──────────────┬────────────────────────────────────────────────┐
│  BARRA        │  [Encabezado de marca: título + subtítulo]      │
│  LATERAL      │                                                 │
│  🏠 Inicio     │  Controles (selector / nivel de detalle / rango)│
│  🔎 Explorar   │  ┌───────────────┐  ┌───────────────┐          │
│  📈 Modelos    │  │  Visualización │  │  Visualización │          │
│  🧭 Perfil     │  └───────────────┘  └───────────────┘          │
│               │  Nota explicativa (qué muestra / para qué sirve)│
│  (contexto)   │  …                                              │
└──────────────┴────────────────────────────────────────────────┘
```

- **Navegación lateral** de cuatro páginas, siguiendo el recorrido del directivo
  (Inicio → Explorar → Modelos → Perfil).
- Cada página: **controles arriba**, visualizaciones en el cuerpo y **notas breves** que explican
  qué presenta cada gráfico y cómo usarlo; se definen los términos especializados.
- **Vistas enlazadas (coordinated views):** una selección actualiza varias gráficas a la vez
  (ver 4.2).

### Principios de HCI / UX aplicados

- **Reconocimiento sobre memoria:** colores y etiquetas constantes; leyendas visibles.
- **Retroalimentación inmediata:** al cambiar un control, las gráficas responden al instante.
- **Prevención de errores:** mensajes claros cuando una selección no tiene datos.
- **Distinción hallazgo vs. estimación:** observado (gris) separado de los pronósticos (color).
- **Carga cognitiva baja:** pocas decisiones por pantalla, textos cortos, sin jerga innecesaria.

---

## 4.2 Elección del tipo de gráfica por visualización

Hay **más de 8** visualizaciones interactivas (sin contar tarjetas, controles, textos ni la tabla
comparativa, que son complementarios). Al menos **dos pares están enlazados**.

| # | Visualización | Tipo de gráfica | Por qué este tipo |
|---|---|---|---|
| 1 | Evolución de la serie (Explorar) | **Línea** con *range slider* (o **barras** en vista anual) | La línea muestra tendencia y continuidad temporal; el *slider* permite aumentar el detalle (zoom) |
| 2 | Estacionalidad | **Mapa de calor** Año × Mes | Revela patrones estacionales y su cambio año a año mejor que una línea |
| 3 | Composición por vía de ingreso | **Área apilada** en el tiempo | Muestra a la vez el total y el aporte de cada vía, y cómo cambia su peso |
| 4 | Ranking de origen *(enlazada)* | **Barras horizontales / lollipop** | Compara magnitudes entre muchas categorías ordenadas; fácil de leer |
| 5 | Detalle del origen seleccionado *(enlazada)* | **Línea** (área) | Da el nivel de detalle temporal del origen elegido en la #4 |
| 6 | Pronóstico vs. observado *(enlazada)* | **Líneas múltiples** | Compara la predicción de cada modelo contra el dato real en el tiempo |
| 7 | Comparación de modelos *(enlazada)* | **Lollipop (puntos + tallo)** | Compara una métrica entre pocos modelos; el punto es seleccionable |
| 8 | Error de pronóstico en el tiempo *(enlazada)* | **Barras divergentes** (cero al centro) | El signo (sub/ sobrestima) y el mes del error se leen de inmediato |
| 9 | Búsqueda de hiperparámetros | **Línea + puntos** (val_loss por ensayo) | Equivale a una curva de aprendizaje: muestra cómo se eligió el mejor modelo |
| 10 | Mapa de similitud entre series | **Dispersión (PCA catch22)** | Ubica series parecidas cerca; comunica agrupamientos |
| 11 | Distancia entre series | **Mapa de calor** | Matriz de parecido entre todas las series de un vistazo |

### Visualizaciones enlazadas y nivel de detalle

- **Par enlazado 1 (Explorar):** al elegir un **origen** (menú o clic en la barra #4), se actualiza
  la **serie temporal de ese origen** (#5) y se **resalta** la barra correspondiente. Además, el
  control *Región / País* **aumenta o disminuye el nivel de detalle** (grandes regiones → países).
- **Par enlazado 2 (Modelos):** al elegir un **modelo** (menú o clic en el punto #7), se resalta en
  el **pronóstico** (#6), cambia el **error en el tiempo** (#8) y la **curva de hiperparámetros**
  (#9). Una sola selección coordina cuatro gráficos.
- **Nivel de detalle adicional:** *range slider* de zoom (#1), conmutador **Mensual / Anual**
  (#1 y #3) y filtro de período por años.

---

## 4.6 Planificación de tareas, fechas y responsables

El historial del repositorio documenta las contribuciones de cada integrante.

| # | Tarea | Fecha de terminación | Responsable |
|---|---|---|---|
| 1 | Selección de preguntas de gestión y alcance | 20/oct/2026 | María José Yee Vidal |
| 2 | Paleta de colores, tipografía y bosquejo de navegación | 21/oct/2026 | Hansel André López Montenegro |
| 3 | Reúso de datos y modelos del Lab 2 (loaders) | 21/oct/2026 | Pablo Andrés Cabrera Argüello |
| 4 | **Avance:** ≥2 visualizaciones interactivas funcionales | 22/oct/2026 (5:20 pm) | Pablo Andrés Cabrera Argüello |
| 5 | Página Explorar (viz 1–5, enlace origen → detalle) | 23/oct/2026 | Pablo José Méndez Alvarado |
| 6 | Página Modelos (viz 6–9, enlace de modelo) | 24/oct/2026 | Pablo Andrés Cabrera Argüello |
| 7 | Página Perfil (viz 10–11) y textos explicativos | 24/oct/2026 | Hansel André López Montenegro |
| 8 | Pruebas de interacción y revisión de diseño/UX | 25/oct/2026 | María José Yee Vidal |
| 9 | Documento de diseño (este PDF) | 25/oct/2026 | Pablo José Méndez Alvarado |
| 10 | **Entrega final** (código + documento) | 25/oct/2026 | Todo el grupo |

---

## Recomendaciones (respaldadas por los datos, con sus límites)

- El ingreso se **recuperó con fuerza** tras 2021 (últimos 12 meses ≈ 40 % por encima de
  2018–2019), pero el **último año se mantuvo plano** (≈ 0 % interanual): conviene vigilar si la
  recuperación se estancó. *Límite: no se analizan causas; los datos solo muestran el volumen.*
- La **temporada alta** (visible en el mapa de calor) debe guiar la planificación de capacidad y
  campañas.
- Los **pronósticos** tienen error alto en esta ventana atípica (todos los MASE > 1, es decir, no
  superan a un pronóstico estacional ingenuo): úselos como **referencia de tendencia**, no como
  cifra de planificación exacta.
- La **vía marítima** se comporta de forma muy distinta al resto (aparece aislada en el perfil):
  requiere pronósticos y estrategia propios.
