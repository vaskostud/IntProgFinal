# listings/views.py
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q, Avg


# Index view
def index(request):
    latest_cars = Car.objects.filter(status='AV').order_by('-created_at')[:5]
    top_sellers = UserProfile.objects.filter(user__car__is_sold=True) \
                      .annotate(avg_rating=Avg('user__review__rating')) \
                      .order_by('-avg_rating')[:5]
    context = {
        'latest_cars': latest_cars,
        'top_sellers': top_sellers,
    }
    return render(request, 'index.html', context)


# User listings view
def user_listings(request, user_id):
    user_profile = get_object_or_404(UserProfile, user__id=user_id)
    seller_cars = Car.objects.filter(owner=user_profile.user).order_by('-created_at')
    context = {
        'seller': user_profile.user,
        'seller_cars': seller_cars,
    }
    return render(request, 'userListings.html', context)


# views.py in your Django app

from .models import Car, UserProfile, CarModel, Review
from django.http import JsonResponse
from django.db.models import Q

# Car listings view
def car_listings(request):
    cars = Car.objects.all()

    if 'search' in request.GET:
        search_query = request.GET['search']
        cars = cars.filter(
            Q(make__name__icontains=search_query) |
            Q(model__name__icontains=search_query) |
            Q(owner__username__icontains=search_query) |
            Q(year__icontains=search_query) |
            Q(color__icontains=search_query) |
            Q(price__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(status__icontains=search_query) |
            Q(body_type__type__icontains=search_query) |
            Q(fuel_type__type__icontains=search_query) |
            Q(displacement__icontains=search_query) |
            Q(horsepower__icontains=search_query) |
            Q(torque__icontains=search_query)
        )

    context = {'cars': cars}
    return render(request, 'car_listings.html', context)


# AJAX load models view
def ajax_load_models(request):
    make_id = request.GET.get('make')
    models = CarModel.objects.filter(make_id=make_id).order_by('name')
    return JsonResponse(list(models.values('id', 'name')), safe=False)


# views.py

from .forms import UserRegistrationForm


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after successful registration
            return redirect('home')  # Redirect to a different page after registration
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})


# views.py
from django.contrib.auth import authenticate, login
from django.contrib import messages


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('')  # Redirect to home or another appropriate page
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


# views.py
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm


@login_required
def profile(request):
    # No form handling here, as this page is for display only
    return render(request, 'profile.html')


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to the profile page after update
    else:
        form = UserProfileForm(instance=request.user.userprofile)

    return render(request, 'edit_profile.html', {'form': form})


from django.contrib.auth import logout


def custom_logout(request):
    logout(request)  # Log out the user
    # return redirect('login')  # Previously used immediate redirect
    return render(request, 'logout_confirmation.html')  # Render a confirmation page


# views.py in your app (e.g., listings/views.py)
from django.contrib.auth.decorators import login_required
from .models import Car, Wishlist


@login_required
def dashboard(request):
    user_cars = Car.objects.filter(owner=request.user)
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {
        'user_cars': user_cars,
        'wishlist_items': wishlist_items,
    })


from django.contrib.auth.decorators import login_required


@login_required
def add_listing(request):
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            new_car = form.save(commit=False)
            new_car.owner = request.user
            new_car.save()
            return redirect('dashboard')
    else:
        form = CarForm()
    return render(request, 'add_listing.html', {'form': form})


# views.py
from django.shortcuts import render, get_object_or_404
from .models import Car, Purchase
from django.contrib.auth.decorators import login_required



from django.shortcuts import get_object_or_404, render
from .models import Car, Purchase

def car_detail(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    context = {'car': car}

    if request.user.is_authenticated:
        # Add 'has_purchased' to the context only if the user is authenticated
        context['has_purchased'] = Purchase.objects.filter(car=car, buyer=request.user).exists()

    return render(request, 'car_detail.html', context)


from django.contrib.auth.decorators import login_required


@login_required
def delete_listing(request, pk):
    car = get_object_or_404(Car, pk=pk, owner=request.user)
    car.delete()
    return redirect('dashboard')


from django.contrib.auth.decorators import login_required

from .forms import CarForm


@login_required
def edit_listing(request, car_id):
    car = get_object_or_404(Car, pk=car_id, owner=request.user)
    form = CarForm(request.POST or None, request.FILES or None, instance=car)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            # Assuming you have a 'car_detail' view to show the car details.
            return redirect('car_detail', car_id=car.id)

    # For GET request or if form is not valid, render the page with the form.
    return render(request, 'edit_listing.html', {'form': form, 'car': car})


from django.contrib.auth.decorators import login_required
from .forms import NewCarImageForm
from .models import Car


@login_required
def add_car_image(request, car_id):
    car = get_object_or_404(Car, pk=car_id, owner=request.user)
    if request.method == 'POST':
        new_image_form = NewCarImageForm(request.POST, request.FILES)
        if new_image_form.is_valid():
            new_image = new_image_form.save(commit=False)
            new_image.car = car
            new_image.save()
            # Redirect to the image management page, or wherever you see fit
            return redirect('manage_car_images', car_id=car_id)
    else:
        new_image_form = NewCarImageForm()

    return render(request, 'add_car_image.html', {
        'new_image_form': new_image_form,
        'car': car,
        'car_id': car_id,
    })


from django.shortcuts import get_object_or_404, render

# views.py
from django.shortcuts import render, get_object_or_404
from .models import Car, Purchase



from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import CarImage


@login_required
def manage_car_images(request, car_id):
    car = get_object_or_404(Car, pk=car_id, owner=request.user)
    current_images = car.images.all()  # Assuming 'images' is the related_name for CarImage

    if request.method == 'POST':
        image_id = request.POST.get('image_id')
        if image_id:
            image = CarImage.objects.get(id=image_id, car=car)
            image.delete()
            # Optionally add a message to the user about successful deletion
            # messages.success(request, 'Image deleted successfully.')
        return redirect('manage_car_images', car_id=car_id)

    return render(request, 'manage_car_images.html', {
        'car': car,
        'current_images': current_images
    })


# views.py


from django.shortcuts import render, redirect, get_object_or_404
from .forms import BidForm
from .models import Car, Bid
from django.contrib.auth.decorators import login_required


@login_required
def create_bid(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.car = car
            bid.bidder = request.user
            bid.save()
            # Redirect to a confirmation page or back to the car detail page
            return redirect('bid_confirmation', bid.id)
    else:
        form = BidForm()
    return render(request, 'create_bid.html', {'form': form, 'car': car})


from django.shortcuts import get_object_or_404, redirect
from .models import Bid, Car
from django.contrib.auth.decorators import login_required


@login_required
def accept_bid(request, bid_id):
    bid = get_object_or_404(Bid, pk=bid_id)
    car = bid.car
    if request.user == car.owner:
        car.mark_as_sold()  # Assuming CarStatus is an inner class in your Car model
        car.save()
        # Optionally, update bid to reflect acceptance
        bid.is_accepted = True
        bid.save()
        bid.accept_bid()
        # Redirect to a confirmation page or back to the bids list
        return redirect('car_listings')
    else:
        # Handle unauthorized access attempt
        return redirect('dashboard')


@login_required
def reject_bid(request, bid_id):
    bid = get_object_or_404(Bid, pk=bid_id)
    car = bid.car
    if request.user == car.owner:
        car.mark_as_available()
        car.save()
        bid.is_accepted = False
        bid.is_rejected = True
        bid.save()
        # No specific bid, the owner decides to reserve the car

        return redirect('car_listings')
    else:
        # Handle unauthorized access attempt
        return redirect('dashboard')


@login_required
def reserve_car(request, bid_id):
    bid = get_object_or_404(Bid, pk=bid_id)
    car = bid.car
    if request.user == car.owner:
        car.mark_as_reserved()
        car.save()

        bid.is_accepted = False
        bid.is_rejected = False
        bid.save()
        # No specific bid, the owner decides to reserve the car

        return redirect('car_listings')
    else:
        # Handle unauthorized access attempt
        return redirect('dashboard')


@login_required
def view_bids(request, car_id):
    car = get_object_or_404(Car, pk=car_id, owner=request.user)
    bids = car.bids.all()

    return render(request, 'view_bids.html', {'car': car, 'bids': bids, 'car_id': car.id})


@login_required
def bid_confirmation(request, bid_id):
    bid = get_object_or_404(Bid, pk=bid_id, bidder=request.user)
    return render(request, 'bid_confirmation.html', {'bid': bid})



from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ReviewForm
from .models import Car


@login_required
def add_review(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    # Check if the user has purchased the car
    if not Purchase.objects.filter(car=car, buyer=request.user).exists():
        messages.error(request, "You must have purchased the car to leave a review.")
        return redirect('car_detail', car_id=car_id)

    # Check if the user has already left a review
    if Review.objects.filter(car=car, reviewer=request.user).exists():
        messages.error(request, "You have already reviewed this car.")
        return redirect('car_detail', car_id=car_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.car = car
            review.reviewer = request.user
            try:
                review.save()
                messages.success(request, "Your review has been added.")
            except IntegrityError:
                messages.error(request, "You can only leave one review per car.")
            return redirect('car_detail', car_id=car_id)
    else:
        form = ReviewForm()

    return render(request, 'add_review.html', {'form': form, 'car': car})
