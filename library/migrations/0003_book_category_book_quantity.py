                                                

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_remove_book_available_quantity_remove_book_category_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='category',
            field=models.CharField(default='General', max_length=100),
        ),
        migrations.AddField(
            model_name='book',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
