"""
Convertidor d'imatges a ASCII art (versió millorada)
------------------------------------------------------
Ús:
    python3 imatge_ascii.py ruta_imatge.jpg

Opcions:
    --amplada N      amplada en caràcters (per defecte: s'ajusta a la terminal)
    --invertir       inverteix els tons clars/foscos (útil per fons clars)
    --sortida NOM    guarda el resultat en un fitxer de text
    --contrast       estira el contrast automàticament (recomanat)
    --color          pinta cada caràcter amb el color original del píxel (ANSI)
"""

import sys
import shutil
import argparse
from PIL import Image, ImageOps

# Caràcters ordenats de més "fosc" (dens) a més "clar" (buit)
CARACTERS = "@%#*+=-:. "

RESET = "\033[0m"


def _codi_color(r, g, b):
    """Retorna la seqüència ANSI de color veritable (24 bits) per a un píxel RGB."""
    return f"\033[38;2;{r};{g};{b}m"


def imatge_a_ascii(ruta, amplada=None, invertir=False, contrast=False, color=False):
    img_original = Image.open(ruta).convert("RGB")

    # Si no s'indica amplada, l'ajustem automàticament a la mida de la terminal
    if amplada is None:
        amplada = shutil.get_terminal_size((100, 24)).columns - 2

    # Estirem el contrast: el píxel més fosc passa a ser negre pur
    # i el més clar a blanc pur, aprofitant tot el rang de grisos
    if contrast:
        img_original = ImageOps.autocontrast(img_original)

    # Calculem l'alçada mantenint la proporció
    # (multipliquem per 0.55 perquè els caràcters de text són més alts que amples)
    relacio = img_original.height / img_original.width
    alcada = max(1, int(amplada * relacio * 0.55))

    img_original = img_original.resize((amplada, alcada))

    img_gris = img_original.convert("L")  # lluminositat ponderada, per triar el caràcter
    valors_l = list(img_gris.getdata())

    caracters = CARACTERS[::-1] if invertir else CARACTERS
    escala = len(caracters)

    if color:
        colors_rgb = list(img_original.getdata())  # color real, per pintar

        caracters_pintats = []
        for l, (r, g, b) in zip(valors_l, colors_rgb):
            idx = l * (escala - 1) // 255
            caracters_pintats.append(f"{_codi_color(r, g, b)}{caracters[idx]}")

        # Com que cada "caràcter" ara porta enganxat un codi de color (longitud variable),
        # no podem tallar per longitud de text; tallem per nombre de píxels originals
        linies = []
        for fila in range(alcada):
            inici = fila * amplada
            fi = inici + amplada
            linia = "".join(caracters_pintats[inici:fi]) + RESET
            linies.append(linia)
        return "\n".join(linies)

    # --- Versió sense color ---
    ascii_str = "".join(
        caracters[l * (escala - 1) // 255] for l in valors_l
    )

    linies = [
        ascii_str[i:i + amplada] for i in range(0, len(ascii_str), amplada)
    ]
    return "\n".join(linies)


def main():
    parser = argparse.ArgumentParser(description="Converteix una imatge en ASCII art")
    parser.add_argument("ruta", help="ruta a la imatge (jpg, png, etc.)")
    parser.add_argument("--amplada", type=int, default=None,
                         help="amplada en caràcters (per defecte: mida de la terminal)")
    parser.add_argument("--invertir", action="store_true", help="inverteix tons")
    parser.add_argument("--sortida", type=str, default=None, help="fitxer de sortida")
    parser.add_argument("--contrast", action="store_true", help="estira el contrast automàticament")
    parser.add_argument("--color", action="store_true", help="pinta cada caràcter amb el seu color original (ANSI)")
    args = parser.parse_args()

    resultat = imatge_a_ascii(
        args.ruta, args.amplada, args.invertir, args.contrast, args.color
    )
    print(resultat)

    if args.sortida:
        with open(args.sortida, "w", encoding="utf-8") as f:
            f.write(resultat)
        print(f"\nGuardat a: {args.sortida}", file=sys.stderr)


if __name__ == "__main__":
    main()
