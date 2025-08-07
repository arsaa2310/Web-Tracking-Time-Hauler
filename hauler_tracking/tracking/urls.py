from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_driver, name='login_driver'),
    path("submit-delay/", views.submit_delay, name="submit_delay"),
    path('main/', views.main_menu, name='main_menu'),
    path('next/', views.next_activity, name='next_activity'),
    path('delay/', views.delay_site, name='delay_site'),
    path('delay_activity/', views.delay_activity, name='delay_activity'),
    path('logout/', views.logout_driver, name='logout_driver'),
]





    



