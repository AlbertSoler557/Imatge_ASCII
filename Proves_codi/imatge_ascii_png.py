"""
Convertidor d'imatges a ASCII art (versió millorada)
------------------------------------------------------
Ús:
    python3 imatge_ascii.py ruta_imatge.jpg

Opcions:
    --amplada N      amplada en caràcters (per defecte: s'ajusta a la terminal)
    --invertir       inverteix els tons clars/foscos (útil per fons clars)
    --sortida NOM    guarda el resultat en un fitxer de text (.txt)
    --png NOM        guarda el resultat com a imatge (.png). Per defecte, amb
                      el mateix detall que es veu per terminal
    --amplada-png N  (opcional) genera el PNG amb una amplada diferent/major
                      a la de la terminal, per a més detall en la imatge
    --contrast       estira el contrast automàticament (recomanat)
    --color          pinta cada caràcter amb el color original del píxel
    --barreja N      pes de V (HSV) barrejat amb L, de 0.0 (només L) a 1.0 (només V)
                      per defecte 0.0. Prova 0.3-0.5 en fotos amb llums/reflexos
    --neofetch       genera una versió amb color compatible amb neofetch, fent
                      servir només 6 colors (${c1}-${c6}), en lloc de color
                      RGB complet (que trenca el càlcul d'amplada de neofetch)
"""

import sys
import shutil
import argparse
from PIL import Image, ImageOps, ImageDraw, ImageFont

# Caràcters ordenats de més "fosc" (dens) a més "clar" (buit)
# Nota: evitem el símbol '%' perquè trenca eines com neofetch (el processen
# amb printf internament, i '%' hi té significat especial de format)
CARACTERS = "@%#*+=-:. "

RESET = "\033[0m"

RUTA_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def _codi_color(r, g, b):
    """Retorna la seqüència ANSI de color veritable (24 bits) per a un píxel RGB."""
    return f"\033[38;2;{r};{g};{b}m"


def _rgb_a_256(r, g, b):
    """Converteix un color RGB al codi de color més proper de la paleta
    estàndard de 256 colors de terminal (la que neofetch sap interpretar
    correctament a través de --ascii_colors)."""
    passos = [0, 95, 135, 175, 215, 255]

    def _canal(v):
        return min(range(6), key=lambda i: abs(passos[i] - v))

    ri, gi, bi = _canal(r), _canal(g), _canal(b)
    return 16 + 36 * ri + 6 * gi + bi


def generar_dades(ruta, amplada=None, invertir=False, contrast=False, barreja=0.0):
    """Llegeix la imatge i calcula, per a cada 'cel·la' final, quin caràcter
    i quin color li correspon. Retorna les dades en brut, sense encara
    decidir si es mostraran per terminal o es dibuixaran com a PNG."""
    img_original = Image.open(ruta).convert("RGB")

    if amplada is None:
        amplada = shutil.get_terminal_size((100, 24)).columns - 2

    if contrast:
        img_original = ImageOps.autocontrast(img_original)

    relacio = img_original.height / img_original.width
    alcada = max(1, int(amplada * relacio * 0.55))

    img_original = img_original.resize((amplada, alcada))

    img_gris = img_original.convert("L")
    valors_l = list(img_gris.getdata())

    if barreja > 0:
        img_hsv = img_original.convert("HSV")
        valors_v = [v for (_, _, v) in img_hsv.getdata()]
        valors_brillantor = [
            int(round(l * (1 - barreja) + v * barreja))
            for l, v in zip(valors_l, valors_v)
        ]
    else:
        valors_brillantor = valors_l

    colors_rgb = list(img_original.getdata())
    caracters = CARACTERS[::-1] if invertir else CARACTERS

    return amplada, alcada, valors_brillantor, colors_rgb, caracters


def renderitzar_terminal(amplada, alcada, valors_brillantor, colors_rgb, caracters, color=False):
    """Genera el text final (amb o sense codis de color ANSI) per mostrar
    per terminal o guardar en un fitxer .txt."""
    escala = len(caracters)

    if color:
        caracters_pintats = []
        for b_val, (r, g, b) in zip(valors_brillantor, colors_rgb):
            idx = b_val * (escala - 1) // 255
            caracters_pintats.append(f"{_codi_color(r, g, b)}{caracters[idx]}")

        linies = []
        for fila in range(alcada):
            inici = fila * amplada
            fi = inici + amplada
            linia = "".join(caracters_pintats[inici:fi]) + RESET
            linies.append(linia)
        return "\n".join(linies)

    ascii_str = "".join(
        caracters[b_val * (escala - 1) // 255] for b_val in valors_brillantor
    )
    linies = [
        ascii_str[i:i + amplada] for i in range(0, len(ascii_str), amplada)
    ]
    return "\n".join(linies)


def renderitzar_neofetch(amplada, alcada, valors_brillantor, img_colors, caracters):
    """Genera text compatible amb neofetch: en lloc de color RGB per píxel
    (que trenca el càlcul d'amplada de neofetch), redueix la imatge a només
    6 colors representatius i fa servir els marcadors ${c1}-${c6}, que
    neofetch sap reconèixer i ignorar correctament en calcular l'amplada.

    Retorna: (text_generat, llista_de_6_codis_256_per_a_ascii_colors)
    """
    # Reduïm la imatge (ja redimensionada) a només 6 colors representatius
    img_quant = img_colors.quantize(colors=6, method=Image.MEDIANCUT)
    paleta = img_quant.getpalette()
    colors_6 = [tuple(paleta[i * 3: i * 3 + 3]) for i in range(6)]
    idx_colors = list(img_quant.getdata())  # índex 0-5 per a cada píxel

    codis_256 = [_rgb_a_256(*c) for c in colors_6]

    escala = len(caracters)
    caracters_marcats = []
    for b_val, idx_c in zip(valors_brillantor, idx_colors):
        idx_char = b_val * (escala - 1) // 255
        caracters_marcats.append(f"${{c{idx_c + 1}}}{caracters[idx_char]}")

    linies = []
    for fila in range(alcada):
        inici = fila * amplada
        fi = inici + amplada
        linies.append("".join(caracters_marcats[inici:fi]))

    return "\n".join(linies), codis_256


def renderitzar_png(ruta_sortida, amplada, alcada, valors_brillantor, colors_rgb,
                     caracters, color=False, mida_font=14):
    """Dibuixa els mateixos caràcters que es veurien per terminal, però sobre
    un llenç d'imatge, fent servir un tipus de lletra monoespai. El resultat
    es guarda com a PNG: es pot veure a qualsevol mida, copiar, compartir..."""
    try:
        font = ImageFont.truetype(RUTA_FONT, mida_font)
    except OSError:
        font = ImageFont.load_default()

    # Mida real de cada 'cel·la' de caràcter amb aquesta font concreta
    ascent, descent = font.getmetrics()
    alcada_cela = ascent + descent
    amplada_cela = font.getlength("A")

    mida_imatge = (
        int(amplada_cela * amplada),
        int(alcada_cela * alcada),
    )
    img_final = Image.new("RGB", mida_imatge, color=(0, 0, 0))
    draw = ImageDraw.Draw(img_final)

    escala = len(caracters)
    for fila in range(alcada):
        for col in range(amplada):
            idx_pixel = fila * amplada + col
            b_val = valors_brillantor[idx_pixel]
            idx_char = b_val * (escala - 1) // 255
            ch = caracters[idx_char]
            if ch == " ":
                continue

            if color:
                fill = colors_rgb[idx_pixel]
            else:
                fill = (255, 255, 255)

            x = col * amplada_cela
            y = fila * alcada_cela
            draw.text((x, y), ch, font=font, fill=fill)

    img_final.save(ruta_sortida)


def main():
    parser = argparse.ArgumentParser(description="Converteix una imatge en ASCII art")
    parser.add_argument("ruta", help="ruta a la imatge (jpg, png, etc.)")
    parser.add_argument("--amplada", type=int, default=None,
                         help="amplada en caràcters (per defecte: mida de la terminal)")
    parser.add_argument("--invertir", action="store_true", help="inverteix tons")
    parser.add_argument("--sortida", type=str, default=None, help="fitxer de sortida de text (.txt)")
    parser.add_argument("--png", type=str, default=None,
                         help="guarda el resultat com a imatge PNG (mateix detall que la terminal)")
    parser.add_argument("--amplada-png", type=int, default=None,
                         help="amplada en caràcters específica per al PNG (per defecte: la mateixa que --amplada)")
    parser.add_argument("--mida-font", type=int, default=14,
                         help="mida de lletra per al PNG en píxels (per defecte 14)")
    parser.add_argument("--contrast", action="store_true", help="estira el contrast automàticament")
    parser.add_argument("--color", action="store_true", help="pinta cada caràcter amb el seu color original")
    parser.add_argument("--barreja", type=float, default=0.0,
                         help="pes de V(HSV) barrejat amb L, de 0.0 a 1.0 (per defecte 0.0)")
    parser.add_argument("--neofetch", action="store_true",
                         help="genera color compatible amb neofetch (6 colors, marcadors ${c1}-${c6})")
    args = parser.parse_args()

    amplada, alcada, valors_brillantor, colors_rgb, caracters = generar_dades(
        args.ruta, args.amplada, args.invertir, args.contrast, args.barreja
    )

    if args.neofetch:
        # Necessitem la imatge redimensionada (no la llista plana) per fer la quantització de color
        img_tmp = Image.open(args.ruta).convert("RGB")
        if args.contrast:
            img_tmp = ImageOps.autocontrast(img_tmp)
        img_tmp = img_tmp.resize((amplada, alcada))

        text, codis_256 = renderitzar_neofetch(amplada, alcada, valors_brillantor, img_tmp, caracters)
        print(text)
        print(f"\nAfegeix aquesta línia al teu config.conf de neofetch:", file=sys.stderr)
        print(f'ascii_colors=({" ".join(str(c) for c in codis_256)})', file=sys.stderr)

        if args.sortida:
            with open(args.sortida, "w", encoding="utf-8") as f:
                f.write(text + "\n")
            print(f"\nGuardat com a text a: {args.sortida}", file=sys.stderr)
        return

    text = renderitzar_terminal(amplada, alcada, valors_brillantor, colors_rgb, caracters, args.color)
    print(text)

    if args.sortida:
        with open(args.sortida, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"\nGuardat com a text a: {args.sortida}", file=sys.stderr)

    if args.png:
        if args.amplada_png:
            # Recalculem les dades amb una amplada diferent, específica per al PNG
            amplada_p, alcada_p, valors_p, colors_p, caracters_p = generar_dades(
                args.ruta, args.amplada_png, args.invertir, args.contrast, args.barreja
            )
        else:
            amplada_p, alcada_p, valors_p, colors_p, caracters_p = amplada, alcada, valors_brillantor, colors_rgb, caracters

        renderitzar_png(
            args.png, amplada_p, alcada_p, valors_p, colors_p,
            caracters_p, args.color, args.mida_font
        )
        print(f"Guardat com a imatge a: {args.png}", file=sys.stderr)


if __name__ == "__main__":
    main()
