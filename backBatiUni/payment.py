import json
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from requests import Response
import stripe

stripe.api_key = 'sk_test_51LDlcoAdZaSfQS2Y5oVOhfGwVMRtAs70kWfaqJOUcSqaQPrbkbtPLnHizh3mdZfxKoVYcxYALiisIDXP6uxsC4sK00wVLBWBXH'

class PaymentManager():
    @classmethod
    def createPaymentIntent(cls, request):

        customer = stripe.Customer.create()
        
        def computeTotalAmount(itemList = {}):
            return 1000

        try:
            print("payment data", request.data)

            # Create a PaymentIntent with the order amount and currency
            intent = stripe.PaymentIntent.create(
                customer = customer["id"],
                setup_future_usage = "off_session",
                amount=computeTotalAmount(),
                currency='eur',
                automatic_payment_methods={
                'enabled': True,
                },
            )
            return {"CreatePaylentIntent":"OK", "clientSecret": intent["client_secret"]}
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