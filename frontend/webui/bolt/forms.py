from django import forms
from bootstrap_toolkit.widgets import *

class RetypeForm(forms.Form):
    sentence = forms.CharField(max_length=100, widget=BootstrapTextInput(prepend='Your input', attrs={'class':'input-xxlarge'})
    , label='', required=True,)