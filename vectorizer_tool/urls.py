from django.urls import path
from . import views
from .views import PaintByNumberView, VectorizeImageView, download_resized_jpeg, download_resized_pdf,vectorizer_form_view



urlpatterns = [
    path('', vectorizer_form_view, name='vectorizer_ui'),
    path('vectorize/',  VectorizeImageView.as_view(), name='vectorize'),
    path('test-pbn/<int:job_id>/', views.test_pbn_frontend, name='test_pbn_frontend'),
    path("generate-pbn/", PaintByNumberView.as_view(), name="generate_pbn"),
    path('download-resized-jpeg/', download_resized_jpeg, name='download_resized_jpeg'),
    path("download-resized-pdf/", download_resized_pdf, name="download_resized_pdf"),

   
]


