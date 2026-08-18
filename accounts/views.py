from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.contrib.auth.models import User
from master.models import Client, Service
from transaction.models import Invoice, Payment

@never_cache
def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "accounts/home.html")


@never_cache
def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if username == "" or password == "":
            messages.error(request, "Please enter Username and Password.")
            return redirect("login")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request, user)

            if not request.POST.get("remember"):
                request.session.set_expiry(0)

            return redirect("dashboard")

        messages.error(request, "Invalid Username or Password.")

    return render(request, "accounts/login.html")


@never_cache
@login_required(login_url="login")
def dashboard(request):
    return render(request, "accounts/dashboard.html")


def logout_view(request):
    logout(request)
    return redirect("login")




@never_cache
def register_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username").strip()
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if username == "" or password == "" or confirm == "":
            messages.error(request, "All fields are required.")
            return redirect("register")

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        User.objects.create_user(
            username=username,
            password=password
        )

        messages.success(request, "Account created successfully.")
        return redirect("login")

    return render(request, "accounts/register.html")

@login_required(login_url="login")
@never_cache
def dashboard(request):

    context = {

        "client_count": Client.objects.count(),

        "service_count": Service.objects.count(),

        "invoice_count": Invoice.objects.count(),

        "payment_count": Payment.objects.count(),

        "recent_invoices": Invoice.objects.order_by("-id")[:5],

        "recent_payments": Payment.objects.order_by("-id")[:5],

    }

    return render(
        request,
        "accounts/dashboard.html",
        context
    )