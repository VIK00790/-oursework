from django import forms
from .models import Comment, Marketplace, Tag

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Оставьте комментарий...',
            })
        }

class MarketplaceForm(forms.ModelForm):
    class Meta:
        model = Marketplace
        fields = ['title', 'price', 'content', 'tags', 'is_public', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название товара'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Описание товара...'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].help_text = 'Удерживайте Ctrl (Cmd) для выбора нескольких тегов'
        self.fields['image'].required = False