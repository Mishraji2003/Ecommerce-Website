# Generated by Django 5.0.2 on 2024-08-11 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MilkMagic', '0016_alter_product_category_delete_wishlist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('CR', 'Curd'), ('ML', 'Milk'), ('LS', 'Lassi'), ('MS', 'MilkShake'), ('Paneer', 'PR'), ('GH', 'Ghee'), ('CH', 'Cheese'), ('IC', 'Icebars'), ('kulfi', 'KF')], max_length=9),
        ),
    ]