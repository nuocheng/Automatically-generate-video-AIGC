#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Module Documentation 
    here
"""

# Created by  : Zhang Chengdong
# Create Date : 2024/7/24 19:44
# Version = v0.1.0

__author__ = "Zhang Chengdong"
__copyright__ = "Copyright 2024. Large scale model"
__credits__ = ['Zhang Chengdong']

__liscence__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Zhang Chengdong"
__status__ = "Production"
from django.urls import path
from . import views
app_name = 'video_gen'

urlpatterns = [
    path("v1/video/",views.get_relate_img,name="get_relate_img"),
]
