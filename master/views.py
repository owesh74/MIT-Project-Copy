from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import CompanyProfile, GstConfiguration, Client, Service
from .forms import (
    CompanyProfileForm,
    GstConfigurationForm,
    ClientForm,
    ServiceForm
)

# ==========================
# COMPANY PROFILE
# ==========================

@login_required
def company_profile(request):

    company = CompanyProfile.objects.first()

    if company:
        return redirect("edit_company", pk=company.id)

    form = CompanyProfileForm(request.POST or None,
                              request.FILES or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Company Profile Saved.")
        return redirect("dashboard")

    return render(request,
                  "master/company_profile.html",
                  {"form": form})


@login_required
def edit_company(request, pk):

    company = get_object_or_404(CompanyProfile, pk=pk)

    form = CompanyProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=company
    )

    if form.is_valid():
        form.save()
        messages.success(request, "Company Updated.")
        return redirect("dashboard")

    return render(request,
                  "master/company_profile.html",
                  {"form": form})


# ==========================
# GST
# ==========================

@login_required
def gst_list(request):

    gst = GstConfiguration.objects.all()

    return render(request,
                  "master/gst_list.html",
                  {"gst": gst})


@login_required
def add_gst(request):

    form = GstConfigurationForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "GST Added.")
        return redirect("gst_list")

    return render(request,
                  "master/gst_form.html",
                  {"form": form})


@login_required
def edit_gst(request, pk):

    gst = get_object_or_404(GstConfiguration, pk=pk)

    form = GstConfigurationForm(
        request.POST or None,
        instance=gst
    )

    if form.is_valid():
        form.save()
        messages.success(request, "GST Updated.")
        return redirect("gst_list")

    return render(request,
                  "master/gst_form.html",
                  {"form": form})


@login_required
def delete_gst(request, pk):

    gst = get_object_or_404(GstConfiguration, pk=pk)

    gst.delete()

    messages.success(request, "GST Deleted.")

    return redirect("gst_list")


# ==========================
# CLIENT
# ==========================

@login_required
def client_list(request):

    clients = Client.objects.all()

    return render(request,
                  "master/client_list.html",
                  {"clients": clients})


@login_required
def add_client(request):

    form = ClientForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Client Added.")
        return redirect("client_list")

    return render(request,
                  "master/client_form.html",
                  {"form": form})


@login_required
def edit_client(request, pk):

    client = get_object_or_404(Client, pk=pk)

    form = ClientForm(
        request.POST or None,
        instance=client
    )

    if form.is_valid():
        form.save()
        messages.success(request, "Client Updated.")
        return redirect("client_list")

    return render(request,
                  "master/client_form.html",
                  {"form": form})


@login_required
def delete_client(request, pk):

    client = get_object_or_404(Client, pk=pk)

    client.delete()

    messages.success(request, "Client Deleted.")

    return redirect("client_list")


# ==========================
# SERVICE
# ==========================

@login_required
def service_list(request):

    services = Service.objects.all()

    return render(request,
                  "master/service_list.html",
                  {"services": services})


@login_required
def add_service(request):

    form = ServiceForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Service Added.")
        return redirect("service_list")

    return render(request,
                  "master/service_form.html",
                  {"form": form})


@login_required
def edit_service(request, pk):

    service = get_object_or_404(Service, pk=pk)

    form = ServiceForm(
        request.POST or None,
        instance=service
    )

    if form.is_valid():
        form.save()
        messages.success(request, "Service Updated.")
        return redirect("service_list")

    return render(request,
                  "master/service_form.html",
                  {"form": form})


@login_required
def delete_service(request, pk):

    service = get_object_or_404(Service, pk=pk)

    service.delete()

    messages.success(request, "Service Deleted.")

    return redirect("service_list")