from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import os
from django.conf import settings

def upload_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']

        # Guardar el archivo en la carpeta media/invcg
        upload_path = os.path.join(settings.MEDIA_ROOT, 'invcg', excel_file.name)
        with open(upload_path, 'wb+') as destination:
            for chunk in excel_file.chunks():
                destination.write(chunk)

        # Mensaje de éxito
        messages.success(request, f'Archivo "{excel_file.name}" subido correctamente.')

        # Leer el archivo Excel con pandas
        try:
            excel_data = pd.ExcelFile(upload_path)
            sheets = {}
            for sheet_name in excel_data.sheet_names:
                df = excel_data.parse(sheet_name)
                sheets[sheet_name] = df.to_html(classes='table table-bordered', index=False)

            # Pasar los datos al template
            return render(request, 'invcg/upload_excel.html', {'sheets': sheets})
        except Exception as e:
            messages.error(request, f'Error al procesar el archivo: {str(e)}')
            return redirect('upload_excel')

    return render(request, 'invcg/upload_excel.html')

def view_sheets(request, file_name):
    # Ruta del archivo Excel
    file_path = os.path.join(settings.MEDIA_ROOT, 'invcg', file_name)

    # Leer el archivo Excel
    try:
        excel_data = pd.ExcelFile(file_path)
        sheets = {sheet_name: excel_data.parse(sheet_name) for sheet_name in excel_data.sheet_names}
    except Exception as e:
        return render(request, 'invcg/error.html', {'error': str(e)})

    return render(request, 'invcg/view_sheets.html', {
        'file_name': file_name,
        'sheets': sheets
    })

def view_sheet(request, file_name, sheet_name):
    # Ruta del archivo Excel
    file_path = os.path.join(settings.MEDIA_ROOT, 'invcg', file_name)

    # Leer la hoja específica del archivo Excel
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        table_html = df.to_html(classes='table table-bordered', index=False)
    except Exception as e:
        return render(request, 'invcg/error.html', {'error': str(e)})

    return render(request, 'invcg/view_sheet.html', {
        'file_name': file_name,
        'sheet_name': sheet_name,
        'table_html': table_html
    })

def list_files(request):
    # Obtener la lista de archivos en media/invcg/
    files_path = os.path.join(settings.MEDIA_ROOT, 'invcg')
    files = [f for f in os.listdir(files_path) if os.path.isfile(os.path.join(files_path, f))]

    return render(request, 'invcg/list_files.html', {'files': files})

@csrf_exempt
def save_data(request):
    if request.method == 'POST':
        # Obtener los datos enviados por AJAX
        file_name = request.POST.get('file_name')
        sheet_name = request.POST.get('sheet_name')
        row_id = request.POST.get('row_id')
        column_name = request.POST.get('column_name')
        new_value = request.POST.get('new_value')

        # Validar los datos recibidos
        if not all([file_name, sheet_name, row_id, column_name, new_value]):
            return JsonResponse({'status': 'error', 'message': 'Datos incompletos.'})

        # Ruta del archivo Excel
        file_path = os.path.join(settings.MEDIA_ROOT, 'invcg', file_name)

        try:
            # Leer el archivo Excel
            excel_data = pd.ExcelFile(file_path)
            sheets = {sheet: excel_data.parse(sheet) for sheet in excel_data.sheet_names}
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error al leer el archivo: {str(e)}'})

        # Verificar que la hoja exista
        if sheet_name not in sheets:
            return JsonResponse({'status': 'error', 'message': 'Hoja no encontrada.'})

        # Obtener el DataFrame de la hoja
        df = sheets[sheet_name]

        # Verificar que la fila y columna existan
        if int(row_id) >= len(df) or column_name not in df.columns:
            return JsonResponse({'status': 'error', 'message': 'Fila o columna no válida.'})

        # Actualizar el valor en la hoja correspondiente
        df.at[int(row_id), column_name] = new_value

        try:
            # Guardar los cambios en el archivo Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                for sheet, df_sheet in sheets.items():
                    df_sheet.to_excel(writer, sheet_name=sheet, index=False)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error al guardar el archivo: {str(e)}'})

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})