from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100, required=True)
    password = forms.CharField(label='Password', max_length=100, required=True)

class ItemSearchForm(forms.Form):
    search = forms.CharField(label='Search through services', widget=forms.TextInput(attrs={'placeholder': 'Type something...'}), help_text="Leave empty to browse all available services", max_length=100, required=False)