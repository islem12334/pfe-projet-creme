from django.db import migrations, models
import django.db.models.deletion
import decimal


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_stock', '0009_of_unique'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reception',
            name='lot_code1',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='reception',
            name='lot_code2',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='reception',
            name='lot_code3',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.CreateModel(
            name='LotReception',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50)),
                ('quantite', models.DecimalField(decimal_places=3, default=decimal.Decimal('0'), max_digits=10)),
                ('ordre', models.PositiveIntegerField(default=1)),
                ('reception', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lots', to='gestion_stock.reception')),
            ],
            options={
                'ordering': ['ordre'],
                'unique_together': {('reception', 'ordre')},
            },
        ),
    ]
