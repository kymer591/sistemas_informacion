import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('personal', '0004_alter_destinopolicial_descripcion_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistroTemporal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                    serialize=False, verbose_name='ID')),
                ('estado', models.CharField(
                    choices=[
                        ('pendiente',  'Pendiente — esperando que el policía complete sus datos'),
                        ('completado', 'Completado — esperando revisión del administrativo'),
                        ('aprobado',   'Aprobado — cuenta activada como normal'),
                        ('rechazado',  'Rechazado'),
                    ],
                    default='pendiente', max_length=12)),
                ('observaciones_rev', models.TextField(blank=True, null=True)),
                ('fecha_creacion',   models.DateTimeField(auto_now_add=True)),
                ('fecha_completado', models.DateTimeField(null=True, blank=True)),
                ('fecha_aprobacion', models.DateTimeField(null=True, blank=True)),
                ('personal', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='registro_temporal',
                    to='personal.personalpolicial')),
                ('usuario', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='registro_temporal',
                    to=settings.AUTH_USER_MODEL)),
                ('creado_por', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='registros_creados',
                    to=settings.AUTH_USER_MODEL)),
                ('revisado_por', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='registros_revisados',
                    to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name'        : 'Registro Temporal',
                'verbose_name_plural' : 'Registros Temporales',
                'ordering'            : ['-fecha_creacion'],
            },
        ),
    ]