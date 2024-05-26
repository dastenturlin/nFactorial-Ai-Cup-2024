from django.db import models


class Stock(models.Model):
    name = models.CharField(max_length=100)
    ticker = models.CharField(max_length=50, unique=True)
    description = models.TextField()
