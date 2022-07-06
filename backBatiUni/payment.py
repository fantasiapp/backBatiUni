import json
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from requests import Response
import stripe
from backBatiUni.models import Company, UserProfile

from backBatiUni.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY

class PaymentManager():
    @classmethod
    def createPaymentIntent(cls, request):
        userProfile = UserProfile.objects.get(userNameInternal = request.user)
        print("userProfile", userProfile.Company.id, type(userProfile.Company.id))
        company = Company.objects.get(id = userProfile.Company.id)
        customerId = company.stripeCustomerId

        try:
            print("payment data", request.data)

            stripeProduct = stripe.Product.retrieve(request.data["product"])
            price = stripe.Price.retrieve(stripeProduct.default_price)

            print("amount", price.amount)
            # Create a PaymentIntent with the order amount and currency
            intent = stripe.PaymentIntent.create(
                customer = customerId,
                setup_future_usage = "off_session",
                amount=price.amount,
                currency='eur',
                automatic_payment_methods={
                'enabled': True,
                },
            )
            return {
                    "createPaymentIntent":"OK", 
                    "clientSecret": intent["client_secret"], 
                    "price": intent["price"],
                    "productName": stripeProduct.name
                    }
        except Exception as e:
            return {"Error": str(e)}
    
    @classmethod
    def createPaymentCheckout(cls, request):
        # Will not be used 
        try:
            print("checkout")

            checkout_session = stripe.checkout.Session.create(
                line_items = [
                    {
                        'price': "price_1LDlpRAdZaSfQS2YNV1as9tx",
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url= "http://localhost:4200/home",
                cancel_url = "http://localhost:4200/profile"
            )

        except Exception as e:
            return {"Error": str(e)}
        
        print("Redirect to", checkout_session.url)

        return {"checkoutUrl": checkout_session.url}