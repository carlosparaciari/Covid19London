from django.urls import path

from . import views

app_name = 'plots'
urlpatterns = [
	path('', views.index, name='index'),
	path('abs/<borough_name>/', views.cumul_abs, name='cumulative_single'),
	path('rel/', views.cumul_rel, name='cumulative_multiple'),
	path('italy/', views.cumul_ita, name='cumulative_italy'),
]
