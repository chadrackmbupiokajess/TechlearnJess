from django.db import migrations
from django.conf import settings

def create_default_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    Site.objects.update_or_create(
        id=settings.SITE_ID,
        defaults={
            'domain': 'example.com',
            'name': 'example.com',
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        # Assurez-vous que la migration des sites est appliquée avant celle-ci
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_site),
    ]
