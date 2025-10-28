from django import forms
from .models import *




class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__' #['tittle', 'slug', 'content', 'category', 'is_published', 'tags']
        exclude = ['author', 'views', 'created_at', 'updated_at']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control mb-4'}),
        }
