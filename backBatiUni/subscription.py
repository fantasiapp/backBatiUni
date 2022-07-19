import stripe
from backBatiUni.models import Company, UserProfile

from backBatiUni.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY

class SubscriptionManager():
    @classmethod
    def createSubscription(cls, request):
        userProfile = UserProfile.objects.get(userNameInternal = request.user)
        print("userProfile", userProfile.Company.id, type(userProfile.Company.id))
        company = Company.objects.get(id = userProfile.Company.id)
        customerId = company.stripeCustomerId

        priceId = request.data["priceId"]

        stripeProduct = stripe.Product.retrieve(request.data["product"])
        price = stripe.Price.retrieve(priceId)

        try:
            # Create the subscription. Note we're expanding the Subscription's
            # latest invoice and that invoice's payment_intent
            # so we can pass it to the front end to confirm the payment
            subscription = stripe.Subscription.create(
                customer=customerId,
                items=[{
                    'price': priceId,
                }],
                payment_behavior='default_incomplete',
                payment_settings={'save_default_payment_method': 'on_subscription'},
                expand=['latest_invoice.payment_intent'],
            )
            return {
                    "createSubscription": "OK",
                    "subscriptionId": subscription.id, 
                    "clientSecret": subscription.latest_invoice.payment_intent.client_secret,
                    "price": price.unit_amount,
                    "productName": stripeProduct.name,
                    
            }

        except Exception as e:
            return {"Error": str(e)}

    @classmethod
    def cancelSubscription(cls, request):
        try:
            deletedSubscription = stripe.Subscription.delete(request.susbscriptionId)

            return {
                "subscriptionId": deletedSubscription.id
            }
        except Exception as e:
            return {"Error": str(e)}

    @classmethod
    def fetchPrice(cls, request):
        print(request)
        try:
            prices = stripe.Price.list(
                active = True,
                product = request.data["product"]
            )
            return {
                "fetchPrices": "OK",
                "prices": prices
            }
        except Exception as e:
            return {"Error": str(e)}