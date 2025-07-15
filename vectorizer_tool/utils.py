import os
import tempfile
import string
import numpy as np
import cv2
from PIL import Image, ImageOps
from shapely.geometry import Polygon, box
from skimage import measure
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import math

def place_label(canv, sketch, label, cx, cy, sx, sy, h_px, label_boxes, poly, offset_x, offset_y):
    for font_size in range(6, 0, -1):
        canv.setFont("Helvetica", font_size)
        text_w = canv.stringWidth(label, "Helvetica", font_size)
        text_h = font_size
        label_box_img = box(
            cx - text_w / (2 * sx),
            cy - text_h / (2 * sy),
            cx + text_w / (2 * sx),
            cy + text_h / (2 * sy)
        )
        if poly.contains(label_box_img) and all(not label_box_img.intersects(b) for b in label_boxes):
            label_boxes.append(label_box_img)

            canv.drawCentredString(offset_x + cx * sx, offset_y + (h_px - cy) * sy - font_size / 2, label)

            font_scale = font_size / 10.0
            thickness = 1
            text_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
            text_x = int(cx - text_size[0] / 2)
            text_y = int(cy + text_size[1] / 2)

            cv2.rectangle(
                sketch,
                (text_x - 1, text_y - text_size[1]),
                (text_x + text_size[0] + 1, text_y + 2),
                (255, 255, 255),
                cv2.FILLED
            )

            cv2.putText(
                sketch,
                label,
                (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (0, 0, 0),
                thickness,
                cv2.LINE_AA
            )
            return True
    return False


def process_image_to_pbn_pdf(file_obj):
    PAGE_WIDTH, PAGE_HEIGHT = A4
    BORDER = 1 * cm
    INNER_X = BORDER
    INNER_Y = BORDER
    INNER_WIDTH = PAGE_WIDTH - 2 * BORDER
    INNER_HEIGHT = PAGE_HEIGHT - 2 * BORDER

    PALETTE = [
        "#FFFFFF", "#1A1A1A", "#DADADA", "#999999", "#B7D79A", "#4C8C4A",
        "#2E472B", "#FDE74C", "#F5C243", "#F28C28", "#C85A27", "#F88379",
        "#D63E3E", "#8C1C13", "#AED9E0", "#4A90E2", "#1B3B6F", "#3CCFCF",
        "#FBE3D4", "#D5A97B", "#5C3B28", "#F5E0C3", "#A24B7B", "#FFCFD8"
    ]
    letters = string.ascii_uppercase
    LABEL_MAP = dict(zip([c.lower() for c in PALETTE], [f"{letters[i // 10]}{i % 10}" for i in range(len(PALETTE))]))

    image_data = file_obj.read()
    image_array = np.asarray(bytearray(image_data), dtype=np.uint8)
    src = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if src is None:
        raise ValueError("Failed to decode image. Ensure it's a valid PNG or JPEG.")

    h_px, w_px = src.shape[:2]
    dpi_x = dpi_y = 96
    px_to_cm_x = 2.54 / dpi_x
    px_to_cm_y = 2.54 / dpi_y
    px_to_cm2 = px_to_cm_x * px_to_cm_y

    original_width_cm = w_px * px_to_cm_x
    original_height_cm = h_px * px_to_cm_y
    original_image_area_cm2 = original_width_cm * original_height_cm

    img_ratio = w_px / h_px
    box_ratio = INNER_WIDTH / INNER_HEIGHT
    draw_width = INNER_WIDTH if img_ratio > box_ratio else INNER_HEIGHT * img_ratio
    draw_height = draw_width / img_ratio if img_ratio > box_ratio else INNER_HEIGHT

    sx = draw_width / w_px
    sy = draw_height / h_px
    offset_x = INNER_X + (INNER_WIDTH - draw_width) / 2
    offset_y = INNER_Y + (INNER_HEIGHT - draw_height) / 2

    pdf_path = tempfile.mktemp(suffix=".pdf")
    canv = canvas.Canvas(pdf_path, pagesize=A4)
    canv.setStrokeColorRGB(0, 0, 0)
    canv.setLineWidth(1)
    canv.rect(INNER_X, INNER_Y, INNER_WIDTH, INNER_HEIGHT)

    label_areas = {}
    label_dimensions = {}
    label_boxes = []
    sketch = np.ones((h_px, w_px, 3), dtype=np.uint8) * 255

    for hex_col in PALETTE:
        bgr = np.array([int(hex_col[i:i + 2], 16) for i in (5, 3, 1)], dtype=np.uint8)
        mask = cv2.inRange(src, bgr, bgr)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        contours = measure.find_contours(mask, level=0.5)

        label = LABEL_MAP[hex_col.lower()]
        for cnt in contours:
            if cnt.shape[0] < 4:
                continue
            cnt = cnt[:, [1, 0]]
            epsilon = 0.0015 * cv2.arcLength(cnt.astype(np.float32), True)
            approx = cv2.approxPolyDP(cnt.astype(np.float32), epsilon, True)[:, 0, :]
            pixel_area = cv2.contourArea(approx.astype(np.int32))
            if pixel_area < 50:
                continue
            x, y, w, h = cv2.boundingRect(approx.astype(np.int32))
            if max(w / h, h / w) > 10:
                continue
            perimeter = cv2.arcLength(approx.astype(np.float32), True)
            if 4 * np.pi * pixel_area / (perimeter**2 + 1e-6) < 0.05:
                continue

            area_cm2 = pixel_area * px_to_cm2
            width_cm = round(w * px_to_cm_x, 3)
            height_cm = round(h * px_to_cm_y, 3)

            if width_cm < 0.1 or height_cm < 0.1:
                continue

            label_areas.setdefault(label, []).append(round(area_cm2, 3))
            label_dimensions.setdefault(label, []).append((width_cm, height_cm))

            path = canv.beginPath()
            path.moveTo(offset_x + approx[0][0] * sx, offset_y + (h_px - approx[0][1]) * sy)
            for x1, y1 in approx[1:]:
                path.lineTo(offset_x + x1 * sx, offset_y + (h_px - y1) * sy)
            path.close()
            canv.setLineWidth(0.4)
            canv.drawPath(path)

            cv2.polylines(sketch, [approx.astype(np.int32)], isClosed=True, color=(0, 0, 0), thickness=1)

            poly = Polygon(approx)
            m = cv2.moments(approx.astype(np.float32))
            if m["m00"] == 0:
                continue
            cx = int(m["m10"] / m["m00"])
            cy = int(m["m01"] / m["m00"])

            place_label(canv, sketch, label, cx, cy, sx, sy, h_px, label_boxes, poly, offset_x, offset_y)

    canv.setFont("Helvetica-Bold", 6)
    canv.drawCentredString(PAGE_WIDTH / 2, 0.5 * cm, "Habitus")
    canv.save()

    jpeg_path = tempfile.mktemp(suffix=".jpeg")
    cv2.imwrite(jpeg_path, sketch)

    per_label_summary = {}
    total_label_area_cm2 = 0.0

    # ==== NEW: Box calculation ====
    box_width_cm = 3.16
    box_height_cm = 3.16
    box_area_cm2 = box_width_cm * box_height_cm
    box_requirements = {}

    for label, areas in label_areas.items():
        total_area = sum(areas)
        per_label_summary[label] = {
            "count": len(areas),
            "total_area_cm2": round(total_area, 3)
        }
        total_label_area_cm2 += total_area

        num_boxes = math.ceil(total_area / box_area_cm2)
        box_requirements[label] = num_boxes

    # Optional: print box count summary
    print("\n📦 Box Requirements Per Label:")
    for label, boxes in box_requirements.items():
        print(f"🔸 {boxes} {label} boxes required")

    area_summary = {
        "original_image_width_cm": round(original_width_cm, 3),
        "original_image_height_cm": round(original_height_cm, 3),
        "original_image_area_cm2": round(original_image_area_cm2, 3),
        "labels_total_area_cm2": round(total_label_area_cm2, 3),
        "per_label_summary": per_label_summary,
        "box_requirements": box_requirements
    }

    return pdf_path, jpeg_path, area_summary, label_areas, label_dimensions