"""Tile still frames into one labelled contact sheet: python tools/sheet.py out.jpg cols width frame.png..."""
import sys
from PIL import Image, ImageDraw
out, cols, w, files = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4:]
ims = [Image.open(f).convert("RGB") for f in files]
h = int(w * ims[0].height / ims[0].width)
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (w + 6), rows * (h + 26)), "white")
for i, (f, im) in enumerate(zip(files, ims)):
    x, y = (i % cols) * (w + 6), (i // cols) * (h + 26)
    sheet.paste(im.resize((w, h)), (x, y))
    ImageDraw.Draw(sheet).text((x + 4, y + h + 6), f.split("/")[-1], fill="black")
sheet.save(out, quality=88)
