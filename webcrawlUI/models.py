from django.db import models

# Create your models here.
from django.db import models


class States(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30, unique=True)
    weblink = models.CharField(max_length=255, default="")

class Cities(models.Model):
    name = models.CharField(max_length=50, unique=True)
    state = models.ForeignKey(States, on_delete=models.CASCADE)
    state_name = models.CharField(max_length=30, default="")

class Weblinks(models.Model):
    city = models.ForeignKey(Cities, on_delete=models.CASCADE)
    city_name = models.CharField(max_length=50, default="")
    weblink = models.CharField(max_length=255, default="")

class WebData(models.Model):
    weblink = models.CharField(max_length=255, default="")
    city_name = models.CharField(max_length=50, default="")
    text = models.TextField()

