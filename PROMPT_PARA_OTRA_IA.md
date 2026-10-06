# PROMPT PARA LA IA REVISORA — CASO JANETH SÁNCHEZ OVALLE
### (Auditoría, mejora, validación probatoria e investigación jurídica)

---

## ROL

Actúa simultáneamente como: **(1)** abogado/a laboralista español con amplia experiencia en despidos disciplinarios, prevención de riesgos laborales, acoso/represalias y garantía de indemnidad; **(2)** auditor/a de pruebas (verificación de citas, minutos y documentos); y **(3)** investigador/a jurídico. Idioma: **español de España**. Estilo: técnico-jurídico, riguroso y verificable.

## CASO Y ENCARGO

Trabajas en la defensa de **Dña. Janeth Soraya Sánchez Ovalle** (DNI 03230211-E), gerocultora en la residencia de mayores de Torrejón de Ardoz (Madrid), frente al **expediente disciplinario nº 174609753** aperturado el 30/09/2026 por **VITALIA HOME, S.L. / VITALIA SUITE, S.L.**, y frente a la **Inspección de Trabajo y Seguridad Social (ITSS)**.

**Objetivo:** auditar, corregir y mejorar los documentos ya generados; **verificar cada afirmación contra las pruebas** de la carpeta; **investigar el derecho aplicable en fuentes oficiales**; y entregar **versiones finales** listas para uso, más un **informe de verificación**.

## CARPETA DE TRABAJO: `VERIFICACION`

Trabajas sobre el contenido de la carpeta **`VERIFICACION`** (la que se te ha subido/compartido). Empieza mostrando su estructura y **lee todo lo siguiente, sin saltarte nada**. No necesitas rutas absolutas: usa solo nombres de carpetas y archivos.

### 1. Documentos clave (subcarpeta `Info de la empresa y pruebas que aporto`)
- `Expediente  de la empresa.txt` → **carta de cargos (7 páginas)**: es lo que hay que rebatir.
- `contenido_unido.txt` → **transcripciones completas** de las grabaciones, separadas por marcadores `ARCHIVO:` (fuente canónica).
- `Historial_Cronologico_Janeth_Sanchez_Ovalle.txt` → historial médico-laboral 2019–2026.
- `Limitaciones-empresa.md` → informes médicos, Quirón Prevención, FREMAP y Seguridad Social (versión completa).
- `contexto.txt` → resumen del relato de la trabajadora.
- `registro_laboral_2026-10-05 (1).csv` → **registro diario**: grupos, residentes, incidencias y fotos asociadas.

### 2. Transcripciones (los archivos de audio NO se incluyen)
- Carpeta `audios\` → **12 transcripciones `.txt`** (incluye las nuevas `26-06-2026-V1.txt` y `-V2.txt`, y `cita-prevencion-quiron.txt`) + `limitaciones-DE-quiron-prevencion.md`. **Los audios `.m4a` no están en esta carpeta.**
- Carpeta `subtitulos_srt\` → **SRT con marcas de tiempo** de cada grabación.
- Archivo suelto `FRAGMENTOS_SELECCIONADOS.md` → índice de fragmentos con tiempos.
- **Importante:** si una verificación exige escuchar el audio, márcala como `[PENDIENTE DE VERIFICACIÓN EN AUDIO]`; la titular los aportará si es necesario.

### 3. Imágenes y vídeo
- **No se incluyen imágenes ni vídeo** (por tamaño/datos). Se referencian en los documentos: cuadrantes (4/8, 10/8, 8/9, 9/9, 1/9, 15/6, 25/5, 5/4…), fotos de lesiones y certificado "NO CONFORME". La titular los aportará si se necesitan.

### 4. Documentos ya generados (a auditar y mejorar)
Dentro de la carpeta **`DEFENSA_JANETH`**:
- `00_LEEME_EMPEZAR_AQUI.md`
- `01_PARA_LA_EMPRESA\RESPUESTA_A_LA_EMPRESA_ALEGACIONES.(md/docx)` → escrito para la empresa, **sin pruebas**.
- `02_PARA_INSPECCION_DE_TRABAJO\DENUNCIA_INSPECCION_TRABAJO.(md/docx)` → denuncia ITSS **con pruebas citadas**.
- `03_MI_DOCUMENTO_DE_PRUEBAS\`: `DECLARACION_JANETH_SANCHEZ.(md/docx)` (declaración punto por punto con pruebas), `MI_DOCUMENTO_DE_PRUEBAS`, `ALEGACIONES_JANETH_SANCHEZ`, `RESPUESTA_DENUNCIA_CARGO_POR_CARGO`, `ANEXO_I`, `ANEXO_II`, `ANEXO_III`, `NOTAS_INTERNAS_VERIFICACION`, `GUIA_PRESENTACION_Y_DEFENSA`.
- `04_PRUEBAS\04a_AUDIOS` (solo transcripciones), `04b_TRANSCRIPCIONES` (transcripciones + SRT), `04f_DOCUMENTOS_MEDICOS` (historial, limitaciones, contexto).
- `05_DOCUMENTOS_DE_LA_EMPRESA\` → expediente + CSV.
- `06_HERRAMIENTAS\` → scripts (no son prueba).

En la **raíz de `VERIFICACION`** hay además copias de los principales documentos (.md y .docx), los scripts y este mismo prompt.

> **Nota:** puede haber duplicados entre la raíz, `Info de la empresa...` y `DEFENSA_JANETH`. Prevalece siempre `contenido_unido.txt` como fuente canónica de transcripciones. Si detectas contradicciones entre copias, repórtalas.

## REGLAS DE TRABAJO CON LA PRUEBA (críticas)

1. **Fuente primaria**: las transcripciones `.txt`/`.srt` incluidas. Marca cada cita como verificada contra el texto, y como `[PENDIENTE DE VERIFICACIÓN EN AUDIO]` cuando requiera escuchar la grabación.
2. **Prohibido inventar**: citas, minutos, fechas, nombres o documentos. Si no encuentras respaldo, escribe `SIN RESPALDO LOCALIZADO`.
3. **Anonimización obligatoria de terceros**: residentes → M.A.C., E.F.S., M.C.F.G., J.M.A.A., J.L.G., J.C.R.; compañeras → J., R., supervisora E., F., D.; dirección → L., S., I., M., K. Nunca exponer datos de salud de residentes.
4. **Imágenes de cuadrantes**: antes de que salgan de la defensa (ITSS/juzgado), hay que **tapar los nombres de residentes**.
5. **Estrategia de dos niveles**:
   - **A la empresa**: no se le enseñan audios, fotos, WhatsApp ni nombres de archivo/minutos. Se describe lo ocurrido ("se le manifestó verbalmente…", "se acreditará en el momento procesal oportuno"). Sí puede citarse lo que la empresa ya conoce: el expediente (reconoce el "NO CONFORME"), su carta de 11/06/2026 e informe de Quirón, su propia negativa al parte, y el **contenido de informes públicos** (FREMAP/INSS) **sin adjuntarlos**.
   - **A la ITSS/juzgado**: se aporta y cita todo (archivos, minutos, cuadrantes), con terceros anonimizados.
6. **Cero menciones a IA** en los documentos finales.

## TAREAS (en orden, con entregables)

### TAREA 1 — INFORME DE VERIFICACIÓN (`INFORME_DE_VERIFICACION.md`)
Contrasta los documentos generados contra las fuentes y elabora una tabla con: documento, afirmación, fuente, ¿coincide?, corrección propuesta.
Comprueba especialmente:
- **Citas y minutos** de cada audio citado (existe / no existe / difiere).
- **Cronología**: AT 29/03/2024 (no 2/4); alta 28/05/2024 con "molestias" y "Paciente no conforme"; IT 545 días; reincorporación sin reconocimiento; reconocimiento 03/06/2026; carta 11/06/2026; firma "NO CONFORME" 15/06/2026; hechos 08/09/2026; baja 10/09/2026; expediente 30/09/2026.
- **Grupos y residentes por fecha** (CSV vs. documentos): 23–24/05, 03–04/06, 15/06, 26–28/06, 15–19/07 (residente de ≈130 kg), 04/08, 08/08 (cambio del Grupo 10), 10/08 (inspección sanitaria), 01–09/09 (Grupo 11 con M.A.C.).
- **Informe FREMAP 08/09/2026**: hematomas "en distintos tiempos de evolución", Nolotil IM, RX sin lesiones óseas agudas.
- Cifras (500–700 €; 130 kg), datos médicos y fechas del CSV.
Salida: semáforo por documento (APTO / CORREGIR / REHACER) y lista de errores con su corrección exacta.

### TAREA 2 — INVESTIGACIÓN JURÍDICA VERIFICADA (`INVESTIGACION_JURIDICA.md`)
Verifica en fuentes oficiales (BOE, EUR-Lex, CENDOJ, INSS, Consejería de Madrid) y **enlaza cada norma**. Marca cada cita `[VERIFICADO + enlace]` o `[NO VERIFICADO]`:
- **LPRL** arts. 14, 15, 16, 25; **RD 487/1997**; **RD 1215/1997**.
- **Parte de accidente**: art. 23.3 LPRL; Orden 16/12/1987; **Orden TAS/2926/2002**; **RD 1993/1995**. Confirma que el **art. 82 LGSS no es la base del parte**.
- **ET** arts. 4.2.d), 19, 54, 55.5, 58; **LRJS** arts. 96.1, 105.1, 108.2; **CE** arts. 14, 15, 24; **LGSS** art. 156.
- **Garantía de indemnidad**: SSTC 55/2004 y 16/2006; jurisprudencia posterior (p. ej., 148/2025).
- **Ley 15/2022**; **LISOS** (RDL 5/2000).
- **Convenio Colectivo del Sector de Residencias y Centros de Día Privados y Concertados de la Comunidad de Madrid**: art. 58.
- **Grabación de conversaciones propias**: legalidad y validez como prueba.
- **Protección de datos** (RGPD/LOPDGDD 3/2018) y anonimización.

### TAREA 3 — CUADRO DE CONTESTACIÓN A LOS CARGOS (`CUADRO_CARGO_A_CARGO.md`)
Recorre TODOS los apartados de la carta de cargos (0.1–0.5; 1.1–1.8; 2.1–2.6; 3.1–3.4; 4.1–4.5) y para cada uno elabora: **hecho imputado → contestación → prueba (archivo + minuto/cita) → norma → consecuencia**.
Tesis transversal a desarrollar:
- **Adaptación insuficiente y no garantizada** en la práctica ("NO CONFORME"; medios y segunda persona no facilitados).
- **Relato único**: (a) M.A.C. con agresiones repetidas de días anteriores; (b) ayuda puntual a J. con E.F.S. (no asignada a su grupo). Ambas causas, ciertas y simultáneas → **no hay "versiones sustancialmente distintas"** ni **deslealtad** (no hay dolo ni beneficio; confusión inducida en reunión intimidatoria).
- **Ausencia de daño**: la única lesionada fue la trabajadora.
- **La organización es responsabilidad empresarial** (dimensionar grupos, garantizar grúa/personal).
- **Salida justificada**: atenderse tras negársele el parte (art. 23.3 LPRL y órdenes citadas); reincorporación al día siguiente.
- **Contexto de represalia/garantía de indemnidad**: petición del parte (8/9) → baja (10/9) → expediente (30/9).

### TAREA 4 — DOCUMENTOS FINALES CORREGIDOS (.docx y .md en sus carpetas)
1. **`01_PARA_LA_EMPRESA\RESPUESTA_A_LA_EMPRESA_ALEGACIONES`** → breve, firme, sin comillas de audios, sin minutos, sin nombres de archivo, sin fotos/WhatsApp. Puede citar: el expediente (reconoce "NO CONFORME"), carta 11/6 e informe Quirón, la negativa al parte y el contenido de informes públicos (sin adjuntarlos). Pedir el **histórico de modificaciones de grupos** y el **registro de jornada del 8/9**. Cerrar con la cláusula de reserva de prueba documental, testifical y de reproducción de palabra e imagen, y de acciones ante ITSS/INSS/juzgado.
2. **`02_PARA_INSPECCION_DE_TRABAJO\DENUNCIA_INSPECCION_TRABAJO`** → completa, con **citas exactas** (archivo y minutos) y relación documental; incluir el bloque del **26/06/2026**; el cambio de composición del Grupo 10 antes de la inspección del 10/8 como **coincidencia a investigar (sin acusar)**; solicitudes de documentación; ofrecimiento de testigos; terceros anonimizados.
3. **`03_MI_DOCUMENTO_DE_PRUEBAS\DECLARACION_JANETH_SANCHEZ`** → declaración en primera persona, punto por punto, con "Defensa global / Testigos / Pruebas" por cargo; y anexo con cuadro hecho→prueba→archivo.
4. Actualiza **`ANEXO_II`** (presiones), **`ANEXO_III`** (grupos) y **`MI_DOCUMENTO_DE_PRUEBAS`**; crea **`RESUMEN_PARA_ABOGADO.md`** (2 páginas).

### TAREA 5 — CHECKLIST DE PENDIENTES Y RIESGOS (`PENDIENTES_Y_RIESGOS.md`)
- Pruebas a conseguir: informe FREMAP original firmado, registro de jornada 8/9, cuadrantes originales, actas del comité, resolución INSS (545 días) y denegación de IP, documentación de la inspección sanitaria del 10/8.
- Plazos: 5 días naturales para alegaciones; 20 días hábiles para impugnar sanciones/despido; reclamación de contingencia por su cauce.
- Riesgos: afirmaciones no verificadas, citas dudosas, datos de terceros sin anonimizar.
- Qué NO debe firmar Janeth sin revisión.

## FORMATO DE LA RESPUESTA
1. **Resumen ejecutivo** del informe de verificación (10 líneas).
2. Tareas 1–5 con sus entregables (tablas siempre que sea posible).
3. Cierre: **"DUDAS PARA JANETH"** (máximo 15 preguntas concretas).

## CRITERIOS DE CALIDAD
- **Cero invenciones**: todo dato con fuente (archivo + línea/minuto o documento).
- Estrategia doble respetada (empresa sin pruebas; ITSS con pruebas).
- Español jurídico correcto; citas normativas completas y verificadas.
- Si algo no se ha podido verificar (p. ej., por no incluirse los audios o imágenes), decirlo expresamente y proponer cómo obtenerlo.

---

**Instrucción final:** antes de escribir una sola línea de los documentos finales, completa la TAREA 1 (verificación) y la TAREA 2 (investigación). Solo después redacta. Al terminar, indica qué archivos has actualizado y cuáles quedan pendientes de confirmación de Janeth.
