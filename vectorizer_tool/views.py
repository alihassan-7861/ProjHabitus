import os
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import VectorizerSerializer
import requests
from django.http import HttpResponse
import json 
import re
from rest_framework.parsers import MultiPartParser, FormParser
from .utils import process_image_to_pbn_pdf
from django.http import FileResponse
import base64
import traceback
import tempfile
from io import BytesIO
import math
import json

from django.http import FileResponse, JsonResponse
from PIL import Image
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .utils import process_image_to_pbn_pdf

def vectorizer_form_view(request):
    return render(request, 'vectorizer_tool/vectorizer.html')


class VectorizeImageView(APIView):
    def post(self, request):
        serializer = VectorizerSerializer(data=request.data)
        if serializer.is_valid():
            validated = serializer.validated_data

            api_id = os.environ.get("VECTORIZER_API_ID")
            api_key = os.environ.get("VECTORIZER_API_KEY")

            if not api_id or not api_key:
                return Response({"error": "Missing Vectorizer API credentials"}, status=500)

            image = validated['image']
            output_format = validated.get("output_format", "svg").lower()

            HABITUS_PALETTE = [
                "#FFFFFF", "#1A1A1A", "#DADADA", "#999999",
                "#B7D79A", "#4C8C4A", "#2E472B", "#FDE74C",
                "#F5C243", "#F28C28", "#C85A27", "#F88379",
                "#D63E3E", "#8C1C13", "#AED9E0", "#4A90E2",
                "#1B3B6F", "#3CCFCF", "#FBE3D4", "#D5A97B",
                "#5C3B28", "#F5E0C3", "#A24B7B", "#FFCFD8"
            ]
            palette_string = ";".join(HABITUS_PALETTE)

            # 🔧 Flattened form data
            form_data = {
                "format": output_format,
                "mode": "preview" if output_format == "png" else "production",
                "processing.palette": palette_string,
            }

            # Optional fields mapping
            if "minimum_area" in validated:
                form_data["processing.shapes.min_area_px"] = str(validated["minimum_area"])
            if "smoothing" in validated:
                form_data["output.bitmap.anti_aliasing_mode"] = validated["smoothing"]
            if "level_of_details" in validated:
                form_data["output.curves.line_fit_tolerance"] = str(validated["level_of_details"])
            if output_format == "png":
                form_data["output.bitmap.enabled"] = "true"
                form_data["output.bitmap.resolution_dpi"] = "300"

            # ✅ Debug payload
            print("📦 Final payload:", json.dumps(form_data, indent=2))

            try:
                response = requests.post(
                    "https://api.vectorizer.ai/api/v1/vectorize",
                    data=form_data,
                    files={"image": image},
                    auth=(api_id, api_key),
                )

                print("🧪 Response status code:", response.status_code)

                if response.status_code == 200:
                    content_type = response.headers.get("Content-Type", "")
                    if "image/png" in content_type:
                        file_extension = "png"
                    elif "image/svg+xml" in content_type:
                        file_extension = "svg"
                    else:
                        return Response({
                            "error": "Unknown content type from Vectorizer API",
                            "content_type": content_type
                        }, status=400)

                    # 🎯 Check colors only if SVG
                    if file_extension == "svg":
                        svg_text = response.content.decode('utf-8', errors='ignore')
                        used_colors = set(re.findall(r'fill="(#(?:[0-9a-fA-F]{3}){1,2})"', svg_text))
                        used_colors = {c.lower() for c in used_colors}
                        habitus_palette = {c.lower() for c in HABITUS_PALETTE}
                        if used_colors.issubset(habitus_palette):
                            print("✅ Verified: Only Habitus® palette colors used.")
                        else:
                            print("❌ Extra colors found:", used_colors - habitus_palette)

                    return HttpResponse(
                        response.content,
                        content_type=content_type,
                        headers={
                            "Content-Disposition": f'attachment; filename="vectorized_output.{file_extension}"'
                        }
                    )

                else:
                    return Response({
                        "error": "Vectorizer API returned an error",
                        "status_code": response.status_code,
                        "details": response.text
                    }, status=response.status_code)

            except requests.exceptions.RequestException as e:
                return Response({
                    "error": "Request to Vectorizer API failed",
                    "details": str(e)
                }, status=500)

        else:
            return Response(serializer.errors, status=400)







def test_pbn_frontend(request):
    return render(request, "vectorizer_tool/register.html")




class PaintByNumberView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        selected_format = request.POST.get("format", "pdf").lower()
        image_file = request.FILES.get("image")
        base64_image = request.POST.get("base64_image")

        print("\U0001F4E6 Incoming Request:")
        print("🔹 Format:", selected_format)
        print("📌 request.FILES:", request.FILES)
        print("🪼 base64_image present:", bool(base64_image and len(base64_image) > 50))

        if not image_file and not base64_image:
            return Response({"error": "No image uploaded."}, status=400)

        try:
            # Step 1: Convert uploaded or base64 image to PIL Image
            if image_file:
                pil_image = Image.open(image_file).convert("RGB")
            else:
                if base64_image.startswith("data:image"):
                    base64_image = base64_image.split(";base64,")[-1].strip()
                img_data = base64.b64decode(base64_image)
                pil_image = Image.open(BytesIO(img_data)).convert("RGB")

            # Step 2: Save image temporarily
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                pil_image.save(tmp.name, format="PNG")
                tmp.flush()
                tmp.seek(0)

                # Step 3: Process the image
                pdf_path, jpeg_path, area_summary, label_areas, label_dimensions = process_image_to_pbn_pdf(tmp)

            # ✅ Summary Report
            print("\n📊 Summary Report:")
            print(f"🔸 original_image_width_cm: {area_summary['original_image_width_cm']}")
            print(f"🔸 original_image_height_cm: {area_summary['original_image_height_cm']}")
            print(f"🔸 original_image_area_cm2: {area_summary['original_image_area_cm2']}")
            print(f"🔸 labels_total_area_cm2: {area_summary['labels_total_area_cm2']}")

            # ✅ Per-label dimensions
            print("\n📜 Per-Label Region Dimensions:\n")
            grand_total_area = 0.0
            for label, areas in label_areas.items():
                print(f"🔸 Label {label} ({len(areas)} regions):")
                for idx, area in enumerate(areas, 1):
                    width, height = label_dimensions.get(label, [(0, 0)] * len(areas))[idx - 1]
                    print(f"  ➔ Region {idx}: width: {width:.2f} cm, height: {height:.2f} cm, area: {area:.3f} cm²")
                label_total = sum(areas)
                grand_total_area += label_total
                print(f"  ✅ Total area for {label}: {round(label_total, 3)} cm²\n")
            print(f"🔹 Grand Total Area for All Labels: {grand_total_area:.3f} cm²")

            # ✅ Color Box Calculation and Display
            print("\n📦 Color Box Requirements:")
            box_width_cm = 3.16
            box_height_cm = 3.16
            box_area_cm2 = box_width_cm * box_height_cm
            
            # NEW: Create box requirements dictionary to send to frontend
            box_requirements = {}
            for label, summary in area_summary.get("per_label_summary", {}).items():
                total_area = summary["total_area_cm2"]
                boxes_required = math.ceil(total_area / box_area_cm2)
                box_requirements[label] = boxes_required
                print(f"🔸 {boxes_required} {label} boxes required")

            # Step 4: Check if this is a preview request (format=jpeg for preview)
            # or if we need to return box requirements data
            if selected_format == "jpeg" and request.POST.get("preview") == "true":
                # Return JSON with preview image URL and box requirements
                with open(jpeg_path, 'rb') as f:
                    jpeg_data = f.read()
                    jpeg_base64 = base64.b64encode(jpeg_data).decode('utf-8')
                    
                return JsonResponse({
                    "success": True,
                    "image_url": f"data:image/jpeg;base64,{jpeg_base64}",
                    "box_requirements": box_requirements,
                    "area_summary": area_summary,
                    "label_areas": label_areas
                })
            
            # Step 5: Return file for download
            if selected_format == "jpeg":
                return FileResponse(open(jpeg_path, 'rb'), as_attachment=True, filename="habitus.jpeg")
            else:
                return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename="habitus.pdf")

        except Exception as e:
            print("❌ ERROR:", e)
            print("🖌 TRACEBACK:\n", traceback.format_exc())
            return Response({"error": str(e)}, status=500)


