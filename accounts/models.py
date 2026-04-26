from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone

def ten_days_later():
    return timezone.now() + timedelta(days=10)

class Members (models.Model):
    member_id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50,default='')
    email=models.CharField(max_length=100,default='')
    password=models.CharField(max_length=100,default='')
    contact=models.IntegerField()
    role=models.CharField(max_length=50,default='')

    def __str__(self):
        return self.name
    

class Products (models.Model):
    product_id=models.AutoField(primary_key=True)
    product_name=models.CharField(max_length=50,default='')
    product_category=models.CharField(max_length=50,default='')
    product_desc=models.CharField(max_length=1000,default='')
    product_pub_date = models.DateTimeField(default=timezone.now)
    product_end_date = models.DateTimeField(default=ten_days_later)
   
    product_image=models.ImageField(upload_to='auctions/images',default='')
    product_start_price= models.IntegerField(default=0)
    product_current_price= models.IntegerField(default=0)
    product_end_price=models.IntegerField(default=0)
    product_mid_price=models.IntegerField(default=0)
    product_owner=models.IntegerField(default=0)
    product_winner=models.CharField(max_length=50,default=-1)
    product_winner_id=models.IntegerField(default=-1)
    product_bidders=models.CharField(max_length=20000,default='')
    product_status=models.CharField(max_length=50,default='pending')
    product_bids_count=models.IntegerField(default=0)
    
    def __str__(self):
        return self.product_name


class Messages (models.Model):
    message_id=models.AutoField(primary_key=True)
    seller_id=models.IntegerField(default=0)
    time=models.DateTimeField(default=timezone.now)
    message_head=models.CharField(max_length=100,default='')
    message=models.CharField(max_length=100,default='')
    type=models.CharField(max_length=50,default='')

    def __str__(self):
        return self.message