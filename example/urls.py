# example/urls.py
from django.urls import path
from example.views import player, index, cta_clicked, main_page  # Import cta_clicked
from . import views

from django.views import defaults as default_views

handler404 = default_views.page_not_found


urlpatterns = [
    path('player/<slug:slug>/', player),  # URL for video player
    path('videos/<slug:slug>/', index),  # URL for landing page
    path('cta-clicked/', views.cta_clicked, name='cta_clicked'),
    path('exit-page/', views.exit_page, name='exit_page'),
    path('', main_page)
]