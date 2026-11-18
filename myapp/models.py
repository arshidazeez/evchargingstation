from django.db import models

class Register(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField()
    phone=models.IntegerField()
    password=models.CharField(max_length=100)
    address=models.TextField()
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    zip=models.IntegerField()
    latitude=models.FloatField()
    longitude=models.FloatField()
    rights=models.CharField(max_length=100,default='User')
    date=models.DateField(auto_now_add=True)
    def __str__(self):
        return self.name

class Manager(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField()
    phone=models.IntegerField()
    company=models.CharField(max_length=100)
    type=models.CharField(max_length=100)
    stations=models.CharField(max_length=100)
    password=models.CharField(max_length=100)
    date=models.DateField(auto_now_add=True)
    rights=models.CharField(max_length=100,default='New Manager')
    def __str__(self):
        return self.name

class Station(models.Model):
    manager=models.ForeignKey(Manager,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    description=models.TextField()
    email=models.EmailField()
    phone=models.IntegerField()
    type=models.CharField(max_length=100)
    hours=models.CharField(max_length=100)
    image=models.ImageField(upload_to='images/')
    latitude=models.FloatField()
    longitude=models.FloatField()
    address=models.TextField()
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    zip=models.IntegerField()
    country=models.CharField(max_length=100)
    total_ports=models.IntegerField(null=True)
    rate=models.FloatField()
    fast_rate=models.FloatField()
    parking_fee=models.FloatField()
    service_fee=models.FloatField()
    def __str__(self):
        return self.name

class Port(models.Model):
    station=models.ForeignKey(Station,on_delete=models.CASCADE,related_name='ports')
    type=models.CharField(max_length=100)
    power=models.FloatField()
    price=models.FloatField()
    status=models.CharField(max_length=100,default='Available')

class Booking(models.Model):
    user=models.ForeignKey(Register,on_delete=models.CASCADE)
    port=models.ForeignKey(Port,on_delete=models.CASCADE)
    date=models.DateField()
    time=models.TimeField()
    vehicle_model=models.CharField(max_length=100)
    vehicle_type=models.CharField(max_length=100)
    duration=models.CharField(max_length=100)
    amount=models.FloatField()
    created_at=models.DateField(auto_now_add=True)
    status=models.CharField(max_length=100,default='Booked')
    def __str__(self):
        return self.user.name

class Seller(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField()
    phone=models.IntegerField()
    business_name=models.CharField(max_length=100)
    tax=models.CharField(max_length=100)
    address=models.TextField()
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    zip=models.IntegerField()
    country=models.CharField(max_length=100)
    password=models.CharField(max_length=100)
    image=models.ImageField(upload_to='images/')
    date=models.DateField(auto_now_add=True)
    rights=models.CharField(max_length=100,default='New Seller')

class Product(models.Model):
    seller=models.ForeignKey(Seller,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    category=models.CharField(max_length=100)
    brand=models.CharField(max_length=100)
    price=models.FloatField()
    stock=models.IntegerField()
    sku=models.CharField(max_length=100)
    image=models.ImageField(upload_to='images/')
    description=models.TextField()
    features=models.TextField()
    warranty=models.IntegerField()
    @property
    def features_list(self):
        if not self.features:
            return []
        return [line.strip() for line in self.features.splitlines() if line.strip()]
    def __str__(self):
        return self.name

class Cart(models.Model):
    user=models.ForeignKey(Register,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    @property
    def total_price(self):
        return self.quantity * self.product.price

class Order(models.Model):
    user=models.ForeignKey(Register,on_delete=models.CASCADE)
    fname=models.CharField(max_length=100)
    lname=models.CharField(max_length=100)
    email=models.EmailField()
    phone=models.IntegerField()
    address=models.TextField()
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    zip=models.IntegerField()
    country=models.CharField(max_length=100)
    billing_address=models.TextField()
    billing_city=models.CharField(max_length=100)
    billing_state=models.CharField(max_length=100)
    billing_zip=models.IntegerField()
    status=models.CharField(max_length=100,default='Booked')
    created_at=models.DateField(auto_now_add=True)
    def __str__(self):
        return self.user.name

class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    @property
    def total_price(self):
        return self.quantity * self.product.price
    def __str__(self):
        return self.product.name

class Emergency(models.Model):
    user=models.ForeignKey(Register,on_delete=models.CASCADE)
    station=models.ForeignKey(Station,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    email=models.EmailField()
    phone=models.IntegerField()
    vehicle_model=models.CharField(max_length=100)
    battery_level=models.CharField(max_length=100)
    location=models.CharField(max_length=100)
    latitude=models.FloatField(null=True)
    longitude=models.FloatField(null=True)
    details=models.TextField(null=True)
    price=models.FloatField()
    status=models.CharField(max_length=100,default='Booked')
    created_at=models.DateField(auto_now_add=True)
    def __str__(self):
        return self.user.name