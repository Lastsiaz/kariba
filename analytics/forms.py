from django import forms
from .models import AnalyticsQuery, DataExport

class AnalyticsQueryForm(forms.ModelForm):
    class Meta:
        model = AnalyticsQuery
        fields = ['query_type', 'parameters', 'schedule_type', 'schedule_interval']
        widgets = {
            'parameters': forms.Textarea(attrs={'rows': 3}),
            'schedule_type': forms.Select(choices=[
                ('', 'No Schedule'),
                ('daily', 'Daily'),
                ('weekly', 'Weekly'),
                ('monthly', 'Monthly')
            ])
        }

    def clean_parameters(self):
        parameters = self.cleaned_data['parameters']
        try:
            # Ensure parameters is valid JSON
            import json
            json.loads(parameters)
            return parameters
        except json.JSONDecodeError:
            raise forms.ValidationError("Parameters must be valid JSON")

class DataExportForm(forms.ModelForm):
    class Meta:
        model = DataExport
        fields = ['format', 'query']
        widgets = {
            'format': forms.Select(choices=[
                ('csv', 'CSV'),
                ('json', 'JSON'),
                ('excel', 'Excel')
            ])
        } 