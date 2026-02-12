import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_policial.settings')
django.setup()

from core.models import Usuario

print("🔄 Migrando roles...")

# Migrar roles
encargados = Usuario.objects.filter(rol='encargado').update(rol='oficial_administrativo')
policiales = Usuario.objects.filter(rol='policial').update(rol='usuario_autorizado')

print(f"✅ {encargados} encargados → oficiales administrativos")
print(f"✅ {policiales} policiales → usuarios autorizados")
print("✅ Migración completada")