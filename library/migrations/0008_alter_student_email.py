                                                

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0007_student_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
