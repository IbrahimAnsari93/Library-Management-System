                                                

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0004_issue'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='roll_no',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
