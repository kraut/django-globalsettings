# -*- coding: utf-8 -*-
import django
from django.contrib import admin
from django.utils.translation import ugettext as _
from django.contrib.contenttypes import generic
from django_settings import models, forms

def get_setting_value(obj):
    return obj.setting_object.value
get_setting_value.short_description = _('Value')

#def get_setting_description(obj):
#    return obj.setting_object.description



class SettingAdmin(admin.ModelAdmin):
    model = models.Setting
    form = forms.SettingForm
    list_display = ('name',  'setting_type','description',
            get_setting_value )
    add_form = forms.SettingCreationForm

    
    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults.update({
                'form': self.add_form,
                'fields': ('name', 'setting_type', 'description', 'is_required'),
            })
        defaults.update(kwargs)
        return super(SettingAdmin, self).get_form(request, obj, **defaults)
admin.site.register(models.Setting, SettingAdmin)
