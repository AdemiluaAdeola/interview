from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('polling-unit-result/', views.polling_unit_result, name='polling_unit_result'),
    path('lga-results/', views.lga_results, name='lga_results'),
    path('new-polling-unit/', views.new_polling_unit, name='new_polling_unit'),
]