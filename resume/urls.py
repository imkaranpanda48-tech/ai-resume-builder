from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_resume, name='upload_resume'),
    path('ats/', views.ats_score, name='ats_score'),
    path('edit/', views.edit, name='edit'),
    path('templates/', views.choose_template, name='choose_template'),
    path("pdf/<str:template>/", views.generate_pdf, name="generate_pdf"),
]