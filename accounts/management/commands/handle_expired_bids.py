from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import Products,Members,Messages
from django.core.mail import send_mail


class Command(BaseCommand):
    help = "Update product status after end_time"

    def handle(self, *args, **kwargs):
        now = timezone.now()

        expired_products = Products.objects.filter(product_status="live", product_end_date__lt=now)

        updated_count = 0
        for product in expired_products:
            if product.product_current_price < product.product_mid_price or product.product_bids_count==0:
                product.product_status = "inactive"
                product.save()
                msg=Messages(seller_id=product.product_owner,message_head='Product Inactivated',message=f'your product named {product.product_name} has been inactivated because of no suitable bid',type='inactive')
                msg.save()
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

            
            updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"{updated_count} products updated"))
