from sqlite3 import Timestamp
from django.shortcuts import render
from .models import *
from django.http import JsonResponse
from django.contrib import messages
import json
import datetime

# Create your views here.
def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order,created = Order.objects.get_or_create(customer=customer,complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total':0,'get_cart_items':0,'shipping':False}
    products = Product.objects.all()
    
    context = {'products':products}
    return render(request,'store/store.html',context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order,created = Order.objects.get_or_create(customer=customer,complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total':0,'get_cart_items':0,'shipping':False}
    context = {'items':items,'order':order}
    return render(request,'store/checkout.html',context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order,created = Order.objects.get_or_create(customer=customer,complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_total':0,'get_cart_items':0,'shipping':False}

    context = {'items':items,'order':order}
    return render(request,'store/cart.html',context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('productId: ',productId)
    print('action: ',action)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order,created = Order.objects.get_or_create(customer=customer,complete=False)
    orderItem,created = OrderItem.objects.get_or_create(order=order,product=product)

    if action == "add":
        orderItem.quantity = (orderItem.quantity + 1)
        messages.success(request,f'{orderItem.product.name} is added to the cart!')
    elif action == "remove":
        orderItem.quantity = (orderItem.quantity - 1)
        messages.success(request,f'{orderItem.product.name} is removed to the cart!')
    
    orderItem.save()

    if orderItem.quantity <=0 :
        orderItem.delete()
    
    

    return JsonResponse('Item was added',safe=False)



def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order,created = Order.objects.get_or_create(customer=customer,complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if( total == float(order.get_cart_total)):
            order.complete = True
        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer = customer,
                order = order,
                address = data['shipping']['address'],
                city = data['shipping']['city'],
                state = data['shipping']['state'],
                zipcode = data['shipping']['zipcode'],


            )

    return JsonResponse('Payment complete!',safe=False)