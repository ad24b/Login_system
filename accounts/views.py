from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import  PhoneForm, OTPForm
from .models import Profile
from twilio.rest import Client
from decouple import config
import random

# إعدادات Twilio
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = config('TWILIO_WHATSAPP_NUMBER')

# إرسال رمز التحقق عبر واتساب
def send_otp_whatsapp(to_phone, otp_code):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"رمز التحقق الخاص بك هو: {otp_code}",
        from_=TWILIO_WHATSAPP_NUMBER,
        to=f'whatsapp:{to_phone}'
    )
    print("تم إرسال الرسالة:", message.sid)

# تسجيل الدخول عبر اسم المستخدم أو رقم الجوال


# تسجيل الدخول عبر رقم الجوال باستخدام OTP
def phone_login(request):
    if request.method == 'POST':
        form = PhoneForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data.get('phone')

            try:
                user = Profile.objects.get(phone=phone).user
                request.session['phone'] = phone

                # إنشاء رمز التحقق
                otp = str(random.randint(100000, 999999))
                request.session['otp'] = otp

                # تحويل الرقم إلى الصيغة الدولية إذا لزم الأمر
                if phone.startswith('0'):
                    to_phone = '+966' + phone[1:]
                elif not phone.startswith('+'):
                    to_phone = '+966' + phone  # في حال لم يبدأ بـ + ولا 0
                else:
                    to_phone = phone

                # إرسال رمز التحقق
                send_otp_whatsapp(to_phone, otp)
                print("✅ تم إرسال رمز OTP بنجاح إلى:", to_phone)

                messages.success(request, "تم إرسال رمز التحقق إلى رقم واتساب الخاص بك.")
                return redirect('verify_otp')

            except Profile.DoesNotExist:
                messages.error(request, "رقم الهاتف غير مسجل.")
                return redirect('phone_login')

    else:
        form = PhoneForm()

    return render(request, 'accounts/phone_login.html', {'form': form})



# التحقق من رمز OTP
def verify_otp(request):
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data.get('otp')
            saved_otp = request.session.get('otp')
            phone = request.session.get('phone')

            if otp == saved_otp:
                user = Profile.objects.get(phone=phone).user
                login(request, user)
                del request.session['otp']
                del request.session['phone']
                return redirect('home')
            else:
                messages.error(request, "رمز التحقق غير صحيح.")
                return redirect('verify_otp')
    else:
        form = OTPForm()
    return render(request, 'accounts/verify.html', {'form': form})

# تسجيل الخروج
def user_logout(request):
    logout(request)
    return redirect('login')

# الصفحة الرئيسية - محمية بتسجيل الدخول
@login_required(login_url='phone_login')
def home(request):
    return render(request, 'accounts/home.html')
