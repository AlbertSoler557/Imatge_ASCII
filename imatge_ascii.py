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
"""

import sys
import shutil
import argparse
from PIL import Image, ImageOps

# Caràcters ordenats de més "fosc" (dens) a més "clar" (buit)
CARACTERS = "@%#*+=-:. "


def imatge_a_ascii(ruta, amplada=None, invertir=False, contrast=False):
    img = Image.open(ruta).convert("L")  # escala de grisos

    # Si no s'indica amplada, l'ajustem automàticament a la mida de la terminal
    if amplada is None:
        amplada = shutil.get_terminal_size((100, 24)).columns - 2

    # Estirem el contrast: el píxel més fosc passa a ser negre pur
    # i el més clar a blanc pur, aprofitant tot el rang de grisos
    if contrast:
        img = ImageOps.autocontrast(img)

    # Calculem l'alçada mantenint la proporció
    # (multipliquem per 0.55 perquè els caràcters de text són més alts que amples)
    relacio = img.height / img.width
    alcada = max(1, int(amplada * relacio * 0.55))

    img = img.resize((amplada, alcada))
    pixels = list(img.getdata())

    caracters = CARACTERS[::-1] if invertir else CARACTERS
    escala = len(caracters)

    ascii_str = "".join(
        caracters[pixel * (escala - 1) // 255] for pixel in pixels
    )

    # Tallem la cadena en línies de l'amplada indicada
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
    args = parser.parse_args()

    resultat = imatge_a_ascii(
        args.ruta, args.amplada, args.invertir, args.contrast
    )
    print(resultat)

    if args.sortida:
        with open(args.sortida, "w", encoding="utf-8") as f:
            f.write(resultat)
        print(f"\nGuardat a: {args.sortida}", file=sys.stderr)


if __name__ == "__main__":
    main()
