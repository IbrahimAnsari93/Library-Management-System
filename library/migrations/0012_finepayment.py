                                                

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0011_alter_book_description_alter_book_edition_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinePayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fine_amount', models.PositiveIntegerField(default=0)),
                ('paid_amount', models.PositiveIntegerField(default=0)),
                ('payment_status', models.CharField(choices=[('Pending', 'Pending'), ('Partial', 'Partial'), ('Paid', 'Paid')], default='Pending', max_length=20)),
                ('payment_method', models.CharField(blank=True, choices=[('Cash', 'Cash'), ('UPI', 'UPI'), ('Card', 'Card'), ('Bank Transfer', 'Bank Transfer')], default='', max_length=30)),
                ('payment_date', models.DateField(blank=True, null=True)),
                ('transaction_id', models.CharField(blank=True, default='', max_length=100)),
                ('notes', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('issue', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='fine_payment', to='library.issue')),
            ],
        ),
    ]
