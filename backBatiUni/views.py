from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from backBatiUni.payment import PaymentManager
from backBatiUni.subscription import SubscriptionManager
from .models import *
from .modelData.buildDataBase import CreateNewDataBase
from .modelData.dataAccessor import DataAccessor
import json

class DefaultView(APIView):
  permission_classes = (IsAuthenticated,)

  @classmethod
  def myResponse (cls, json):
    json["timestamp"] = datetime.datetime.now().timestamp()
    return Response(json)

  def confirmToken(self, user):
    userProfile = UserProfile.objects.filter(userNameInternal=user)
    if userProfile:
      return not userProfile[0].token
    return False

class Data(DefaultView):
  def get(self, request):
    if 'action' in request.GET and self.confirmToken(request.user):
      currentUser = request.user
      action = request.GET["action"]
      if action == "getUserData": return DefaultView.myResponse(DataAccessor.getData("user", currentUser))
      elif action == "getEnterpriseDataFrom": return DefaultView.myResponse(DataAccessor.getEnterpriseDataFrom(request, currentUser))
      elif action == "deletePost": return DefaultView.myResponse(DataAccessor.deletePost(request.GET["id"]))
      elif action == "downloadFile": return DefaultView.myResponse(DataAccessor.downloadFile(request.GET["id"], currentUser))
      elif action == "deleteFile": return DefaultView.myResponse(DataAccessor.deleteFile(request.GET["id"], currentUser))
      elif action == "removeLabelForCompany": return DefaultView.myResponse(DataAccessor.removeLabelForCompany(request.GET["labelId"], currentUser))
      elif action == "handleCandidateForPost": return DefaultView.myResponse(DataAccessor.handleCandidateForPost(request.GET["Candidate"], request.GET["response"], currentUser))
      elif action == "blockCompany": return DefaultView.myResponse(DataAccessor.blockCompany(request.GET["companyId"], request.GET["status"], currentUser))
      elif action == "signContract": return DefaultView.myResponse(DataAccessor.signContract(request.GET["missionId"], request.GET["view"], currentUser))
      elif action == "switchDraft": return DefaultView.myResponse(DataAccessor.switchDraft(request.GET["id"], currentUser))
      elif action == "duplicatePost": return DefaultView.myResponse(DataAccessor.duplicatePost(request.GET["id"], currentUser))
      elif action == "candidateViewed": return DefaultView.myResponse(DataAccessor.candidateViewed(request.GET["candidateId"], currentUser))
      elif action == "applyPost": return DefaultView.myResponse(DataAccessor.applyPost(request.GET["Post"], request.GET["amount"] if "amount" in request.GET else 0.0, request.GET["devis"] if "devis" in request.GET else "Prix Total", currentUser))
      elif action == "setFavorite": return DefaultView.myResponse(DataAccessor.setFavorite(request.GET["Post"], request.GET["value"], currentUser))
      elif action == "isViewed": return DefaultView.myResponse(DataAccessor.isViewed(request.GET["Post"], currentUser))
      elif action == "inviteFriend": return DefaultView.myResponse(DataAccessor.inviteFriend(request.GET["mail"], request.GET["register"], request.GET["isParrain"], currentUser))
      elif action == "askRecommandation": return DefaultView.myResponse(DataAccessor.askRecommandation(request.GET["email"], currentUser, request.GET["view"]))
      elif action == "giveNotificationToken": return DefaultView.myResponse(DataAccessor.giveNotificationToken(request.GET["token"], currentUser))
      elif action == "unapplyPost": return DefaultView.myResponse(DataAccessor.unapplyPost(request.GET["postId"], request.GET["candidateId"], currentUser))
      return DefaultView.myResponse({"data GET":"Error", "messages":{"action":action}})
    return DefaultView.myResponse({"data GET":"Warning", "messages":"La confirmation par mail n'est pas réalisée."})

  def post(self, request):
    if self.confirmToken(request.user):
      currentUser = request.user
      jsonBin = request.body
      jsonString = jsonBin.decode("utf8")
      response = DataAccessor().dataPost(jsonString, currentUser)
      return DefaultView.myResponse(response)
    return DefaultView.myResponse ({"data POST":"Warning", "messages":"La confirmation par mail n'est pas réalisée."})

class Initialize(APIView):
  permission_classes = (AllowAny,)
  def get(self, request):
    if 'action' in request.GET:
      action = request.GET["action"]
      if action == "getGeneralData":
        return Response(DataAccessor().getData("general", False))
      elif action == "registerConfirm":
        return Response(DataAccessor().registerConfirm(request.GET["token"]))
      elif action == "getEnterpriseDataFrom": return Response(DataAccessor.getEnterpriseDataFrom(request))
      elif action == "forgetPassword": return Response(DataAccessor.forgetPassword(request.GET["email"]))
    return Response({"Initialize GET":"OK"})

  def post(self, request):
    jsonBin = request.body
    jsonString = jsonBin.decode("utf8")
    data = json.loads(jsonString)
    if "action" in data and data["action"] == "newPassword":  return Response(DataAccessor.newPassword(data))
    elif "action" in data and data["action"] == "giveRecommandation": return Response(DataAccessor.giveRecommandation(data))
    elif "action" in data and data["action"] == "register": return Response(DataAccessor().register(data))
    else: return Response({"Error":f"Action unknown"})

class CreateBase(DefaultView):
  def get(self, request):
    if 'action' in request.GET:
      action = request.GET["action"]
      if action == "reload":
        print("reload")
        return Response(CreateNewDataBase().reloadDataBase())
      if action == "emptyDB":
        return Response(CreateNewDataBase().emptyDataBase())
    return Response({"CreateBase GET":"Error"})

class Payment(DefaultView):
  def get(self, request):
    return Response({"Error": f"Not implemented yet"})

  def post(self, request):
    jsonBin = request.body
    jsonString = jsonBin.decode("utf8")
    data = json.loads(jsonString)
    userProfile = UserProfile.objects.get(userNameInternal=request.user)
    if "action" in data and self.confirmToken(request.user):
      if data["action"] == "createPaymentIntent":
        return Response(PaymentManager.createPaymentIntent(request))
    return Response({"Error": f"Action unknown"})

class Webhook(DefaultView):
  permission_classes = (AllowAny,)
  def get(self, request):
    return Response({"Error": f"Not implemented yet"}, status=400)

  def post(self, request):
    jsonBin = request.body
    jsonString = jsonBin.decode("utf8")
    event = json.loads(jsonString)
    # Handle the event
    if event:
      print("Webhook", event['type'])
      if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']  # contains a stripe.PaymentIntent
        if payment_intent["metadata"]["type"] == "boostPost":
          boostPostDict = {
            "action": "boostPost",
            "postId": int(payment_intent["metadata"]["post"]),
            "duration": int(payment_intent["metadata"]["duration"])
          }
          DataAccessor.dataPost(json.dumps(boostPostDict), False)
          return Response({"payment_intent.succeeded": "OK"})
      elif event['type'] ==  'customer.subscription.created':
        subscribeDict = {
          "action": "subscribeUser",
          "status": event['data']['object']['status'],
          "id": event['data']['object']['id'],
          "stripeCustomerId": event['data']['object']['customer']
        }
        DataAccessor.dataPost(json.dumps(subscribeDict), False)
        return Response({"Error": f"Not implemented yet"}, status=400)
      elif event['type'] ==  'customer.subscription.updated':
        updateSubscribeDict = {
          "action": "updateSubscribeUser",
          "status": event['data']['object']['status'],
          "id": event['data']['object']['id'],
          "stripeCustomerId": event['data']['object']['customer']
        }
        DataAccessor.dataPost(json.dumps(updateSubscribeDict), False)
        return Response({"Error": f"Not implemented yet"}, status=400)
      elif event['type'] ==  'customer.subscription.deleted':
        return Response({"Error": f"Not implemented yet"}, status=400)      
      else:
        # Unexpected event type
        print(f"Unhandled event type {event['type']}")

    return Response({"Error": "Not yet implemented"}, status=400)

class Subscription(DefaultView):
  def get(self, request):
    return Response({"Error": f"Not implemented yet"})

  def post(self, request):
    jsonBin = request.body
    jsonString = jsonBin.decode("utf8")
    data = json.loads(jsonString)

    if "action" in data and self.confirmToken(request.user):
      if data["action"] == "createSubscription":
        return Response(SubscriptionManager.createSubscription(request))
      if data["action"] == "cancelSubscription":
        return Response(SubscriptionManager.cancelSubscription(request))
      if data["action"] == "fetchPrice":
        return Response(SubscriptionManager.fetchPrice(request))
    return Response({"Error": f"Not implemented yet"})
