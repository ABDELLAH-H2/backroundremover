# remove_bg

Local, CPU-only background removal CLI built on [rembg](https://github.com/danielgatis/rembg).

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The first run downloads the segmentation model (~170 MB) to `~/.u2net/`. Subsequent runs work offline.

## Usage

```bash
# Single image — writes photo_nobg.png next to the source
python remove_bg.py photo.jpg

# Custom output path
python remove_bg.py photo.jpg -o cutout.png

# Batch a folder — writes into ./input_dir/nobg/ by default
python remove_bg.py ./input_dir
python remove_bg.py ./input_dir -o ./output_dir

# Cleaner edges for hair / fur (slower)
python remove_bg.py portrait.jpg --alpha-matting

# Pick a different model
python remove_bg.py product.jpg --model isnet-general-use   # sharper edges
python remove_bg.py thumb.jpg   --model u2netp              # ~3x faster
python remove_bg.py person.jpg  --model u2net_human_seg     # tuned for people
```

## Models

| Model                | Best for           | Speed   |
| -------------------- | ------------------ | ------- |
| `u2net` *(default)*  | general            | medium  |
| `u2netp`             | general, lite      | fastest |
| `isnet-general-use`  | sharper edges      | medium  |
| `u2net_human_seg`    | people / portraits | medium  |
| `silueta`            | people, lite       | fast    |

## Supported input formats

`.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`, `.tiff`. Output is always PNG (alpha channel required).
