# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.forms import extras

class BaseSetting(models.Model):
    
    class Meta:
        abstract = True

    def __unicode__(self):
        return u'%s' % self.value



class String(BaseSetting):
    value = models.CharField(max_length=254, null=True)



class Integer(BaseSetting):
    value = models.IntegerField(null=True)



class PositiveInteger(BaseSetting):
    value = models.PositiveIntegerField(null=True)


class Boolean(BaseSetting):
    value = models.BooleanField()

class Date(BaseSetting):
    value = models.DateField( auto_now=True, auto_now_add=True)
    widget = extras.widgets.SelectDateWidget()


class SettingManager(models.Manager):
    def get_value(self, name, **kw):
        if 'default' in kw:
            if not self.value_object_exists(name):
                return kw.get('default')
        return self.get(name=name).setting_object.value


    def value_object_exists(self, name):
        queryset = self.filter(name=name)
        return queryset.exists() and queryset[0].setting_object


    def set_value(self, name, SettingClass, value, desc=''):
        setting = Setting(name=name, description=desc)

        if self.value_object_exists(name):
            setting = self.get(name=name)
            setting_object = setting.setting_object
            setting_object.delete()

        setting.setting_object = SettingClass.objects.create(value=value)#,
               
                #description=desc)
        setting.save()
        return setting



class Setting(models.Model):
    class Meta:
        verbose_name = _('Setting')
        verbose_name_plural = _('Settings')

    objects = SettingManager()

    setting_type = models.ForeignKey(ContentType)
    setting_id = models.PositiveIntegerField()
    setting_object = generic.GenericForeignKey('setting_type', 'setting_id')

    name = models.CharField(max_length=255)
    description = models.TextField(_('description'))
    is_required = models.BooleanField(_('required'))
