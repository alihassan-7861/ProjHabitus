from collections import Counter
import numpy as np
import cv2
import svgwrite
import tempfile
from django.conf import settings
from sklearn.metrics import pairwise_distances_argmin_min
from string import ascii_uppercase
from shapely.geometry import Polygon, box
from .models import ColorPalette
import svgwrite


def get_palette_colors(name="Habitus Palette"):
    try:
        palette = ColorPalette.objects.get(name=name)
        colors = [c.strip().upper() for c in palette.colors.split(";") if c.strip()]
        return colors
    except ColorPalette.DoesNotExist:
        return []


def generate_labels(n):
    return [f"{ascii_uppercase[i // 10]}{i % 10}" for i in range(n)]


HABITUS_PALETTE_HEX = get_palette_colors()
LABELS = generate_labels(len(HABITUS_PALETTE_HEX))
HEX_TO_LABEL = {color: label for color, label in zip(HABITUS_PALETTE_HEX, LABELS)}
HABITUS_PALETTE_BGR = [
    tuple(reversed(tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))))
    for h in HABITUS_PALETTE_HEX
]

LINE_COLOR_BGR = (147, 152, 157)
LABEL_COLOR_BGR = (161, 158, 194)


def rgb_to_hex(rgb):
    return '#{:02X}{:02X}{:02X}'.format(*rgb)


def remap_image_to_palette(image, palette_bgr):
    h, w = image.shape[:2]
    flat = image.reshape((-1, 3))
    palette_np = np.array(palette_bgr)
    closest_idx = pairwise_distances_argmin_min(flat, palette_np)[0]
    mapped = palette_np[closest_idx].reshape((h, w, 3))
    return mapped.astype(np.uint8)


def detect_region_color(mapped_img, contour):
    mask = np.zeros(mapped_img.shape[:2], dtype=np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, -1)
    region_pixels = mapped_img[mask == 255]
    if len(region_pixels) == 0:
        return None
    most_common_bgr = Counter([tuple(p) for p in region_pixels]).most_common(1)[0][0]
    return rgb_to_hex(most_common_bgr[::-1])


def fallback_label_center(mask):
    dist = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    _, _, _, max_loc = cv2.minMaxLoc(dist)
    return max_loc


def place_label(canv, sketch, label, cx, cy, sx, sy, h_px, label_boxes, poly, offset_x, offset_y):
    for font_size in range(10, 0, -1):
        text_w = font_size * 0.6 * len(label)
        text_h = font_size

        label_box_img = box(
            cx - text_w / (2 * sx), cy - text_h / (2 * sy),
            cx + text_w / (2 * sx), cy + text_h / (2 * sy)
        )

        if poly.contains(label_box_img) and all(not label_box_img.intersects(b) for b in label_boxes):
            label_boxes.append(label_box_img)

            if canv:
                text_element = canv.text(
                    label,
                    insert=(cx, cy),
                    font_size=font_size,
                    font_family="Helvetica",
                    fill=svgwrite.rgb(*LABEL_COLOR_BGR[::-1]),
                    text_anchor="middle",
                    alignment_baseline="middle"
                )
                canv.add(text_element)

            if sketch is not None:
                font_scale = font_size / 10.0
                thickness = 1
                text_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
                text_x = int(cx - text_size[0] / 2)
                text_y = int(cy + text_size[1] / 2)

                cv2.rectangle(sketch, (text_x - 1, text_y - text_size[1]),
                              (text_x + text_size[0] + 1, text_y + 2), (255, 255, 255), cv2.FILLED)
                cv2.putText(sketch, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX,
                            font_scale, LABEL_COLOR_BGR, thickness, cv2.LINE_AA)
            return True

    return False


def process_image_to_pbn_svg(file_obj):
    image_data = file_obj.read()
    image_array = np.asarray(bytearray(image_data), dtype=np.uint8)
    src_bgr = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if src_bgr is None:
        raise ValueError("Failed to decode image")

    h_px, w_px = src_bgr.shape[:2]
    mapped_img = remap_image_to_palette(src_bgr, HABITUS_PALETTE_BGR)
    gray = cv2.cvtColor(mapped_img, cv2.COLOR_BGR2GRAY)
    blur = cv2.bilateralFilter(gray, 9, 75, 75)
    edges = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY_INV, 11, 2)
    edges = cv2.dilate(edges, np.ones((2, 2), np.uint8), iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    dwg = svgwrite.Drawing(size=(f"{w_px}px", f"{h_px}px"))
    label_boxes = []
    dynamic_label_index = 0

    for cnt in contours:
        if cv2.contourArea(cnt) < 5:
            continue

        points = cnt[:, 0, :].tolist()
        if len(points) < 3:
            continue
        if points[0] != points[-1]:
            points.append(points[0])

        poly = Polygon(points)
        if not poly.is_valid:
            poly = poly.buffer(0)
        if poly.is_empty or not poly.is_valid:
            continue

        cnt_np = np.array(points[:-1], dtype=np.int32)
        hex_color = detect_region_color(mapped_img, cnt_np) or "#000000"

        if hex_color not in HEX_TO_LABEL:
            HEX_TO_LABEL[hex_color] = f"X{dynamic_label_index}"
            dynamic_label_index += 1

        label = HEX_TO_LABEL[hex_color]

        path_str = "M " + " L ".join([f"{x},{y}" for x, y in cnt_np]) + " Z"
        dwg.add(dwg.path(
            d=path_str,
            stroke=svgwrite.rgb(*LINE_COLOR_BGR[::-1]),
            fill="none",
            stroke_width=1
        ))

        m = cv2.moments(cnt_np.astype(np.float32))
        if m["m00"] != 0:
            cx = int(m["m10"] / m["m00"])
            cy = int(m["m01"] / m["m00"])
        else:
            mask = np.zeros((h_px, w_px), dtype=np.uint8)
            cv2.drawContours(mask, [cnt_np], -1, 255, -1)
            cx, cy = fallback_label_center(mask)

        placed = place_label(dwg, None, label, cx, cy, 1, 1, h_px, label_boxes, poly, 0, 0)

        if not placed:
            # fallback: force place without label overlap check
            text_element = dwg.text(
                label,
                insert=(cx, cy),
                font_size=5,
                font_family="Helvetica",
                fill=svgwrite.rgb(*LABEL_COLOR_BGR[::-1]),
                text_anchor="middle",
                alignment_baseline="middle"
            )
            dwg.add(text_element)

    svg_path = tempfile.mktemp(suffix=".svg")
    dwg.saveas(svg_path)
    return svg_path
