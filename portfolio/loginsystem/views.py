from base64 import urlsafe_b64decode
from email.message import EmailMessage
from http.client import HTTPResponse
from tokenize import generate_tokens
from django.shortcuts import redirect,render
from django.http import HttpResponse
from django.contrib.auth.models import User 
from django.contrib import messages 
from django.contrib.auth import authenticate, login, logout 
from portfolio import settings
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str

from portfolio.info import EMAIL_HOST_USER
from . token import generate_token



from . import views
# Create your views here.
def home(request):
    return render(request,"loginsystem/index.html")

def signup(request):
    
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        emailid = request.POST['emailid']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try another one")
            return redirect('home')

        if User.objects.filter(email=emailid):
            messages.error(request, "Email already registered")

        if len(username)>10:
            messages.error(request, "Username name must be short")

        if pass1 != pass2:
            messages.error(request, "Passwords didnt match")

        if not username.isalnum():
            messages.error(request, "Username should be alphanumeric!!!")
            return redirect('home')  

        myuser = User.objects.create_user(username, emailid, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()

        messages.success(request,"Your account has been succesfully created")

        subject = "Welcome to My Portfolio Page LoginSystem"
        message = "Hello " + myuser.first_name + "!! \n" + "We have sent you a confirmation mail, please acknowledge the mail for email confirmation \n Thank you!!!"
        from_mail = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_mail, to_list, fail_silently=True)

        current_site = get_current_site(request)
        email_subject = "Confirm your Email - JYK Portfolios"
        message2 = render_to_string('email_confirmation.html',{
            'name' : myuser.first_name,
            'domain' : current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)

        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()
        
        return redirect('signin')

    return render(request, "loginsystem/signup.html")

def signin(request):

    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username,password=pass1)

        if user is not None:
            login(request, user)
            return render(request, "loginsystem/index.html")

        else:
            messages.error(request, "Bad Credentials!")
            return redirect('home')

    return render(request,"loginsystem/signin.html")

def signout(request):
    logout(request) 
    messages.success(request, "Logged out Successfully")
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.active = True
        myuser.save()
        login(request,myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')




