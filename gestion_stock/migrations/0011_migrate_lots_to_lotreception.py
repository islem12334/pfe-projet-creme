from django.db import migrations


def copy_lots_forward(apps, schema_editor):
    Reception = apps.get_model('gestion_stock', 'Reception')
    LotReception = apps.get_model('gestion_stock', 'LotReception')

    for reception in Reception.objects.all():
        for i in range(1, 11):
            code = getattr(reception, f'lot_code{i}', '') or ''
            quantite = getattr(reception, f'lot_quantite{i}', None) or 0
            if code.strip():
                LotReception.objects.create(
                    reception=reception,
                    code=code.strip(),
                    quantite=quantite,
                    ordre=i,
                )


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_stock', '0010_lotreception'),
    ]

    operations = [
        migrations.RunPython(copy_lots_forward, migrations.RunPython.noop),
    ]
