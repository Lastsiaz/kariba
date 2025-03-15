from django import forms
from .models import SentimentAnalysis, SentimentConfiguration

class SentimentAnalysisForm(forms.ModelForm):
    class Meta:
        model = SentimentAnalysis
        fields = ['text', 'source_type', 'language']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter text for sentiment analysis...'
            }),
            'source_type': forms.Select(choices=[
                ('manual', 'Manual Input'),
                ('twitter', 'Twitter'),
                ('news', 'News Articles'),
                ('reviews', 'Customer Reviews')
            ]),
            'language': forms.Select(choices=[
                ('en', 'English'),
                ('es', 'Spanish'),
                ('fr', 'French'),
                ('de', 'German')
            ])
        }

class SentimentConfigurationForm(forms.ModelForm):
    class Meta:
        model = SentimentConfiguration
        fields = ['algorithm', 'threshold', 'batch_size', 'is_active']
        widgets = {
            'algorithm': forms.Select(choices=[
                ('vader', 'VADER'),
                ('textblob', 'TextBlob'),
                ('transformers', 'Transformers'),
                ('custom', 'Custom Model')
            ]),
            'threshold': forms.NumberInput(attrs={
                'step': '0.1',
                'min': '0',
                'max': '1'
            })
        }

    def clean_threshold(self):
        threshold = self.cleaned_data['threshold']
        if threshold < 0 or threshold > 1:
            raise forms.ValidationError("Threshold must be between 0 and 1")
        return threshold 