from django import forms
from personal.models import PersonalPolicial


class CrearTemporalForm(forms.Form):
    """
    Solo CI, nombre completo y contraseña.
    El policía completará todo lo demás al iniciar sesión.
    """
    ci = forms.CharField(
        label='CI (Cédula de Identidad)',
        max_length=15,
        widget=forms.TextInput(attrs={
            'class'      : 'form-control form-control-lg',
            'placeholder': 'Ej: 12345678',
            'autofocus'  : True,
        }),
    )
    nombres = forms.CharField(
        label='Nombres',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class'      : 'form-control form-control-lg',
            'placeholder': 'Ej: Juan Carlos',
        }),
    )
    apellido_paterno = forms.CharField(
        label='Apellido Paterno',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class'      : 'form-control form-control-lg',
            'placeholder': 'Ej: Mamani',
        }),
    )
    apellido_materno = forms.CharField(
        label='Apellido Materno',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class'      : 'form-control form-control-lg',
            'placeholder': 'Ej: Quispe (opcional)',
        }),
    )
    password = forms.CharField(
        label='Contraseña temporal',
        required=False,
        widget=forms.TextInput(attrs={
            'class'       : 'form-control form-control-lg',
            'placeholder' : 'Dejar vacío = CI invertido',
            'autocomplete': 'off',
        }),
        help_text='Si lo dejas vacío se usará el CI al revés como contraseña.',
    )

    def clean_ci(self):
        ci = self.cleaned_data['ci'].strip()
        from personal.models import PersonalPolicial
        from core.models import Usuario
        if PersonalPolicial.objects.filter(ci=ci).exists():
            raise forms.ValidationError(
                f'Ya existe un personal con el CI "{ci}" en el sistema.'
            )
        if Usuario.objects.filter(username=ci).exists():
            raise forms.ValidationError(
                f'Ya existe un usuario con el nombre "{ci}".'
            )
        return ci


class CompletarRegistroForm(forms.ModelForm):
    """
    Formulario que el policía completa al iniciar sesión.
    Usa commit=False internamente y solo actualiza los campos
    que el policía puede editar, sin tocar los campos base
    (grado, unidad, estado_actual, etc.) que ya puso el admin.
    """
    class Meta:
        model  = PersonalPolicial
        # Solo los campos que el policía puede completar
        fields = [
            'codigo_identificacion',
            'expedido',
            'fecha_nacimiento',
            'genero',
            'grado',
            'unidad',
            'estado_actual',
            'fecha_ingreso',
            'telefono_personal',
            'telefono_emergencia',
            'correo_institucional',
            'direccion_domicilio',
            'cargo',
            'otra_profesion',
            'foto',
        ]
        widgets = {
            'codigo_identificacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código de identificación institucional',
            }),
            'expedido': forms.Select(
                choices=[
                    ('LP', 'La Paz'),   ('CB', 'Cochabamba'), ('SC', 'Santa Cruz'),
                    ('OR', 'Oruro'),    ('PT', 'Potosí'),     ('CH', 'Chuquisaca'),
                    ('TJ', 'Tarija'),   ('BE', 'Beni'),       ('PD', 'Pando'),
                ],
                attrs={'class': 'form-select'}
            ),
            'fecha_nacimiento'    : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'genero'              : forms.Select(attrs={'class': 'form-select'}),
            'grado'               : forms.Select(attrs={'class': 'form-select'}),
            'unidad'              : forms.Select(attrs={'class': 'form-select'}),
            'estado_actual'       : forms.Select(attrs={'class': 'form-select'}),
            'fecha_ingreso'       : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'telefono_personal'   : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 70012345'}),
            'telefono_emergencia' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 72234567'}),
            'correo_institucional': forms.EmailInput(attrs={'class': 'form-control'}),
            'direccion_domicilio' : forms.TextInput(attrs={'class': 'form-control'}),
            'cargo'        : forms.TextInput(attrs={'class': 'form-control'}),
            'otra_profesion'      : forms.TextInput(attrs={'class': 'form-control'}),
            'foto'                : forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Campos obligatorios para que el modelo pueda guardarse
        obligatorios = {
            'fecha_nacimiento', 'genero', 'grado',
            'unidad', 'estado_actual', 'fecha_ingreso',
        }
        for name, field in self.fields.items():
            if name not in obligatorios:
                field.required = False