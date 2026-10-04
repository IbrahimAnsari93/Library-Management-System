                                                

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0012_finepayment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('notification_type', models.CharField(choices=[('overdue', 'Overdue Book'), ('due_soon', 'Due Soon'), ('low_stock', 'Low Stock'), ('out_of_stock', 'Out of Stock'), ('fine', 'Pending Fine')], max_length=30)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
