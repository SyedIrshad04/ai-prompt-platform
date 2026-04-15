import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Prompt',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(db_index=True, max_length=255)),
                ('content', models.TextField()),
                ('complexity', models.IntegerField(default=5)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'prompts',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='prompt',
            index=models.Index(fields=['complexity', 'is_active'], name='prompts_complexity_is_active_idx'),
        ),
        migrations.AddIndex(
            model_name='prompt',
            index=models.Index(fields=['created_at', 'is_active'], name='prompts_created_at_is_active_idx'),
        ),
        migrations.AddIndex(
            model_name='prompt',
            index=models.Index(fields=['title'], name='prompts_title_idx'),
        ),
    ]
