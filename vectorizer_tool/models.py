from django.db import models
from django.contrib.auth.models import User  # or use your custom user model

# Create your models here.
class ColorPalette(models.Model):
    name = models.CharField(max_length=100, default="Habitus Palette")
    colors = models.TextField(help_text="Semicolon-separated hex colors like #FFFFFF;#1A1A1A;...")

    def __str__(self):
        return self.name



class VectorizationJob(models.Model):  # Assuming this is the updated model
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # <-- Add this line

    original_image = models.ImageField(upload_to="original_images/")
    vectorized_image = models.ImageField(upload_to="vector_output/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    palette_used = models.ForeignKey(ColorPalette, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Job {self.id} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"




class PBNOutput(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    output_svg = models.FileField(upload_to='pbn_outputs/svgs/', null=True, blank=True)  # <-- Add this line

    output_pdf = models.FileField(upload_to='pbn_outputs/pdfs/', null=True, blank=True)
    resized_jpeg = models.ImageField(upload_to='outputs/resized_jpeg/', null=True, blank=True)  # <-- Add this
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PBNOutput for {self.user.username} at {self.created_at}"