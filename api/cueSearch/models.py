from django.db import models
from dataset.models import Dataset, ConnectionType

# Create your models here.


class GlobalDimension(models.Model):

    name = models.CharField(unique=True, max_length=500)
    published = models.BooleanField(default=False)

    def __repr__(self):
        return self.name


class GlobalDimensionValues(models.Model):

    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    dimension = models.CharField(max_length=500)
    globalDimension = models.ForeignKey(GlobalDimension, on_delete=models.CASCADE)

    def __str__(self):
        return self.dimension


class SearchCardTemplate(models.Model):
    RENDER_TYPE_TABLE = "table"
    RENDER_TYPE_LINE = "line"

    connectionType = models.ManyToManyField(ConnectionType, blank=True)
    templateName = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    bodyText = models.TextField(null=True, blank=True)
    sql = models.TextField(null=True, blank=True)
    renderType = models.CharField(default=RENDER_TYPE_TABLE, max_length=200)
    published = models.BooleanField(default=False)

    def __repr__(self):
        return self.templateName
