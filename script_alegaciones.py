# -*- coding: utf-8 -*-
"""
SCRIPT DE PRUEBAS AUDIOVISUALES — DEFENSA DE JANETH SÁNCHEZ OVALLE
=================================================================

Adaptación del script original ("script.py") para generar:
  1) Los archivos SRT individuales a partir de "contenido_unido.txt".
  2) Un vídeo de pruebas con los fragmentos clave para la defensa:
     "PRUEBAS_RESPUESTA_DENUNCIA.mp4" (portada + separadores + clips subtitulados).
     El vídeo NO muestra imágenes: solo audio y subtítulos.
  3) Un índice "FRAGMENTOS_SELECCIONADOS.md" y un "metadata.json" con SHA-256 (integridad).

USO:
  python script_alegaciones.py                -> genera todo (vídeo + SRT + índice)
  python script_alegaciones.py --only-srt     -> solo extrae los SRT y el índice
  python script_alegaciones.py --list         -> solo lista los fragmentos

NOTAS:
  - Los audios deben estar en esta carpeta o en .\audios (m4a, mp3, wav, opus, aac).
    Si falta un audio, el script continúa con los demás y lo reporta al final.
  - Si no existe un .srt original, se extrae de "contenido_unido.txt".
  - Las imágenes de prueba (cuadrantes, certificado NO CONFORME, lesiones) se
    aportan APARTE, como anexo independiente: carpeta "pruebas_imagenes".
  - Requiere FFmpeg instalado y accesible en el PATH.
"""

import os
import re
import sys
import json
import hashlib
import textwrap
import subprocess
import unicodedata

# ==========================================================
# CONFIGURACIÓN
# ==========================================================
CONTENIDO_UNIDO = "contenido_unido.txt"
SRT_DIR = "subtitulos_srt"
OUTDIR = "video_alegaciones"

W, H = 1280, 720
FPS = 25
AUDIO_SR = 44100
VIDEO_CRF = 20
VIDEO_PRESET = "medium"
AUDIO_BITRATE = "160k"

CONTEXT_BEFORE = 1.5
CONTEXT_AFTER = 0.8
SEPARATOR_DURATION = 1.6
SEPARATOR_TONE_DURATION = 0.28

HEADER_H = 220
TITLE_SIZE = 30
DESC_SIZE = 19
SUBTITLE_SIZE = 20
FADE = 0.18
SUBTITLE_WRAP = 60

EXTENSIONES_AUDIO = [".m4a", ".mp3", ".wav", ".opus", ".aac", ".ogg", ".wma"]

FONT_CANDIDATAS = [
    r"C:/Windows/Fonts/arialbd.ttf",
    r"C:/Windows/Fonts/arial.ttf",
    r"C:/Windows/Fonts/calibrib.ttf",
    r"C:/Windows/Fonts/segoeuib.ttf",
]

FONT = next((f for f in FONT_CANDIDATAS if os.path.isfile(f)), None)

# ==========================================================
# FRAGMENTOS SELECCIONADOS PARA LA DEFENSA
# (Las imágenes de prueba –cuadrantes, certificado NO CONFORME, lesiones–
#  se aportan APARTE, como anexo independiente; no se muestran en el vídeo).
# Cada proyecto: (nombre SRT, posibles nombres de audio, título, [fragmentos])
# Cada fragmento: (id, inicio, fin, título, descripción)
# ==========================================================
PROYECTOS = [
    {
        "srt": "25-05-2026-Vitalia",
        "audio": ["25-05-2026-Vitalia"],
        "titulo": "Presión para no ir a urgencias y baja voluntaria (25-05-2026)",
        "fragmentos": [
            ("A1", "00:00:19.000", "00:00:29.000",
             "ADVERTENCIA DE COBRO POR URGENCIAS",
             "Se advierte a Janeth de que si acude a urgencias puede recibir un recibo o factura por la atención."),
            ("A2", "00:01:25.000", "00:01:40.960",
             "REITERACIÓN: FACTURA DE UNOS 300 EUROS (CASO ARTURO)",
             "Se repite la advertencia de que el hospital puede cobrar la atención, citando el caso de un compañero, Arturo."),
            ("A3", "00:03:00.380", "00:04:27.360",
             "REITERACIÓN DE FACTURA HOSPITALARIA",
             "Se insiste en el cobro y se relata el caso de Arturo con importe aproximado de trescientos euros."),
            ("A4", "00:09:29.000", "00:10:00.720",
             "NUEVA ADVERTENCIA DE COBRO",
             "Se vuelve a condicionar su decisión de buscar atención sanitaria con el argumento del cobro."),
            ("A5", "00:08:11.000", "00:09:30.060",
             "MINIMIZACIÓN DEL GRUPO Y MENCIÓN A LA BAJA VOLUNTARIA",
             "Se califica el grupo como 'light', se minimiza el dolor y se plantea la baja voluntaria."),
            ("A6", "00:11:15.960", "00:12:17.420",
             "SUGERENCIA DE CAMBIO DE TRABAJO (TELETRABAJO)",
             "Se sugiere a Janeth buscar un teletrabajo o trabajo de teleoperadora y replantear su continuidad."),
            ("A7", "00:12:17.440", "00:13:41.144",
             "MINIMIZACIÓN DE LA ADAPTACIÓN ('ES UN FAVOR')",
             "Se cuestiona la adaptación del puesto y se dice que el grupo es un favor de la empresa."),
            ("A8", "00:15:11.504", "00:15:56.264",
             "DISCRECIONALIDAD DE LA EMPRESA SOBRE EL GRUPO",
             "La dirección afirma que la organización y el grupo corresponden a la empresa."),
            ("A9", "00:15:56.304", "00:17:35.764",
             "AMENAZA ECONÓMICA: 500 A 700 EUROS",
             "Se reitera que el hospital puede facturar entre quinientos y setecientos euros por urgencias."),
            ("A10", "00:17:37.004", "00:18:40.076",
             "SUGERENCIA DIRECTA DE BAJA VOLUNTARIA",
             "Se plantea expresamente causar baja voluntaria como salida y se dice que físicamente no está para trabajo físico."),
            ("A11", "00:02:19.080", "00:02:43.460",
             "RONDAS PESADAS CON DOLOR",
             "Janeth manifiesta que le asignan rondas y tareas de carga que le producen dolor intenso."),
            ("A12", "00:04:48.200", "00:05:18.780",
             "EXPOSICIÓN DE DATOS MÉDICOS ANTE TERCERO",
             "Se informa a un tercero sobre su IT, tribunal de incapacidad y baja delante de ella."),
        ],
    },
    {
        "srt": "15-06-2026-Vitalia-3",
        "audio": ["15-06-2026-Vitalia-3"],
        "titulo": "Presión para firmar el documento de adaptación (15-06-2026)",
        "fragmentos": [
            ("B1", "00:29:50.000", "00:31:00.000",
             "«SI FIRMAS NO CONFORME, NO SE TE APLICA NINGUNA ADAPTACIÓN»",
             "Se condiciona la protección de su salud a la firma 'conforme', falseando los efectos de firmar 'no conforme'."),
            ("B2", "00:34:15.000", "00:35:10.000",
             "PRESIÓN PARA FIRMAR CONFORME",
             "Se reitera que si firma como no conforme no se le aplicará ninguna adaptación."),
            ("B3", "00:35:50.000", "00:36:15.000",
             "ADVERTENCIA DEL COMITÉ: NO ROMPER COPIAS",
             "Se advierte a Janeth que nunca rompa sus copias de los documentos."),
            ("B4", "00:38:00.000", "00:38:20.000",
             "REIMPRESIÓN: «ESTOS SON LOS NUEVOS QUE VAS A FIRMAR CONFORME»",
             "Tras firmar 'no conforme', se reimprimen los documentos y se le hace firmar de nuevo 'conforme'."),
            ("B5", "00:40:05.000", "00:40:30.000",
             "FIRMA FINAL DE LA ADAPTACIÓN",
             "Se entrega la copia y se da por firmada la adaptación tras la presión."),
        ],
    },
    {
        "srt": "15-06-2026-Vitalia-1",
        "audio": ["15-06-2026-Vitalia-1"],
        "titulo": "Regreso al grupo con la usuaria agresiva (15-06-2026)",
        "fragmentos": [
            ("C1", "00:00:10.000", "00:00:25.000",
             "USUARIA AGRESIVA EN EL GRUPO",
             "Janeth relata que le tocó con Ángeles Calleja, la usuaria que ya le dañó la mano."),
        ],
    },
    {
        "srt": "cita-prevencion-quiron",
        "audio": ["cita-prevencion-quiron"],
        "titulo": "Reconocimiento de prevención: «no apta» y «despido procedente» (03-06-2026)",
        "fragmentos": [
            ("D1", "00:28:40.000", "00:29:10.000",
             "«NO APTO: NO PUEDES HACER NADA DE TU PUESTO»",
             "El médico de prevención reconoce que con las limitaciones documentadas no puede cumplir su puesto."),
            ("D2", "00:30:20.000", "00:30:40.000",
             "«…Y LLEGARSE A UN DESPIDO PROCEDENTE»",
             "El médico advierte de la posible consecuencia de un despido procedente."),
            ("D3", "00:31:15.000", "00:31:50.000",
             "«NO PUEDES CUMPLIR CON TU PUESTO… DESPIDO PROCEDENTE»",
             "Se insiste en que, según los informes, no puede cumplir su puesto de trabajo."),
            ("D4", "00:33:35.000", "00:34:00.000",
             "«ES UNA CONSECUENCIA DIRECTA PARA TI»",
             "Se le confirma que el despido procedente sería una consecuencia directa para ella."),
        ],
    },
    {
        "srt": "08-09-2026-Vitalia-2",
        "audio": ["08-09-2026-Vitalia-2"],
        "titulo": "Negativa de la hoja de derivación a la Mutua (08-09-2026)",
        "fragmentos": [
            ("E1", "00:07:40.000", "00:08:10.000",
             "NEGATIVA DEL PARTE DE ACCIDENTE",
             "Se niega a Janeth la hoja de derivación a la Mutua y se dice que no se ha hecho daño."),
        ],
    },
    {
        "srt": "08-09-2026-Vitalia-3",
        "audio": ["08-09-2026-Vitalia-3"],
        "titulo": "«No es un accidente de trabajo» y descalificación del testimonio (08-09-2026)",
        "fragmentos": [
            ("F1", "00:02:00.000", "00:02:25.000",
             "«LO TUYO NO ES UN ACCIDENTE DE TRABAJO»",
             "Se niega la naturaleza laboral de la lesión."),
            ("F2", "00:04:45.000", "00:05:25.000",
             "NEGATIVA A INCLUIR A LA RESIDENTE ELENA EN EL PARTE",
             "Se rechaza investigar y tramitar lo ocurrido con la residente."),
            ("F3", "00:07:35.000", "00:08:40.000",
             "«A LA MUTUA SE VA POR UN ACCIDENTE… NO POR UNA DOLENCIA CRÓNICA»",
             "Se la deriva al médico de cabecera y se califica su lesión como dolencia crónica."),
            ("F4", "00:09:05.000", "00:09:30.000",
             "«TU TESTIMONIO SE CONTRADICE»",
             "Se descalifica su versión durante el interrogatorio."),
            ("F5", "00:07:05.000", "00:07:20.000",
             "«TE HAS HECHO DAÑO… PORQUE TÚ HAS QUERIDO»",
             "Se le atribuye la culpa de su propia lesión por haber ayudado a una compañera."),
        ],
    },
    {
        "srt": "08-07-2026-Vitalia",
        "audio": ["08-07-2026-Vitalia"],
        "titulo": "Presión sobre justificantes y cargas de trabajo (08-07-2026)",
        "fragmentos": [
            ("G1", "00:11:35.000", "00:12:00.000",
             "«SI NO, LO TENEMOS QUE MANDAR COMO FALTAS INJUSTIFICADAS»",
             "Se amenaza con faltas injustificadas por no aportar justificantes médicos."),
            ("G2", "00:07:20.000", "00:07:40.000",
             "PRESIÓN: «LE CARGAS A TUS COMPAÑERAS»",
             "Se culpabiliza a Janeth de la carga de trabajo de las compañeras."),
            ("G3", "00:01:40.000", "00:02:10.000",
             "«NO TE PUEDES NEGAR A REALIZAR LAS FUNCIONES…»",
             "Se prepara el terreno para imputarle una negativa a funciones."),
        ],
    },
    {
        "srt": "05-04-2026-Vitalia",
        "audio": ["05-04-2026-Vitalia"],
        "titulo": "Relato del accidente de trabajo del 05-04-2026",
        "fragmentos": [
            ("H1", "00:01:58.400", "00:03:10.000",
             "RELATO DEL ACCIDENTE EN LA DUCHA",
             "Janeth relata cómo sujetó a la residente para que no se golpeara la cara con el lavabo."),
            ("H2", "00:03:10.000", "00:03:44.740",
             "RECAÍDA DE HOMBRO Y MANO",
             "Relata la recaída del hombro izquierdo y de la mano derecha lesionados."),
        ],
    },
    {
        "srt": "04-08-2026-Vitalia",
        "audio": ["04-08-2026-Vitalia"],
        "titulo": "Instrucción del centro sobre el uso de la grúa (04-08-2026)",
        "fragmentos": [
            ("I1", "00:02:50.000", "00:03:26.000",
             "INSTRUCCIÓN: LOS TRASLADOS DE RIESGO SE HACEN CON GRÚA",
             "La supervisión reconoce que para los traslados que lo requieren 'se utiliza la grúa, para eso las tenemos'."),
        ],
    },
]

# ==========================================================
# UTILIDADES (base del script original)
# ==========================================================
def run(cmd):
    print(">>", " ".join(map(str, cmd)))
    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print("\n--- STDOUT ---"); print(r.stdout)
        print("\n--- STDERR ---"); print(r.stderr)
        raise subprocess.CalledProcessError(r.returncode, cmd)
    return r


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def srt_time_to_seconds(value):
    value = value.strip().replace(",", ".")
    h, m, s = value.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def seconds_to_srt(value):
    value = max(0.0, float(value))
    total_ms = int(round(value * 1000))
    hh, rem = divmod(total_ms, 3600000)
    mm, rem = divmod(rem, 60000)
    ss, ms = divmod(rem, 1000)
    return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"


def seconds_to_hhmmss(value):
    value = max(0, int(round(value)))
    h, rem = divmod(value, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def segundos_a_legible(seg):
    seg = float(seg)
    if seg < 60:
        return f"{seg:.1f} s".replace(".", ",")
    m, s = divmod(int(round(seg)), 60)
    return f"{m} min {s:02d} s"


def limpiar_unicode(texto):
    texto = unicodedata.normalize("NFKC", texto)
    reemplazos = {
        "\ufeff": "", "\ufffd": "", "\u00a0": " ", "\u200b": "",
        "\u200c": "", "\u200d": "", "\u2060": "", "\u00ad": "",
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-", "\u2011": "-", "\u2026": "...",
        "\u2212": "-", "\u2028": "\n", "\u2029": "\n", "\u202f": " ",
        "\u205f": " ", "\u3000": " ", "\u00b7": "-", "\u2022": "-",
        "\u25cf": "-", "\u00ab": '"', "\u00bb": '"', "\u2039": "'",
        "\u203a": "'", "\u02bc": "'", "\u201a": ",", "\u201e": '"',
        "\u00b4": "'", "\u0060": "'", "\u02c6": "^", "\u02dc": "~",
        "\u00b0": "o", "\u00aa": "a", "\u00ba": "o",
    }
    for code in range(0x2000, 0x200B):
        reemplazos[chr(code)] = " "
    for viejo, nuevo in reemplazos.items():
        texto = texto.replace(viejo, nuevo)
    texto = "".join(
        c for c in texto
        if c in "\t\n" or (
            not unicodedata.category(c).startswith("C")
            and unicodedata.category(c) not in ("Zl", "Zp")
        )
    )
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\s+\n\s*", "\n", texto)
    return texto.strip()


def envolver(texto, ancho):
    texto = limpiar_unicode(texto)
    return "\n".join(textwrap.wrap(texto, width=ancho,
                                   break_long_words=False,
                                   break_on_hyphens=False))


def envolver_subtitulo(texto, ancho=SUBTITLE_WRAP):
    texto = limpiar_unicode(texto).replace("\n", " ")
    texto = re.sub(r"\s+", " ", texto).strip()
    if not texto:
        return ""
    return "\n".join(textwrap.wrap(texto, width=ancho,
                                   break_long_words=False,
                                   break_on_hyphens=False))


def escribir_texto(path, contenido):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(limpiar_unicode(contenido))


def path_filtro(path):
    path = os.path.abspath(path).replace("\\", "/")
    return path.replace(":", r"\:").replace("'", r"\'")


def _leer_lineas(path):
    with open(path, "r", encoding="utf-8") as f:
        return [l.rstrip("\n") for l in f]


def _esc_drawtext(s):
    return (s.replace("\\", r"\\").replace(":", r"\:")
             .replace("'", r"\'").replace("%", r"\%"))


def drawtext_bloque(font_path, txt_path, fontsize, color, y_inicial,
                    line_spacing=5, borderw=0, bordercolor="black@0.45",
                    align="center"):
    font_esc = path_filtro(font_path)
    lineas = _leer_lineas(txt_path)
    altura = fontsize + line_spacing
    filtros = []
    y = y_inicial
    for linea in lineas:
        if linea.strip() == "":
            y += altura
            continue
        esc = _esc_drawtext(linea)
        f = (f"drawtext=fontfile='{font_esc}':text='{esc}':"
             f"fontcolor={color}:fontsize={fontsize}:")
        if align == "center":
            f += f"x=(w-text_w)/2:y={y}"
        elif align == "right":
            f += f"x=w-text_w-22:y={y}"
        else:
            f += f"x=22:y={y}"
        if borderw:
            f += f":borderw={borderw}:bordercolor={bordercolor}"
        filtros.append(f)
        y += altura
    return filtros


# ==========================================================
# SRT
# ==========================================================
def parse_srt(path):
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        raw = f.read()
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    bloques = [b for b in raw.split("\n\n") if b.strip()]
    items = []
    for bloque in bloques:
        lineas = bloque.split("\n")
        idx_tiempo = next((i for i, l in enumerate(lineas) if "-->" in l), None)
        if idx_tiempo is None:
            continue
        try:
            ini_s, fin_s = [x.strip() for x in lineas[idx_tiempo].split("-->", 1)]
            ini = srt_time_to_seconds(ini_s)
            fin = srt_time_to_seconds(fin_s)
        except (ValueError, TypeError):
            continue
        texto = limpiar_unicode(" ".join(lineas[idx_tiempo + 1:]).strip())
        if not texto or fin <= ini:
            continue
        items.append((ini, fin, texto))
    return sorted(items, key=lambda x: x[0])


def ajustar_recorte(srt_items, seleccionado_inicio, seleccionado_fin):
    objetivo_inicio = max(0.0, seleccionado_inicio - CONTEXT_BEFORE)
    objetivo_fin = seleccionado_fin + CONTEXT_AFTER
    if not srt_items:
        return objetivo_inicio, objetivo_fin
    for ini, fin, _ in srt_items:
        if ini <= objetivo_inicio < fin:
            clip_inicio = ini
            break
    else:
        anteriores = [x for x in srt_items if x[1] <= objetivo_inicio]
        posteriores = [x for x in srt_items if x[0] > objetivo_inicio]
        if posteriores and not anteriores:
            clip_inicio = posteriores[0][0]
        elif anteriores:
            clip_inicio = anteriores[-1][0]
        else:
            clip_inicio = srt_items[0][0]
    clip_fin = None
    for ini, fin, _ in srt_items:
        if ini < objetivo_fin <= fin:
            clip_fin = fin
            break
    if clip_fin is None:
        siguientes = [x for x in srt_items if x[0] >= objetivo_fin]
        anteriores = [x for x in srt_items if x[1] <= objetivo_fin]
        if anteriores:
            clip_fin = anteriores[-1][1]
        elif siguientes:
            clip_fin = siguientes[0][1]
        else:
            clip_fin = srt_items[-1][1]
    if clip_fin <= clip_inicio:
        clip_fin = max(clip_inicio + 1.0, objetivo_fin)
    return clip_inicio, clip_fin


def extraer_srt_ventana(srt_items, clip_inicio, clip_fin):
    out = []
    numero = 1
    duracion = clip_fin - clip_inicio
    for ini, fin, texto in srt_items:
        if fin <= clip_inicio or ini >= clip_fin:
            continue
        ini_rel = max(0.0, max(ini, clip_inicio) - clip_inicio)
        fin_rel = min(duracion, min(fin, clip_fin) - clip_inicio)
        if fin_rel <= ini_rel:
            continue
        texto_wrapped = envolver_subtitulo(texto, SUBTITLE_WRAP)
        out.append(f"{numero}\n"
                   f"{seconds_to_srt(ini_rel)} --> {seconds_to_srt(fin_rel)}\n"
                   f"{texto_wrapped}\n")
        numero += 1
    return "\n".join(out)


# ==========================================================
# VÍDEO
# ==========================================================
def construir_video_filter(txt_fragmento, txt_titulo, txt_desc,
                           txt_hora, txt_archivo, duracion):
    fade_out_start = max(0.0, duracion - FADE)
    filtros = [
        f"drawbox=x=0:y=0:w={W}:h={H}:color=0x111111:t=fill",
        f"drawbox=x=0:y=0:w={W}:h={HEADER_H}:color=black@0.82:t=fill",
        f"drawbox=x=0:y={HEADER_H-4}:w={W}:h=4:color=0xD6A84F:t=fill",
        f"drawbox=x=0:y=164:w={W}:h=4:color=0xD6A84F:t=fill",
    ]
    filtros += drawtext_bloque(FONT, txt_fragmento, 17, "0xD6A84F",
                               10, 2, align="center")
    filtros += drawtext_bloque(FONT, txt_titulo, TITLE_SIZE, "white",
                               36, 5, borderw=1,
                               bordercolor="black@0.45", align="center")
    filtros += drawtext_bloque(FONT, txt_desc, DESC_SIZE, "0xD8D8D8",
                               114, 4, align="center")
    filtros += drawtext_bloque(FONT, txt_hora, 15, "0xE6E6E6",
                               176, 2, align="right")
    filtros += drawtext_bloque(FONT, txt_archivo, 13, "0x9F9F9F",
                               198, 2, align="right")
    filtros += [f"fade=t=in:st=0:d={FADE}",
                f"fade=t=out:st={fade_out_start}:d={FADE}"]
    return ",".join(filtros)


def construir_subtitulos(srt_path):
    return (
        f"subtitles='{path_filtro(srt_path)}':charenc=UTF-8:"
        "force_style='FontName=Arial,"
        f"FontSize={SUBTITLE_SIZE},Bold=1,"
        "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
        "BackColour=&H99000000,BorderStyle=3,Outline=1,Shadow=0,"
        "Alignment=2,MarginL=90,MarginR=90,MarginV=30,WrapStyle=0'"
    )


def generar_clip(audio, srt_items, frag, outdir, total, duracion_total_audio,
                 nombre_audio):
    fid, ini_txt, fin_txt, titulo, desc = frag
    seleccionado_inicio = srt_time_to_seconds(ini_txt)
    seleccionado_fin = srt_time_to_seconds(fin_txt)
    clip_inicio, clip_fin = ajustar_recorte(srt_items, seleccionado_inicio,
                                            seleccionado_fin)
    duracion = clip_fin - clip_inicio

    srt_clip = os.path.abspath(os.path.join(outdir, f"{fid}.srt"))
    escribir_texto(srt_clip, extraer_srt_ventana(srt_items, clip_inicio, clip_fin))

    txt_fragmento = os.path.abspath(os.path.join(outdir, f"{fid}_fragmento.txt"))
    txt_titulo = os.path.abspath(os.path.join(outdir, f"{fid}_titulo.txt"))
    txt_desc = os.path.abspath(os.path.join(outdir, f"{fid}_desc.txt"))
    txt_hora = os.path.abspath(os.path.join(outdir, f"{fid}_hora.txt"))
    txt_archivo = os.path.abspath(os.path.join(outdir, f"{fid}_archivo.txt"))

    escribir_texto(txt_fragmento, f"FRAGMENTO {fid} / {total:02d}")
    escribir_texto(txt_titulo, envolver(titulo.upper(), 52))
    escribir_texto(txt_desc, envolver(desc, 76))
    escribir_texto(txt_hora,
                   f"INICIO {seconds_to_hhmmss(clip_inicio)}  -  "
                   f"DURACION {segundos_a_legible(duracion)}  -  "
                   f"AUDIO TOTAL {segundos_a_legible(duracion_total_audio)}")
    escribir_texto(txt_archivo, f"ARCHIVO: {nombre_audio}")

    vf = (construir_video_filter(txt_fragmento, txt_titulo, txt_desc,
                                 txt_hora, txt_archivo, duracion)
          + "," + construir_subtitulos(srt_clip))

    filter_script = os.path.abspath(os.path.join(outdir, f"{fid}_filter.txt"))
    escribir_texto(filter_script,
                   f"[0:v]{vf}[v];[1:a]aresample={AUDIO_SR},volume=2.0[a]")

    nombre = re.sub(r"[^A-Za-z0-9_-]+", "_",
                    unicodedata.normalize("NFKD", titulo)
                    .encode("ascii", "ignore").decode("ascii")).strip("_")[:48]
    out_mp4 = os.path.join(outdir, f"{fid}_{nombre}.mp4")

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i",
        f"color=c=0x111111:s={W}x{H}:r={FPS}:d={duracion}",
        "-ss", f"{clip_inicio:.3f}", "-t", f"{duracion:.3f}", "-i", audio,
        "-filter_complex_script", filter_script,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", VIDEO_PRESET, "-crf", str(VIDEO_CRF),
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-ar", str(AUDIO_SR), "-ac", "2",
        "-shortest", "-movflags", "+faststart", out_mp4,
    ]
    run(cmd)
    return {
        "id": fid, "titulo": titulo, "descripcion": desc,
        "seleccion_inicio": ini_txt, "seleccion_fin": fin_txt,
        "recorte_final_inicio": seconds_to_hhmmss(clip_inicio),
        "recorte_final_fin": seconds_to_hhmmss(clip_fin),
        "duracion_segundos": round(duracion, 3),
        "archivo": os.path.abspath(out_mp4),
        "sha256": sha256_file(out_mp4),
    }


def generar_portada(outdir, texto_fecha=""):
    duracion = 4.0
    txt_titulo = os.path.abspath(os.path.join(outdir, "00_titulo.txt"))
    txt_desc = os.path.abspath(os.path.join(outdir, "00_desc.txt"))
    txt_fecha = os.path.abspath(os.path.join(outdir, "00_fecha.txt"))
    txt_duracion = os.path.abspath(os.path.join(outdir, "00_duracion.txt"))

    escribir_texto(txt_titulo, "RESPUESTA A LA DENUNCIA")
    escribir_texto(txt_desc, envolver(
        "Audios y transcripciones de prueba - Defensa de Dña. Janeth "
        "Soraya Sánchez Ovalle - Expediente disciplinario nº 174609753", 62))
    escribir_texto(txt_fecha, texto_fecha or
                   "Grabaciones: abril a septiembre de 2026 - Residencia Vitalia")
    escribir_texto(txt_duracion,
                   "Fragmentos de audio con subtítulos - Transcripciones íntegras adjuntas")

    vf_partes = [
        f"drawbox=x=0:y=0:w={W}:h={H}:color=0x111111:t=fill",
        f"drawbox=x=0:y=208:w={W}:h=4:color=0xD6A84F:t=fill",
    ]
    vf_partes += drawtext_bloque(FONT, txt_titulo, 56, "white", 130, 8, align="center")
    vf_partes += drawtext_bloque(FONT, txt_desc, 28, "0xD8D8D8", 242, 9, align="center")
    vf_partes += drawtext_bloque(FONT, txt_fecha, 20, "0x9F9F9F", 420, 6, align="center")
    vf_partes += drawtext_bloque(FONT, txt_duracion, 18, "0x9F9F9F", 458, 6, align="center")
    vf_partes += [f"fade=t=in:st=0:d={FADE}",
                  f"fade=t=out:st={max(0, duracion-FADE)}:d={FADE}"]

    out = os.path.abspath(os.path.join(outdir, "00_PORTADA.mp4"))
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x111111:s={W}x{H}:r={FPS}:d={duracion}",
        "-f", "lavfi", "-i", f"anullsrc=r={AUDIO_SR}:cl=stereo",
        "-filter_complex", f"[0:v]{','.join(vf_partes)}[v]",
        "-map", "[v]", "-map", "1:a", "-t", str(duracion),
        "-c:v", "libx264", "-preset", VIDEO_PRESET, "-crf", str(VIDEO_CRF),
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-ar", str(AUDIO_SR), "-ac", "2",
        "-movflags", "+faststart", out,
    ]
    run(cmd)
    return out


def generar_separador(fid, titulo, descripcion, index, total, outdir):
    txt_frag = os.path.abspath(os.path.join(outdir, f"sep_{fid}_frag.txt"))
    txt_titulo = os.path.abspath(os.path.join(outdir, f"sep_{fid}_titulo.txt"))
    txt_desc = os.path.abspath(os.path.join(outdir, f"sep_{fid}_desc.txt"))
    escribir_texto(txt_frag, f"FRAGMENTO {fid} / {total:02d}")
    escribir_texto(txt_titulo, envolver(titulo.upper(), 48))
    escribir_texto(txt_desc, envolver(descripcion, 74))

    vf_partes = [
        f"drawbox=x=0:y=0:w={W}:h={H}:color=0x101010:t=fill",
        f"drawbox=x=0:y=205:w={W}:h=310:color=0x1F1F1F:t=fill",
        f"drawbox=x=0:y=205:w={W}:h=4:color=0xD6A84F:t=fill",
    ]
    vf_partes += drawtext_bloque(FONT, txt_frag, 20, "0xD6A84F", 230, 4, align="center")
    vf_partes += drawtext_bloque(FONT, txt_titulo, 34, "white", 278, 6, align="center")
    vf_partes += drawtext_bloque(FONT, txt_desc, 19, "0xD8D8D8", 382, 6, align="center")
    vf_partes += [f"fade=t=in:st=0:d={FADE}",
                  f"fade=t=out:st={max(0, SEPARATOR_DURATION-FADE)}:d={FADE}"]

    out = os.path.abspath(os.path.join(outdir, f"sep_{fid}.mp4"))
    audio_filter = (
        "[1:a]volume=0.10,afade=t=in:st=0:d=0.02,afade=t=out:st=0.18:d=0.10[t1];"
        "[2:a]volume=0.07,adelay=55,afade=t=out:st=0.18:d=0.10[t2];"
        "[t1][t2]amix=inputs=2:duration=longest,"
        f"apad=pad_dur={SEPARATOR_DURATION-SEPARATOR_TONE_DURATION:.3f},"
        f"atrim=duration={SEPARATOR_DURATION:.3f},"
        f"aresample={AUDIO_SR}[a]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i",
        f"color=c=0x101010:s={W}x{H}:r={FPS}:d={SEPARATOR_DURATION}",
        "-f", "lavfi", "-i",
        f"sine=frequency=740:sample_rate={AUDIO_SR}:duration={SEPARATOR_TONE_DURATION}",
        "-f", "lavfi", "-i",
        f"sine=frequency=1100:sample_rate={AUDIO_SR}:duration={SEPARATOR_TONE_DURATION}",
        "-filter_complex", f"[0:v]{','.join(vf_partes)}[v];{audio_filter}",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", VIDEO_PRESET, "-crf", str(VIDEO_CRF),
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-ar", str(AUDIO_SR), "-ac", "2",
        "-t", str(SEPARATOR_DURATION), "-movflags", "+faststart", out,
    ]
    run(cmd)
    return out


def escapar_concat_path(path):
    path = os.path.abspath(path).replace("\\", "/")
    return path.replace("'", r"'\''")


def unir_videos(archivos, salida, outdir):
    lista = os.path.abspath(os.path.join(outdir, "concat.txt"))
    with open(lista, "w", encoding="utf-8", newline="\n") as f:
        for archivo in archivos:
            f.write(f"file '{escapar_concat_path(archivo)}'\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lista,
         "-c", "copy", "-movflags", "+faststart", salida])
    return salida


# ==========================================================
# SPLIT DE CONTENIDO_UNIDO.TXT EN SRT INDIVIDUALES
# ==========================================================
def dividir_contenido_unido(path=CONTENIDO_UNIDO, outdir=SRT_DIR):
    os.makedirs(outdir, exist_ok=True)
    if not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        raw = f.read().replace("\r\n", "\n").replace("\r", "\n")
    patron = re.compile(
        r"={10,}\nARCHIVO:\s*(.+?)\n={10,}\n(.*?)(?=\n={10,}\nARCHIVO:|\Z)",
        re.DOTALL)
    generados = {}
    for m in patron.finditer(raw):
        nombre = m.group(1).strip()
        cuerpo = m.group(2).strip()
        if not cuerpo:
            continue
        ruta = os.path.join(outdir, f"{nombre}.srt")
        with open(ruta, "w", encoding="utf-8", newline="\n") as f:
            f.write(cuerpo + "\n")
        generados[nombre] = ruta
    return generados


def buscar_audio(nombres, carpetas=(".", "audios", "audio")):
    for carpeta in carpetas:
        for nombre in nombres:
            for ext in EXTENSIONES_AUDIO:
                ruta = os.path.join(carpeta, nombre + ext)
                if os.path.isfile(ruta):
                    return ruta
    return None


def buscar_srt(nombre, srt_generados):
    for carpeta in (".", SRT_DIR):
        ruta = os.path.join(carpeta, f"{nombre}.srt")
        if os.path.isfile(ruta):
            return ruta
    return srt_generados.get(nombre)


def escribir_indice(proyectos_estado, outdir, ruta="FRAGMENTOS_SELECCIONADOS.md"):
    lineas = [
        "# FRAGMENTOS SELECCIONADOS PARA EL VÍDEO DE PRUEBAS",
        "",
        "| Proyecto | Nº | Título | Inicio | Fin | Estado del audio |",
        "|----------|----|--------|--------|-----|------------------|",
    ]
    for estado in proyectos_estado:
        for frag in estado["fragmentos"]:
            fid, ini, fin, titulo, _ = frag
            lineas.append(
                f"| {estado['titulo']} | {fid} | {titulo} | {ini} | {fin} | "
                f"{'OK: ' + estado['audio'] if estado['audio'] else 'AUDIO NO ENCONTRADO'} |")
    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lineas) + "\n")
    return os.path.abspath(ruta)


# ==========================================================
# MAIN
# ==========================================================
def main():
    solo_srt = "--only-srt" in sys.argv
    solo_lista = "--list" in sys.argv

    if FONT is None:
        raise SystemExit("No encuentro ninguna fuente TTF en C:/Windows/Fonts/")

    print("=" * 60)
    print("PRUEBAS AUDIOVISUALES - RESPUESTA A LA DENUNCIA")
    print("=" * 60)

    srt_generados = dividir_contenido_unido()
    print(f"SRT individuales generados a partir de {CONTENIDO_UNIDO}: "
          f"{len(srt_generados)}")

    estados = []
    for proy in PROYECTOS:
        audio = buscar_audio(proy["audio"])
        srt = buscar_srt(proy["srt"], srt_generados)
        estados.append({
            "srt": proy["srt"],
            "srt_path": srt,
            "audio": audio,
            "titulo": proy["titulo"],
            "fragmentos": proy["fragmentos"],
        })

    indice = escribir_indice(estados, OUTDIR)
    print(f"Índice de fragmentos: {indice}")

    if solo_lista:
        for e in estados:
            print(f"\n--- {e['titulo']} ---")
            for frag in e["fragmentos"]:
                print(f"  {frag[0]}: {frag[3]} ({frag[1]} -> {frag[2]})")
        return

    if solo_srt:
        print("Modo --only-srt: no se genera vídeo.")
        return

    os.makedirs(OUTDIR, exist_ok=True)

    faltantes = [e["titulo"] for e in estados if not e["audio"] or not e["srt_path"]]
    if faltantes:
        print("\nAVISO: no se encontraron audio o subtítulos para:")
        for f in faltantes:
            print("  -", f)
        print("Coloca los audios (m4a/mp3/wav) en esta carpeta o en .\\audios "
              "y vuelve a ejecutar el script.\n")

    procesables = [e for e in estados if e["audio"] and e["srt_path"]]
    if not procesables:
        print("No hay proyectos procesables. Se dejan los SRT y el índice.")
        return

    clips = []
    separadores = []
    portada = generar_portada(OUTDIR)

    for e in procesables:
        srt_items = parse_srt(e["srt_path"])
        if not srt_items:
            print(f"Sin bloques SRT válidos: {e['srt_path']}")
            continue
        duracion_total = srt_items[-1][1]
        total = len(e["fragmentos"])
        for pos, frag in enumerate(e["fragmentos"], start=1):
            print(f"\n=== {frag[0]}: {frag[3]} ===")
            try:
                clip = generar_clip(e["audio"], srt_items, frag, OUTDIR,
                                    total, duracion_total,
                                    os.path.basename(e["audio"]))
                clips.append(clip)
                separador = generar_separador(frag[0], frag[3], frag[4],
                                              pos, total, OUTDIR)
                separadores.append(separador)
            except subprocess.CalledProcessError as ex:
                print(f"ERROR generando {frag[0]}: {ex}")

    if not clips:
        print("No se generó ningún clip.")
        return

    secuencia = [portada]
    for sep, clip in zip(separadores, clips):
        secuencia.extend([sep, clip["archivo"]])

    final = os.path.abspath(os.path.join(OUTDIR, "PRUEBAS_RESPUESTA_DENUNCIA.mp4"))
    unir_videos(secuencia, final, OUTDIR)

    meta = {
        "expediente": "174609753",
        "trabajadora": "Janeth Soraya Sánchez Ovalle",
        "srt_generados": srt_generados,
        "proyectos": [
            {"srt": e["srt"], "audio": e["audio"], "titulo": e["titulo"],
             "fragmentos": [list(f) for f in e["fragmentos"]]}
            for e in estados
        ],
        "clips": clips,
        "video_final": final,
        "sha256_video_final": sha256_file(final),
    }
    with open(os.path.join(OUTDIR, "metadata.json"), "w",
              encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("LISTO")
    print("Vídeo final:", final)
    print("Carpeta:", os.path.abspath(OUTDIR))
    print("=" * 60)


if __name__ == "__main__":
    main()
