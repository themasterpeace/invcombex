# invcg/forms.py
from django import forms

class UploadExcelForm(forms.Form):
    excel_file = forms.FileField(label='Sube tu archivo Excel')