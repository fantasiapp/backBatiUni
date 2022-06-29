import json
from requests import Response
import stripe

stripe.api_key = 'sk_test_51LDlcoAdZaSfQS2Y5oVOhfGwVMRtAs70kWfaqJOUcSqaQPrbkbtPLnHizh3mdZfxKoVYcxYALiisIDXP6uxsC4sK00wVLBWBXH'

class Payment():
    @classmethod
    def createPaymentIntent(cls, request):
        try:
            print("payment data", request.data)

            # Create a PaymentIntent with the order amount and currency
            intent = stripe.PaymentIntent.create(
                amount=1,
                currency='eur',
                automatic_payment_methods={
                'enabled': True,
                },
            )
            return Response({"Payment":"OK", "clientSecret": intent["client_secret"]})
        except Exception as e:
            return Response({"Error": str(e)})
