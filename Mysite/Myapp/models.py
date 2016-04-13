from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

class site (models.Model):
    site_name=models.TextField()
    is_used=models.CharField(max_length=5)
    def __unicode__(self):
        return self.site_name


class UserShared_animations (models.Model):
    username = models.ManyToManyField(User)
    shared_type=models.ForeignKey(site)
    url = models.TextField()
    def __unicode__(self):
        return self.url

class animation (models.Model):
    animation_url = models.OneToOneField(UserShared_animations)
    url = models.TextField()
    title = models.TextField()
    type = models.TextField()
    time = models.TextField()
    info  = models.TextField()
    tag = models.TextField()
    image_url = models.TextField()
    def __unicode__(self):
        return self.title

class animations_image(models.Model):
    image_url = models.OneToOneField(animation)
    image_id = models.CharField(max_length=30)
    def  __unicode__(self):
        return self.image_id
