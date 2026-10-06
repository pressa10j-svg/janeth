import os
import json
import hashlib
import subprocess
import textwrap
import unicodedata
import re

# ==========================================================
# CONFIGURACIÓN
# ==========================================================
AUDIO_IN = "25-05-2026-Vitalia.m4a"
SRT_IN = "25-05-2026-Vitalia.srt"
SRT_FALLBACK = "25-05-2026-Vitalia.txt"

OUTDIR = "video_janeth_mejorado"

W, H = 1280, 720
FPS = 25
AUDIO_SR = 44100
VIDEO_CRF = 20
VIDEO_PRESET = "medium"
AUDIO_BITRATE = "160k"

CONTEXT_BEFORE = 1.8
CONTEXT_AFTER = 0.8

SEPARATOR_DURATION = 1.8
SEPARATOR_TONE_DURATION = 0.28

# Apariencia.
HEADER_H = 220
TITLE_SIZE = 30
DESC_SIZE = 19
SUBTITLE_SIZE = 20
FADE = 0.18

SUBTITLE_WRAP = 60

# Nombre visible del archivo de audio (para mostrarlo en el vídeo).
NOMBRE_ARCHIVO_AUDIO = os.path.basename(AUDIO_IN)

FONT_CANDIDATAS = [
    r"C:/Windows/Fonts/arialbd.ttf",
    r"C:/Windows/Fonts/arial.ttf",
    r"C:/Windows/Fonts/calibrib.ttf",
    r"C:/Windows/Fonts/segoeuib.ttf",
]

FONT = next((f for f in FONT_CANDIDATAS if os.path.isfile(f)), None)
if FONT is None:
    raise SystemExit("No encuentro ninguna fuente TTF en C:/Windows/Fonts/")


# ==========================================================
# FRAGMENTOS SELECCIONADOS
# ==========================================================
FRAGMENTOS = [
    ("01", "00:00:12.460", "00:01:40.960",
     "ADVERTENCIA DE COBRO POR URGENCIAS",
     "Se indica a Janeth que si acude a urgencias puede recibir un recibo o factura por la atención, citando el caso de un compañero, Arturo."),
    ("02", "00:03:00.380", "00:04:27.360",
     "REITERACIÓN DE FACTURA HOSPITALARIA",
     "Se repite la advertencia de que el hospital puede cobrar la atención y se menciona una factura de unos trescientos euros a Arturo."),
    ("03", "00:09:30.080", "00:10:00.720",
     "NUEVA ADVERTENCIA DE COBRO",
     "Se insiste en que si acude a urgencias puede ser cobrada, condicionando su decisión de buscar atención."),
    ("04", "00:15:56.304", "00:17:35.764",
     "REITERACIÓN DE AMENAZA ECONÓMICA",
     "Se reitera que el hospital puede facturar entre quinientos y setecientos euros por urgencias, citando de nuevo a Arturo."),
    ("05", "00:02:19.080", "00:02:43.460",
     "RONDAS PESADAS CON DOLOR",
     "Janeth manifiesta que le asignan rondas y tareas de carga que le producen dolor intenso en el hombro."),
    ("06", "00:05:18.800", "00:05:58.780",
     "GRUPO NO ADAPTADO A LIMITACIONES",
     "Janeth expone que tiene limitaciones, que no puede trabajar así y que el grupo asignado le sigue generando recarga."),
    ("07", "00:04:48.200", "00:05:18.780",
     "EXPOSICIÓN DE DATOS MÉDICOS ANTE TERCERO",
     "Isabel informa a Luisa sobre la situación de IT, tribunal de incapacidad y baja de Janeth delante de ella."),
    ("08", "00:08:11.720", "00:09:30.060",
     "MINIMIZACIÓN DE GRUPO Y BAJA VOLUNTARIA",
     "Se califica el grupo como light, se minimiza el dolor de Janeth y se menciona la posibilidad de causar baja voluntaria."),
    ("09", "00:11:15.960", "00:12:17.420",
     "SUGERENCIA DE CAMBIO DE TRABAJO",
     "Se sugiere a Janeth buscar un teletrabajo o trabajo de teleoperadora y replantear su continuidad."),
    ("10", "00:12:17.440", "00:13:41.144",
     "MINIMIZACIÓN DE ADAPTACIÓN Y FAVOR",
     "Se cuestiona la adaptación del puesto, se dice que el grupo es un favor y se menciona que podrían asignarle el grupo dieciséis."),
    ("11", "00:15:11.504", "00:15:56.264",
     "DISCRECIONALIDAD DE LA EMPRESA SOBRE GRUPO",
     "La directora afirma que la organización y el grupo corresponden a la empresa y que intentará dar el grupo más ligero por su patología."),
    ("12", "00:17:37.004", "00:18:40.076",
     "SUGERENCIA DIRECTA DE BAJA VOLUNTARIA",
     "Se plantea expresamente causar baja voluntaria como salida y se dice que físicamente Janeth no está para trabajo físico."),
]


# ==========================================================
# UTILIDADES
# ==========================================================
def run(cmd):
    print(">>", " ".join(map(str, cmd)))
    r = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if r.returncode != 0:
        print("\n--- STDOUT ---")
        print(r.stdout)
        print("\n--- STDERR ---")
        print(r.stderr)
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
    """
    Normaliza el texto para evitar glifos raros y cuadritos en FFmpeg.
    Incluye limpieza de separadores Unicode (Zl, Zp) y espacios tipográficos.
    """
    texto = unicodedata.normalize("NFKC", texto)

    reemplazos = {
        "\ufeff": "",
        "\ufffd": "",
        "\u00a0": " ",
        "\u200b": "",
        "\u200c": "",
        "\u200d": "",
        "\u2060": "",
        "\u00ad": "",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2011": "-",
        "\u2026": "...",
        "\u2212": "-",
        "\u2028": "\n",
        "\u2029": "\n",
        "\u202f": " ",
        "\u205f": " ",
        "\u3000": " ",
        "\u00b7": "-",
        "\u2022": "-",
        "\u25cf": "-",
        "\u00ab": '"',
        "\u00bb": '"',
        "\u2039": "'",
        "\u203a": "'",
        "\u02bc": "'",
        "\u201a": ",",
        "\u201e": '"',
        "\u00b4": "'",
        "\u0060": "'",
        "\u02c6": "^",
        "\u02dc": "~",
        "\u00b0": "o",
        "\u00aa": "a",
        "\u00ba": "o",
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
    return "\n".join(
        textwrap.wrap(
            texto,
            width=ancho,
            break_long_words=False,
            break_on_hyphens=False,
        )
    )


def envolver_subtitulo(texto, ancho=SUBTITLE_WRAP):
    texto = limpiar_unicode(texto).replace("\n", " ")
    texto = re.sub(r"\s+", " ", texto).strip()
    if not texto:
        return ""
    return "\n".join(
        textwrap.wrap(
            texto,
            width=ancho,
            break_long_words=False,
            break_on_hyphens=False,
        )
    )


def escribir_texto(path, contenido):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(limpiar_unicode(contenido))


def path_filtro(path):
    path = os.path.abspath(path).replace("\\", "/")
    return path.replace(":", r"\:").replace("'", r"\'")


# ==========================================================
# DRAWTEXT POR LÍNEAS (evita el bug del \n -> cuadrito)
# ==========================================================
def _leer_lineas(path):
    with open(path, "r", encoding="utf-8") as f:
        return [l.rstrip("\n") for l in f]


def _esc_drawtext(s):
    return (
        s.replace("\\", r"\\")
         .replace(":", r"\:")
         .replace("'", r"\'")
         .replace("%", r"\%")
    )



def drawtext_bloque(
    font_path,          # ruta CRUDA de la TTF (p.ej. "C:/Windows/Fonts/arialbd.ttf")
    txt_path,           # ruta CRUDA del .txt
    fontsize,
    color,
    y_inicial,
    line_spacing=5,
    borderw=0,
    bordercolor="black@0.45",
    align="center",     # "center" | "right" | "left"
):
    """
    Dibuja el texto de un .txt línea a línea.
    Recibe rutas CRUDAS; el escapado para FFmpeg se hace aquí dentro.
    """
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
        f = (
            f"drawtext=fontfile='{font_esc}':text='{esc}':"
            f"fontcolor={color}:fontsize={fontsize}:"
        )
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
        idx_tiempo = next(
            (i for i, linea in enumerate(lineas) if "-->" in linea),
            None,
        )
        if idx_tiempo is None:
            continue

        try:
            ini_s, fin_s = [
                x.strip() for x in lineas[idx_tiempo].split("-->", 1)
            ]
            ini = srt_time_to_seconds(ini_s)
            fin = srt_time_to_seconds(fin_s)
        except (ValueError, TypeError):
            continue

        texto = limpiar_unicode(
            " ".join(lineas[idx_tiempo + 1:]).strip()
        )
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

        ini_rel = max(ini, clip_inicio) - clip_inicio
        fin_rel = min(fin, clip_fin) - clip_inicio

        ini_rel = max(0.0, ini_rel)
        fin_rel = min(duracion, fin_rel)

        if fin_rel <= ini_rel:
            continue

        texto_wrapped = envolver_subtitulo(texto, SUBTITLE_WRAP)

        out.append(
            f"{numero}\n"
            f"{seconds_to_srt(ini_rel)} --> {seconds_to_srt(fin_rel)}\n"
            f"{texto_wrapped}\n"
        )
        numero += 1

    return "\n".join(out)


# ==========================================================
# VÍDEO
# ==========================================================
def construir_video_filter(
    txt_fragmento,
    txt_titulo,
    txt_desc,
    txt_hora,
    txt_archivo,
    duracion,
):
    fade_out_start = max(0.0, duracion - FADE)

    filtros = [
        f"drawbox=x=0:y=0:w={W}:h={H}:color=0x111111:t=fill",
        f"drawbox=x=0:y=0:w={W}:h={HEADER_H}:color=black@0.82:t=fill",
        f"drawbox=x=0:y={HEADER_H-4}:w={W}:h=4:color=0xD6A84F:t=fill",
        f"drawbox=x=0:y=164:w={W}:h=4:color=0xD6A84F:t=fill",
    ]

    # OJO: se pasan rutas CRUDAS (sin path_filtro) y FONT cruda.
    filtros += drawtext_bloque(
        FONT, txt_fragmento, fontsize=17, color="0xD6A84F",
        y_inicial=10, line_spacing=2, align="center",
    )
    filtros += drawtext_bloque(
        FONT, txt_titulo, fontsize=TITLE_SIZE, color="white",
        y_inicial=36, line_spacing=5,
        borderw=1, bordercolor="black@0.45", align="center",
    )
    filtros += drawtext_bloque(
        FONT, txt_desc, fontsize=DESC_SIZE, color="0xD8D8D8",
        y_inicial=114, line_spacing=4, align="center",
    )
    filtros += drawtext_bloque(
        FONT, txt_hora, fontsize=15, color="0xE6E6E6",
        y_inicial=176, line_spacing=2, align="right",
    )
    filtros += drawtext_bloque(
        FONT, txt_archivo, fontsize=13, color="0x9F9F9F",
        y_inicial=198, line_spacing=2, align="right",
    )

    filtros += [
        f"fade=t=in:st=0:d={FADE}",
        f"fade=t=out:st={fade_out_start}:d={FADE}",
    ]

    return ",".join(filtros)

def construir_subtitulos(srt_path):
    return (
        f"subtitles='{path_filtro(srt_path)}':charenc=UTF-8:"
        "force_style='"
        "FontName=Arial,"
        f"FontSize={SUBTITLE_SIZE},"
        "Bold=1,"
        "PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,"
        "BackColour=&H99000000,"
        "BorderStyle=3,"
        "Outline=1,"
        "Shadow=0,"
        "Alignment=2,"
        "MarginL=90,"
        "MarginR=90,"
        "MarginV=30,"
        "WrapStyle=0'"
    )


def generar_clip(audio, srt_items, frag, outdir, total, duracion_total_audio):
    fid, ini_txt, fin_txt, titulo, desc = frag
    seleccionado_inicio = srt_time_to_seconds(ini_txt)
    seleccionado_fin = srt_time_to_seconds(fin_txt)

    clip_inicio, clip_fin = ajustar_recorte(
        srt_items,
        seleccionado_inicio,
        seleccionado_fin,
    )
    duracion = clip_fin - clip_inicio

    srt_clip = os.path.abspath(os.path.join(outdir, f"{fid}.srt"))
    escribir_texto(
        srt_clip,
        extraer_srt_ventana(srt_items, clip_inicio, clip_fin),
    )

    txt_fragmento = os.path.abspath(os.path.join(outdir, f"{fid}_fragmento.txt"))
    txt_titulo = os.path.abspath(os.path.join(outdir, f"{fid}_titulo.txt"))
    txt_desc = os.path.abspath(os.path.join(outdir, f"{fid}_desc.txt"))
    txt_hora = os.path.abspath(os.path.join(outdir, f"{fid}_hora.txt"))
    txt_archivo = os.path.abspath(os.path.join(outdir, f"{fid}_archivo.txt"))

    escribir_texto(txt_fragmento, f"FRAGMENTO {fid} / {total:02d}")
    escribir_texto(txt_titulo, envolver(titulo.upper(), 52))
    escribir_texto(txt_desc, envolver(desc, 76))

    escribir_texto(
        txt_hora,
        f"INICIO {seconds_to_hhmmss(clip_inicio)}  -  "
        f"DURACION {segundos_a_legible(duracion)}  -  "
        f"AUDIO TOTAL {segundos_a_legible(duracion_total_audio)}"
    )

    escribir_texto(txt_archivo, f"ARCHIVO: {NOMBRE_ARCHIVO_AUDIO}")

    vf = (
        construir_video_filter(
            txt_fragmento,
            txt_titulo,
            txt_desc,
            txt_hora,
            txt_archivo,
            duracion,
        )
        + ","
        + construir_subtitulos(srt_clip)
    )

    filter_script = os.path.abspath(
        os.path.join(outdir, f"{fid}_filter.txt")
    )
    escribir_texto(
        filter_script,
        f"[0:v]{vf}[v];[1:a]aresample={AUDIO_SR},volume=2.0[a]",
    )

    nombre = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        unicodedata.normalize("NFKD", titulo)
        .encode("ascii", "ignore")
        .decode("ascii"),
    ).strip("_")[:48]

    out_mp4 = os.path.join(outdir, f"{fid}_{nombre}.mp4")

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i",
        f"color=c=0x111111:s={W}x{H}:r={FPS}:d={duracion}",
        "-ss", f"{clip_inicio:.3f}",
        "-t", f"{duracion:.3f}",
        "-i", audio,
        "-filter_complex_script", filter_script,
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264",
        "-preset", VIDEO_PRESET,
        "-crf", str(VIDEO_CRF),
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        "-c:a", "aac",
        "-b:a", AUDIO_BITRATE,
        "-ar", str(AUDIO_SR),
        "-ac", "2",
        "-shortest",
        "-movflags", "+faststart",
        out_mp4,
    ]

    run(cmd)

    return {
        "id": fid,
        "titulo": titulo,
        "descripcion": desc,
        "seleccion_inicio": ini_txt,
        "seleccion_fin": fin_txt,
        "recorte_final_inicio": seconds_to_hhmmss(clip_inicio),
        "recorte_final_fin": seconds_to_hhmmss(clip_fin),
        "duracion_segundos": round(duracion, 3),
        "archivo": os.path.abspath(out_mp4),
        "sha256": sha256_file(out_mp4),
    }


# ==========================================================
# PORTADA
# ==========================================================
def generar_portada(outdir, duracion_total_audio):
    duracion = 4.0

    txt_titulo = os.path.abspath(os.path.join(outdir, "00_titulo.txt"))
    txt_desc = os.path.abspath(os.path.join(outdir, "00_desc.txt"))
    txt_fecha = os.path.abspath(os.path.join(outdir, "00_fecha.txt"))
    txt_duracion = os.path.abspath(os.path.join(outdir, "00_duracion.txt"))
    txt_archivo = os.path.abspath(os.path.join(outdir, "00_archivo.txt"))

    escribir_texto(txt_titulo, "PRUEBA AUDIOVISUAL")
    escribir_texto(
        txt_desc,
        envolver(
            "Selección de fragmentos de audio para revisión del contexto laboral",
            62,
        ),
    )
    escribir_texto(
        txt_fecha,
        "Audio original - 25-05-2026 - Residencia Vitalia",
    )
    escribir_texto(
        txt_duracion,
        f"Duración del audio original: {segundos_a_legible(duracion_total_audio)}",
    )
    escribir_texto(txt_archivo, f"Archivo: {NOMBRE_ARCHIVO_AUDIO}")

    font = path_filtro(FONT)

    vf_partes = [
        f"drawbox=x=0:y=0:w={W}:h={H}:color=0x111111:t=fill",
        f"drawbox=x=0:y=208:w={W}:h=4:color=0xD6A84F:t=fill",
    ]

    vf_partes += drawtext_bloque(
        FONT, txt_titulo, fontsize=56, color="white",
        y_inicial=130, line_spacing=8, align="center",
    )
    vf_partes += drawtext_bloque(
        FONT, txt_desc, fontsize=28, color="0xD8D8D8",
        y_inicial=242, line_spacing=9, align="center",
    )
    vf_partes += drawtext_bloque(
        FONT, txt_fecha, fontsize=20, color="0x9F9F9F",
        y_inicial=420, line_spacing=6, align="center",
    )
    vf_partes += drawtext_bloque(
        FONT, txt_duracion, fontsize=18, color="0x9F9F9F",
        y_inicial=458, line_spacing=6, align="center",
    )
    vf_partes += drawtext_bloque(
        FONT, txt_archivo, fontsize=16, color="0x7F7F7F",
        y_inicial=492, line_spacing=6, align="center",
    )

    vf_partes += [
        f"fade=t=in:st=0:d={FADE}",
        f"fade=t=out:st={max(0, duracion-FADE)}:d={FADE}",
    ]

    vf = ",".join(vf_partes)

    out = os.path.abspath(os.path.join(outdir, "00_PORTADA.mp4"))

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=0x111111:s={W}x{H}:r={FPS}:d={duracion}",
        "-f", "lavfi",
        "-i", f"anullsrc=r={AUDIO_SR}:cl=stereo",
        "-filter_complex", f"[0:v]{vf}[v]",
        "-map", "[v]",
        "-map", "1:a",
        "-t", str(duracion),
        "-c:v", "libx264",
        "-preset", VIDEO_PRESET,
        "-crf", str(VIDEO_CRF),
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        "-c:a", "aac",
        "-b:a", AUDIO_BITRATE,
        "-ar", str(AUDIO_SR),
        "-ac", "2",
        "-movflags", "+faststart",
        out,
    ]

    run(cmd)
    return out


# ==========================================================
# SEPARADORES CON SONIDO SUAVE
# ==========================================================
def generar_separador(fid, titulo, descripcion, index, total, outdir):
    txt_frag = os.path.abspath(os.path.join(outdir, f"sep_{fid}_frag.txt"))
    txt_titulo = os.path.abspath(os.path.join(outdir, f"sep_{fid}_titulo.txt"))
    txt_desc = os.path.abspath(os.path.join(outdir, f"sep_{fid}_desc.txt"))

    escribir_texto(txt_frag, f"FRAGMENTO {fid} / {total:02d}")
    escribir_texto(txt_titulo, envolver(titulo.upper(), 48))
    escribir_texto(txt_desc, envolver(descripcion, 74))

    font = path_filtro(FONT)

    vf_partes = [
        f"drawbox=x=0:y=0:w={W}:h={H}:color=0x101010:t=fill",
        f"drawbox=x=0:y=205:w={W}:h=310:color=0x1F1F1F:t=fill",
        f"drawbox=x=0:y=205:w={W}:h=4:color=0xD6A84F:t=fill",
    ]

    vf_partes += drawtext_bloque(
        FONT, txt_frag, fontsize=20, color="0xD6A84F",
        y_inicial=230, line_spacing=4, align="center",
    )
    vf_partes += drawtext_bloque(
        FONT, txt_titulo, fontsize=34, color="white",
        y_inicial=278, line_spacing=6, align="center",
    )
    vf_partes += drawtext_bloque(
        FONT, txt_desc, fontsize=19, color="0xD8D8D8",
        y_inicial=382, line_spacing=6, align="center",
    )

    vf_partes += [
        f"fade=t=in:st=0:d={FADE}",
        f"fade=t=out:st={max(0, SEPARATOR_DURATION-FADE)}:d={FADE}",
    ]

    vf = ",".join(vf_partes)

    out = os.path.abspath(os.path.join(outdir, f"sep_{fid}.mp4"))

    audio_filter = (
        "[1:a]volume=0.10,"
        f"afade=t=in:st=0:d=0.02,"
        "afade=t=out:st=0.18:d=0.10[t1];"
        "[2:a]volume=0.07,"
        "adelay=55,"
        "afade=t=out:st=0.18:d=0.10[t2];"
        "[t1][t2]amix=inputs=2:duration=longest,"
        f"apad=pad_dur={SEPARATOR_DURATION-SEPARATOR_TONE_DURATION:.3f},"
        f"atrim=duration={SEPARATOR_DURATION:.3f},"
        f"aresample={AUDIO_SR}[a]"
    )

    filter_complex = f"[0:v]{vf}[v];{audio_filter}"

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i",
        f"color=c=0x101010:s={W}x{H}:r={FPS}:d={SEPARATOR_DURATION}",
        "-f", "lavfi",
        "-i",
        f"sine=frequency=740:sample_rate={AUDIO_SR}:duration={SEPARATOR_TONE_DURATION}",
        "-f", "lavfi",
        "-i",
        f"sine=frequency=1100:sample_rate={AUDIO_SR}:duration={SEPARATOR_TONE_DURATION}",
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264",
        "-preset", VIDEO_PRESET,
        "-crf", str(VIDEO_CRF),
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        "-c:a", "aac",
        "-b:a", AUDIO_BITRATE,
        "-ar", str(AUDIO_SR),
        "-ac", "2",
        "-t", str(SEPARATOR_DURATION),
        "-movflags", "+faststart",
        out,
    ]

    run(cmd)
    return out


# ==========================================================
# CONCATENADO FINAL
# ==========================================================
def escapar_concat_path(path):
    path = os.path.abspath(path).replace("\\", "/")
    return path.replace("'", r"'\''")


def unir_videos(archivos, salida, outdir):
    lista = os.path.abspath(os.path.join(outdir, "concat.txt"))

    with open(lista, "w", encoding="utf-8", newline="\n") as f:
        for archivo in archivos:
            f.write(f"file '{escapar_concat_path(archivo)}'\n")

    run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", lista,
        "-c", "copy",
        "-movflags", "+faststart",
        salida,
    ])

    return salida


# ==========================================================
# MAIN
# ==========================================================
def main():
    os.makedirs(OUTDIR, exist_ok=True)

    if not os.path.isfile(AUDIO_IN):
        raise SystemExit(f"No encuentro el audio: {AUDIO_IN}")

    subtitulos_entrada = SRT_IN
    if not os.path.isfile(subtitulos_entrada):
        if os.path.isfile(SRT_FALLBACK):
            subtitulos_entrada = SRT_FALLBACK
        else:
            raise SystemExit(
                f"No encuentro {SRT_IN} ni {SRT_FALLBACK}"
            )

    print("Fuente usada:", FONT)
    print("Audio:", AUDIO_IN)
    print("Subtítulos:", subtitulos_entrada)
    print("SHA-256 audio:", sha256_file(AUDIO_IN))

    srt_items = parse_srt(subtitulos_entrada)
    print(f"Bloques SRT cargados: {len(srt_items)}")

    if not srt_items:
        raise SystemExit("No se encontraron bloques de subtítulos válidos.")

    duracion_total_audio = srt_items[-1][1]
    print(f"Duración audio (aprox.): {segundos_a_legible(duracion_total_audio)}")

    clips = []
    separadores = []
    todos = len(FRAGMENTOS)

    portada = generar_portada(OUTDIR, duracion_total_audio)

    for pos, frag in enumerate(FRAGMENTOS, start=1):
        print(f"\n=== FRAGMENTO {frag[0]}: {frag[3]} ===")

        clip = generar_clip(
            AUDIO_IN,
            srt_items,
            frag,
            OUTDIR,
            todos,
            duracion_total_audio,
        )
        clips.append(clip)

        print(
            f"Recorte final: {clip['recorte_final_inicio']} -> "
            f"{clip['recorte_final_fin']} "
            f"({clip['duracion_segundos']} s)"
        )

        separador = generar_separador(
            frag[0],
            frag[3],
            frag[4],
            pos,
            todos,
            OUTDIR,
        )
        separadores.append(separador)

    secuencia = [portada]
    for separador, clip in zip(separadores, clips):
        secuencia.extend([separador, clip["archivo"]])

    final = os.path.abspath(os.path.join(OUTDIR, "TODO_JANETH.mp4"))

    unir_videos(secuencia, final, OUTDIR)

    meta = {
        "audio_original": os.path.abspath(AUDIO_IN),
        "sha256_audio_original": sha256_file(AUDIO_IN),
        "duracion_audio_original_segundos": round(duracion_total_audio, 3),
        "subtitulos_originales": os.path.abspath(subtitulos_entrada),
        "context_before": CONTEXT_BEFORE,
        "context_after": CONTEXT_AFTER,
        "separator_duration": SEPARATOR_DURATION,
        "clips": clips,
        "video_final": final,
        "sha256_video_final": sha256_file(final),
    }

    with open(os.path.join(OUTDIR, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print("\n==============================================")
    print("LISTO")
    print("Vídeo final:", final)
    print("Carpeta:", os.path.abspath(OUTDIR))
    print("==============================================")


if __name__ == "__main__":
    main()