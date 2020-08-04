from django.urls import path

from . import views

app_name = 'plots'
urlpatterns = [
	path('', views.index, name='index'),
	path('London/abs/<borough_name>/', views.cumul_abs, name='cumulative_single'),
	path('London/rel/', views.cumul_rel, name='cumulative_multiple'),
	path('London/trends/<borough_name>/', views.trends, name='trends'),
	path('Italy/abs/<province_name>/', views.cumul_ita, name='cumulative_italy'),
	path('Italy/trends/<province_name>/', views.trends_ita, name='trends_italy'),
]
