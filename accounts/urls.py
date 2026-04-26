from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing,name='landing_page'),
    path('login', views.custom_login,name='login'),
    path('signup', views.signup,name='signup'),
    path('decision', views.decision,name='decision'),
    path('new_auction', views.new_auction,name='new_auction'),
    path('live', views.live,name='live'),
    path('inactive', views.inactive,name='inactive'),
    path('pending', views.pending,name='pending'),
    path('sold', views.sold,name='sold'),
    path('withdraw/<int:product_id>', views.withdraw,name='withdraw'),
    path('delete/<int:product_id>/<str:token>', views.delete,name='delete'),
    path('custom_logout',views.custom_logout,name='custom_logout'),
    
    path('live_to_show/<str:category>', views.live_to_show,name='live_to_show'),
    path('winnings', views.winnings,name='winnings'),
    path('categories', views.categories,name='categories'),
    path('show_details/<int:product_id>', views.show_details,name='show_details'),
    path('bidder_messages', views.bidder_messages,name='bidder_messages'),
    path('time_up/<int:product_id>', views.time_up,name='time_up'),



    path('all_pendings', views.all_pendings,name='all_pendings'),
    path('all_lives', views.all_live,name='all_live'),
    path('all_solds', views.all_solds,name='all_solds'),
    path('all_inactives', views.all_inactives,name='all_inactives'),
    path("update-status/<int:product_id>", views.update_status, name="update_status"),
    path("inactivate-status/<int:product_id>", views.inactivate_status, name="inactivate_status"),
    path("all_sellers", views.all_sellers, name="all_sellers"),
    path("all_bidders", views.all_bidders, name="all_bidders"),
    
    path("chatbot/api/", views.chatbot_api, name="chatbot_api"),
    path("chatbot", views.chatbot_page, name="chatbot_page"),
    

]
