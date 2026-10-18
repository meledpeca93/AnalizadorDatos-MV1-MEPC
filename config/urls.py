from django.urls import path
from analyzer.views import index

urlpatterns = [path('', index, name='index')]
