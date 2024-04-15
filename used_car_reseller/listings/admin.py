from django.contrib import admin
from .models import UserProfile, Car, Review, UserActivity, UserCarInteraction, CarImage, Wishlist, Message, Make, \
    CarModel, BodyType, FuelType, Purchase


# Inline models for CarImage
class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1

# Admin model for UserProfile
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'email', 'address')
    search_fields = ('user__username', 'phone_number', 'email')

# Admin model for Car
class CarAdmin(admin.ModelAdmin):
    list_display = ('year', 'make', 'model', 'body_type', 'fuel_type', 'price', 'status')
    list_filter = ('status', 'make', 'body_type', 'fuel_type', 'year')
    search_fields = ('make__name', 'model__name', 'year', 'vin')
    inlines = [CarImageInline]



# Admin model for Review
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('car', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('car__model__name', 'reviewer__username')

# Admin model for CarImage
class CarImageAdmin(admin.ModelAdmin):
    list_display = ('car', 'uploaded_at', 'order')
    list_filter = ('car', 'uploaded_at')
    search_fields = ('car__model__name',)

# Registering each model with the admin site
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(UserActivity)
admin.site.register(UserCarInteraction)
admin.site.register(CarImage, CarImageAdmin)
admin.site.register(Wishlist)
admin.site.register(Message)
admin.site.register(Make)
admin.site.register(CarModel)
admin.site.register(BodyType)
admin.site.register(FuelType)
admin.site.register(Purchase)
