from datetime import datetime

from io import BytesIO
import math
import base64
from pathlib import Path
import shutil
import tempfile
import traceback
import os,requests
from PIL import Image
import cairosvg
from django.shortcuts import render,get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseBadRequest, JsonResponse, FileResponse
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.utils.crypto import get_random_string
from .serializers import VectorizerSerializer
from .models import ColorPalette, PBNOutput, VectorizationJob
import glob
from django.core.files import File
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import cairosvg

import os
import re
import requests
from datetime import datetime
from django.conf import settings
from django.utils.crypto import get_random_string
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import VectorizationJob, ColorPalette
from .serializers import VectorizerSerializer


from .utils import  process_image_to_pbn_svg
@login_required(login_url='login')
def vectorizer_form_view(request):
    return render(request, 'vectorizer_tool/vectorizer.html')


# class VectorizeImageView(APIView):
#     def post(self, request):
#         serializer = VectorizerSerializer(data=request.data)
#         if serializer.is_valid():
#             validated = serializer.validated_data

#             # API keys
#             api_id = "vkqi8vk8s2ks85b"
#             api_key = "74vgc7l4527jrha395en131ifuvmbp31iem60vh81pvf76i4b6sn"

#             image = validated['image']
#             output_format = validated.get("output_format", "svg").lower()

#             HABITUS_PALETTE = [   "#FFFFFF", "#1A1A1A", "#DADADA", "#999999", "#B7D79A", "#4C8C4A",
#         "#2E472B", "#FDE74C", "#F5C243", "#F28C28", "#C85A27", "#F88379",
#         "#D63E3E", "#8C1C13", "#AED9E0", "#4A90E2", "#1B3B6F", "#3CCFCF",
#         "#FBE3D4", "#D5A97B", "#5C3B28", "#F5E0C3", "#A24B7B", "#FFCFD8"
#    ]  # Same as before
#             palette_string = ";".join(HABITUS_PALETTE)

#             form_data = {
#                 "format": output_format,
#                 #"mode": "preview" if output_format == "png" else "production",
#                 "mode": "test",

#                 "processing.palette": palette_string,
#             }
#             if "minimum_area" in validated:
#                 form_data["processing.shapes.min_area_px"] = str(validated["minimum_area"])
#             if "smoothing" in validated:
#                 form_data["output.bitmap.anti_aliasing_mode"] = validated["smoothing"]
#             if "level_of_details" in validated:
#                 form_data["output.curves.line_fit_tolerance"] = str(validated["level_of_details"])
#             if output_format == "png":
#                 form_data["output.bitmap.enabled"] = "true"
#                 form_data["output.bitmap.resolution_dpi"] = "300"

#             try:
#                 print("📤 Sending Request to Vectorizer API:")
#                 print("🔹 Endpoint: https://api.vectorizer.ai/api/v1/vectorize")
#                 print("🔹 Auth:", (api_id, "********"))  # Mask the API key in logs
#                 print("🔹 Form Data:", json.dumps(form_data, indent=2))
#                 print("🔹 Files: image =", image.name)

#                 response = requests.post(
#                     "https://api.vectorizer.ai/api/v1/vectorize",
#                     data=form_data,
#                     files={"image": image},
#                     auth=(api_id, api_key),
#                 )

#                 print("\n📥 Response from Vectorizer API:")
#                 print("🔹 Status Code:", response.status_code)
#                 print("🔹 Content-Type:", response.headers.get("Content-Type", ""))
#                 print("🔹 Response Text:", response.text[:500])  # limit for large response


#                 #  Check for subscription or quota issues (402)
#                 if response.status_code == 402:
#                     return Response({
#                         "error": "Payment Required. You may have exceeded the free quota or are using production mode.",
#                         "suggestion": "Switch to preview mode or upgrade your API plan."
#                     }, status=402)


#                 if response.status_code == 200:
#                     content_type = response.headers.get("Content-Type", "")
#                     ext = "svg" if "svg" in content_type else "png"

#                     filename = f'vector_output_{get_random_string(8)}.{ext}'
#                     path = os.path.join('vector_output', filename)
#                     full_path = os.path.join(settings.MEDIA_ROOT, path)

#                     os.makedirs(os.path.dirname(full_path), exist_ok=True)
#                     with open(full_path, 'wb') as f:
#                         f.write(response.content)

#                     # Store path in session for next page
#                     request.session['vectorized_image_path'] = path

#                     return JsonResponse({
#                             "message": "Success",
#                             "vector_url": default_storage.url(path)  # ✅ this matches your JS expectation
#                         })

#                 return Response({
#                     "error": "Vectorizer API error",
#                     "status_code": response.status_code,
#                     "details": response.text
#                 }, status=response.status_code)

#             except requests.exceptions.RequestException as e:
#                 return Response({"error": "Request failed", "details": str(e)}, status=500)

#         return Response(serializer.errors, status=400)





class VectorizeImageView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        serializer = VectorizerSerializer(data=request.data)
        if serializer.is_valid():
            validated = serializer.validated_data
            image = validated["image"]
esponse({"error": "Missing Vectorizer API credentials"}, status=500)

            image = validated['image']
>>>>>>> 621520af405d207041c188a782761be02fda5666
         except ColorPalette.DoesNotExist:
                return Response({"error": "No color palette found in database."}, status=400)

            # 🎨 Use raw palette with tolerance (e.g., "#FFFFFF ~ 0.02; #000000 ~ 0.01")
            raw_palette_string = palette_obj.colors.strip()

            # Extract only color codes (ignoring tolerance) for verification later
            palette_list = [
                color.split("~")[0].strip().lower()
                for color in raw_palette_string.split(";")
                if color.strip()
            ]

            # 🧾 Construct form payload
            form_data = {
                "format": "bitmap",
                # "mode": "test",
                "mode": "production" if output_format == "svg" else "preview",
                "processing.palette": raw_palette_string,
                "processing.max_colors": "0",

                "output.gap_filler.enabled": "false",
            }

            if "minimum_area" in validated:
                form_data["processing.shapes.min_area_px"] = str(validated["minimum_area"])
            if "smoothing" in validated:
                form_data["output.bitmap.anti_aliasing_mode"] = validated["smoothing"]
            if "level_of_details" in validated:
                form_data["output.curves.line_fit_tolerance"] = str(validated["level_of_details"])

            # Set output format flags
            if output_format == "png":
                form_data["output.format"] = "png"
                form_data["output.bitmap.enabled"] = "true"
                form_data["output.vector.enabled"] = "false"
                form_data["output.bitmap.resolution_dpi"] = "300"
            else:
                form_data["output.format"] = "svg"
                form_data["output.vector.enabled"] = "true"
                form_data["output.bitmap.enabled"] = "false"

            print("📤 Sending payload to Vectorizer API:")
            for key, value in form_data.items():
                print(f"    {key}: {value}")
            print("📎 File being sent:", image.name)

            # 🔑 API credentials
            api_id = "vkqi8vk8s2ks85b"
            api_key = "74vgc7l4527jrha395en131ifuvmbp31iem60vh81pvf76i4b6sn"

            try:
                response = requests.post(
                    "https://api.vectorizer.ai/api/v1/vectorize",
                    data=form_data,
                    files={"image": image},
                    auth=(api_id, api_key),
                )

                if response.status_code == 200:
                    content_type = response.headers.get("Content-Type", "")
                    file_extension = "svg" if "svg" in content_type else "png"
                    # if "svg" in content_type:
                    #     try:
                    #         svg_text = response.content.decode('utf-8', errors='ignore')
                    #         print("\n📄 Full SVG content received from Vectorizer API:\n")
                    #         print(svg_text)
                    #     except Exception as e:
                    #         print("⚠️ Failed to decode SVG content:", e)
                    date_str = datetime.now().strftime('%Y%m%d')
                    filename = f'HBT-{get_random_string(4)}-{date_str}.{file_extension}'
                    path = os.path.join("vector_output", filename)
                    full_path = os.path.join(settings.MEDIA_ROOT, path)

                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, 'wb') as f:
                        f.write(response.content)

                    # ✅ Verify used colors in SVG (only if SVG)
                    if file_extension == "svg":
                        svg_text = response.content.decode('utf-8', errors='ignore')
                        used_colors = set(re.findall(r'fill="(#(?:[0-9a-fA-F]{3}){1,2})"', svg_text))
                        used_colors = {c.lower() for c in used_colors}

                        print("\n🎨 Colors extracted from SVG:")
                        for c in sorted(used_colors):
                            print(f"  • {c}")

                        palette_set = set(palette_list)
                        if used_colors.issubset(palette_set):
                            print("✅ Verified: Only Habitus® palette colors used.")
                        else:
                            print("❌ Extra colors found:", used_colors - palette_set)

                    # Save vectorization job
                    vector_job = VectorizationJob.objects.create(
                        user=request.user if request.user.is_authenticated else None,
                        original_image=image,
                        vectorized_image=path,
                        palette_used=palette_obj,
                    )

                    return JsonResponse({
                        "message": "Success",
                        "vector_url": vector_job.vectorized_image.url,
                        "job_id": vector_job.id,
                    })

                return Response({
                    "error": "Vectorizer API error",
                    "status_code": response.status_code,
                    "details": response.text
                }, status=response.status_code)

            except requests.exceptions.RequestException as e:
                return Response({"error": "Request failed", "details": str(e)}, status=500)

        print("❌ Serializer validation errors:", serializer.errors)
        return Response(serializer.errors, status=400)



@login_required(login_url='login')
def test_pbn_frontend(request, job_id):
    job = get_object_or_404(VectorizationJob, id=job_id)
    return render(request, "vectorizer_tool/register.html", {
        "vector_url": job.vectorized_image.url,
        "job": job,
    })

def convert_svg_to_png(svg_file, output_path):
    try:
        svg_data = svg_file.read()
        if not svg_data:
            raise ValueError("⚠️ SVG file is empty or unreadable.")

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Convert SVG to PNG and save to the desired path
        cairosvg.svg2png(
            bytestring=svg_data,
            write_to=output_path,
            dpi=300,
            scale=2.0
        )

        # Confirm the PNG was written
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise IOError("❌ PNG conversion failed.")

        print(f"✅ PNG successfully created at: {output_path}")
        return output_path

    except Exception as e:
        print("🔥 Error during SVG to PNG conversion:", e)
        raise



# class PaintByNumberView(APIView):
#     parser_classes = [MultiPartParser, FormParser]

#     def post(self, request):
#         selected_format = request.POST.get("format", "pdf").lower()

#         try:
#             vector_output_dir = os.path.join(settings.MEDIA_ROOT, "vector_output")
#             svg_files = sorted(
#                 glob.glob(os.path.join(vector_output_dir, "*.svg")),
#                 key=os.path.getmtime,
#                 reverse=True
#             )

#             if not svg_files:
#                 return Response({"error": "No SVG files found in vector_output directory."}, status=404)

#             svg_path = svg_files[0]
#             output_dir = os.path.join(settings.MEDIA_ROOT, 'converted_pngs')
#             os.makedirs(output_dir, exist_ok=True)
#             media_png_path = os.path.join(output_dir, 'latest_image.png')

#             with open(svg_path, 'rb') as svg_file:
#                 convert_svg_to_png(svg_file, media_png_path)
#             pil_image = Image.open(media_png_path).convert("RGB")

#             with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
#                 pil_image.save(tmp.name, format="PNG")
#                 tmp.flush()
#                 tmp.seek(0)

#                 if selected_format == "jpeg":
#                     jpeg_path = process_image_to_pbn_jpeg(tmp)
#                     if request.POST.get("preview") == "true":
#                         with open(jpeg_path, 'rb') as f:
#                             jpeg_data = f.read()
#                             jpeg_base64 = base64.b64encode(jpeg_data).decode('utf-8')
#                         return JsonResponse({
#                             "success": True,
#                             "image_url": f"data:image/jpeg;base64,{jpeg_base64}"
#                         })
#                     return FileResponse(open(jpeg_path, 'rb'), as_attachment=True, filename="habitus.jpeg")
#                 else:
#                     tmp.seek(0)
#                     pdf_path = process_image_to_pbn_pdf(tmp)  # ✅ FIXED: remove unpacking
#                     return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename="habitus.pdf")
#         except Exception as e:
#             print("🖌 TRACEBACK:\n", traceback.format_exc())
#             return Response({"error": str(e)}, status=500)







from .models import PBNOutput  # make sure this import is present
from django.core.files import File  # to wrap saved file in Django's File object

class PaintByNumberView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        selected_format = request.POST.get("format", "pdf").lower()

        try:
            # Load latest SVG
            vector_output_dir = os.path.join(settings.MEDIA_ROOT, "vector_output")
            svg_files = sorted(
                glob.glob(os.path.join(vector_output_dir, "*.svg")),
                key=os.path.getmtime,
                reverse=True
            )

            if not svg_files:
                return Response({"error": "No SVG files found in vector_output directory."}, status=404)

            svg_path = svg_files[0]
            output_dir = os.path.join(settings.MEDIA_ROOT, 'converted_pngs')
            os.makedirs(output_dir, exist_ok=True)
            media_png_path = os.path.join(output_dir, 'latest_image.png')

            # Convert SVG to PNG
            with open(svg_path, 'rb') as svg_file:
                convert_svg_to_png(svg_file, media_png_path)

            pil_image = Image.open(media_png_path).convert("RGB")

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                pil_image.save(tmp.name, format="PNG")
                tmp.flush()
                tmp.seek(0)

                pbn_svg_path = process_image_to_pbn_svg(tmp)

                # Save SVG file to model
                user = request.user
                pbn_output = PBNOutput(user=user)
                pbn_output.output_svg.save(os.path.basename(pbn_svg_path), File(open(pbn_svg_path, 'rb')), save=False)
                pbn_output.save()

                # Encode SVG to base64 for preview
                with open(pbn_svg_path, 'rb') as f:
                    svg_base64 = base64.b64encode(f.read()).decode('utf-8')
                print("SVG File Path:", pbn_output.output_svg.path)
                print("SVG File URL:", pbn_output.output_svg.url)
                return JsonResponse({
                    "success": True,
                    "svg_url": f"data:image/svg+xml;base64,{svg_base64}",
                    "svg_file_url": pbn_output.output_svg.url,
                    "job_id": pbn_output.id,
                    "created_at": pbn_output.created_at,
                })

        except Exception as e:
            print("🖌 TRACEBACK:\n", traceback.format_exc())
            return Response({"error": str(e)}, status=500)

                # else:
                # # On download request, generate final PDF/JPEG from the PBN SVG
                #     if selected_format == "jpeg":
                #         jpeg_path = process_pbn_svg_to_jpeg(pbn_svg_path)
                #         return FileResponse(open(jpeg_path, 'rb'), as_attachment=True, filename="habitus.jpeg")
                #     else:
                #         pdf_path = process_pbn_svg_to_pdf(pbn_svg_path)
                #         return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename="habitus.pdf")


        # except Exception as e:
        #     print("🖌 TRACEBACK:\n", traceback.format_exc())
        #     return Response({"error": str(e)}, status=500)



from django.http import HttpResponse
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from vectorizer_tool.models import PBNOutput
import cairosvg
import logging

logger = logging.getLogger(__name__)

def get_size_px(size_cm):
    cm_to_inch = 0.393701
    dpi = 300
    width_cm, height_cm = map(int, size_cm.lower().split('x'))
    return int(width_cm * cm_to_inch * dpi), int(height_cm * cm_to_inch * dpi)


def download_resized_jpeg(request):
    size = request.GET.get("size")
    if not size:
        return HttpResponse("Missing size parameter", status=400)

    try:
        width_cm, height_cm = map(int, size.lower().split("x"))
        dpi = 300
        cm_to_inch = 0.393701
        width_px = int(width_cm * cm_to_inch * dpi)
        height_px = int(height_cm * cm_to_inch * dpi)
    except Exception:
        return HttpResponse("Invalid size format", status=400)

    try:
        output = PBNOutput.objects.filter(user=request.user).latest("created_at")
        with open(output.output_svg.path, "rb") as svg_file:
            svg_bytes = svg_file.read()

        # Try converting SVG to PNG safely
        png_bytes = cairosvg.svg2png(
            bytestring=svg_bytes,
            output_width=width_px,
            output_height=height_px,
            unsafe=True  # allows fallback fonts rendering
        )

        image = Image.open(BytesIO(png_bytes))

        # Convert RGBA to RGB (JPEG doesn't support transparency)
        if image.mode == 'RGBA':
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        else:
            image = image.convert("RGB")

        buffer = BytesIO()
        image.save(buffer, format="JPEG")

        return HttpResponse(buffer.getvalue(), content_type="image/jpeg", headers={
            'Content-Disposition': f'attachment; filename="pbn_{size}.jpeg"'
        })

    except Exception as e:
        import logging
        logging.exception("Error processing image")
        return HttpResponse("Image processing failed", status=500)

from reportlab.pdfgen import canvas


# views.py
from django.http import HttpResponse
from vectorizer_tool.models import PBNOutput
import cairosvg
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
import os
from reportlab.lib.utils import ImageReader

def download_resized_pdf(request):
    size = request.GET.get("size")
    if not size:
        return HttpResponse("Missing size parameter", status=400)

    try:
        width_cm, height_cm = map(int, size.lower().split("x"))
        width_pts = width_cm * cm
        height_pts = height_cm * cm
    except Exception:
        return HttpResponse("Invalid size format", status=400)

    try:
        # Fetch latest generated SVG
        output = PBNOutput.objects.filter(user=request.user).latest("created_at")
        svg_path = output.output_svg.path

        # Convert SVG to PNG at 300 DPI
        dpi = 300
        cm_to_inch = 0.393701
        width_px = int(width_cm * cm_to_inch * dpi)
        height_px = int(height_cm * cm_to_inch * dpi)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_png:
            cairosvg.svg2png(
                url=svg_path,
                write_to=tmp_png.name,
                output_width=width_px,
                output_height=height_px,
                unsafe=True,
                background_color='white'  # Optional: ensures white background
            )
            tmp_png_path = tmp_png.name

        # Setup paths for branding images
        LOGO_PATH = os.path.join("media", "logos", "habitus_logo.jpeg")
        SECOND_IMAGE_PATH = os.path.join("media", "logos", "website_info_logo.png")

        # Create PDF with styling
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            c = canvas.Canvas(tmp_pdf.name, pagesize=(width_pts, height_pts))

            # Draw border inside page (leave space at bottom for branding)
            border_margin = 1 * cm
            footer_space = 4 * cm
            image_padding = 0.5 * cm  # 👈 Add this padding inside the border

            image_x = border_margin + image_padding
            image_y = border_margin + footer_space + image_padding
            image_width = width_pts - 2 * (border_margin + image_padding)
            image_height = height_pts - 2 * border_margin - footer_space - 2 * image_padding

            # Border
            c.setStrokeColorRGB(0, 0, 0)
            c.setLineWidth(2)
            c.rect(image_x, image_y, image_width, image_height)

            # Draw image centered inside border
            c.drawImage(
                tmp_png_path,
                image_x,
                image_y,
                width=image_width,
                height=image_height,
                preserveAspectRatio=True,
                anchor='c'
            )

            # Draw center-bottom logo (outside border)
            if os.path.exists(LOGO_PATH):
                logo_width = 4 * cm
                logo_height = 2 * cm
                c.drawImage(
                    ImageReader(LOGO_PATH),
                    (width_pts - logo_width) / 2,
                    1 * cm,
                    width=logo_width,
                    height=logo_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )

            # Draw right-bottom secondary image (outside border)
            if os.path.exists(SECOND_IMAGE_PATH):
                sec_width = 4 * cm
                sec_height = 2 * cm
                c.drawImage(
                    ImageReader(SECOND_IMAGE_PATH),
                    width_pts - sec_width - 1 * cm,
                    1 * cm,
                    width=sec_width,
                    height=sec_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )

            c.showPage()
            c.save()

            with open(tmp_pdf.name, "rb") as f:
                pdf_data = f.read()

        # Cleanup
        os.remove(tmp_png_path)
        os.remove(tmp_pdf.name)

        return HttpResponse(
            pdf_data,
            content_type="application/pdf",
            headers={'Content-Disposition': f'attachment; filename="pbn_{size}.pdf"'}
        )

    except Exception as e:
        import logging
        logging.exception("Error processing PDF")
        return HttpResponse("PDF generation failed", status=500)