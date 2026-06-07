from django import forms
from personal.models import PersonalPolicial


# ── Formulario que el policía llena para completar su registro ────
class CompletarRegistroForm(forms.ModelForm):
    """
    Todos los campos que el policía puede completar sobre sí mismo.
    El administrativo ya habrá creado: CI, nombre, grado, unidad, estado, fecha_ingreso.
    El policía completa el resto.
    """

    class Meta:
        model  = PersonalPolicial
        fields = [
            # Identificación adicional
            'expedido',
            # Datos personales
            'fecha_nacimiento',
            'genero',
            # Contacto
            'telefono_personal',
            'telefono_emergencia',
            'correo_institucional',
            'direccion_domicilio',
            # Laboral
            'cargo_actual',
            'otra_profesion',
            # Foto
            'foto',
        ]
        widgets = {
            'expedido': forms.Select(
                choices=[
                    ('LP','La Paz'), ('CB','Cochabamba'), ('SC','Santa Cruz'),
                    ('OR','Oruro'), ('PT','Potosí'), ('CH','Chuquisaca'),
                    ('TJ','Tarija'), ('BE','Beni'), ('PD','Pando'),
                ],
                attrs={'class': 'form-select'}
            ),
            'fecha_nacimiento'   : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'genero'             : forms.Select(attrs={'class': 'form-select'}),
            'telefono_personal'  : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 70012345'}),
            'telefono_emergencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 72234567'}),
            'correo_institucional': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@policia.gob.bo'}),
            'direccion_domicilio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Calle, número, zona, ciudad'}),
            'cargo_actual'       : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Jefe de Patrullaje'}),
            'otra_profesion'     : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Licenciado en Derecho'}),
            'foto'               : forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo fecha_nacimiento y genero son obligatorios; el resto opcional
        obligatorios = {'fecha_nacimiento', 'genero', 'expedido'}
        for name, field in self.fields.items():
            if name not in obligatorios:
                field.required = False


# ── Formulario que el admin usa para crear personal + usuario temporal ──
class CrearPersonalTemporalForm(forms.ModelForm):
    """
    Campos mínimos que el admin llena para crear el registro base.
    El policía completará el resto.
    """
    password = forms.CharField(
        label='Contraseña temporal',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text='Dejar vacío para usar CI invertido como contraseña.',
    )

    class Meta:
        model  = PersonalPolicial
        fields = [
            'codigo_identificacion',
            'ci',
            'nombres',
            'apellido_paterno',
            'apellido_materno',
            'grado',
            'unidad',
            'estado_actual',
            'fecha_ingreso',
        ]
        widgets = {
            'codigo_identificacion': forms.TextInput(attrs={'class': 'form-control'}),
            'ci'                   : forms.TextInput(attrs={'class': 'form-control'}),
            'nombres'              : forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_paterno'     : forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_materno'     : forms.TextInput(attrs={'class': 'form-control'}),
            'grado'                : forms.Select(attrs={'class': 'form-select'}),
            'unidad'               : forms.Select(attrs={'class': 'form-select'}),
            'estado_actual'        : forms.Select(attrs={'class': 'form-select'}),
            'fecha_ingreso'        : forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }