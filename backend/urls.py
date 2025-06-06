"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # path('helloworld/', views.hello, name="hello"),

    # path('stream/', views.stream_test, name='stream'),
    
    path("excute/<str:pool_name>/<path:cmd>/", views.excute, name="excute"),
    path("getImage", views.get_image, name="get_image"),
    path("getText", views.get_text, name="get_text"),
    path('getPageInfo', views.get_page_info, name='get_page_info'),
    path('testApi', views.test_api, name='test_api'),
    
    # path('part1/execute/<str:algo>/<str:dataset>/', views.part1, name="part1"),
    # path('part1/result/<str:algo>/<str:dataset>/', views.get_part1_result, name="part1"),

    # path('part3/cgafile/<str:framework>/<str:algo>/<str:rw>/', views.part3_cgafile, name="part3_cgafile"),
    # path('part3/execute/<str:framework>/<str:algo>/', views.part3_3, name="part3"),
    # path('part3/execute/<str:framework>/<str:algo>/<str:dataset>/', views.part3, name="part3"),
    # path('part3/result/<str:framework>/<str:algo>/', views.get_part3_result, name='get_part3_result'),
    # path('part3data/<str:framework>/<str:algo>/<str:data_type>/', views.part3data, name='part3data'),
    # path('part3/moni/<str:framework>/<str:algo>/<str:dataset>/',views.part3_moni, name="part3_moni"),
    # path('part3/moni2/<str:algo>/<str:dataset>/',views.part3_moni2, name="part3_moni2"),
    

    
    # path('logfile/<str:filename>/', views.read_log_file, name="read_log_file"), 

]
