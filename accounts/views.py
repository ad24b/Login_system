from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .forms import PhoneForm, OTPForm
from .models import Profile
from twilio.rest import Client
from decouple import config
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# إعدادات Twilio
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = config('TWILIO_WHATSAPP_NUMBER')

# إرسال رمز التحقق عبر واتساب
def send_otp_whatsapp(to_phone, otp_code):
    print(f"[تجريبي] رقم التحقق لرقم {to_phone} هو: {otp_code}")
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"رمز التحقق الخاص بك هو: {otp_code}",
            from_=TWILIO_WHATSAPP_NUMBER,
            to=f'whatsapp:{to_phone}'
        )
        print("✅ تم إرسال الرسالة عبر واتساب:", message.sid)
    except Exception as e:
        print("⚠️ خطأ في إرسال رسالة واتساب:", e)


# تسجيل الدخول أو البدء بإنشاء حساب
def phone_login(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        password = request.POST.get('password', '').strip()

        # تحويل الرقم المحلي إلى دولي
        if identifier.startswith('05'):
            identifier = '+966' + identifier[1:]

        user = None
        if User.objects.filter(username=identifier).exists():
            user = User.objects.get(username=identifier)
        elif Profile.objects.filter(phone=identifier).exists():
            user = Profile.objects.get(phone=identifier).user

        if user:
            if password:
                user = authenticate(request, username=user.username, password=password)
                if user:
                    login(request, user)
                    messages.success(request, f"تم تسجيل الدخول بنجاح، مرحباً {user.username}")
                    return redirect('home')
                else:
                    messages.error(request, "كلمة المرور غير صحيحة.")
                    return redirect('phone_login')
            else:
                messages.error(request, "أدخل كلمة المرور.")
                return redirect('phone_login')
        else:
            messages.error(request, "عذرًا، اسم المستخدم أو رقم الجوال غير صحيح.")
            return redirect('phone_login')

    return render(request, 'accounts/phone_login.html')


# التحقق من رمز OTP
def verify_otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        real_otp = request.session.get('otp')
        phone = request.session.get('phone')

        if user_otp == real_otp:
            try:
                profile = Profile.objects.get(phone=phone)
                user = profile.user
                login(request, user)
                messages.success(request, f"تم تسجيل الدخول بنجاح، مرحباً {user.username}")
                return redirect('home')
            except Profile.DoesNotExist:
                return redirect('register_user')
        else:
            messages.error(request, "رمز التحقق غير صحيح.")
            return redirect('verify_otp')

    return render(request, 'accounts/verify.html')

# تسجيل مستخدم جديد
def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "كلمة المرور غير متطابقة.")
            return redirect('register_user')

        phone = request.session.get('phone')
        if not phone:
            messages.error(request, "لا يوجد رقم جوال في الجلسة.")
            return redirect('phone_login')

        user = User.objects.create(
            username=username,
            password=make_password(password)
        )
        Profile.objects.create(user=user, phone=phone)
        login(request, user)
        messages.success(request, "تم إنشاء الحساب وتسجيل الدخول بنجاح.")
        return redirect('home')

    return render(request, 'accounts/us_register.html')

# تحقق عبر Ajax إن كان المستخدم موجودًا
@csrf_exempt
def check_user_exists(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        password = request.POST.get('password', '').strip()

        if identifier.startswith('05'):
            identifier = '+966' + identifier[1:]

        try:
            user = None
            if User.objects.filter(username=identifier).exists():
                user = User.objects.get(username=identifier)
            elif Profile.objects.filter(phone=identifier).exists():
                user = Profile.objects.get(phone=identifier).user
            else:
                # المستخدم غير موجود تمامًا → أرسل OTP وابدأ التسجيل
                otp = str(random.randint(100000, 999999))
                request.session['otp'] = otp
                request.session['phone'] = identifier
                try:
                    send_otp_whatsapp(identifier, otp)
                    return JsonResponse({'status': 'new'})
                except Exception as e:
                    return JsonResponse({'status': 'error', 'message': str(e)})

            if password:
                # محاولة تسجيل الدخول بكلمة المرور
                user = authenticate(request, username=user.username, password=password)
                if user:
                    login(request, user)
                    return JsonResponse({'status': 'success'})
                else:
                    return JsonResponse({'status': 'wrong_password'})
            else:
                # المستخدم موجود لكن لم يتم إدخال كلمة المرور بعد
                return JsonResponse({'status': 'exists'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
        
# بدء عملية تسجيل مستخدم جديد بإدخال رقم الجوال
def start_registration(request):
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()

        if phone.startswith('05'):
            phone = '+966' + phone[1:]

        otp = str(random.randint(100000, 999999))
        request.session['otp'] = otp
        request.session['phone'] = phone

        try:
            send_otp_whatsapp(phone, otp)
            messages.success(request, "تم إرسال رمز التحقق إلى واتساب.")
            return redirect('verify_otp')
        except Exception as e:
            messages.error(request, f"فشل في إرسال رمز التحقق: {e}")
            return redirect('start_registration')

    return render(request, 'accounts/start_registration.html')



# تسجيل الخروج
def user_logout(request):
    logout(request)
    return redirect('phone_login')

# الصفحة الرئيسية
@login_required(login_url='phone_login')
def home(request):
    return render(request, 'accounts/home.html')


#python3 manage.py runserver
#python3 manage.py makemigrations
#python3 manage.py migrate