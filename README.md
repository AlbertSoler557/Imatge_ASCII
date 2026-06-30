# Imatge a ASCII Art

Script en Python que converteix qualsevol imatge en art ASCII directament al terminal.

## Instal·lació

Clona el repositori i entra a la carpeta:

```bash
git clone <url-del-repositori>
cd Imatge_ASCII
```

Crea i activa un entorn virtual (opcional però recomanat):

```bash
python3 -m venv venv
source venv/bin/activate      # Linux / Mac
venv\Scripts\Activate.ps1     # Windows (PowerShell)
```

Instal·la les dependències:

```bash
pip install -r requirements.txt
```

## Ús

```bash
python3 imatge_ascii.py ruta_imatge.jpg
```

### Opcions disponibles

| Opció | Descripció |
|---|---|
| `--amplada N` | Amplada del dibuix en caràcters. Si no s'indica, s'ajusta automàticament a la mida de la terminal. |
| `--invertir` | Inverteix els tons clars/foscos. Útil per a imatges amb fons blanc i línies fosques. |
| `--contrast` | Estira el contrast automàticament abans de convertir. |
| `--sortida NOM` | Guarda el resultat en un fitxer de text en lloc de (o a més de) mostrar-lo per pantalla. |

### Exemples

Conversió bàsica:
```bash
python3 imatge_ascii.py foto.jpg
```

Imatge amb fons blanc i línies (dibuixos, logos, còmics):
```bash
python3 imatge_ascii.py dibuix.png --invertir
```

Amb amplada fixa i guardant el resultat:
```bash
python3 imatge_ascii.py foto.jpg --amplada 100 --sortida resultat.txt
```

Combinant totes les opcions:
```bash
python3 imatge_ascii.py foto.jpg --amplada 80 --invertir --contrast --sortida resultat.txt
```

Veure l'ajuda completa:
```bash
python3 imatge_ascii.py --help
```

## Com funciona

1. **Lectura**: la imatge s'obre i es converteix a escala de grisos amb [Pillow](https://python-pillow.org/).
2. **Redimensionament**: es redueix a un nombre de píxels igual a l'amplada desitjada (mantenint la proporció original, ajustada perquè els caràcters de text són més alts que amples).
3. **Mapeig**: cada píxel (un valor de 0 a 255) s'assigna a un caràcter segons la seva lluminositat, fent servir l'escala `@%#*+=-:. ` (de més fosc a més clar).
4. **Sortida**: els caràcters es mostren per pantalla formant línies, recreant la imatge original.

## Requisits

- Python 3.8 o superior
- Pillow (es llista a `requirements.txt`)

## Llicència

Lliure per a ús personal i educatiu.
