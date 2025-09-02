from django.shortcuts import render
from .forms import ProductForm

def product_form(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            # Process form data
            data = form.cleaned_data
            # Save data or perform any actions as needed
            return render(request, "form_success.html", {"data": data})
    else:
        form = ProductForm()
    return render(request, "product_form.html", {"form": form})