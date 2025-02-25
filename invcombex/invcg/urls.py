from django.urls import path
from . import views

urlpatterns = [
    path('upload_excel', views.upload_excel, name='upload_excel'),
    path('list_files', views.list_files, name='list_files'),
    path('view_sheets/<str:file_name>', views.view_sheets, name='view_sheets'),
    path('view_sheet/<str:file_name>/<str:sheet_name>', views.view_sheet, name='view_sheet'),
    path('save_data', views.save_data, name='save_data'),
]