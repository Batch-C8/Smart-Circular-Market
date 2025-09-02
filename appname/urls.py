from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('enter_otp/', views.enter_otp_view, name='enter_otp'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('upload-bill/', views.upload_bill, name='upload_bill'),
    path('manual-form/', views.manual_form, name='manual_form'),
    path('form-success/', views.form_success, name='form_success'),
    path('display-products/', views.display_products, name='display_products'),
    path('confirm-post-product/', views.confirm_post_product, name='confirm_post_product'),
    path('post-product/', views.post_product, name='post_product'),
    path('request_product/<int:product_id>/', views.request_product, name='request_product'),
    path('incoming_requests/', views.incoming_requests, name='incoming_requests'),
    path('outgoing_requests/', views.outgoing_requests, name='outgoing_requests'),
    path('friends/', views.friends_list, name='friends_list'),
    path('chat/<int:friend_id>/', views.chat_with_friend, name='chat_with_friend'),
    path('display-products/', views.display_products, name='display_products'),
    path('make_request/<int:product_id>/', views.make_request, name='make_request'),
    path('accept_request/<int:request_id>/', views.accept_request, name='accept_request'),
    path('reject_request/<int:request_id>/', views.reject_request, name='reject_request'),
    path('my-products/', views.my_products, name='my_products'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('update-price/<int:product_id>/', views.update_price, name='update_price'),
    path('logout/', views.logout_view, name='logout'),
]

