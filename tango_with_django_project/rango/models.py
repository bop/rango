from django.db import models
# -*- coding: utf-8 -*-
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "catégorie"
        verbose_name_plural = "catégories"


class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=100)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    website = models.URLField(blank=True)
    image = models.ImageField(upload_to='profile_images', blank=True)
    
    def __unicode__(self):
        return self.user.username
