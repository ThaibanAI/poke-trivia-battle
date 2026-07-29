from PIL import Image, ImageDraw

def draw_pokeball(size, pad_ratio=0.0, bg=None):
    img = Image.new("RGBA", (size, size), (0,0,0,0))
    d = ImageDraw.Draw(img)
    if bg:
        d.rectangle([0,0,size,size], fill=bg)

    pad = int(size * pad_ratio)
    x0, y0, x1, y1 = pad, pad, size - pad, size - pad
    r = (x1 - x0) / 2
    cx, cy = size/2, size/2
    band = max(2, int(r * 0.16))

    # top red half
    d.pieslice([x0,y0,x1,y1], 180, 360, fill="#e3350d")
    # bottom white half
    d.pieslice([x0,y0,x1,y1], 0, 180, fill="#f5f5f0")
    # outer black ring
    d.ellipse([x0,y0,x1,y1], outline="#111111", width=max(2,int(r*0.05)))
    # black band
    d.rectangle([x0, cy-band/2, x1, cy+band/2], fill="#111111")
    # center button
    br = r*0.30
    d.ellipse([cx-br, cy-br, cx+br, cy+br], fill="#111111")
    br2 = r*0.19
    d.ellipse([cx-br2, cy-br2, cx+br2, cy+br2], fill="#f5f5f0", outline="#111111", width=max(2,int(r*0.04)))

    return img

# Standard icons (transparent-safe, but PWA wants opaque bg typically) — use dark screen bg
icon192 = draw_pokeball(192, pad_ratio=0.06, bg="#0f1a16")
icon192.save("icon-192.png")

icon512 = draw_pokeball(512, pad_ratio=0.06, bg="#0f1a16")
icon512.save("icon-512.png")

# Maskable needs extra safe-zone padding (~20%) since OS crops to shape
maskable = draw_pokeball(512, pad_ratio=0.22, bg="#0f1a16")
maskable.save("icon-maskable-512.png")

print("icons written")
