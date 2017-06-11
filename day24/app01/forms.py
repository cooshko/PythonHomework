#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
from django import forms
from .models import *
import os, sys, datetime, re


class LoginFrm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="密码")
    password2 = forms.CharField(widget=forms.PasswordInput, label="确认密码")

    class Meta:
        model = User
        fields = ("login_name", "password", )


class RegisterFrm(forms.ModelForm):
    login_name = forms.CharField(required=True, error_messages={
        'required': '用户名不能为空',
    })
    email = forms.EmailField(error_messages={
        'required': '邮箱不能为空',
    })
    password = forms.CharField(widget=forms.PasswordInput, label="密码", error_messages={
        'required': '密码不能为空',
    })
    password2 = forms.CharField(widget=forms.PasswordInput, label="确认密码", error_messages={
        'required': '确认密码不能为空',
    })
    verify_code = forms.CharField(max_length=4, error_messages={
        'required': '验证码不能为空',
    })

    class Meta:
        model = User
        fields = ("login_name", "password", "email")

    def clean_login_name(self):
        """login_name里不允许有空格"""
        cd = self.cleaned_data
        login_name = cd.get("login_name").strip()
        if "\s" in login_name:
            raise forms.ValidationError("用户名不能有空格")
        return login_name

    def clean_password2(self):
        """两次密码是否一致"""
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('确认密码不一致')
        return cd['password2']
