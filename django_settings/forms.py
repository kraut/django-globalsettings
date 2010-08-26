# -*- coding: utf-8 -*-
from django import forms
from django.db.models import Q
from django.forms.models import modelform_factory
from django.contrib.contenttypes.models import ContentType 
from django.utils.translation import ugettext_lazy as _

from django_settings import models



class SettingForm(forms.ModelForm):
    class Meta:
        model = models.Setting
        fields = ('value',)
        #readonly_fields=('setting_id', 'setting_type')

    value = forms.CharField()

    def __init__(self, *a, **kw):
        forms.ModelForm.__init__(self, *a, **kw)
        instance = kw.get('instance')
        if 'setting_type' in self.fields :
            setting_type = self.fields['setting_type']
        elif instance:
            setting_type = instance.setting_type
        setting_type.queryset = ContentType.objects.filter( 
                Q(app_label='django_settings') ).exclude(name='Setting')
        if instance and 'value' in self.fields.keys():
            print "after"
            self.fields['value'].required = False 
            value = getattr(instance.setting_object, 'value', '')
            #set original form field for validation
            #than we need no own clean methoden!
            value_class = instance.setting_type.model_class()
            value_form = forms.models.modelform_factory(value_class)
            if  'value' in value_form().fields:
                self.fields['value']= value_form().fields['value']

            self.fields['value'].initial = value 
            widget = getattr(instance.setting_object,'widget', False)
            if widget:
                self.fields['value'].widget=widget
            self.fields['value'].label = instance.name
            self.fields['value'].help_text = instance.description


    def save(self, *args, **kwargs):
        cd = self.clean()

        if self.instance and self.instance.setting_id:
            setting_object = self.instance.setting_object
            setting_object.delete()
        kwargs['commit'] = False
        if 'setting_type' in cd.keys():
            setting_type = cd['setting_type']
        elif self.instance:
            setting_type=self.instance.setting_type
        instance = forms.ModelForm.save(self, *args, **kwargs)
        SettingClass = setting_type.model_class()

        setting_object= SettingClass.objects.create()
        if 'value' in cd.keys() and cd['value']:#we have no ajax right now thats why first time 
                                #creation is without a nice gui. so allow empty 
                                #values.
            setting_object.value = cd['value']
        setting_object.save()
        instance.setting_id = setting_object.id
        instance.save()
        return instance

class SettingCreationForm(SettingForm):
    ''' Settings create form does not include  value field. 
        Cause at this time widget and validation do not work.
    '''
    class Meta:
        model = models.Setting
        fields =  ('setting_type', 'name')

    def __init__(self, *a, **kw):
        #del self.value
        super(SettingCreationForm, self).__init__(*a, **kw)
        self.fields['value'].widget= forms.widgets.MultipleHiddenInput()
        self.fields['value'].required = False 
        self.fields['value'].help_text = _("You can set the value after saving this setting!")
        #del self.fields['value']
