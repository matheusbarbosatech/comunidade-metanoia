"""Gerador de Favicons e Ícones Oficiais da Comunidade Metanoia.
Cria o favicon.svg vetorial e renderiza os formatos PNG (512x512, 180x180, 32x32, 16x16) e favicon.ico multi-resolução.
"""
from pathlib import Path
from PIL import Image, ImageDraw

STATIC_DIR = Path(__file__).resolve().parent.parent / "app" / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

SVG_CONTENT = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
  <defs>
    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#141824"/>
      <stop offset="100%" stop-color="#080A0F"/>
    </linearGradient>
    <linearGradient id="border-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FCD34D"/>
      <stop offset="50%" stop-color="#F59E0B"/>
      <stop offset="100%" stop-color="#EA580C"/>
    </linearGradient>
    <linearGradient id="flame-outer" x1="0%" y1="100%" x2="50%" y2="0%">
      <stop offset="0%" stop-color="#EA580C"/>
      <stop offset="60%" stop-color="#F59E0B"/>
      <stop offset="100%" stop-color="#FCD34D"/>
    </linearGradient>
    <linearGradient id="flame-inner" x1="0%" y1="100%" x2="50%" y2="0%">
      <stop offset="0%" stop-color="#F59E0B"/>
      <stop offset="50%" stop-color="#FCD34D"/>
      <stop offset="100%" stop-color="#FFFFFF"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="12" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- Squircle Base Obsidian -->
  <rect x="20" y="20" width="472" height="472" rx="112" fill="url(#bg-grad)" stroke="url(#border-grad)" stroke-width="10"/>

  <!-- Halo de Luz Âmbar -->
  <circle cx="256" cy="290" r="140" fill="#F59E0B" opacity="0.15" filter="url(#glow)"/>

  <!-- Chama Sagrada Externa (Metanoia / Avivamento) -->
  <path d="M256 68 C238 140 156 215 156 308 C156 384 202 432 256 432 C310 432 356 384 356 308 C356 235 304 172 292 120 C278 180 248 214 228 214 C218 214 210 204 213 194 C224 156 244 110 256 68 Z" fill="url(#flame-outer)" filter="url(#glow)"/>

  <!-- Núcleo de Fogo Dourado -->
  <path d="M256 195 C244 240 204 280 204 335 C204 380 228 410 256 410 C284 410 308 380 308 335 C308 290 280 250 274 220 C265 250 252 270 242 270 C236 270 232 264 235 256 C242 234 252 210 256 195 Z" fill="url(#flame-inner)"/>

  <!-- Cruz Central em Destaque Nobre -->
  <g fill="#0D111A">
    <!-- Haste Vertical -->
    <rect x="249" y="270" width="14" height="92" rx="7"/>
    <!-- Haste Horizontal -->
    <rect x="228" y="295" width="56" height="14" rx="7"/>
  </g>
</svg>'''

def gerar_arquivos():
    # 1. Salvar favicon.svg
    svg_path = STATIC_DIR / "favicon.svg"
    svg_path.write_text(SVG_CONTENT, encoding="utf-8")
    print(f"[OK] Favicon SVG gerado em: {svg_path}")

    # 2. Renderizar PNG em alta resolução com PIL
    size = 512
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Fundo Squircle arredondado Dark Obsidian
    # raio 112
    r = 112
    # Desenhar squircle com cor #0E111A
    draw.rounded_rectangle([20, 20, 492, 492], radius=r, fill=(14, 17, 26, 255), outline=(245, 158, 11, 255), width=8)

    # Brilho central
    draw.ellipse([156, 190, 356, 390], fill=(234, 88, 12, 45))

    # Chama estilizada desenhada com curvas/polígonos
    # Pontos da chama externa
    flame_outer_pts = [
        (256, 70), (280, 110), (292, 140), (320, 190), (344, 250), (356, 308),
        (350, 360), (325, 405), (290, 428), (256, 432), (222, 428), (187, 405),
        (162, 360), (156, 308), (168, 250), (192, 190), (220, 140), (236, 194),
        (228, 214), (248, 214), (278, 180), (292, 120), (256, 70)
    ]
    draw.polygon(flame_outer_pts, fill=(245, 158, 11, 255))

    # Núcleo de fogo interno (Amarelo / Dourado Claro)
    flame_inner_pts = [
        (256, 195), (270, 220), (274, 240), (294, 275), (308, 335), (300, 375),
        (280, 402), (256, 410), (232, 402), (212, 375), (204, 335), (218, 275),
        (238, 240), (242, 270), (252, 270), (265, 250), (274, 220), (256, 195)
    ]
    draw.polygon(flame_inner_pts, fill=(252, 211, 77, 255))

    # Cruz Central estilizada Dark Obsidian
    # Haste Vertical (256 centralizado -> x=249 a 263, y=270 a 362)
    draw.rounded_rectangle([249, 270, 263, 362], radius=6, fill=(13, 17, 26, 255))
    # Haste Horizontal (x=228 a 284, y=295 a 309)
    draw.rounded_rectangle([228, 295, 284, 309], radius=6, fill=(13, 17, 26, 255))

    # 3. Salvar 512x512 PNG
    png512_path = STATIC_DIR / "favicon-512x512.png"
    img.save(png512_path, format="PNG")
    print(f"[OK] Favicon 512x512 salvo em: {png512_path}")

    # 4. Salvar Apple Touch Icon (180x180)
    img_180 = img.resize((180, 180), Image.Resampling.LANCZOS)
    apple_path = STATIC_DIR / "apple-touch-icon.png"
    img_180.save(apple_path, format="PNG")
    print(f"[OK] Apple Touch Icon 180x180 salvo em: {apple_path}")

    # 5. Salvar 32x32 e 16x16
    img_32 = img.resize((32, 32), Image.Resampling.LANCZOS)
    png32_path = STATIC_DIR / "favicon-32x32.png"
    img_32.save(png32_path, format="PNG")

    img_16 = img.resize((16, 16), Image.Resampling.LANCZOS)
    png16_path = STATIC_DIR / "favicon-16x16.png"
    img_16.save(png16_path, format="PNG")

    # 6. Salvar favicon.ico (multi-size: 16, 32, 48)
    ico_path = STATIC_DIR / "favicon.ico"
    img.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    print(f"[OK] Favicon ICO multi-resolução salvo em: {ico_path}")

if __name__ == "__main__":
    gerar_arquivos()
