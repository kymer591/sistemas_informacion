from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personal', '0002_destinopolicial'),  # ajustar al nombre de tu última migración
    ]

    operations = [
        migrations.AddField(
            model_name='personalpolicial',
            name='direccion_domicilio',
            field=models.CharField(
                blank=True, null=True,
                max_length=300,
                verbose_name='Dirección del domicilio'
            ),
        ),
        migrations.AddField(
            model_name='personalpolicial',
            name='cargo_actual',
            field=models.CharField(
                blank=True, null=True,
                max_length=200,
                verbose_name='Cargo actual'
            ),
        ),
        migrations.AddField(
            model_name='personalpolicial',
            name='otra_profesion',
            field=models.CharField(
                blank=True, null=True,
                max_length=200,
                verbose_name='Otra profesión (Licenciatura/Técnico)',
                help_text='Profesión fuera de la institución policial'
            ),
        ),
    ]


