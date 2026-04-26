from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from .models import Members,Products,Messages
from django.contrib import messages
from django.db.models import Avg
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import timedelta

import requests
import json
import os
from dotenv import load_dotenv


def landing(request):
    return render(request,'accounts/homepage.html')

def custom_login(request):
    if request.method=='POST':
        email=request.POST.get('email','')
        email=email.lower()
        p=request.POST.get('password','')
        role=request.POST.get("role",'')

        members=Members.objects.filter(email=email,password=p,role=role)
        user=authenticate(request,username=email,password=p)
        if len(members)>0:
            login(request,user)
            record=members[0]
            
           
            return redirect('decision')
            
        else:
            messages.error(request,'No User Found')
            return render(request,'accounts/login.html')
    return render(request,'accounts/login.html')

def signup(request):
    if request.method=='POST':
        name=request.POST.get('fullName','')
        email=request.POST.get('email','')
        email=email.lower()
        contact=request.POST.get('phoneNumber','')
        p1=request.POST.get('password','')
        p2=request.POST.get('confirmPassword','')
        role=request.POST.get('role','')
 
        members=Members.objects.filter(email=email)
        if len(members)>0:
            messages.error(request,'user already exists')
            return render(request,'accounts/signup.html')
        elif len(name)<=0 or len(email)<=12 or len(contact)<11 or len(p1)<=6 or len(p2)<=6 or len(role)<5:
            messages.error(request,'Please fill all the details caerfully!')
            return render(request,'accounts/signup.html')
        elif p1!=p2:
            messages.error(request,'Please choose the password caerfully!')
            return render(request,'accounts/signup.html')
        else:
            try:
                send_mail(subject='Account Created',message=f'Congrats! Your account on bid master has been created and activated successfully!' ,from_email='auctionsystem786@gmail.com',   recipient_list=[email],fail_silently=False,)
                record=Members(name=name,email=email,contact=contact,password=p1,role=role)
                record.save()
                user=User.objects.create_user(username=email,password=p1,email=email)
                messages.success(request,'Account created Successfully')
                return render(request,'accounts/signup.html')
            except:
                messages.error(request,'Please Enter Valid Email!')
                return render(request,'accounts/signup.html')

 
    return render(request,'accounts/signup.html')


@login_required
def decision(request):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    record=Members.objects.filter(member_id=member_id)[0]

    if record.role=='admin':
        lives=len(Products.objects.filter(product_status='live'))
        pending=len(Products.objects.filter(product_status='pending'))
        solds=len(Products.objects.filter(product_status='sold'))
        inactives=len(Products.objects.filter(product_status='inactive'))
        sellers=len(Members.objects.filter(role='seller'))
        bidders=len(Members.objects.filter(role='bidder'))
        members=sellers+bidders
        products=lives+pending+solds+inactives

        return render(request,'accounts/admin_dashboard.html',{'admin':record,'id':member_id,'lives':lives,'inactives':inactives,'solds':solds,'pendings':pending,'sellers':sellers,'bidders':bidders,'members':members,'products':products})
    

    if record.role=='seller':
        name=record.name
        pendings=len(Products.objects.filter(product_owner=member_id,product_status='pending'))
        live=len(Products.objects.filter(product_owner=member_id,product_status='live'))
        sold=len(Products.objects.filter(product_owner=member_id,product_status='sold'))
        inactive=len(Products.objects.filter(product_owner=member_id,product_status='inactive'))
        messages=Messages.objects.filter(seller_id=member_id).order_by('-time')
        if len(messages)>=5:
            messages=messages[:5]

        return render(request,'accounts/dashboard_seller.html',{'id':member_id,'pendings':pendings,'live':live,'sold':sold,'inactive':inactive,'name':name,'updates':messages})
    

    if record.role=='bidder':
        name=record.name
        live=len(Products.objects.filter(product_status='live'))
        win=len(Products.objects.filter(product_winner_id=member_id))
        messages=len(Messages.objects.filter(seller_id=member_id))
        print(live,win,messages)
        return render(request,'accounts/bidderDashboard.html',{'name':name,'id':member_id,'live':live,'winnings':win,'messages':messages})    

# ADMIN DASHBOARD FUNCTIONS
@login_required
def all_pendings(request):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    member_role=Members.objects.get(email=email).role
    if member_role=='admin':
        products=Products.objects.filter(product_status='pending')
        return render(request,'accounts/all_pendings.html',{'id':member_id,'items':len(products),'records':products})
    else:
        return HttpResponse("Page not found")
    
@login_required
def all_inactives(request):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    member_role=Members.objects.get(email=email).role
    if member_role=='admin':
        records=Products.objects.filter(product_status='inactive')
        if len(records)>0:
            good=True
        else:
            good=False
        return render(request,'accounts/all_inactive.html',{'records':records,'id':member_id,'good':good,'items':len(records)})
    else:
        return HttpResponse("Page not found")
    
@login_required
def all_solds(request):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    member_role=Members.objects.get(email=email).role
    if member_role=='admin':

        records=Products.objects.filter(product_status='sold')
        total=[]
        for record in records:
            total.append(record.product_current_price)
        if len(records)>0:
            totals=sum(total)
            max1=max(total)
            avg=sum(total)/len(total)

            good=True
        else:
            totals=0
            max1=0
            avg=0
            good=False
        return render(request,'accounts/all_sold.html',{'id':member_id,'items':len(records),'revenue':totals,'max':max1,'avg':avg,'records':records,'good':good})
    else:
        return HttpResponse("Page not found")
    
@login_required
def all_live(request):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    member_role=Members.objects.get(email=email).role
    if member_role=='admin':
        records=Products.objects.filter(product_status='live').order_by('-product_pub_date')
        total=[]
        for record in records:
            total.append(record.product_bids_count)
        if len(records)>0:
            bids=sum(total)
            good=True
        else:
            bids=0
            good=False
        return render(request,'accounts/all_live.html',{'records':records,'id':member_id,'good':good,'items':len(records),'bids':bids})
    else:
        return HttpResponse("Page not found")

@login_required
def update_status(request, product_id):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    member_role=Members.objects.get(email=email).role

    if member_role=='admin':
        if request.method == "POST":
            action = request.POST.get("action")
        
            try:
                product = Products.objects.get(product_id=product_id)
                if action in ["approved", "rejected"]:  # safety check
                    if action == "approved":
                        product.product_status = "live"
                        start_date = timezone.now()
                        product.product_end_date=start_date + timedelta(days=10)
                    elif action == "rejected":
                        product.product_status = "inactive"
                    product.save()

                    return JsonResponse({
                        "success": True,
                        "new_status": product.product_status  # ✅ correct field
                    })
                else:
                    return JsonResponse({"success": False, "error": "Invalid action"}, status=400)
            except Products.DoesNotExist:
                return JsonResponse({"success": False, "error": "Product not found"}, status=404)

        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
    else:
        return HttpResponse("Page not found")
    
@login_required
def inactivate_status(request, product_id):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    member_role=Members.objects.get(email=email).role

    if member_role=='admin':
        if request.method == "POST":
            action = request.POST.get("action")
        
            try:
                product = Products.objects.get(product_id=product_id)
                if action in ["inactivate"]:  # safety check
                    product.product_status = "inactive"
                    product.save()

                    return JsonResponse({
                    "success": True,
                    "new_status": product.product_status  # ✅ correct field
                })
                else:
                    return JsonResponse({"success": False, "error": "Invalid action"}, status=400)
            except Products.DoesNotExist:
                return JsonResponse({"success": False, "error": "Product not found"}, status=404)

        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
    else:
        return HttpResponse("Page not found")

@login_required
def all_sellers(request):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    member_role=Members.objects.get(email=email).role
    if member_role=='admin':
        sellers=Members.objects.filter(role='seller')
        return render(request,'accounts/all_sellers.html',{'members':sellers,'total':len(sellers),'id':member_id})
    else:
        return HttpResponse("Page not found")
    
@login_required
def all_bidders(request):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    member_role=Members.objects.get(email=email).role
    if member_role=='admin':
        sellers=Members.objects.filter(role='bidder')
        return render(request,'accounts/all_bidders.html',{'members':sellers,'total':len(sellers),'id':member_id})
    else:
        return HttpResponse("Page not found")



# SELLER DASHBOARD FUNCTIONS
@login_required  
def new_auction(request):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    member_role=Members.objects.get(email=email).role
    if member_role=='seller':
        if request.method=='POST':
            name=request.POST.get('name','')
            category=request.POST.get('category','')
            description=request.POST.get('description','')
            starting_price=request.POST.get('starting_price','')
            reserve_price=request.POST.get('reserve_price','')
            buy_now_price=request.POST.get('buy_now_price','')
            image = request.FILES.get('images')
            checkbox_value = request.POST.get('checkbox', '')
            if checkbox_value:
                record=Products(product_name=name,product_category=category,product_desc=description,product_image=image,product_start_price=starting_price,product_current_price=starting_price,product_end_price=buy_now_price,product_mid_price=reserve_price,product_owner=member_id,product_winner=-1,product_bidders='',product_status='pending')
                record.save()
                messages.success(request,'Your Product has been sent to admin for approval!')
                return render(request,'accounts/form.html',{'id':member_id})
            else:
                messages.error(request,'Please mark the checkbox ')
                return render(request,'accounts/form.html',{'id':member_id})
        
        return render(request,'accounts/form.html',{'id':member_id})
    else:
        return HttpResponse("Page not found")

@login_required
def categories(request):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    member_role=Members.objects.get(email=email).role
    if member_role=='bidder':
        categories = Products.objects.filter(product_status="live").values_list('product_category', flat=True).distinct()
        categories_details=[]
        live=0
        for category in categories:
            cat=len(Products.objects.filter(product_status="live",product_category=category))
            live+=cat
            cat1=len(Products.objects.filter(product_category=category))
            avg_price = Products.objects.filter(product_category=category,product_status="live").aggregate(avg_price=Avg('product_current_price'))['avg_price']
            categories_details.append([category,cat,cat1,avg_price])
        members=len(Members.objects.filter(role='bidder'))
        return render(request,'accounts/allAuctions.html',{'id':member_id,'categories_count':len(categories),'categories':categories_details,'live':live,'members':members})
    else:
        return HttpResponse("Page not found")
   
@login_required
def live_to_show(request,category):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    member_role=Members.objects.get(email=email).role
    if member_role=='bidder':
        print(member_id,category)
        live=Products.objects.filter(product_category=category,product_status='live')
        return render(request,'accounts/bidderCatagoryDetail.html',{'category':category,'id':member_id,'live':len(live),'products':live})
    else:
        return HttpResponse("Page not found")
    
@login_required
def bidder_messages(request):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    member_role=Members.objects.get(email=email).role
    if member_role=='bidder':
        messages=Messages.objects.filter(seller_id=member_id).order_by('-time')
        return render(request,'accounts/bidder_messages.html',{'members': messages,'total':len(messages),'id':member_id})
    else:
        return HttpResponse("Page not found")
    
@login_required
def winnings(request):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    member_role=Members.objects.get(email=email).role
    if member_role=='bidder':
        products=Products.objects.filter(product_status='sold',product_winner_id=member_id).order_by('-product_end_date')
        if len(products)>0:
            true=True
        else:
            true=False
        win=len(products)
        return render(request,'accounts/bidderWonAuctions.html',{'id':member_id,'win':win,'true':true,'products':products})
    else:
        return HttpResponse("Page not found")


@login_required
def show_details(request,product_id):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    member_role=Members.objects.get(email=email).role
    if member_role=='bidder':
        product=Products.objects.get(product_id=product_id)
        if request.method=='POST':
            bid=request.POST.get('bid_amount','')
            if bid=='':
                bid=0

            if int(bid)<=int(product.product_current_price):
                less=True
                return render(request,'accounts/product_details.html',{'id':member_id,'product':product,'less':less})


            elif int(bid)>int(product.product_end_price):
                won=True
                product.product_bidders=product.product_bidders+f',{member_id}'
                product.product_current_price=bid
                product.product_winner_id=member_id
                product.product_winner=Members.objects.get(member_id=member_id).name
                product.product_bids_count=product.product_bids_count+1
                product.product_status='sold'
                product.product_end_date=timezone.now()
                owner=Members.objects.get(member_id=product.product_owner).contact
                winner=Members.objects.get(member_id=member_id).email
                send_mail(subject='Auction Update',message=f'Congrats! You won the bid of product named {product.product_name} for ${int(bid)}. Kindly contact on {owner} 🎉',from_email='auctionsystem786@gmail.com',   recipient_list=[winner],fail_silently=False,)

                product.save()
                message=Messages(seller_id=member_id,time=timezone.now(),message_head='YOU WON THE BIT',message=f'Congratulations you have won the product,named {product.product_name}  for ${int(bid)}. Kindly contact on {owner} 🎉',type='winnings')
                message.save()
                customer=Members.objects.get(member_id=member_id).name
                msg=Messages(seller_id=product.product_owner,message_head='Sold Out',message=f'Your product named {product.product_name} has been sold out to {customer} for ${int(bid)}',type='sold')
                msg.save()
                return render(request,'accounts/product_details.html',{'id':member_id,'product':product,'won':won})

            elif int(bid)<int(product.product_end_price):
                save=True
                product.product_bidders=product.product_bidders+f',{member_id}'
                product.product_current_price=bid
                product.product_bids_count=product.product_bids_count+1
                product.save()
                customer=Members.objects.get(member_id=member_id).name
                msg=Messages(seller_id=product.product_owner,message_head='New bid',message=f'New bid of ${int(bid)} on your product named {product.product_name} is received from {customer}',type='bid')
                msg.save()
                return render(request,'accounts/product_details.html',{'id':member_id,'product':product,'save':save})
    
        return render(request,'accounts/product_details.html',{'id':member_id,'product':product})
    else:
        return HttpResponse("Page not found")
    
@login_required
def time_up(request,product_id):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    member_role=Members.objects.get(email=email).role
    if member_role=='bidder':
        product=Products.objects.get(product_id=product_id)
        category=product.product_category
    
        if product.product_current_price < product.product_mid_price or product.product_bids_count==0:
            product.product_status = "inactive"
            product.save()
            msg=Messages(seller_id=product.product_owner,message_head='Product Inactivated',message=f'your product named {product.product_name} has been inactivated because of no suitable bid',type='inactive')
            msg.save()
            live=Products.objects.filter(product_category=category,product_status='live')
            return render(request,'accounts/bidderCatagoryDetail.html',{'category':category,'id':member_id,'live':len(live),'products':live})

        else:
            winner_id=int(product.product_bidders.split(',')[-1])
            winner_name=Members.objects.get(member_id=winner_id).name
            winner_email=Members.objects.get(member_id=winner_id).email
            owner=Members.objects.get(member_id=product.product_owner).contact

            product.product_winner_id=winner_id
            product.product_winner=winner_name
            product.product_status = "sold"
                
            send_mail(subject='Auction Update',message=f'Congrats! You won the bid of product named {product.product_name} for ${int(product.product_current_price)}. Kindly contact on {owner} 🎉',from_email='auctionsystem786@gmail.com',   recipient_list=[winner_email],fail_silently=False,)

            product.save()
            message=Messages(seller_id=winner_id,time=timezone.now(),message_head='YOU WON THE BIT',message=f'Congratulations you have won the product,named {product.product_name}  for ${int(product.product_current_price)}. Kindly contact on {owner} 🎉',type='winnings')
            message.save()
            msg=Messages(seller_id=product.product_owner,message_head='Sold Out',message=f'Your product named {product.product_name} has been sold out to {winner_name} for ${int(product.product_current_price)}',type='sold')
            msg.save()
            live=Products.objects.filter(product_category=category,product_status='live')
            return render(request,'accounts/bidderCatagoryDetail.html',{'category':category,'id':member_id,'live':len(live),'products':live})

    else:
        return HttpResponse("Page not found")
            

@login_required
def live(request):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    member_role=Members.objects.get(email=email).role
    if member_role=='seller':
        records= Products.objects.filter(product_owner=member_id,product_status='live')
        total=[]
        for record in records:
            total.append(record.product_bids_count)
        if len(records)>0:
            bids=sum(total)
            good=True
        else:
            bids=0
            good=False
        return render(request,'accounts/live-auctions.html',{'records':records,'id':member_id,'good':good,'items':len(records),'bids':bids})
    else:
        return HttpResponse("ERROR:PAGE NOT FOUND")



@login_required
def inactive(request):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    member_role=Members.objects.get(email=email).role
    if member_role=='seller':
        records= Products.objects.filter(product_owner=member_id,product_status='inactive')
        if len(records)>0:
            good=True
        else:
            good=False
        return render(request,'accounts/inactive.html',{'records':records,'id':member_id,'good':good,'items':len(records)})
    else:
        return HttpResponse("ERROR:PAGE NOT FOUND")

@login_required
def pending(request):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    member_role=Members.objects.get(email=email).role
    if member_role=='seller':
        records= Products.objects.filter(product_owner=member_id,product_status='pending')
        return render(request,'accounts/pending-approval.html',{'records':records,'items':len(records),'id':member_id})
    else:
        return HttpResponse("ERROR:PAGE NOT FOUND")


@login_required
def sold(request):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    member_role=Members.objects.get(email=email).role
    if member_role=='seller':
        records= Products.objects.filter(product_owner=member_id,product_status='sold')
        total=[]
        for record in records:
            total.append(record.product_current_price)
        if len(records)>0:
            totals=sum(total)
            max1=max(total)
            avg=sum(total)/len(total)

            good=True
        else:
            totals=0
            max1=0
            avg=0
            good=False
        return render(request,'accounts/sold-items.html',{'id':member_id,'items':len(records),'revenue':totals,'max':max1,'avg':avg,'records':records,'good':good})
    else:
        return HttpResponse("ERROR:PAGE NOT FOUND")

@login_required
def withdraw(request,product_id):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    member_role=Members.objects.get(email=email).role
    if member_role=='seller':
        product=Products.objects.get(product_id=product_id)
        product.product_status='inactive'
        product.save()
        return render(request,'accounts/pending-approval.html',{'id':member_id,'success':True})
    else:
        return HttpResponse("ERROR:PAGE NOT FOUND")

@login_required
def delete(request,product_id,token):
    user=request.user
    email=user.email
    member_id=Members.objects.get(email=email).member_id
    member_role=Members.objects.get(email=email).role
    if member_role=='seller':
        if token=='true':
            product=Products.objects.get(product_id=product_id)
            product.delete()
            return render(request,'accounts/live-auctions.html',{'id':member_id,'success':True})
        else:
            return render(request,'accounts/live-auctions.html',{'id':member_id,'confirm':True,'product_id':product_id})
    else:
        return HttpResponse("ERROR:PAGE NOT FOUND")

@login_required
def custom_logout(request):
    logout(request)
    return redirect('landing_page')







load_dotenv()
MODEL_NAME = "llama-3.1-8b-instant"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY=os.getenv('GROQ_API_KEY')


# ========================
# 🚀 SYSTEM PROMPT (UPDATED)
# ========================

SYSTEM_PROMPT = """
You are **BidMaster Bot** — an intelligent, friendly, and fully dedicated assistant
specialized for the BidMaster online auction platform.

Your Responsibilities:
• Help sellers create perfect product listings: titles, descriptions, starting price, and category guidance.  
• Assist bidders by explaining how to place bids, how the current price updates, bid increments, highest bidder logic, and auction deadlines.  
• Explain platform rules, policies, dispute process, safety tips, verification steps, and payment flow.  
• Provide guidance about bid history, number of bids, auction status, notifications, and winner selection (only if allowed by platform rules).  
• Answer all questions strictly related to bidding, auctions, buyers, sellers, product listing, pricing, and BidMaster features.  

Your Behavior:
• Always friendly, simple, and confidence-building.  
• Never give academic, unrelated, or off-topic information.  
• Never answer programming, study, exam, or irrelevant questions.  
• Stay strictly focused on BidMaster auction support.

Goal:
Make every BidMaster seller and bidder feel confident and well-guided throughout their auction experience.
"""


# ========================
# 🚀 API QUERY FUNCTION
# ========================

def query_groq(message, chat_history, max_tokens):

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add past messages
    for user_msg, bot_msg in chat_history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})

    # Add current message
    messages.append({"role": "user", "content": message})

    try:
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json={
                "model": MODEL_NAME,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": max_tokens,
            },
            timeout=20
        )
    except requests.exceptions.RequestException as e:
        return f"Network Error: {str(e)}"

    if response.status_code == 200:
        try:
            return response.json()["choices"][0]["message"]["content"]
        except Exception:
            return "Unexpected API response format."
    else:
        return f"Error {response.status_code}: {response.text}"


# ========================
# 🚀 PAGE RENDER VIEW
# ========================

@login_required
def chatbot_page(request):
    user = request.user
    email = user.email
    member_role = Members.objects.get(email=email).role
    if member_role == 'seller' or member_role == 'bidder':
        return render(request, "accounts/chatbot.html")
    else:
        return HttpResponse("Error: Page not found")


# ========================
# 🚀 CHATBOT API ENDPOINT
# ========================

@login_required
def chatbot_api(request):
    if request.method == "POST":

        data = json.loads(request.body.decode("utf-8"))
        message = data.get("message", "")
        category = data.get("category", "")
        max_tokens = int(data.get("max_tokens", 300))
        chat_history = data.get("history", [])

        # Ensure list format
        chat_history = [list(item) for item in chat_history]

        # Add category prefix only if present
        final_message = f"[{category}] {message}" if category else message

        reply = query_groq(final_message, chat_history, max_tokens)

        # Store conversation step
        chat_history.append([message, reply])

        return JsonResponse({"reply": reply, "history": chat_history})

    return JsonResponse({"error": "Invalid request"}, status=400)
