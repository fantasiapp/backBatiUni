from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import *
from .modelData.buildDataBase import CreateNewDataBase
from .modelData.dataAccessor import DataAccessor
import json

class DefaultView(APIView):
  permission_classes = (IsAuthenticated,)

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
      if action == "getUserData": return Response(DataAccessor.getData("user", currentUser))
      elif action == "getEnterpriseDataFrom": return Response(DataAccessor.getEnterpriseDataFrom(request, currentUser))
      elif action == "deletePost": return Response(DataAccessor.deletePost(request.GET["id"]))
      elif action == "downloadFile": return Response(DataAccessor.downloadFile(request.GET["id"], currentUser))
      elif action == "deleteFile": return Response(DataAccessor.deleteFile(request.GET["id"]))
      elif action == "getPost": return Response(DataAccessor.getPost(currentUser))
      elif action == "handleCandidateForPost": return Response(DataAccessor.handleCandidateForPost(request.GET["Candidate"], request.GET["response"], currentUser))
      elif action == "signContract": return Response(DataAccessor.signContract(request.GET["missionId"], request.GET["view"], currentUser))
      elif action == "switchDraft": return Response(DataAccessor.switchDraft(request.GET["id"], currentUser))
      elif action == "duplicatePost": return Response(DataAccessor.duplicatePost(request.GET["id"], currentUser))
      elif action == "candidateViewed": return Response(DataAccessor.candidateViewed(request.GET["candidateId"], currentUser))
      elif action == "applyPost": return Response(DataAccessor.applyPost(request.GET["Post"], request.GET["amount"] if "amount" in request.GET else 0.0, request.GET["devis"] if "devis" in request.GET else "Prix Total", currentUser))
      elif action == "setFavorite": return Response(DataAccessor.setFavorite(request.GET["Post"], request.GET["value"], currentUser))
      elif action == "isViewed": return Response(DataAccessor.isViewed(request.GET["Post"], currentUser))
      elif action == "inviteFriend": return Response(DataAccessor.inviteFriend(request.GET["mail"], currentUser))
      return Response({"data GET":"Error", "messages":{"action":action}})
    return Response({"data GET":"Warning", "messages":"La confirmation par mail n'est pas réalisée."})

  def post(self, request):
    if self.confirmToken(request.user):
      currentUser = request.user
      jsonBin = request.body
      jsonString = jsonBin.decode("utf8")
      response = DataAccessor().dataPost(jsonString, currentUser)
      print("post response", response)
      return Response(response)
    return Response ({"data POST":"Warning", "messages":"La confirmation par mail n'est pas réalisée."})

class Initialize(APIView):
  permission_classes = (AllowAny,)
  def get(self, request):
    if 'action' in request.GET:
      action = request.GET["action"]
      print("initialize action", action)
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
    return Response(DataAccessor().register(data))

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
