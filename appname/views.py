from random import randint
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings  # <-- Add this import for email settings
from django.contrib.auth import authenticate, login, logout
from .forms import ManualForm, BillForm, RegistrationForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from .models import CustomUser,Product,Request,Chat  # Assuming you're using a custom user model
from datetime import datetime
from dateutil import parser
import re
from PIL import Image
import shutil
import pytesseract
tesseract_path = shutil.which("tesseract")
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
else:
    pytesseract.pytesseract.tesseract_cmd = "/nix/store/*-tesseract-*/bin/tesseract"
import io
import pandas as pd
from django.contrib.auth.models import User
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.db.models import Q

def home(request):
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'registration.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return HttpResponse('Invalid credentials')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            otp = randint(1000, 9999)
            send_mail(
                'Password Reset OTP',
                f'Your OTP for resetting the password is {otp}.',
                'no-reply@example.com',
                [email],
                fail_silently=False,
            )
            request.session['otp'] = otp
            return redirect('enter_otp')
    else:
        form = ForgotPasswordForm()
    return render(request, 'forgot_password.html', {'form': form})

def enter_otp_view(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        if int(otp_entered) == request.session.get('otp'):
            return redirect('reset_password')
        else:
            return HttpResponse('Invalid OTP')
    return render(request, 'enter_otp.html')

CustomUser = get_user_model()

def reset_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # Get the email from form
        new_password = request.POST.get('new_password')  # Get the new password
        confirm_password = request.POST.get('confirm_password')  # Get the confirm password
        
        # Check if new password and confirm password match
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('reset_password')

        try:
            # Fetch user by email
            user = CustomUser.objects.get(email=email)

            # Hash the new password and update it
            user.password = make_password(new_password)
            user.save()  # Save the updated user

            messages.success(request, "Password updated successfully! Please log in.")
            return redirect('login')

        except CustomUser.DoesNotExist:
            messages.error(request, "No user found with the provided email.")
            return redirect('reset_password')

        except Exception as e:
            # Handle any other exceptions
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('reset_password')

    return render(request, 'reset_password.html')

def logout_view(request):
    logout(request)  
    return redirect('login')  

# Dataset Path Configuration
DATASET_PATH = str(settings.BASE_DIR / "appname" / "static" / "datasets" / "bike_dataset_2000.csv")

# Load Dataset
try:
    vehicle_df = pd.read_csv(DATASET_PATH)
    print("Dataset loaded successfully!")
except Exception as e:
    print(f"Error loading dataset: {e}")

# Extract vehicle details from text
import re

def extract_vehicle_details(text):
    patterns = {
        'Bike_Name': r"Bike Name:\s*(.*?)\n",
        'Model': r"Model:\s*(.*?)\n",
        'Manufacturer': r"Manufacturer:\s*(.*?)\n",
        'Manufacturing_Date': r"Manufacturing Date:\s*(.*?)\n",
        'kilometers_driven': r"kilometers[_\s]?driven:\s*(.*?)\n"

    }
    
    extracted = {key: None for key in patterns}
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            value = match.group(1).strip()
            if key == 'kilometers_driven':
                # Clean commas and convert to integer
                try:
                    value = int(value.replace(",", ""))
                except ValueError:
                    value = None
            extracted[key] = value
    
    return extracted


# Remaining lifespan calculation  

from datetime import datetime

def calculate_remaining_lifespan(manufacturing_date_str, avg_lifespan):
    try:
        manufacturing_date = datetime.fromisoformat(manufacturing_date_str)
        current_year = datetime.now().year
        manufactured_year = manufacturing_date.year
        used_years = current_year - manufactured_year

        remaining_years = max(avg_lifespan - used_years, 0)
        return remaining_years
    except Exception as e:
        print(f"Error calculating remaining lifespan: {e}")
        return avg_lifespan  # fallback to average if date parsing fails
 # Ensure lifespan is never negative



# Extract text from image using OCR
def extract_text_from_image(file_content):
    try:
        image = Image.open(io.BytesIO(file_content))
        extracted_text = pytesseract.image_to_string(image)
        print("Extracted OCR Text:")
        print(extracted_text)
        return extracted_text
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""

# Condition Mapping
condition_mapping = {
    'good': 0.9,
    'average': 0.7,
    'bad': 0.5,
    'worst': 0.3
}

# Data fetching and regression
import traceback

def manual_data_fetch_and_regression(extracted_details, condition_value, kilometers_driven):
    try:
        bike_name = extracted_details.get('Bike_Name')
        model_name = extracted_details.get('Model')
        manufacturer_name = extracted_details.get('Manufacturer')
        manufacturing_date = extracted_details.get('Manufacturing_Date')

        # Filter based on details
        filtered_df = vehicle_df[
            (vehicle_df['Bike Name'].str.lower() == bike_name.casefold()) &
            (vehicle_df['Model'].str.lower() == model_name.casefold()) &
            (vehicle_df['Manufacturer'].str.lower() == manufacturer_name.casefold())
        ]

        if filtered_df.empty:
            return None, "No matching records found"

        filtered_df = filtered_df.copy()

        # Map Demand
        demand_mapping = {'High': 2, 'Medium': 1, 'Low': 0}
        filtered_df['Demand'] = filtered_df['Demand'].map(demand_mapping)

        # Inject the user input kilometers_driven as a new column for the model
        filtered_df['kilometers_driven'] = kilometers_driven

        # Drop rows with missing data for features and target
        filtered_df.dropna(subset=['Avg Lifespan (years)', 'Demand', 'Base Price (INR)'], inplace=True)

        X = filtered_df[['Avg Lifespan (years)', 'Demand', 'kilometers_driven']]
        y = filtered_df['Base Price (INR)']

        if X.empty or y.empty:
            return None, "Insufficient data for regression"

        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train model
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)

        y_pred = rf_model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        print(f"Random Forest Model MSE: {mse}")

        # Calculate remaining lifespan
        avg_lifespan = filtered_df['Avg Lifespan (years)'].mean()
        remaining_lifespan = calculate_remaining_lifespan(manufacturing_date, avg_lifespan)

        demand = filtered_df['Demand'].mean()

        # Predict price based on user inputs
        input_features = pd.DataFrame([[remaining_lifespan, demand, kilometers_driven]],
                                      columns=['Avg Lifespan (years)', 'Demand', 'kilometers_driven'])
        predicted_price = rf_model.predict(input_features)[0]

        # Adjust by condition
        adjusted_price = predicted_price * condition_value

        return round(adjusted_price, 2), None

    except Exception as e:
        return None, str(e)

def upload_bill(request):
    if request.method == 'POST':
        form = BillForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES.get('bill_image')
            condition = form.cleaned_data.get('product_condition')
            Product_Image = form.cleaned_data.get('product_image')
            Product_Video = form.cleaned_data.get('product_video')
            condition_value = condition_mapping.get(condition, 1.0)
            # Ensure the uploaded file is being processed correctly
            if uploaded_file:
                file_content = uploaded_file.read()
                extracted_text = extract_text_from_image(file_content)
                extracted_details = extract_vehicle_details(extracted_text)
            else:
                return render(request, 'form_success.html', {'error': 'No bill image provided.'})

            if all(value is None for value in extracted_details.values()):
                return render(request, 'form_success.html', {'error': 'Not enough data to calculate price'})

            # Handle the product image and video files as well
            product_image_path = None
            product_video_path = None

            if Product_Image:
                product_image_path = default_storage.save('products/' + Product_Image.name, ContentFile(Product_Image.read()))

            if Product_Video:
                product_video_path = default_storage.save('products/' + Product_Video.name, ContentFile(Product_Video.read()))

            predicted_price, error = manual_data_fetch_and_regression(extracted_details, condition_value)
            request.session['extracted_details'] = extracted_details
            request.session['predicted_price'] = predicted_price
            request.session['condition_value'] = condition_value
            request.session['product_image'] = product_image_path
            request.session['product_video'] = product_video_path
            if error:
                return render(request, 'form_success.html', {'error': error})

            # Pass the necessary data to the post_product function
            return redirect('confirm_post_product')
    else:
        form = BillForm()
    return render(request, 'upload_bill.html', {'form': form})

# Manual form handling
def manual_form(request):
    if request.method == 'POST':
        form = ManualForm(request.POST, request.FILES)
        if form.is_valid():
            manufacturing_date = form.cleaned_data.get('manufacturing_date')
            kilometers_driven = form.cleaned_data.get('kilometers_driven')

            # Validate kilometers_driven is numeric and positive
            try:
                kilometers_driven = float(kilometers_driven)
                if kilometers_driven < 0:
                    raise ValueError("Negative kilometers driven")
            except (ValueError, TypeError):
                return render(request, 'form_success.html', {'error': 'Invalid value for kilometers driven.'})

            extracted_details = {
                'Bike_Name': form.cleaned_data.get('vehicle_name'),
                'Model': form.cleaned_data.get('model_name'),
                'Manufacturer': form.cleaned_data.get('manufacturer_name'),
                'Manufacturing_Date': manufacturing_date.isoformat() if manufacturing_date else None,
                'kilometers_driven': kilometers_driven,
            }

            condition = form.cleaned_data.get('product_condition')
            product_image = form.cleaned_data.get('product_image')
            product_video = form.cleaned_data.get('product_video')
            condition_value = condition_mapping.get(condition, 1.0)

            # Check if we have sufficient data to predict
            if not any(extracted_details.values()):
                return render(request, 'form_success.html', {'error': 'Not enough data to calculate price.'})

            # Save uploaded files if any
            product_image_path = None
            if product_image:
                product_image_path = default_storage.save(
                    f'products/images/{product_image.name}',
                    ContentFile(product_image.read())
                )

            product_video_path = None
            if product_video:
                product_video_path = default_storage.save(
                    f'products/videos/{product_video.name}',
                    ContentFile(product_video.read())
                )

            # Perform price prediction
            predicted_price, error = manual_data_fetch_and_regression(
                extracted_details, condition_value, kilometers_driven
            )
            if error:
                return render(request, 'form_success.html', {'error': error})

            # Store relevant data in session
            request.session['extracted_details'] = extracted_details
            request.session['predicted_price'] = predicted_price
            request.session['condition_value'] = condition_value
            request.session['product_image'] = product_image_path
            request.session['product_video'] = product_video_path

            # Redirect user to confirmation page
            return redirect('confirm_post_product')

    else:
        form = ManualForm()

    return render(request, 'manual_form.html', {'form': form})

def confirm_post_product(request):
    extracted_details = request.session.get('extracted_details')
    predicted_price = request.session.get('predicted_price')
    condition_value = request.session.get('condition_value')
    product_image_path = request.session.get('product_image')
    product_video_path = request.session.get('product_video')

    product_image_url = None
    if product_image_path:
        product_image_url = settings.MEDIA_URL + product_image_path
    
    product_video_url = None
    if product_video_path:
        product_video_url = settings.MEDIA_URL + product_video_path

    if request.method == 'POST':
        # You might want to validate these before posting in a real app
        return post_product(
            request, 
            extracted_details, 
            condition_value, 
            product_image_path, 
            product_video_path, 
            predicted_price
        )

    return render(request, 'confirm_post_product.html', {
        'extracted_details': extracted_details,
        'condition_value': condition_value,
        'product_image_url': product_image_url,
        'product_video_url': product_video_url,
        'predicted_price': predicted_price,
        'kilometers_driven': extracted_details.get('kilometers_driven') if extracted_details else None,
    })


# Post product view to save the product and redirect to display_products
def post_product(request, extracted_details, condition, product_image_path, product_video_path, predicted_price):
    user_email = request.user.email
    owner = CustomUser.objects.get(email=user_email)
    product = Product(
        user_email=user_email,
        owner = owner,
        vehicle_name=extracted_details['Bike_Name'],  # Ensure these keys are correct
        model_name=extracted_details['Model'],
        manufacturer_name=extracted_details['Manufacturer'],
        product_condition=condition,
        product_image=product_image_path,
        product_video=product_video_path,
        predicted_price=predicted_price
    )
    product.save()
    return redirect('display_products')


# Display all products by user
@login_required
def display_products(request):
    products = Product.objects.all()  # Retrieve all products from the database
    return render(request, 'display_products.html', {'products': products})

# Form success page
def form_success(request):
    return render(request, 'form_success.html')

@login_required
def request_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    request_obj = Request.objects.create(product=product, requester=request.user)
    return redirect('product_detail', product_id=product.id)  # Redirect to product detail or another page
@login_required
def incoming_requests(request):
    products = Product.objects.filter(owner=request.user)
    incoming = Request.objects.filter(product__in=products, status="pending")
    return render(request, 'incoming_requests.html', {'incoming': incoming})
@login_required
def outgoing_requests(request):
    outgoing = Request.objects.filter(requester=request.user).select_related('product')
    print("Outgoing Requests:", outgoing)
    return render(request, 'outgoing_requests.html', {'outgoing': outgoing})
User = get_user_model()
@login_required
def friends_list(request):
    user = request.user  # Logged-in user
    # Query for requests the user has accepted (user is the owner and status is approved)
    accepted_by_me = Request.objects.filter(
        product__owner=user, 
        status='approved'
    ).values_list('requester', flat=True)

    # Query for requests others have accepted (user is the requester and status is approved)
    accepted_for_me = Request.objects.filter(
        requester=user, 
        status='approved'
    ).values_list('product__owner', flat=True)

    # Combine both sets of IDs and fetch user objects, excluding the logged-in user
    friend_ids = set(accepted_by_me).union(set(accepted_for_me))
    friends = CustomUser.objects.filter(id__in=friend_ids).exclude(id=user.id)

    # Pass the filtered friends to the template
    return render(request, 'friends_list.html', {'friends': friends})


@login_required
def chat_with_friend(request, friend_id):
    user = request.user  # Logged-in user
    friend = get_object_or_404(CustomUser, id=friend_id)  # Fetch the friend

    # Fetch chats between the logged-in user and the selected friend
    chats = Chat.objects.filter(
        (Q(sender=user) & Q(receiver=friend)) |
        (Q(sender=friend) & Q(receiver=user))
    ).order_by('timestamp')  # Order by the correct field

    if request.method == "POST":
        message = request.POST.get("message")
        if message:
            # Create a new chat message
            Chat.objects.create(sender=user, receiver=friend, message=message)

    return render(request, 'chat.html', {'friend': friend, 'chats': chats})



@login_required
def make_request(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    requester = request.user
    product_owner = product.owner
    if requester == product_owner:
        messages.error(request, "You cannot send a request for your own product.")
        return redirect('display_products')  
    existing_request = Request.objects.filter(product=product, requester=requester).exists()
    if existing_request:
        messages.warning(request, "You have already sent a request for this product.")
        return redirect('display_products')
    Request.objects.create(
        product=product,
        requester=requester,
        status='pending'  # Default status is pending
    )
    messages.success(request, "Your request has been sent successfully!")
    return redirect('display_products')


def update_request_status(request, request_id, action):
    if request.user.is_authenticated:
        req = get_object_or_404(Request, id=request_id)

        if req.product.owner == request.user:
            if action == 'accept':
                req.status = 'approved'
            elif action == 'reject':
                req.status = 'rejected'

            req.save()
            return redirect('incoming_requests')
        else:
            return redirect('home')  # User is not the owner of the product
    else:
        return redirect('login')
@login_required
def accept_request(request, request_id):
    req = get_object_or_404(Request, id=request_id, product__owner=request.user)
    req.status = 'approved'
    req.save()
    messages.success(request, "Request approved successfully.")
    return redirect('incoming_requests')

@login_required
def reject_request(request, request_id):
    req = get_object_or_404(Request, id=request_id, product__owner=request.user)
    req.status = 'rejected'
    req.save()
    messages.success(request, "Request rejected.")
    return redirect('incoming_requests')

@login_required
def my_products(request):
    """Fetch and display products added by the logged-in user."""
    user_email = request.user.email  # Get logged-in user email
    products = Product.objects.filter(user_email=user_email)  # Fetch user's products
    return render(request, 'my_products.html', {'products': products})

@login_required
def delete_product(request, product_id):
    """Delete a product only if it belongs to the logged-in user."""
    product = get_object_or_404(Product, id=product_id)

    # Ensure that the product belongs to the logged-in user
    if product.user_email != request.user.email:
        messages.error(request, "You are not authorized to delete this product.")
        return redirect('my_products')

    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect('my_products')
@login_required
def update_price(request, product_id):
    """Update the predicted price of a product manually."""
    if request.method == "POST":
        new_price = request.POST.get("new_price")

        if new_price:
            try:
                new_price = float(new_price)
                product = get_object_or_404(Product, id=product_id, user_email=request.user.email)
                product.predicted_price = new_price  # Update the price
                product.save()  # Save to DB
                messages.success(request, "Price updated successfully!")
            except ValueError:
                messages.error(request, "Invalid price. Please enter a valid number.")
    
    return redirect('my_products')




