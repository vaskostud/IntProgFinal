from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True,
                                 validators=[
                                     MinValueValidator(1.0),
                                       MaxValueValidator(10.0)
                                 ],
                                 help_text=_("User rating based on transaction history"))
    bio = models.TextField(_("Biography"), blank=True)

    def __str__(self):
        return self.user.username

    def update_rating(self):
        reviews = Review.objects.filter(car__owner=self.user)
        if reviews.exists():
            total_rating = sum(review.rating for review in reviews)
            self.rating = total_rating / reviews.count()
            self.save()


class Make(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class CarModel(models.Model):
    make = models.ForeignKey(Make, related_name='models', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('make', 'name',)  # Ensures the combination of make and model is unique


    def __str__(self):
        return f"{self.make.name} {self.name}"


class BodyType(models.Model):
    type = models.CharField(max_length=100, unique=True, default="Sedan")

    def __str__(self):
        return self.type

class FuelType(models.Model):
    type = models.CharField(max_length=100, unique=True, default="Gas")

    def __str__(self):
        return self.type

class Car(models.Model):
    class CarStatus(models.TextChoices):
        AVAILABLE = 'AV', _('Available')
        RESERVED = 'RV', _('Reserved')
        SOLD = 'SD', _('Sold')

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    make = models.ForeignKey(Make, on_delete=models.CASCADE)
    model = models.ForeignKey(CarModel, on_delete=models.CASCADE)
    body_type = models.ForeignKey(BodyType, on_delete=models.CASCADE, null=True)
    fuel_type = models.ForeignKey(FuelType, on_delete=models.CASCADE, null=True)
    year = models.PositiveIntegerField()
    color = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    displacement = models.PositiveIntegerField(help_text="Displacement in cubic centimeters (cc)")
    horsepower = models.PositiveIntegerField(help_text="Horsepower (bhp)")
    torque = models.PositiveIntegerField(help_text="Torque in Newton-meters (Nm)")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=15, choices=CarStatus.choices, default=CarStatus.AVAILABLE)
    mileage = models.PositiveIntegerField(help_text="Mileage of the car in kilometers")
    vin = models.CharField(max_length=17, unique=True, help_text="Vehicle Identification Number")
    is_sold = models.BooleanField(default=False)
    sold_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.year} {self.make.name} {self.model.name} - OWNER: {self.owner.username}"

    def mark_as_sold(self):
        self.status = Car.CarStatus.SOLD
        self.is_sold = True
        self.sold_at = timezone.now()
        self.save()

    def mark_as_reserved(self):
        self.is_sold= False
        self.status = Car.CarStatus.RESERVED
        self.save()

    def mark_as_available(self):
        self.is_sold= False
        self.status = Car.CarStatus.AVAILABLE
        self.save()

class Purchase(models.Model):
    buyer = models.ForeignKey(User, related_name='purchases', on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, help_text="Final sale price of the car.")
    purchase_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.buyer.username} purchased {self.car}"

    def save(self, *args, **kwargs):
        # When a purchase is saved for the first time, mark the related car as sold
        if not self.pk:  # Ensuring this only happens on first save, not on updates
            self.car.mark_as_sold()
        super().save(*args, **kwargs)



class Review(models.Model):
    car = models.ForeignKey(Car, related_name='reviews', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Rating on a scale from 1 to 10."
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Review for {self.car} by {self.reviewer.username}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['car', 'reviewer'], name='unique_review_per_user_per_car')
        ]


class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=100)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.timestamp}"


class UserCarInteraction(models.Model):
    user = models.ForeignKey(User, related_name='interactions', on_delete=models.CASCADE)
    car = models.ForeignKey(Car, related_name='interactions', on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=100)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.interaction_type} with {self.car} at {self.timestamp}"


class CarImage(models.Model):
    car = models.ForeignKey(Car, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='car_images/')
    alt_text = models.CharField(max_length=255, blank=True, help_text="A brief description of the image.")
    order = models.PositiveIntegerField(default=0, help_text="Order in which the image will appear in a carousel.")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image of {self.car} ({self.order})"

    class Meta:
        ordering = ['order']




class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"

    class Meta:
        ordering = ['-timestamp']


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'car')  # Ensuring a user cannot add the same car multiple times

    def __str__(self):
        return f"{self.user.username}'s wishlist item: {self.car}"


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Add to your existing models:

class Bid(models.Model):
    car = models.ForeignKey(Car, related_name='bids', on_delete=models.CASCADE)
    bidder = models.ForeignKey(User, related_name='bids', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    message = models.TextField()

    def __str__(self):
        return f"Bid by {self.bidder.username} on {self.car}"

    def accept_bid(self):
        # Mark the car as sold
        self.car.mark_as_sold()

        # Create a purchase record
        Purchase.objects.create(
            car=self.car,
            buyer=self.bidder,
            price_at_purchase=self.amount,
            purchase_date=timezone.now()
        )

        # Optionally mark the bid as accepted
        self.is_accepted = True
        self.save()
