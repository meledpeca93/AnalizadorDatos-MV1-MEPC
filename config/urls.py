from django.urls import path
from analyzer.views import home, index, uth_logo

urlpatterns = [
    path('', home, name='home'),
    path('analizador/', index, name='index'),
    path('identidad/logo-uth.png', uth_logo, name='uth-logo'),
]
