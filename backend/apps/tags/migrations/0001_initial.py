from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('prompts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=50, unique=True)),
                ('prompts', models.ManyToManyField(blank=True, related_name='tags', to='prompts.prompt')),
            ],
            options={
                'db_table': 'tags',
                'ordering': ['name'],
            },
        ),
    ]
