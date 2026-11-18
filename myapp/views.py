from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.shortcuts import render,redirect
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import *
import json,random

def index(request):
    stations = Station.objects.all()
    return render(request,'index.html',{'stations':stations})

def register(request):
    if request.method=="POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        phone=request.POST.get("phone")
        password=request.POST.get("password")
        address=request.POST.get("address")
        city=request.POST.get("city")
        state=request.POST.get("state")
        zip=request.POST.get("zip")
        latitude=request.POST.get("latitude")
        longitude=request.POST.get("longitude")
        reg=Register.objects.create(name=name,email=email,phone=phone,address=address,city=city,state=state,zip=zip,
                     latitude=latitude,longitude=longitude)
        reg.password = make_password(password)
        reg.save()
        return redirect('/login/')
    return render(request,'register.html')

def manager_register(request):
    msg=False
    if request.method=="POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        phone=request.POST.get("phone")
        company=request.POST.get("company")
        type=request.POST.get("type")
        stations=request.POST.get("stations")
        password=request.POST.get("password")
        reg=Manager.objects.create(name=name,email=email,phone=phone,company=company,type=type,stations=stations)
        reg.password = make_password(password)
        reg.save()
        msg=True
    return render(request,'manager-register.html',{'msg':msg})

def login(request):
    msg=''
    if request.method=="POST":
        email=request.POST.get("email")
        password=request.POST.get("password")
        reg=Register.objects.filter(email=email)
        mng=Manager.objects.filter(email=email)
        seller=Seller.objects.filter(email=email)
        if reg:
            for i in reg:
                if check_password(password,i.password):
                    if i.rights=='User':
                        request.session['uid']=i.id
                        return redirect('/user/')
                    elif i.rights=='Admin':
                        return redirect('/adminp/')
        elif mng:
            for i in mng:
                if check_password(password,i.password):
                    if i.rights=='Manager':
                        request.session['mid']=i.id
                        return redirect('/manager/')
                    elif i.rights=='New Manager':
                        msg='Your application is in progress.'
                    elif i.rights=='Blocked':
                        msg='Your account has been blocked.'
                    elif i.rights=='Rejected':
                        msg='Your application has been rejected.'
        elif seller:
            for i in seller:
                if check_password(password,i.password):
                    if i.rights=='Seller':
                        request.session['sid']=i.id
                        return redirect('/seller/')
                    elif i.rights=='New Seller':
                        msg='Your application is in progress.'
                    elif i.rights=='Blocked':
                        msg='Your account has been blocked.'
                    elif i.rights=='Rejected':
                        msg='Your application has been rejected.'
        else:
            msg='Invalid email or password'
    return render(request,'login.html',{'msg':msg})

def user(request):
    stations=Station.objects.all()
    return render(request,'user/user.html',{'stations':stations})

def admin(request):
    stations=Station.objects.all()
    managers=Manager.objects.filter(rights='Manager')
    sellers=Seller.objects.filter(rights='Seller')
    users=Register.objects.filter(rights='User')
    return render(request,'admin/admin.html',{'stations':stations,'managers':managers,'sellers':sellers,'users':users})

def manager(request):
    mid=request.session.get("mid")
    manager=Manager.objects.get(id=mid)
    stations=Station.objects.filter(manager=manager)
    bookings=Booking.objects.filter(port__station__manager=manager)
    emergency=Emergency.objects.filter(station__manager=manager)
    return render(request,'manager/manager.html',{'stations':stations,'bookings':bookings,'emergency':emergency})

def new_managers(request):
    managers=Manager.objects.filter(rights='New Manager')
    return render(request,'admin/new-managers.html',{'managers':managers})

def manage_manager(request,id,status):
    Manager.objects.filter(id=id).update(rights=status)
    return redirect(request.META['HTTP_REFERER'])

def managers(request):
    managers=Manager.objects.exclude(rights__in=['New Manager','Rejected'])
    return render(request,'admin/managers.html',{'managers':managers})

def add_station(request):
    mid=request.session.get("mid")
    mng=Manager.objects.get(id=mid)
    if request.method=="POST":
        name=request.POST.get("name")
        description=request.POST.get("description")
        email=request.POST.get("email")
        phone=request.POST.get("phone")
        type=request.POST.get("type")
        hours=request.POST.get("hours")
        image=request.FILES.get("image")
        latitude=request.POST.get("latitude")
        longitude=request.POST.get("longitude")
        address=request.POST.get("address")
        city=request.POST.get("city")
        state=request.POST.get("state")
        zipcode=request.POST.get("zip")
        country=request.POST.get("country")
        ports=request.POST.get("total_ports")
        rate=request.POST.get("rate")
        fast_rate=request.POST.get("fast_rate")
        parking_fee=request.POST.get("parking_fee")
        service_fee=request.POST.get("service_fee")
        st=Station.objects.create(manager=mng,name=name,description=description,email=email,phone=phone,type=type,hours=hours,image=image,latitude=latitude,longitude=longitude,
                   address=address,city=city,state=state,zip=zipcode,country=country,total_ports=ports,rate=rate,fast_rate=fast_rate,parking_fee=parking_fee,
                   service_fee=service_fee)
        port_type=request.POST.getlist("port_type")
        power=request.POST.getlist("power")
        price=request.POST.getlist("price")
        for i,j,k in zip(port_type,power,price):
            Port(station=st,type=i,power=j,price=k).save()
        return redirect(request.META['HTTP_REFERER'])
    return render(request,'manager/add-station.html')

def my_stations(request):
    mid=request.session.get("mid")
    mng=Manager.objects.get(id=mid)
    stations=Station.objects.filter(manager=mng)
    return render(request,'manager/my-stations.html',{'stations':stations})

def edit_station(request,id):
    sts=Station.objects.get(id=id)
    if request.method=="POST":
        name=request.POST.get("name")
        description=request.POST.get("description")
        email=request.POST.get("email")
        phone=request.POST.get("phone")
        type=request.POST.get("type")
        hours=request.POST.get("hours")
        image=request.FILES.get("image")
        latitude=request.POST.get("latitude")
        longitude=request.POST.get("longitude")
        address=request.POST.get("address")
        city=request.POST.get("city")
        state=request.POST.get("state")
        zip=request.POST.get("zip")
        country=request.POST.get("country")
        ports=request.POST.get("total_ports")
        rate=request.POST.get("rate")
        fast_rate=request.POST.get("fast_rate")
        parking_fee=request.POST.get("parking_fee")
        service_fee=request.POST.get("service_fee")
        sts.name=name
        sts.description=description
        sts.email=email
        sts.phone=phone
        sts.type=type
        sts.hours=hours
        if image:
            sts.image=image
        sts.latitude=latitude
        sts.longitude=longitude
        sts.address=address
        sts.city=city
        sts.state=state
        sts.zip=zip
        sts.country=country
        sts.total_ports=ports
        sts.rate=rate
        sts.fast_rate=fast_rate
        sts.parking_fee=parking_fee
        sts.service_fee=service_fee
        sts.save()
        return redirect(request.META['HTTP_REFERER'])
    return render(request,'manager/edit-station.html',{'sts':sts})

def delete_station(request,id):
    Station.objects.filter(id=id).delete()
    return redirect(request.META['HTTP_REFERER'])

def station_view(request,id):
    station=Station.objects.get(id=id)
    return render(request,'user/station-view.html',{'station':station})

def booking(request,id):
    port=Port.objects.get(id=id)
    uid=request.session.get("uid")
    reg=Register.objects.get(id=uid)
    if request.method=="POST":
        date=request.POST.get("date")
        time=request.POST.get("time")
        vehicle_model=request.POST.get("model")
        vehicle_type=request.POST.get("vtype")
        duration=request.POST.get("duration")
        amount=request.POST.get("amount")
        bk=Booking(user=reg,port=port,date=date,time=time,vehicle_model=vehicle_model,vehicle_type=vehicle_type,duration=duration,amount=amount)
        bk.save()
        return redirect('/success/')
    return render(request,'user/booking.html',{'port':port})


def check_port_availability(request, port_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            date = data.get('date')
            time = data.get('time')
            duration = data.get('duration', '2 hours')

            if not date or not time:
                return JsonResponse({
                    'error': 'Date and time are required'
                }, status=400)

            try:
                port = Port.objects.get(id=port_id)
            except Port.DoesNotExist:
                return JsonResponse({
                    'error': 'Port not found'
                }, status=404)

            station = port.station

            all_ports = station.ports.all()
            total_ports = all_ports.count()

            duration_parts = duration.split()
            duration_hours = 2

            if 'min' in duration:
                duration_minutes = int(duration_parts[0])
                duration_hours = duration_minutes / 60
            elif 'hour' in duration:
                if len(duration_parts) > 1 and duration_parts[1] == 'hours':
                    duration_hours = int(duration_parts[0])
                else:
                    duration_hours = 1

            try:
                start_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
                end_datetime = start_datetime + timedelta(hours=duration_hours)
            except ValueError as e:
                return JsonResponse({
                    'error': f'Invalid date or time format: {str(e)}'
                }, status=400)

            existing_bookings = Booking.objects.filter(
                port__in=all_ports,
                date=date
            ).select_related('port')

            booked_port_ids = set()

            for booking in existing_bookings:
                booking_time_str = booking.time.strftime("%H:%M")

                try:
                    booking_datetime = datetime.strptime(f"{booking.date} {booking_time_str}", "%Y-%m-%d %H:%M")
                except ValueError as e:
                    continue

                booking_duration_parts = booking.duration.split()
                booking_duration_hours = 2

                if 'min' in booking.duration:
                    booking_minutes = int(booking_duration_parts[0])
                    booking_duration_hours = booking_minutes / 60
                elif 'hour' in booking.duration:
                    if len(booking_duration_parts) > 1 and booking_duration_parts[1] == 'hours':
                        booking_duration_hours = int(booking_duration_parts[0])
                    else:
                        booking_duration_hours = 1

                booking_end_datetime = booking_datetime + timedelta(hours=booking_duration_hours)
                overlap = (start_datetime < booking_end_datetime) and (end_datetime > booking_datetime)

                if overlap:
                    booked_port_ids.add(booking.port.id)

            station_full = len(booked_port_ids) >= total_ports
            port_booked = port.id in booked_port_ids

            available = not (station_full or port_booked)
            available_ports = total_ports - len(booked_port_ids)

            return JsonResponse({
                'available': available,
                'station_full': station_full,
                'port_booked': port_booked,
                'available_ports': available_ports,
                'total_ports': total_ports,
                'station_name': station.name,
                'port_name': port.type,
                'message': f"{available_ports} of {total_ports} ports available" if available_ports > 0 else "All ports booked",
                'suggested_times': suggest_alternative_times(station, date, time) if not available else [],
                'debug_info': {
                    'booked_port_count': len(booked_port_ids),
                    'total_port_count': total_ports,
                    'port_id': port.id,
                    'port_booked': port.id in booked_port_ids
                }
            })

        except json.JSONDecodeError as e:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'error': f'Server error: {str(e)}'
            }, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def suggest_alternative_times(station, date, time):
    suggestions = []

    try:
        original_time = datetime.strptime(time, "%H:%M").time()

        times_to_check = [
            (datetime.combine(datetime.strptime(date, "%Y-%m-%d"), original_time) + timedelta(
                hours=-1)).time().strftime("%H:%M"),
            (datetime.combine(datetime.strptime(date, "%Y-%m-%d"), original_time) + timedelta(hours=1)).time().strftime(
                "%H:%M"),
            (datetime.combine(datetime.strptime(date, "%Y-%m-%d"), original_time) + timedelta(
                hours=-2)).time().strftime("%H:%M"),
            (datetime.combine(datetime.strptime(date, "%Y-%m-%d"), original_time) + timedelta(hours=2)).time().strftime(
                "%H:%M"),
        ]

        for suggested_time in times_to_check:
            try:
                bookings_count = Booking.objects.filter(
                    port__station=station,
                    date=date,
                    time=suggested_time
                ).count()

                total_ports = station.ports.count()

                if bookings_count < total_ports:
                    suggestions.append({
                        'time': suggested_time,
                        'available_ports': total_ports - bookings_count
                    })
            except:
                continue

    except:
        pass

    return suggestions[:3]


def success(request):
    return render(request,'user/success.html')

def my_bookings(request):
    uid=request.session.get("uid")
    reg=Register.objects.get(id=uid)
    bookings=Booking.objects.filter(user=reg)
    return render(request,'user/my-bookings.html',{'bookings':bookings})

def manage_booking(request,id,status):
    Booking.objects.filter(id=id).update(status=status)
    return redirect(request.META['HTTP_REFERER'])

def bookings(request):
    mid=request.session.get("mid")
    manager=Manager.objects.get(id=mid)
    bookings=Booking.objects.filter(port__station__manager=manager)
    return render(request,'manager/bookings.html',{'bookings':bookings})

def seller_register(request):
    if request.method == "POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        phone=request.POST.get("phone")
        business_name=request.POST.get("business_name")
        tax=request.POST.get("tax")
        address=request.POST.get("address")
        city=request.POST.get("city")
        state=request.POST.get("state")
        zip=request.POST.get("zip")
        country=request.POST.get("country")
        password=request.POST.get("password")
        image=request.FILES.get("image")
        seller=Seller.objects.create(name=name,email=email,phone=phone,business_name=business_name,tax=tax,address=address,city=city,state=state,
                      zip=zip,country=country,image=image)
        seller.password=make_password(password)
        seller.save()
        return redirect('/login/')
    return render(request,'seller-register.html')

def seller(request):
    sid=request.session.get("sid")
    seller=Seller.objects.get(id=sid)
    revenue=OrderItem.objects.filter(product__seller=seller)
    products=Product.objects.filter(seller=seller)
    bookings=[]
    for i in revenue:
        bookings=Order.objects.filter(id=i.order.id)
    return render(request,'seller/seller.html',{'seller':seller,'products':products,'revenue':revenue,'bookings':bookings})

def new_sellers(request):
    sellers=Seller.objects.filter(rights='New Seller')
    return render(request,'admin/new-sellers.html',{'sellers':sellers})

def manage_seller(request,id,status):
    Seller.objects.filter(id=id).update(rights=status)
    return redirect(request.META['HTTP_REFERER'])

def sellers(request):
    sellers=Seller.objects.exclude(rights__in=['New Seller','Rejected'])
    return render(request,'admin/sellers.html',{'sellers':sellers})

def add_products(request):
    sid=request.session.get("sid")
    seller=Seller.objects.get(id=sid)
    products=Product.objects.filter(seller=seller)
    if request.method == "POST":
        name=request.POST.get("name")
        category=request.POST.get("category")
        brand=request.POST.get("brand")
        price=request.POST.get("price")
        stock=request.POST.get("stock")
        sku=request.POST.get("sku")
        image=request.FILES.get("image")
        description=request.POST.get("description")
        features=request.POST.get("features")
        warranty=request.POST.get("warranty")
        pid=request.POST.get("pid")
        if pid:
            product=Product.objects.get(id=pid)
            product.name=name
            product.category=category
            product.brand=brand
            product.price=price
            product.stock=stock
            product.sku=sku
            if image:
                product.image=image
            product.description=description
            product.features=features
            product.warranty=warranty
            product.save()
        else:
            pro=Product(seller=seller,name=name,category=category,brand=brand,price=price,stock=stock,sku=sku,image=image,description=description,
                        features=features,warranty=warranty)
            pro.save()
        return redirect(request.META['HTTP_REFERER'])

    return render(request,'seller/add-products.html',{'products':products})

def delete_product(request,id):
    Product.objects.filter(id=id).delete()
    return redirect(request.META['HTTP_REFERER'])

def products(request):
    products=Product.objects.all()
    return render(request,'user/products.html',{'products':products})

def cart(request):
    uid=request.session.get("uid")
    reg=Register.objects.get(id=uid)
    cart=Cart.objects.filter(user=reg)
    total=0
    for i in cart:
        total+=i.total_price
    return render(request,'user/cart.html',{'cart_items':cart,'total':total})

def add_cart(request,id):
    uid=request.session.get("uid")
    reg=Register.objects.get(id=uid)
    product=Product.objects.get(id=id)
    cart=Cart.objects.filter(user=reg,product=product)
    if cart:
        for i in cart:
            quantity=i.quantity
            cart.update(quantity=quantity+1)
    else:
        Cart(user=reg,product=product,quantity=1).save()
    return redirect(request.META['HTTP_REFERER'])

def remove_cart(request,id):
    Cart.objects.filter(id=id).delete()
    return redirect(request.META['HTTP_REFERER'])

def update_cart(request, id, quantity):
    cart_item = Cart.objects.get(id=id)
    quantity = max(1, int(quantity))
    cart_item.quantity = quantity
    cart_item.save()

    item_total = cart_item.quantity * cart_item.product.price

    cart_items = Cart.objects.filter(user=cart_item.user)
    cart_subtotal = sum(i.quantity * i.product.price for i in cart_items)
    cart_total = cart_subtotal
    cart_count = cart_items.count()

    return JsonResponse({
        'item_total': item_total,
        'cart_subtotal': cart_subtotal,
        'cart_total': cart_total,
        'cart_count': cart_count
    })

def checkout(request):
    uid=request.session.get("uid")
    reg=Register.objects.get(id=uid)
    cart=Cart.objects.filter(user=reg)
    total=0
    for i in cart:
        total+=i.total_price
    if request.method == "POST":
        fname=request.POST.get("fname")
        lname=request.POST.get("lname")
        email=request.POST.get("email")
        phone=request.POST.get("phone")
        address=request.POST.get("address")
        city=request.POST.get("city")
        state=request.POST.get("state")
        zipcode=request.POST.get("zipcode")
        country=request.POST.get("country")
        billing_address=request.POST.get("billing_address")
        billing_city=request.POST.get("billing_city")
        billing_state=request.POST.get("billing_state")
        billing_zipcode=request.POST.get("billing_zipcode")
        ord=Order.objects.create(user=reg,fname=fname,lname=lname,email=email,phone=phone,address=address,city=city,state=state,zip=zipcode,
                                 country=country,billing_address=billing_address,billing_city=billing_city,billing_state=billing_state,billing_zip=billing_zipcode)
        for j in cart:
            OrderItem(order=ord,product=j.product,quantity=j.quantity).save()
        return redirect('/order-success/')
    return render(request,'user/checkout.html',{'order_items':cart,'total':total})

def order_success(request):
    return render(request,'user/order-success.html')

def my_orders(request):
    uid=request.session.get("uid")
    reg=Register.objects.get(id=uid)
    orders=Order.objects.filter(user=reg)
    return render(request,'user/my-orders.html',{'orders':orders})

def manage_order(request,id,status):
    Order.objects.filter(id=id).update(status=status)
    return redirect(request.META['HTTP_REFERER'])

def orders(request):
    sid=request.session.get("sid")
    seller=Seller.objects.get(id=sid)
    oi=OrderItem.objects.filter(product__seller=seller)
    orders=[]
    for i in oi:
        orders=Order.objects.filter(id=i.order.id)
    return render(request,'seller/orders.html',{'orders':orders})

def emergency_service(request,id):
    station=Station.objects.get(id=id)
    uid=request.session.get("uid")
    reg=Register.objects.get(id=uid)
    if request.method=="POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        phone=request.POST.get("phone")
        vehicle_model=request.POST.get("vehicle_model")
        battery_level=request.POST.get("battery_level")
        location=request.POST.get("location")
        latitude=request.POST.get("latitude")
        longitude=request.POST.get("longitude")
        details=request.POST.get("details")
        emer=Emergency(user=reg,station=station,name=name,email=email,phone=phone,vehicle_model=vehicle_model,
                       battery_level=battery_level,location=location,latitude=latitude,longitude=longitude,details=details,price=141)
        emer.save()
        return redirect('/my-emergency-bookings/')
    return render(request,'user/emergency-service.html',{'station':station,'reg':reg})

def my_emergency_bookings(request):
    uid=request.session.get("uid")
    reg=Register.objects.get(id=uid)
    bookings=Emergency.objects.filter(user=reg)
    return render(request,'user/my-emergency-bookings.html',{'bookings':bookings,'reg':reg})

def emergency_bookings(request):
    mid=request.session.get("mid")
    manager=Manager.objects.get(id=mid)
    bookings=Emergency.objects.filter(station__manager=manager)
    return render(request,"manager/emergency-bookings.html",{'bookings':bookings})

def manage_emergency_bookings(request,id,status):
    Emergency.objects.filter(id=id).update(status=status)
    return redirect(request.META['HTTP_REFERER'])

def profile(request):
    uid=request.session.get("uid")
    reg=Register.objects.get(id=uid)
    if request.method=="POST":
        reg.name=request.POST.get("name")
        reg.email=request.POST.get("email")
        reg.phone=request.POST.get("phone")
        reg.address=request.POST.get("address")
        reg.city=request.POST.get("city")
        reg.state=request.POST.get("state")
        reg.zip=request.POST.get("zip")
        password=request.POST.get("password")
        if password:
            reg.password=make_password(password)
        reg.save()
        return redirect(request.META['HTTP_REFERER'])
    return render(request,'user/profile.html',{'reg':reg})

def email(request):
    msg=False
    if request.method=="POST":
        email=request.POST.get('email')
        reg=Register.objects.filter(email=email)
        mng=Manager.objects.filter(email=email)
        sell=Seller.objects.filter(email=email)
        if reg or mng or sell:
            request.session['email']=email
            rid=str(random.randint(0000,9999))
            request.session['otp']=rid
            subject = 'EV Charging Station - Password Reset OTP'
            message = f'Hi,this is one time password to change your password!{rid}'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, email_from, recipient_list)
            return redirect('/otp/')
        else:
            msg=True
    return render(request, 'email.html',{'msg':msg})

def otp(request):
    msg=False
    if request.method=="POST":
        otp=request.POST.get('otp')
        rid=request.session['otp']
        if otp==rid:
            return redirect('/password/')
        else:
            msg=True
    return render(request, 'otp.html',{'msg':msg})

def password(request):
    msg=False
    if request.method=="POST":
        password=request.POST.get('np')
        cpassword=request.POST.get('cp')
        if password==cpassword:
            email=request.session['email']
            reg = Register.objects.filter(email=email)
            mng = Manager.objects.filter(email=email)
            sell = Seller.objects.filter(email=email)
            if reg:
                reg.password = make_password(password)
            elif mng:
                mng.password = make_password(password)
            elif sell:
                sell.password = make_password(password)
            return redirect('/login/')
        else:
            msg=True
    return render(request, 'password.html',{'msg':msg})

def manager_profile(request):
    mid=request.session.get("mid")
    manager=Manager.objects.get(id=mid)
    if request.method=="POST":
        manager.name=request.POST.get("name")
        manager.email=request.POST.get("email")
        manager.phone=request.POST.get("phone")
        manager.company=request.POST.get("company")
        password=request.POST.get("password")
        if password:
            manager.password=make_password(password)
        manager.save()
        return redirect(request.META['HTTP_REFERER'])
    return render(request,'manager/manager-profile.html',{'manager':manager})

def seller_profile(request):
    sid=request.session.get("sid")
    seller=Seller.objects.get(id=sid)
    if request.method=="POST":
        seller.name=request.POST.get("name")
        seller.email=request.POST.get("email")
        seller.phone=request.POST.get("phone")
        seller.business_name=request.POST.get("business_name")
        seller.tax=request.POST.get("tax")
        seller.address=request.POST.get("address")
        seller.city=request.POST.get("city")
        seller.state=request.POST.get("state")
        seller.zip=request.POST.get("zip")
        seller.country=request.POST.get("country")
        password=request.POST.get("password")
        if password:
            seller.password=make_password(password)
        seller.save()
        return redirect(request.META['HTTP_REFERER'])
    return render(request,'seller/seller-profile.html',{'seller':seller})
def logout(request):
    request.session.flush()
    return redirect('/')

def users(request):
    users=Register.objects.exclude(rights='Admin')
    return render(request,'admin/users.html',{'users':users})

def manage_user(request,id,status):
    Register.objects.filter(id=id).update(rights=status)
    return redirect(request.META['HTTP_REFERER'])