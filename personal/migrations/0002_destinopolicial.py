from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogos', '0001_initial'),
        ('personal', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DestinoPolicial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_destino', models.CharField(
                    max_length=20,
                    choices=[
                        ('asignacion',    'Asignación de Unidad'),
                        ('comision',      'Comisión de Servicio'),
                        ('destacamento',  'Destacamento'),
                        ('capacitacion',  'Capacitación'),
                        ('temporal',      'Destino Temporal'),
                    ]
                )),
                ('fecha_inicio',    models.DateField()),
                ('fecha_fin',       models.DateField(null=True, blank=True)),
                ('activo',          models.BooleanField(default=True)),
                ('lugar_destino',   models.CharField(max_length=200)),
                ('descripcion',     models.TextField()),
                ('numero_resolucion', models.CharField(max_length=100, blank=True, null=True)),
                ('observaciones',   models.TextField(blank=True, null=True)),
                ('fecha_registro',  models.DateTimeField(auto_now_add=True)),
                ('personal', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='destinos',
                    to='personal.personalpolicial'
                )),
                ('unidad_destino', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='destinos_asignados',
                    to='catalogos.unidad',
                    null=True, blank=True
                )),
                ('registrado_por', models.ForeignKey(
                    on_delete=django.db.models.deletion.SET_NULL,
                    null=True,
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Destino Policial',
                'verbose_name_plural': 'Destinos Policiales',
                'ordering': ['-fecha_inicio'],
            },
        ),
    ]


