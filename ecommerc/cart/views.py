from django.shortcuts import render, redirect, get_object_or_404
from shop.models import Product
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist

# import logging
#
# logger = logging.getLogger(__name__)


def _cart_id(request):
    cart_id = request.session.get('cart_id')
    if not cart_id:
        cart = Cart.objects.create()
        cart_id = cart.pk
        request.session['cart_id'] = cart_id
    return cart_id


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
        cart.save()
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if int(cart_item.quantity) < int(cart_item.product.stock):
            cart_item.quantity = int(cart_item.quantity) + 1  # Convert to integer and then add 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        cart_item.save()

    return redirect('cart:cart_detail')



def cart_detail(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        total = 0
        counter = 0
        for cart_item in cart_items:
            # Ensure that cart_item.product.price is properly converted to a numerical value
            price = float(cart_item.product.price)
            total += (price * int(cart_item.quantity))
            counter += int(cart_item.quantity)
    except ObjectDoesNotExist:
        cart_items = None
        total = 0
        counter = 0

    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total, 'counter': counter})

def cart_remove(request,product_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(Product,id=product_id)
    cart_item=CartItem.objects.get(product=product,cart=cart)
    if int(cart_item.quantity)> 1:
        cart_item.quantity = int(cart_item.quantity) - 1

        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart:cart_detail')

def full_remove(request,product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart:cart_detail')

