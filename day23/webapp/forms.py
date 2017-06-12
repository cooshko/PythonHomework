#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh

from django import forms
from django.contrib.admin import widgets
from .models import *


class LoginForm(forms.Form):
    username = forms.CharField(max_length=60, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


# class ScoreForm(forms.ModelForm):
#     class Meta:
#         model = CourseScore
#         fields = ("course", "score", "test_at")


class FollowUp(forms.ModelForm):
    class Meta:
        model = ClientFollowUp
        fields = ("result", )
        labels = {"result": "跟进结果", }


class ClientInfoForm(forms.ModelForm):
    class Meta:
        model = ClientInfo
        fields = ("name", "phone", "qq", "email", "remark",)
        labels = {"name": "称谓",
                  "phone": "电话",
                  "qq": "QQ",
                  "remark": "备注",
                  }
        widgets = {
            "phone": forms.TextInput,
            "qq": forms.TextInput,
        }

    def clean(self):
        cleaned_data = super(ClientInfoForm, self).clean()
        if not (cleaned_data.get("phone") or cleaned_data.get("qq") or  cleaned_data.get("email")):
            raise forms.ValidationError("电话、Email、QQ，至少需提供一个")
