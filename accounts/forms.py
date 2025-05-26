# forms.py (النسخة المعدّلة بعد الحذف)

from django import forms

class PhoneForm(forms.Form):
    phone = forms.CharField(label='')

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, label='رمز التحقق')
