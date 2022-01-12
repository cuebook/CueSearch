from django.db import models
from dataset.models import Dataset

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
