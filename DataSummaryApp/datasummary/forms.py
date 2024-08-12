from django import forms
from django.core.exceptions import ValidationError

class UploadFileForm(forms.Form):
    file = forms.FileField()
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            valid_extensions = ['.csv', '.xls', '.xlsx']
            extension = '.' + file.name.split('.')[-1].lower()
            
            if extension not in valid_extensions:
                raise ValidationError('Unsupported file extension. Please upload a CSV or Excel file.')
        
        return file
    