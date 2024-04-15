# urls.py in the listings app
from django.contrib.auth.views import LogoutView
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('seller/<int:user_id>/', views.user_listings, name='user_listings'),
    path('listings/', views.car_listings, name='car_listings'),
    path('ajaxload/', views.ajax_load_models, name='ajax_load_models'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('logout/', views.custom_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-listing/', views.add_listing, name='add_listing'),
    path('car-detail/<int:pk>/', views.car_detail, name='car_detail'),
    path('delete-listing/<int:pk>/', views.delete_listing, name='delete_listing'),
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    path('edit-listing/<int:car_id>/', views.edit_listing, name='edit_listing'),
    path('cars/<int:car_id>/add_image/', views.add_car_image, name='add_car_image'),
    path('cars/<int:car_id>/images/manage/', views.manage_car_images, name='manage_car_images'),
    path('car/<int:car_id>/create_bid/', views.create_bid, name='create_bid'),
    path('bid/<int:bid_id>/accept/', views.accept_bid, name='accept_bid'),
    path('bid/<int:bid_id>/reject/', views.reject_bid, name='reject_bid'),
    path('bid/<int:bid_id>/reserve/', views.reserve_car, name='reserve_car'),
    path('my-car/<int:car_id>/bids/', views.view_bids, name='view_bids'),
    path('bids/<int:bid_id>/confirmation/', views.bid_confirmation, name='bid_confirmation'),
    path('car/<int:car_id>/review/', views.add_review, name='add_review'),

    # ... other URL patterns ...
]
