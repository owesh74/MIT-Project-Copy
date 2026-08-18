from django.urls import path
from . import views

urlpatterns = [

    # ==========================
    # COMPANY PROFILE
    # ==========================

    path(
        "company/",
        views.company_profile,
        name="company_profile"
    ),

    path(
        "company/<int:pk>/",
        views.edit_company,
        name="edit_company"
    ),

    # ==========================
    # GST
    # ==========================

    path(
        "gst/",
        views.gst_list,
        name="gst_list"
    ),

    path(
        "gst/add/",
        views.add_gst,
        name="add_gst"
    ),

    path(
        "gst/edit/<int:pk>/",
        views.edit_gst,
        name="edit_gst"
    ),

    path(
        "gst/delete/<int:pk>/",
        views.delete_gst,
        name="delete_gst"
    ),

    # ==========================
    # CLIENT
    # ==========================

    path(
        "clients/",
        views.client_list,
        name="client_list"
    ),

    path(
        "clients/add/",
        views.add_client,
        name="add_client"
    ),

    path(
        "clients/edit/<int:pk>/",
        views.edit_client,
        name="edit_client"
    ),

    path(
        "clients/delete/<int:pk>/",
        views.delete_client,
        name="delete_client"
    ),

    # ==========================
    # SERVICE
    # ==========================

    path(
        "services/",
        views.service_list,
        name="service_list"
    ),

    path(
        "services/add/",
        views.add_service,
        name="add_service"
    ),

    path(
        "services/edit/<int:pk>/",
        views.edit_service,
        name="edit_service"
    ),

    path(
        "services/delete/<int:pk>/",
        views.delete_service,
        name="delete_service"
    ),

]