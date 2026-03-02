from django import forms
from .models import Usuario

class AsignarRolForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        help_text="Dejar en blanco para no cambiar la contraseña"
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'password', 'rol']