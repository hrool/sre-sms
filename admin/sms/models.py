from django.db import models

# Project
class Project(models.Model):
    name = models.CharField(verbose_name='名称', max_length=20, unique=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = '项目'
        verbose_name_plural = verbose_name