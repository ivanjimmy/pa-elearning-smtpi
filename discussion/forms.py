from django import forms
from .models import SiswaDiscussion, PengasuhDiscussion


class SiswaDiscussionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SiswaDiscussionForm, self).__init__(*args, **kwargs)
        self.fields['content'].required = True
        self.fields['content'].label = ''

    class Meta:
        model = SiswaDiscussion
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={'class': 'form-control', 'id': 'content', 'name': 'content', 'placeholder': 'Write message...', 'type': 'text'}),
        }


class PengasuhDiscussionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PengasuhDiscussionForm, self).__init__(*args, **kwargs)
        self.fields['content'].required = True
        self.fields['content'].label = ''

    class Meta:
        model = PengasuhDiscussion
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={'class': 'form-control', 'id': 'content', 'name': 'content', 'placeholder': 'Write message...', 'type': 'text'}),
        }
