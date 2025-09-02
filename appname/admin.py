from django.contrib import admin
from .models import CustomUser,Product,Request,Chat
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(Request)
admin.site.register(Chat)