from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from . models import Product, Customer, Cart, Payment, OrderPlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm, MyPasswordResetForm, SetPasswordForm
from django.contrib import messages
import razorpay #type: ignore
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import views as auth_views
from django.db.models import Q



# Create your views here.
def home(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'app/home.html',locals())

def about(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'app/about.html',locals())

def contact(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'app/contact.html',locals())

class categoryview(View):
    def get(self,request,val):
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        product = Product.objects.filter(category = val)
        title = Product.objects.filter(category = val).values('title')
        return render(request, 'app/category.html',locals())
    
class categoryTitle(View):
    def get(self,request,val):
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        product = Product.objects.filter(title = val)
        title = Product.objects.filter(category = product[0].category).values('title')
        return render(request, 'app/category.html',locals())
    
class ProductDetail(View):
    def get(self,request,pk):
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        product = Product.objects.get(pk=pk)
        return render(request, 'app/productdetail.html',locals())

class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request, 'app/registration.html',locals())
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Congratulations!!! User Register Successfully...")
        else:
            messages.warning(request,"Somthing wrong! Please check again...")
        return render(request, 'app/registration.html',locals())
    
class ProfileView(View):
    def get(self,request):
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        form = CustomerProfileForm()
        return render(request, 'app/profile.html',locals())
    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            reg = Customer(user=user,name=name,locality=locality,city=city,mobile=mobile,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request, "Congratulations! Profile Save Successfully...")
        else:
            messages.warning(request,"Something went Wrong !!!")
        return render(request, 'app/profile.html',locals())

def address(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    add = Customer.objects.filter(user=request.user)
    return render(request,'app/address.html',locals())

class UpdateAddress(View):
    def get(self,request,pk):
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request,'app/updateAddress.html',locals())
    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request,"Congratulations !!! Profile update Successfully ...")
        else:
            messages.warning(request,"Please enter the details carefully...")
        return redirect("address")
    
def custom_logout_view(request):
    logout(request)
    return redirect('login')


def password_reset_view(request):
    if request.method == 'POST':
        form = MyPasswordResetForm(request.POST)
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name='registration/password_reset_email.html',
            )
            return render(request, 'app/password_reset.html', {'step': 'email_sent'})
    else:
        form = MyPasswordResetForm()
    return render(request, 'app/password_reset.html', {'form': form, 'step': 'reset_request'})

def password_reset_confirm_view(request, uidb64=None, token=None):
    if uidb64 is not None and token is not None:
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            if request.method == 'POST':
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    return render(request, 'app/password_reset.html', {'step': 'reset_completed'})
            else:
                form = SetPasswordForm(user)
            return render(request, 'app/password_reset.html', {'form': form, 'step': 'password_confirm'})
    return render(request, 'password_reset.html', {'step': 'invalid'})

class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'app/password_reset.html'
    extra_context = {'step': 'email_sent'}

class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'app/password_reset.html'
    extra_context = {'step': 'reset_completed'}

def add_to_cart(request):
    user = request.user
    product_id= request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    return redirect("/cart")


def show_cart(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    user=request.user
    cart= Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity * p.product.discounted_price
        amount = amount + value
    totalamount = amount + 12
    return render(request,'app/addcart.html',locals())

def plus_cart(request):
    if request.method == "GET":
        prod_id = request.GET.get('prod_id')
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
    totalamount = amount + 12
    data ={
        'quantity': c.quantity,
        'amount':amount,
        'totalamount': totalamount
    }
    return JsonResponse(data)

def minus_cart(request):
    if request.method == "GET":
        prod_id = request.GET.get('prod_id')
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
    totalamount = amount + 12
    data ={
        'quantity': c.quantity,
        'amount':amount,
        'totalamount': totalamount
    }
    return JsonResponse(data)

def remove_cart(request):
    if request.method == "GET":
        prod_id = request.GET.get('prod_id')
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
    totalamount = amount + 12
    data ={
        'amount':amount,
        'totalamount': totalamount
    }
    return JsonResponse(data)

class checkout(View):
    def get(self,request):
        user=request.user
        add=Customer.objects.filter(user=user)
        cart_items=Cart.objects.filter(user=user)
        famount=0
        for p in cart_items:
            value = p.quantity * p.product.discounted_price
            famount = famount + value
        totalamount = famount + 12
        razoramount = int(totalamount * 100)
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        data = {
                'amount': razoramount, 
                'currency':'INR',
                'receipt':'order_recptid_11'
                }
        payment_response = client.order.create(data=data)
        print(payment_response)
        order_id = payment_response['id']
        order_status = payment_response['status']

        if order_status == 'created':
            payment = Payment(
                user=user,
                amount = totalamount,
                razorpay_order_id = order_id,
                razorpay_payment_status = order_status
            )
            payment.save()
        return render(request, 'app/checkout.html',locals())

def payment_done(request):
    order_id = request.GET.get("order_id")
    payment_id = request.GET.get("payment_id")
    cust_id = request.GET.get("cust_id")
    user = request.user
    customer = Customer.objects.get(id=cust_id)
    payment = Payment.objects.get(razorpay_order_id = order_id)
    payment.paid = True
    payment.razorpay_payment_id = payment_id
    payment.save()

    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user, customer=customer,product=c.product,quantity=c.quantity,payment=payment).save()
        c.delete()

    return redirect("orders")

def orders(request):
    orders = OrderPlaced.objects.filter(user=request.user)
    return render(request,'app/orders.html',locals())

