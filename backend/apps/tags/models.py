from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True)
    prompts = models.ManyToManyField('prompts.Prompt', related_name='tags', blank=True)

    class Meta:
        db_table = 'tags'
        ordering = ['name']

    def __str__(self):
        return self.name
