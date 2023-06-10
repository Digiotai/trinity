from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.registerPage,name="register"),
    path('login/', views.loginPage,name="login"),
    path('logout/', views.logoutUser,name="logout"),
    path('',views.dashboard,name='dashboard'),
    path('monitor/',views.arima,name='arima'),
    path('RF/',views.RF,name='RF'),
    path('Insights/', views.XGB, name='Insights'),


]
