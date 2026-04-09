from pathlib import Path

from PIL import Image, ImageDraw


BASE_DIR = Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR / "assets"
PNG_PATH = ASSET_DIR / "walkdist_icon.png"
ICO_PATH = ASSET_DIR / "walkdist_icon.ico"


def create_icon(size: int = 1024) -> Image.Image:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    margin = int(size * 0.08)
    card_radius = int(size * 0.22)
    card_box = (margin, margin, size - margin, size - margin)
    draw.rounded_rectangle(card_box, radius=card_radius, fill="#F4F6EE")

    inner_margin = int(size * 0.14)
    inner_box = (inner_margin, inner_margin, size - inner_margin, size - inner_margin)
    draw.rounded_rectangle(inner_box, radius=int(size * 0.18), fill="#FFFFFF")

    grid_left = int(size * 0.19)
    grid_top = int(size * 0.54)
    grid_size = int(size * 0.24)
    grid_gap = int(size * 0.018)
    cell = int((grid_size - grid_gap * 2) / 3)
    for row in range(3):
        for column in range(3):
            x0 = grid_left + column * (cell + grid_gap)
            y0 = grid_top + row * (cell + grid_gap)
            x1 = x0 + cell
            y1 = y0 + cell
            fill = "#DFF0E6" if (row, column) in {(0, 0), (1, 1), (2, 2)} else "#EEF5EF"
            draw.rounded_rectangle((x0, y0, x1, y1), radius=int(size * 0.015), fill=fill)

    route_points = [
        (int(size * 0.30), int(size * 0.68)),
        (int(size * 0.44), int(size * 0.56)),
        (int(size * 0.54), int(size * 0.60)),
        (int(size * 0.66), int(size * 0.41)),
    ]
    draw.line(route_points, fill="#2E8F83", width=int(size * 0.045), joint="curve")
    draw.line(route_points, fill="#8ED0C5", width=int(size * 0.016), joint="curve")

    start_radius = int(size * 0.045)
    sx, sy = route_points[0]
    draw.ellipse((sx - start_radius, sy - start_radius, sx + start_radius, sy + start_radius), fill="#FFC968")

    pin_center_x = int(size * 0.68)
    pin_center_y = int(size * 0.31)
    pin_radius = int(size * 0.115)
    pin_color = "#2E8F83"
    draw.ellipse(
        (
            pin_center_x - pin_radius,
            pin_center_y - pin_radius,
            pin_center_x + pin_radius,
            pin_center_y + pin_radius,
        ),
        fill=pin_color,
    )
    pointer = [
        (pin_center_x, int(size * 0.52)),
        (pin_center_x - int(size * 0.08), int(size * 0.37)),
        (pin_center_x + int(size * 0.08), int(size * 0.37)),
    ]
    draw.polygon(pointer, fill=pin_color)

    center_radius = int(size * 0.05)
    draw.ellipse(
        (
            pin_center_x - center_radius,
            pin_center_y - center_radius,
            pin_center_x + center_radius,
            pin_center_y + center_radius,
        ),
        fill="#FFFFFF",
    )

    return image


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    image = create_icon()
    image.save(PNG_PATH)
    image.save(
        ICO_PATH,
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    print(PNG_PATH)
    print(ICO_PATH)


if __name__ == "__main__":
    main()
