from lib2to3.pgen2 import token
from django.forms import EmailInput
from ..models import *
from django.contrib.auth.models import User
from django.utils import timezone
from django.apps import apps
import sys
import os
import shutil
from datetime import datetime
import base64
from django.core.files.base import ContentFile
from ..smtpConnector import SmtpConnector
import json
import secrets

from dotenv import load_dotenv

load_dotenv()
if os.getenv('PATH_MIDDLE'):
  sys.path.append(os.getenv('PATH_MIDDLE'))
  from profileScraping import getEnterpriseDataFrom
  from geocoding import getCoordinatesFrom # argument str address


class DataAccessor():
  loadTables = {"user":[UserProfile, Company, JobForCompany, LabelForCompany, File, Post, Candidate, DetailedPost, DatePost, Mission, Disponibility, Supervision, Notification], "general":[Job, Role, Label]}
  dictTable = {}
  portSmtp = os.getenv('PORT_SMTP')

  @classmethod
  def getData(cls, profile, user):
    if not UserProfile.objects.filter(userNameInternal=user) and profile == "user":
      {"register":"Error", "messages":"currentUser does not exist"} 
    dictAnswer = {"currentUser":UserProfile.objects.get(userNameInternal=user).id} if profile == "user" else {}
    for table in cls.loadTables[profile]:
      dictAnswer.update(table.dumpStructure(user))
    with open(f"./backBatiUni/modelData/{profile}Data.json", 'w') as jsonFile:
      json.dump(dictAnswer, jsonFile, indent = 3)
    return dictAnswer

  @classmethod
  def register(cls, data):
    message = cls.__registerCheck(data, {})
    if message:
      return {"register":"Warning", "messages":message}
    token = SmtpConnector(cls.portSmtp).register(data["firstname"], data["lastname"], data["email"])
    if token != "token not received" or data["email"] == "jeanluc":
      userProfile = cls.__registerAction(data, token)
      cls.__checkIfHaveBeenInvited(userProfile, data['proposer'], data['email'])
      return {"register":"OK"}
    cls.__registerAction(data, "empty token")
    return {"register":"Error", "messages":"token not received"} 

  @classmethod
  def __checkIfHaveBeenInvited(cls, userProfile, tokenReceived, emailReceived):
    inviteFriend =  None
    if InviteFriend.objects.filter(emailTarget=emailReceived):
      inviteFriend = InviteFriend.objects.get(emailTarget=emailReceived)
    elif InviteFriend.objects.filter(token=tokenReceived):
      inviteFriend = InviteFriend.objects.get(token=tokenReceived)
    if inviteFriend:
      inviteFriend.invitedUser = userProfile
      inviteFriend.date = timezone.now()
      inviteFriend.save()


  @classmethod
  def __registerCheck(cls, data, message):
    if not data["firstname"]:
      message["firstname"] = "Le prénom est un champ obligatoire."
    if not data["lastname"]:
      message["lastname"] = "Le nom est un champ obligatoire."
    if not data["email"]:
      message["email"] = "L'adresse e-mail est un champ obligatoire."
    if not data["password"]:
      message["password"] = "Le mot de passe est un champ obligatoire."
    if not data["company"]:
      message["company"] = "Le nom de l'entreprise est un champ obligatoire."
    userProfile = UserProfile.objects.filter(email=data["email"])
    if userProfile or User.objects.filter(username=data["email"]):
      userProfile = userProfile[0]
      if userProfile.password:
        userProfile.delete()
      else:
        message["email"] = "Cet email et déjà utilisé."
    companyData = data['company']
    company = Company.objects.filter(name=companyData['name'])
    if company:
      message["company"] = "Le nom de l'entreprise est déjà utilisé."
    return message

  @classmethod
  def __registerAction(cls, data, token):
    print("registerAction", data)
    companyData = data['company']
    company = Company.objects.create(name=companyData['name'], address=companyData['address'], activity=companyData['activity'], ntva=companyData['ntva'], siret=companyData['siret'])
    cls.__getGeoCoordinates(company)
    company.Role = Role.objects.get(id=data['Role'])
    company.save()
    proposer = None
    if data['proposer'] and User.objects.get(id=data['proposer']):
      proposer = User.objects.get(id=data['proposer'])
    userProfile = UserProfile.objects.create(Company=company, firstName=data['firstname'], lastName=data['lastname'], proposer=proposer, token=token, email=data["email"], password=data["password"])
    if 'jobs' in data:
      for idJob in data['jobs']:
        job = Job.objects.get(id=idJob)
        jobCompany = JobForCompany.objects.filter(Job=job, Company=company)
        if not jobCompany:
          JobForCompany.objects.create(Job=job, Company=company, number=1)
    userProfile.save()
    return userProfile

  @classmethod
  def registerConfirm(cls, token):
    for user in UserProfile.objects.all():
      if user.token:
        print("user pending", user.token)
    userProfile = UserProfile.objects.filter(token=token)
    if userProfile:
      userProfile = userProfile[0]
      user = User.objects.create(username=userProfile.email, email=userProfile.email)
      user.set_password(userProfile.password)
      user.save()
      userProfile.userNameInternal = user
      userProfile.token = None
      userProfile.password = None
      userProfile.save()

      inviteFriend =  InviteFriend.objects.filter(invitedUser=userProfile)
      if inviteFriend:
        company = inviteFriend[0].invitationAuthor.Company
        role = "ST" if company.Role.id == 2 else "PME"
        Notification.objects.create(Company=company, nature="alert", Role=role, content=f"{userProfile.firstName} {userProfile.lastName} de la société {userProfile.Company.name} s'est inscrit sur BatiUni. Vous êtes son parrain.", timestamp=datetime.now().timestamp())
        Notification.objects.create(Company=userProfile.Company, nature="alert", Role=role, content=f"{userProfile.firstName} {userProfile.lastName} de la société {userProfile.Company.name} s'est inscrit sur BatiUni. Vous êtes son parrain.", timestamp=datetime.now().timestamp())
      return {"registerConfirm":"OK"}
    return {"registerConfirm":"Error", "messages":"wrong token or email"}


  @classmethod
  def dataPost(cls, jsonString, currentUser):
    data = json.loads(jsonString)
    if "action" in data:
      if data["action"] == "modifyPwd": return cls.__modifyPwd(data, currentUser)
      elif data["action"] == "modifyUser": return cls.__updateUserInfo(data, currentUser)
      elif data["action"] == "changeUserImage": return cls.__changeUserImage(data, currentUser)
      elif data["action"] == "uploadPost": return cls.__uploadPost(data, currentUser)
      elif data["action"] == "modifyPost": return cls.__modifyPost(data, currentUser)
      elif data["action"] == "createDetailedPost": return cls.__createDetailedPost(data, currentUser)
      elif data["action"] == "modifyDetailedPost": return cls.__modifyDetailedPost(data, currentUser)
      elif data["action"] == "deleteDetailedPost": return cls.__deleteDetailedPost(data, currentUser)
      elif data["action"] == "createSupervision": return cls.__createSupervision(data, currentUser)
      elif data["action"] == "modifySupervision": return cls.__modifySupervision(data, currentUser)
      elif data["action"] == "deleteSupervision": return cls.__deleteSupervision(data, currentUser)
      elif data["action"] == "uploadFile": return cls.__uploadFile(data, currentUser)
      elif data["action"] == "modifyDisponibility": return cls.__modifyDisponibility(data["disponibility"], currentUser)
      elif data["action"] == "uploadImageSupervision": return cls.__uploadImageSupervision(data, currentUser)
      elif data["action"] == "modifyMissionDate": return cls.__modifyMissionDate(data, currentUser)
      elif data["action"] == "validateMissionDate": return cls.__validateMissionDate(data, currentUser)
      elif data["action"] == "closeMission": return cls.__closeMission(data, currentUser)
      elif data["action"] == "closeMissionST": return cls.__closeMissionST(data, currentUser)
      elif data["action"] == "notificationViewed": return cls.__notificationViewed(data, currentUser)
      return {"dataPost":"Error", "messages":f"unknown action in post {data['action']}"}
    return {"dataPost":"Error", "messages":"no action in post"}

  @classmethod
  def __changeUserImage(cls, dictData, currentUser):
    fileStr = dictData["imageBase64"]
    if not dictData["name"]:
      return {"changeUserImage":"Error", "messages":"field name is empty"}
    objectFile = File.createFile("userImage", dictData["name"], dictData['ext'], currentUser)
    file = ContentFile(base64.b64decode(fileStr), name=objectFile.path + dictData['ext'])
    with open(objectFile.path, "wb") as outfile:
        outfile.write(file.file.getbuffer())
    return {"changeUserImage":"OK", objectFile.id:objectFile.computeValues(objectFile.listFields(), currentUser, True)}

  @classmethod
  def __uploadPost(cls, dictData, currentUser):
    kwargs, listObject = cls.__createPostKwargs(dictData, currentUser)
    print("uploadPost", kwargs)
    if "uploadPost" in kwargs and kwargs["uploadPost"] == "Error":
      return kwargs
    objectPost = Post.objects.create(**kwargs)
    cls.__getGeoCoordinates(objectPost)
    if listObject:
      for subObject in listObject:
        subObject.Post = objectPost
        subObject.save()
    return {"uploadPost":"OK", objectPost.id:objectPost.computeValues(objectPost.listFields(), currentUser, True)}

  @classmethod
  def __getGeoCoordinates(cls, objectPost):
    if os.getenv('PATH_MIDDLE'):
      dictCoord = getCoordinatesFrom(objectPost.address)
      if dictCoord["getCoordinatesFrom"] == "OK":
        objectPost.address = dictCoord["address"]
        objectPost.latitude = dictCoord["latitude"]
        objectPost.longitude = dictCoord["longitude"]
        objectPost.save()
        return
    objectPost.latitude = 0.0
    objectPost.longitude = 0.0

  @classmethod
  def __createPostKwargs(cls, dictData, currentUser):
    print("dictData", dictData)
    userProfile = UserProfile.objects.get(userNameInternal=currentUser)
    kwargs, listFields, listObject = {"Company":userProfile.Company, "startDate":None, "endDate":None, "subContractorName":None}, Post.listFields(), []
    for fieldName, value in dictData.items():
      fieldObject = None
      try:
        fieldObject = Post._meta.get_field(fieldName)
      except:
        fieldObject = None
      if fieldName in listFields:
        if fieldObject and isinstance(fieldObject, models.ForeignKey):
          foreign = Post._meta.get_field(fieldName).remote_field.model
          objectForeign = foreign.objects.filter(id=value)
          if objectForeign:
            kwargs[fieldName]=objectForeign[0]
          else:
            return {"uploadPost":"Error", "messages":{fieldName:"is not documented"}}, False
        if fieldObject and isinstance(fieldObject, models.DateField):
          date = datetime.strptime(dictData[fieldName], "%Y-%m-%d") if dictData[fieldName] else None
          kwargs[fieldName]=date
        if fieldObject and isinstance(fieldObject, models.IntegerField):
          kwargs[fieldName]=int(dictData[fieldName]) if dictData[fieldName] else 0
        if fieldObject and isinstance(fieldObject, models.FloatField):
          kwargs[fieldName]=float(dictData[fieldName]) if dictData[fieldName] else 0.0
        if fieldObject and isinstance(fieldObject, models.BooleanField) or isinstance(fieldObject, models.CharField) :
          kwargs[fieldName]= dictData[fieldName]
        if fieldName in Post.manyToManyObject:
          modelObject = apps.get_model(app_label='backBatiUni', model_name=fieldName)
          for content in value:
            print("pb", content, fieldName)
            if fieldName == "DatePost":
              cls.__computeStartEndDate(kwargs, content)
              listObject.append(modelObject.objects.create(date=content))
            else:
              listObject.append(modelObject.objects.create(content=content))
    kwargs["contactName"] = f"{userProfile.firstName} {userProfile.lastName}"
    return kwargs, listObject


  @classmethod
  def __computeStartEndDate(cls, limitDate, strDate):
    date = datetime.strptime(strDate, "%Y-%m-%d")
    if not limitDate["startDate"] or limitDate["startDate"] > date:
      limitDate["startDate"] = date
    if not limitDate["endDate"] or limitDate["endDate"] < date:
      limitDate["endDate"] = date
    


  @classmethod
  def __modifyPost(cls, dictData, currentUser):
    post = Post.objects.filter(id=dictData["id"])
    if post:
      post = post[0]
      DatePost.objects.filter(Post=post).delete()
      kwargs, listObject = cls.__createPostKwargs(dictData, currentUser)
      for key, value in kwargs.items():
        if getattr(post, key, "empty field") != "empty field" and getattr(post, key, "empty field") != value:
          setattr(post, key, value)
          if key == "address":
            cls.__getGeoCoordinates(post)
      post.save()
      if listObject:
        for subObject in listObject:
          subObject.Post = post
          subObject.save()
      if dictData["DetailedPost"]:
        DetailedPost.objects.filter(Post=post).delete()
        for content in dictData["DetailedPost"]:
          DetailedPost.objects.create(Post=post, content=content)
      return {"modifyPost":"OK", post.id:post.computeValues(post.listFields(), currentUser, True)}
    return {"modifyPost":"Error", "messages":f"{dictData['id']} is not a Post id"}

  @classmethod
  def applyPost(cls, postId, amount, unitOfTime, currentUser):
    userProfile = UserProfile.objects.get(userNameInternal=currentUser)
    subContractor = userProfile.Company
    contact = userProfile.firstName + " " + userProfile.lastName
    post = Post.objects.get(id=postId)
    company = post.Company
    if subContractor == company:
      return {"applyPost":"Warning", "messages":f"Le sous-traitant {subContractor.name} ne peut pas être l'entreprise commanditaire."}
    if subContractor.Role.id == 1:
      return {"applyPost":"Warning", "messages":f"La société {subContractor.name} n'est pas sous-traitante."}
   # tce = Job.objects.get(name= "TCE (Tout Corps d'Etat)")
    # if not(post.Job in subContractor.jobs or subContractor.allQualifications):
    #   return {"applyPost":"Warning", "messages":f"Le métier {post.Job.name} n'est pas une compétence du sous-traitant {subContractor.name}."}
    exists = Candidate.objects.filter(Post=post, Company=subContractor)
    if exists:
      return {"applyPost":"Warning", "messages":f"Le sous-traitant {subContractor.name} a déjà postulé."}
    candidate = Candidate.objects.create(Post=post, Company=subContractor, amount=amount, contact=contact, unitOfTime=unitOfTime)
    Notification.objects.create(Post=post, Company=company, subContractor=subContractor, nature="ST", Role="PME", content=f"Un nouveau sous traitant : {subContractor.name} pour le chantier du {post.address} a postulé.", timestamp=datetime.now().timestamp())
    return {"applyPost":"OK", candidate.id:candidate.computeValues(candidate.listFields(), currentUser, True)}


  @classmethod
  def candidateViewed(cls, candidateId, currentUser):
    print("candidateViewed", candidateId)
    candidate = Candidate.objects.get(id=candidateId)
    candidate.isViewed = True
    candidate.save()
    post = candidate.Post
    return {"candidateViewed":"OK", post.id:post.computeValues(post.listFields(), currentUser, True)}



  @classmethod
  def __createDetailedPost(cls, data, currentUser):
    kwargs, post, mission = {"Post":None, "Mission":None, "content":None, "date":None, "validated":False}, None, None
    if "postId" in data:
      post = Post.objects.get(id=data["postId"])
      kwargs["Post"] = post
    if "missionId" in data:
      mission = Mission.objects.get(id=data["missionId"])
      kwargs["Mission"] = mission
    if "content" in data:
      kwargs["content"] = data["content"]
    if "date" in data:
      kwargs["date"] = datetime.strptime(data["date"], "%Y-%m-%d")
    if "validated" in data:
      kwargs["validated"] = data["validated"]
    detailedPost = DetailedPost.objects.create(**kwargs)
    if detailedPost:
      if post:
        return {"createDetailedPost":"OK", post.id:post.computeValues(post.listFields(), currentUser, True)}
      if mission:
        return {"createDetailedPost":"OK", mission.id:mission.computeValues(mission.listFields(), currentUser, True)}
    return {"createDetailedPost":"Warning", "messages":"La tâche n'a pas été créée"}

  @classmethod
  def __modifyDetailedPost(cls, data, currentUser):
    print("modifyDetailedPost", data)
    data = data["detailedPost"]
    # return {"modifyDetailedPost":"OK", "d":["a", "b", "c"]}
    detailedPost = DetailedPost.objects.filter(id=data["id"])
    if detailedPost:
      detailedPost = detailedPost[0]
      if "date" in data and data["date"]:
        date = datetime.strptime(data["date"], "%Y-%m-%d")
        dateNowString = detailedPost.date.strftime("%Y-%m-%d") if detailedPost.date else None
        if dateNowString != data["date"] and dateNowString:
          detailedPost = DetailedPost.objects.create(Post=detailedPost.Post, Mission=detailedPost.Mission, content=detailedPost.content, date=date, validated=detailedPost.validated)
          if detailedPost:
            PorM = detailedPost.Post if detailedPost.Post else detailedPost.Mission
            return {"modifyDetailedPost":"OK", PorM.id:PorM.computeValues(PorM.listFields(), currentUser, True)}
        else:
          detailedPost.date = date
      for field in ["content", "validated", "refused"]:
        if field in data:
          setattr(detailedPost, field, data[field])
      detailedPost.save()
      PorM = detailedPost.Post if detailedPost.Post else detailedPost.Mission
      dumpPorM = PorM.computeValues(PorM.listFields(), currentUser, True)
      return {"modifyDetailedPost":"OK", PorM.id:dumpPorM}
    return {"modifyDetailedPost":"Error", "messages":f"No Detailed Post with id {data['id']}"}

  @classmethod
  def __deleteDetailedPost(cls, data, currentUser):
    detailedPost = DetailedPost.objects.filter(id=data["detailedPostId"])
    if detailedPost:
      detailedPost = detailedPost[0]
      post, mission = detailedPost.Post, detailedPost.Mission
      Supervision.objects.filter(DetailedPost=detailedPost).delete()
      detailedPost.delete()
      if post:
        return {"deleteDetailedPost":"OK", post.id:post.computeValues(post.listFields(), currentUser, True)}
      if mission:
        return {"deleteDetailedPost":"OK", mission.id:mission.computeValues(mission.listFields(), currentUser, True)}
    return {"deleteDetailedPost":"Error", "messages":f"No Detailed Post with id {data['detailedPost']['id']}"}

  @classmethod
  def __createSupervision(cls, data, currentUser):
    print("createSupervision", data, currentUser.id)
    userProfile = UserProfile.objects.get(userNameInternal=currentUser)
    author = f'{userProfile.firstName} {userProfile.lastName}'
    kwargs, mission = {"DetailedPost":None, "author":author, "companyId":userProfile.Company.id,"comment":""}, None
    if "missionId" in data and data["missionId"]:
      mission = Mission.objects.get(id=data["missionId"])
      kwargs["Mission"] = mission
    if "detailedPostId" in data and data["detailedPostId"]:
      detailedPost = DetailedPost.objects.get(id=data["detailedPostId"])
      mission = detailedPost.Mission
      kwargs["DetailedPost"] = detailedPost
    if "parentId" in data and data["parentId"]:
      parentSupervision = Supervision.objects.get(id=data["parentId"]) 
      kwargs["parentId"] = parentSupervision
    if "comment" in data:
      kwargs["comment"] = data["comment"]
    if "date" in data and data["date"]:
      kwargs["date"] = datetime.strptime(data["date"], "%Y-%m-%d")
    print('createSupervision kwargs', kwargs)
    supervision = Supervision.objects.create(**kwargs)
    if supervision:
      return {"createSupervision":"OK", mission.id:mission.computeValues(mission.listFields(), currentUser, True)}
    return {"createSupervision":"Warning", "messages":"La supervision n'a pas été créée"}

  @classmethod

  @classmethod
  def __modifySupervision(cls, data, currentUser):
    print("modifySupervision", data, currentUser.id)
    return {"modifySupervision":"Warning", "messages":"Work in progress"}

  @classmethod
  def __deleteSupervision(cls, data, currentUser):
    print("deleteSupervision", data, currentUser.id)
    supervision = Supervision.objects.get(id=data["supervisionId"])
    if supervision.SupervisionAssociated:
      return {"deleteSupervision":"Warning", "messages":"Ce post possède des messages associés"}
    files = File.objects.filter(Supervision=supervision)
    for file in files:
      file.delete()
    mission = supervision.Mission
    supervision.delete()
    return {"deleteSupervision":"OK", mission.id:mission.computeValues(mission.listFields(), currentUser, True)}


  @classmethod
  def setFavorite(cls, postId, value, currentUser):
    userProfile = UserProfile.objects.get(userNameInternal=currentUser)
    favorite = FavoritePost.objects.filter(UserProfile=userProfile, postId=postId)
    if favorite and value == "false":
        favorite[0].delete()
    elif value == "true" and not favorite:
      FavoritePost.objects.create(UserProfile=userProfile, postId=postId)
    return {"setFavorite":"OK"}

  @classmethod
  def isViewed(cls, postId, currentUser):
    userProfile = UserProfile.objects.get(userNameInternal=currentUser)
    viewPost = ViewPost.objects.filter(UserProfile=userProfile, postId=postId)
    if not viewPost:
      ViewPost.objects.create(UserProfile=userProfile, postId=postId)
    return {"isViewed":"OK"}

  @classmethod
  def getPost(cls, currentUser):
    return {objectPost.id:objectPost.computeValues(objectPost.listFields(), currentUser, dictFormat=True) for objectPost in Post.objects.all()}

  @classmethod
  def deletePost(cls, id):
    post = Post.objects.filter(id=id)
    if post:
      for detail in DetailedPost.objects.filter(Post=post[0]):
        detail.delete()
      for file in File.objects.filter(Post=post[0]):
        file.delete()
        
      post.delete()
      return {"deletePost":"OK", "id":id}
    return {"deletePost":"Error", "messages":f"{id} does not exist"}

  @classmethod
  def handleCandidateForPost(cls, candidateId, status, currentUser):
    candidate = Candidate.objects.get(id=candidateId)
    if candidate.Mission:
      return {"handleCandidateForPost":"Error", "messages":f"The post of id {candidate.Mission.id} is allready a mission"}
    postId = candidate.Post.id
    if status == "true": candidate.isChoosen = True
    if status == "false": candidate.isRefused = True
    if candidate.isChoosen:
      candidate.Post = None
      candidate.Mission = Mission.objects.get(id=postId)
      candidate.date = timezone.now()
      candidate.save()
      mission = candidate.Mission
      for model in [DetailedPost, File, Notification]:
        for modelObject in model.objects.all():
          if modelObject.Post and modelObject.Post.id == postId:
            modelObject.Post = None
            modelObject.Mission = mission
            modelObject.save()
      contractImage = cls.createContract(candidate.Mission, currentUser)
      candidate.Mission.subContractorName = candidate.Company.name
      candidate.Mission.subContractorContact = candidate.contact
      candidate.Mission.contract = contractImage.id
      if candidate.Mission.counterOffer:
        candidate.Mission.amount = candidate.amount
      cls.__updateDatePost(candidate.Mission)
      candidate.Mission.save()
      Notification.objects.create(Mission=candidate.Mission, nature="PME", Company=candidate.Company, Role="ST", content=f"Votre candidature pour le chantier du {candidate.Mission.address} a été retenue.", timestamp=datetime.now().timestamp())
      response = mission.computeValues(mission.listFields(), currentUser, dictFormat=True)
      print("handleCandidateForPost", response[39], len(response))
      return {"handleCandidateForPost":"OK", mission.id:mission.computeValues(mission.listFields(), currentUser, dictFormat=True)}
    candidate.save()
    Notification.objects.create(Post=candidate.Post, nature="PME", Company=candidate.Company, Role="ST", content=f"Votre candidature pour le chantier du {candidate.Post.address} n'a pas été retenue.", timestamp=datetime.now().timestamp())
    post = candidate.Post
    return {"handleCandidateForPost":"OK", post.id:post.computeValues(post.listFields(), currentUser, dictFormat=True)}


  @classmethod
  def __updateDatePost(cls, mission):
    listdatePost = DatePost.objects.filter(Post=mission)
    for datePost in listdatePost:
      datePost.Post = None
      datePost.Mission = mission
      datePost.save()



  @classmethod
  def createContract(cls, mission, user):
    contractImage = File.createFile("contract", "contract", "png", user, post=mission)
    source = "./files/documents/contractUnsigned.png"
    dest = contractImage.path
    shutil.copy2(source, dest)
    return contractImage

  @classmethod
  def signContract(cls, missionId, view, currentUser):
    mission = Mission.objects.get(id=missionId)
    contractImage = File.objects.get(id=mission.contract)
    if view == "PME":
      source = "./files/documents/ContractSignedST_PME.png" if mission.signedBySubContractor else "./files/documents/ContractSignedPME.png"
    else:
      source = "./files/documents/ContractSignedST_PME.png" if mission.signedByCompany else "./files/documents/ContractSignedST.png"
    dest = contractImage.path
    shutil.copy2(source, dest)
    contractImage.timestamp = datetime.now().timestamp()
    contractImage.save()
    candidate = Candidate.objects.get(Mission=mission, isChoosen=True)
    if view == "PME" :
      Notification.objects.create(Mission=mission, nature="PME", Company=candidate.Company, Role="ST", content=f"Le contrat pour le chantier du {mission.address}  a été signé.", timestamp=datetime.now().timestamp())
      mission.signedByCompany = True
    else:
      Notification.objects.create(Mission=mission, subContractor=candidate.Company, nature="ST", Company=mission.Company, Role="PME", content=f"Le contrat pour le chantier du {mission.address}  a été signé.", timestamp=datetime.now().timestamp())
      mission.signedBySubContractor = True
    mission.save()
    return {"signContract":"OK", mission.id:mission.computeValues(mission.listFields(), currentUser, dictFormat=True)}

  @classmethod
  def uploadSupervision(cls, detailedPostId, comment, currentUser):
    print("uploadSupervision", detailedPostId, comment, currentUser)
    detailed = DetailedPost.objects.get(id=detailedPostId)
    userProfile = UserProfile.objects.get(userNameInternal=currentUser)
    if detailed.Post:
      return {"uploadSuperVision":"Error", "messages":"associated Post is not a mission"}
    supervision = Supervision.objects.create(DetailedPost=detailed, UserProfile=userProfile, comment=comment)
    return {"uploadSupervision":"OK", supervision.id:supervision.computeValues(supervision.listFields(), currentUser, dictFormat=True)}

  @classmethod
  def switchDraft(cls, id, currentUser):
    company = UserProfile.objects.get(userNameInternal=currentUser).Company
    post = Post.objects.filter(id=id)
    if post:
      post = post[0]
      if company == post.Company:
        post.draft = not post.draft
        post.save()
        return {"switchDraft":"OK", post.id:post.computeValues(post.listFields(), currentUser, dictFormat=True)}
      return {"switchDraft":"Error", "messages":f"{currentUser.username} does not belongs to {company.name}"}
    return {"switchDraft":"Error", "messages":f"{id} does not exist"}

  @classmethod
  def __modifyMissionDate(cls, data, currentUser):
    print("modifyMissionDate", data)
    mission, subContractor = cls.__modifyMissionTimeTable(data)
    return cls.__modifyMissionDateAction(data, currentUser, mission, subContractor)

  @classmethod
  def __modifyMissionDateAction(cls, data, currentUser, mission, subContractor):
    data["calendar"] = [date for date in data["calendar"] if date]
    existingDateMission = DatePost.objects.filter(Mission=mission)
    for task in existingDateMission:
      if task.date:
        strDate = task.date.strftime("%Y-%m-%d")
        if not strDate in data["calendar"]:
          Notification.objects.create(Mission=mission, nature="alert", Company=subContractor, Role="ST", content=f"Votre journée de travail du {strDate} pour le chantier du {mission.address} est proposée à la suppression, à vous de valider la modification.", timestamp=datetime.now().timestamp())
          date = datetime.strptime(strDate, "%Y-%m-%d")
          datePost = DatePost.objects.get(Mission=mission, date=date)
          datePost.deleted = True
          datePost.validated = False
          datePost.save()
        else:
          data["calendar"].remove(strDate)
    for strDate in data["calendar"]:
      date = datetime.strptime(strDate, "%Y-%m-%d")
      DatePost.objects.create(Mission=mission, date=date, validated=False)
      Notification.objects.create(Mission=mission, nature="alert", Company=subContractor, Role="ST", content=f"Une journée de travail pour le chantier du {mission.address} vous est proposée {strDate}, à vous de valider la proposition.", timestamp=datetime.now().timestamp())
    return {"modifyMissionDate":"OK", mission.id:mission.computeValues(mission.listFields(), currentUser, dictFormat=True)}

  @classmethod
  def __modifyMissionTimeTable(cls, data):
    mission = Mission.objects.get(id=data["missionId"])
    candidate = Candidate.objects.get(Mission=mission, isChoosen=True)
    subContractor = candidate.Company
    roleST = "ST"
    if mission.hourlyStart != data["hourlyStart"]:
      mission.hourlyStartChange = data["hourlyStart"]
      Notification.objects.create(Mission=mission, nature="alert", Company=subContractor, Role=roleST, content=f"Votre horaire de départ pour le chantier du {mission.address} va changé et pour {mission.hourlyStart}, à vous de valider la modification.", timestamp=datetime.now().timestamp())
    if mission.hourlyEnd != data["hourlyEnd"]:
      mission.hourlyEndChange = data["hourlyEnd"]
      Notification.objects.create(Mission=mission, nature="alert", Company=subContractor, Role=roleST, content=f"Votre horaire de fin de journée pour le chantier du {mission.address} va changer et pour {mission.hourlyEnd}, à vous de valider la modification.", timestamp=datetime.now().timestamp())
    mission.save()
    return mission, subContractor

  @classmethod
  def __validateMissionDate(cls, data, currentUser):
    print("validateMissionDate", data)
    mission, answer = cls.__validateMissionTimeTable(data)
    if answer:
      return {"validateMissionDate":"OK", mission.id:mission.computeValues(mission.listFields(), currentUser, dictFormat=True)}
    return cls.__validateMissionDateAction(data, currentUser, mission)
    
  @classmethod
  def __validateMissionTimeTable(cls, data):
    mission = Mission.objects.get(id=data["missionId"])
    answer = False
    if data["field"] == "hourlyStart":
      answer = True
      if data["state"]:
        Notification.objects.create(Mission=mission, nature="alert", Company=mission.Company, Role="PME", content=f"Votre horaire de début pour le chantier du {mission.address} est maintenant validée et est {mission.hourlyStart}.", timestamp=datetime.now().timestamp())
        mission.hourlyStart = mission.hourlyStartChange
      else:
        Notification.objects.create(Mission=mission, nature="alert", Company=mission.Company, Role="PME", content=f"Votre horaire de début pour le chantier du {mission.address} a été refusée.", timestamp=datetime.now().timestamp())
      mission.hourlyStartChange = ''
    elif data["field"] == "hourlyEnd":
      answer = True
      if data["state"]:
        Notification.objects.create(Mission=mission, nature="alert", Company=mission.Company, Role="PME", content=f"Votre horaire de fin de journée pour le chantier du {mission.address} est maintenant validée et est {mission.hourlyStart}.", timestamp=datetime.now().timestamp())
        mission.hourlyEnd = mission.hourlyEndChange
      else:
         Notification.objects.create(Mission=mission, nature="alert", Company=mission.Company, Role="PME", content=f"Votre horaire de fin de journée pour le chantier du {mission.address} a été refusée.", timestamp=datetime.now().timestamp())
      mission.hourlyEndChange = ''
    mission.save()
    return mission, answer

  @classmethod
  def __validateMissionDateAction(cls, data, currentUser, mission):
    if data["field"] == "date":
      date = datetime.strptime(data["date"], "%Y-%m-%d")
      datePost = DatePost.objects.get(Mission=mission, date=date)
      stillExist = True
      if data["state"]:
        stillExist = False
        if datePost.deleted:
          datePost.delete()
          Notification.objects.create(Mission=mission, nature="alert", Company=mission.Company, Role="PME", content=f"La journée de travail du {data['date']} pour le chantier du {mission.address} a été refusée.", timestamp=datetime.now().timestamp())
        else:
          Notification.objects.create(Mission=mission, nature="alert", Company=mission.Company, Role="PME", content=f"La journée de travail du {data['date']} pour le chantier du {mission.address} est maintenant validée.", timestamp=datetime.now().timestamp())
      else:
        if datePost.deleted:
          Notification.objects.create(Mission=mission, nature="alert", Company=mission.Company, Role="PME", content=f"Le retrait de la journée de travail du {data['date']} pour le chantier du {mission.address} a été refusé.", timestamp=datetime.now().timestamp())
          datePost.deleted = False
        else:
          Notification.objects.create(Mission=mission, nature="alert", Company=mission.Company, Role="PME", content=f"La journée supplémentaire de travail du {data['date']} pour le chantier du {mission.address} a été refusé.", timestamp=datetime.now().timestamp())
      if stillExist:
        datePost.validated = True
        datePost.save()
      return {"validateMissionDate":"OK", mission.id:mission.computeValues(mission.listFields(), currentUser, dictFormat=True)}
    return {"validateMissionDate":"Error", "messages":f'field {data["field"]} is not recognize'}



  @classmethod
  def __closeMission(cls, data, currentUser):
    mission = Mission.objects.get(id=data["missionId"])
    mission.quality = data["qualityStars"]
    mission.qualityComment = data["qualityComment"]
    mission.security = data["securityStars"]
    mission.securityComment = data["securityComment"]
    mission.organisation = data["organisationStars"]
    mission.organisationComment = data["organisationComment"]
    mission.isClosed = True
    mission.save()
    cls.__newStars(mission, "st")
    candidate = Candidate.objects.get(Mission=mission, isChoosen=True)
    return {"closeMission":"OK", mission.id:mission.computeValues(mission.listFields(), currentUser, dictFormat=True)}

  @classmethod
  def __closeMissionST(cls, data, currentUser):
    mission = Mission.objects.get(id=data["missionId"])
    mission.vibeST = data["vibeSTStars"]
    mission.vibeCommentST = data["vibeSTComment"]
    mission.securityST = data["securitySTStars"]
    mission.securityCommentST = data["securitySTComment"]
    mission.organisationST = data["organisationSTStars"]
    mission.organisationCommentST = data["organisationSTComment"]
    mission.save()
    cls.__newStars(mission, "pme")
    userProfile = UserProfile.objects.get(userNameInternal=currentUser)
    subContractor = userProfile.Company
    Notification.objects.create(Mission=mission, subContractor=subContractor, nature="ST", Company=mission.Company, Role="PME", content=f"La mission du {mission.address} a été notée.", timestamp=datetime.now().timestamp())
    return {"closeMissionST":"OK", mission.id:mission.computeValues(mission.listFields(), currentUser, dictFormat=True)}

  @classmethod
  def __notificationViewed(cls, data, currentUser):
    company = Company.objects.get(id=data["companyId"])
    notifications = Notification.objects.filter(Company=company, Role=data["role"])
    for notification in notifications:
      notification.hasBeenViewed = True
      notification.save()
    response = {notification.id:notification.computeValues(notification.listFields(), currentUser, dictFormat=True) for notification in notifications}
    response["notificationViewed"] = "OK"
    return response


  @classmethod
  def __newStars(cls, mission, companyRole):
    candidate = Candidate.objects.filter(isChoosen=True, Mission=mission)
    subContractor = candidate[0].Company
    company = mission.Company
    if companyRole == "st":
      listMission = [(candidate.Mission.quality + candidate.Mission.security + candidate.Mission.organisation) / 3 for candidate in Candidate.objects.filter(Company = subContractor, isChoosen = True) if candidate.Mission.isClosed]
      subContractor.starsST = round(sum(listMission)/len(listMission)) if len(listMission) else 0
      subContractor.save()
    else:
      listMission = [(mission.vibeST + mission.securityST + mission.organisationST) / 3 for mission in Mission.objects.filter(Company=company, isClosed=True)]
      company.starsPME = round(sum(listMission)/len(listMission)) if len(listMission) else 0
      company.save()

  @classmethod
  def duplicatePost(cls, id, currentUser):
    company = UserProfile.objects.get(userNameInternal=currentUser).Company
    post = Post.objects.filter(id=id)
    if post:
      post = post[0]
      if company == post.Company:
        exceptionField = ['signedByCompany', 'signedBySubContractor', 'subContractorContact', 'subContractorName', 'quality', 'qualityComment', 'security', 'securityComment', 'organisation', 'organisationComment', 'vibeST',  'vibeCommentST',  'securityST',  'securityCommentST',  'signedByCompany',  'organisationST',  'organisationCommentST',  'isClosed', 'contract']
        kwargs = {field.name:getattr(post, field.name) for field in Post._meta.fields[1:] if not field in exceptionField}
        kwargs["draft"] = True
        duplicate = Post.objects.create(**kwargs)
        for detailPost in DetailedPost.objects.filter(Post=post):
          DetailedPost.objects.create(Post=duplicate, content=detailPost.content)
        for file in File.objects.filter(Post=post):
          kwargs =  {field.name:getattr(file, field.name) for field in File._meta.fields[1:]}
          newName = File.dictPath["post"] + kwargs["name"] + '_' + str(duplicate.id) + '.' + kwargs["ext"]
          shutil.copy(kwargs["path"], newName)
          kwargs["path"] = File.dictPath["post"] + kwargs["name"] + '_' + str(duplicate.id) + '.' + kwargs["ext"]
          newFile= File.objects.create(**kwargs)
          newFile.Post = duplicate
          newFile.save()
        return {"duplicatePost":"OK", duplicate.id:duplicate.computeValues(duplicate.listFields(), currentUser, dictFormat=True)}
      return {"duplicatePost":"Error", "messages":f"{currentUser.username} does not belongs to {company.name}"}
    return {"duplicatePost":"Error", "messages":f"{id} does not exist"}

  @classmethod
  def downloadFile(cls, id, currentUser):
    file = File.objects.get(id=id)
    content = file.getAttr("file")
    listFields = file.listFields()
    fileList = file.computeValues(listFields, currentUser)
    indexContent = listFields.index("content")
    fileList[indexContent] = content
    return {"downloadFile":"OK", id:fileList}

  @classmethod
  def deleteFile(cls, id):
    file = File.objects.filter(id=id)
    if file:
      file = file[0]
      os.remove(file.path)
      file.delete()
      return {"deleteFile":"OK", "id":id}
    return {"deleteFile":"Error", "messages":f"No file width id {id}"}


  @classmethod
  def __uploadFile(cls, data, currentUser):
    if not data['ext'] in File.authorizedExtention:
      return {"uploadFile":"Warning", "messages":f"L'extention {data['ext']} n'est pas traitée"}
    fileStr, message = data["fileBase64"], {}
    for field in ["name", "ext", "nature"]:
      if not data[field]:
        message[field] = f"field {field} is empty"
    if not fileStr:
      message["fileBase64"] = "field fileBase64 is empty"
    if message:
      return {"uploadFile":"Error", "messages":message}
    expirationDate = datetime.strptime(data["expirationDate"], "%Y-%m-%d") if "expirationDate" in data and data["expirationDate"] else None
    post = None
    if "Post" in data:
      post = Post.objects.filter(id=data["Post"])
      if not post:
        return {"uploadFile":"Error", "messages":f"no post with id {data['Post']}"}
      else:
        post = post[0]
    objectFile = File.createFile(data["nature"], data["name"], data['ext'], currentUser, expirationDate=expirationDate, post=post)
    file = None
    try:
      file = ContentFile(base64.urlsafe_b64decode(fileStr), name=objectFile.path + data['ext']) if data['ext'] != "txt" else fileStr
      with open(objectFile.path, "wb") as outfile:
          outfile.write(file.file.getbuffer())
      return {"uploadFile":"OK", objectFile.id:objectFile.computeValues(objectFile.listFields(), currentUser, True)[:-1]}
    except:
      if file: file.delete()
      return {"uploadFile":"Warning", "messages":"Le fichier ne peut être sauvegardé"}

  @classmethod
  def __uploadImageSupervision(cls, data, currentUser):
    print("uploadImageSupervision", data.keys(), currentUser, data["taskId"], data["missionId"])
    if not data['ext'] in File.authorizedExtention:
      return {"uploadImageSupervision":"Warning", "messages":f"L'extention {data['ext']} n'est pas traitée"}
    fileStr = data["imageBase64"]
    if not fileStr:
      return {"uploadImageSupervision":"Error", "messages":"field fileBase64 is empty"}
    name = "supervision"
    if data["taskId"]:
      detailedPost = DetailedPost.objects.get(id=data["taskId"])
      supervisions = Supervision.objects.filter(Mission=None, DetailedPost=detailedPost)
      mission = None
    else:
      detailedPost = None
      mission = Mission.objects.get(id=data["missionId"])
      supervisions = Supervision.objects.filter(Mission=mission)
      print("uploadImageSupervision", supervisions)
      if supervisions:
        supervision = supervisions[len(supervisions) - 1]
      else:
        return {"uploadImageSupervision":"Error", "messages":f"No supervision associated to mission id {mission.id}"}

    objectFile = File.createFile("supervision", name, data['ext'], currentUser, post=None, mission=mission, detailedPost=detailedPost, supervision=supervision)
    file = None
    try:
      file = ContentFile(base64.urlsafe_b64decode(fileStr), name=objectFile.path + data['ext']) if data['ext'] != "txt" else fileStr
      with open(objectFile.path, "wb") as outfile:
          outfile.write(file.file.getbuffer())
      return {"uploadImageSupervision":"OK", objectFile.id:objectFile.computeValues(objectFile.listFields(), currentUser, True)[:-1]}
    except:
      if file: file.delete()
      return {"uploadImageSupervision":"Warning", "messages":"Le fichier ne peut être sauvegardé"}

  @classmethod
  def getEnterpriseDataFrom(cls, request):
    subName = request.GET["subName"]
    siret = request.GET["siret"] if "siret" in request.GET else None
    if os.getenv('PATH_MIDDLE'):
      externalResponse = getEnterpriseDataFrom(subName=subName, siret=siret)
      externalResponse = externalResponse["data"] if "data" in externalResponse else None
      if isinstance(externalResponse, dict) and externalResponse:
        response = {"getEnterpriseDataFrom":"OK"}
        response.update(externalResponse)
        return response
      else:
        return {"getEnterpriseDataFrom":"Error", "messages":{"list":"empty"}}
    else:
      return {"getEnterpriseDataFrom":"Error", "messages":{"local":"no installation"}}


  @classmethod
  def __modifyPwd(cls, data, currentUser):
    if data['oldPwd'] == data['newPwd']:
      return {"modifyPwd":"Warning", "messages":{"oldPwd", "L'ancien et le nouveau mot de passe sont identiques"}}
    currentUser.set_password(data['newPwd'])
    currentUser.save()
    return {"modifyPwd":"OK"}

  @classmethod
  def __updateUserInfo(cls, data, user):
    print("__updateUserInfo", data)
    if "UserProfile" in data:
      message, valueModified, userProfile = {}, {"UserProfile":{}}, UserProfile.objects.get(id=data["UserProfile"]["id"])
      flagModified = cls.__setValues(data["UserProfile"], user, message, valueModified["UserProfile"], userProfile, False)
      if not flagModified:
        message["general"] = "Aucun champ n'a été modifié" 
      if message:
        return {"modifyUser":"Warning", "messages":message, "valueModified": valueModified}
      company = userProfile.Company
      return {"modifyUser":"OK","UserProfile":{userProfile.id:userProfile.computeValues(userProfile.listFields(), user, True)}, "Company":{company.id:company.computeValues(company.listFields(), user, True)}}
    return {"modifyUser":"Warning", "messages":"Pas de valeur à mettre à jour"}
    
  @classmethod
  def __setValues(cls, dictValue, user, message, valueModified, objectInstance, flagModified):
    for fieldName, value in dictValue.items():
      print("setValue", fieldName)
      valueToSave = value
      if fieldName != "id" and fieldName != 'userName':
        fieldObject = None
        try:
          fieldObject = objectInstance._meta.get_field(fieldName)
        except:
          pass
        if fieldObject and isinstance(fieldObject, models.ForeignKey):
          valueModified[fieldName], instance = {}, getattr(objectInstance, fieldName)
          flagModifiedNew = cls.__setValues(value, user, message, valueModified[fieldName], instance, flagModified)
          flagModified = flagModifiedNew if not flagModified else flagModified
        elif fieldName in objectInstance.manyToManyObject:
          valueModified[fieldName] = {}
          flagModifiedNew = cls.__setValuesLabelJob(fieldName, value, valueModified[fieldName], user)
          flagModified = flagModifiedNew if not flagModified else flagModified
        elif getattr(objectInstance, fieldName, "does not exist") != "does not exist":
          print("setValue", fieldObject, fieldName, value)
          # valueToSave = value == "true"
          if fieldObject and isinstance(fieldObject, models.DateField):
            valueToSave = value.strftime("%Y-%m-%d") if value else None
          elif fieldObject and isinstance(fieldObject, models.IntegerField):
            valueToSave = int(value) if value else None
          elif fieldObject and isinstance(fieldObject, models.FloatField):
            valueToSave = float(value) if value else None
          elif fieldObject and isinstance(fieldObject, models.BooleanField):
            print("bool", fieldName, value, objectInstance.getAttr(fieldName))
          if valueToSave != objectInstance.getAttr(fieldName):
            objectInstance.setAttr(fieldName, valueToSave)
            objectInstance.save()
            valueModified[fieldName] = value
            flagModified = True
        else:
          message[fieldName] = "is not a field"
    return flagModified

  @classmethod
  def __setValuesLabelJob(cls, modelName, dictValue, valueModified, user):
    if modelName == "JobForCompany":
      return cls.__setValuesJob(dictValue, valueModified, user)
    else:
      return cls.__setValuesLabel(dictValue, valueModified, user)

  @classmethod
  def __setValuesJob(cls, dictValue, valueModified, user):
    company = UserProfile.objects.get(userNameInternal=user).Company
    jobForCompany = JobForCompany.objects.filter(Company=company)
    if jobForCompany:
      jobForCompany.delete()
    for listValue in dictValue:
      if listValue[1]:
        job = Job.objects.get(id=listValue[0])
        jobForCompany = JobForCompany.objects.create(Job=job, number=listValue[1], Company=company)
        if jobForCompany.number != 0:
          valueModified[jobForCompany.id] = [jobForCompany.Job.id, jobForCompany.number]
    return True

  @classmethod
  def __setValuesLabel(cls, dictValue, valueModified, user):
    company = UserProfile.objects.get(userNameInternal=user).Company
    LabelForCompany.objects.filter(Company=company).delete()
    for listValue in dictValue:
      label = Label.objects.get(id=listValue[0])
      date = datetime.strptime(listValue[1], "%Y-%m-%d") if listValue[1] else None
      labelForCompany = LabelForCompany.objects.create(Label=label, date=date, Company=company)
      date = labelForCompany.date.strftime("%Y-%m-%d") if labelForCompany.date else ""
      valueModified[labelForCompany.id] = [labelForCompany.Label.id, date]
    return True

  @classmethod
  def __modifyDisponibility(cls, listValue, user):
    company, messages = UserProfile.objects.get(userNameInternal=user).Company, {}
    if company.Role.id == 1:
      return {"modifyDisponibility":"Error", "messages":f"User company is not sub contractor {company.name}"}
    Disponibility.objects.filter(Company=company).delete()
    for date, nature in listValue:
      if not nature in ["Disponible", "Disponible Sous Conditions", "Non Disponible"]:
        messages[date] = f"nature incorrect: {nature} replaced by Disponible"
        nature = "Disponible"
      Disponibility.objects.create(Company=company, date=datetime.strptime(date, "%Y-%m-%d"), nature=nature)
    answer = {"modifyDisponibility":"OK"}
    answer.update({disponibility.id:[disponibility.date.strftime("%Y-%m-%d"), disponibility.nature] for disponibility in Disponibility.objects.filter(Company=company)})
    if messages:
      answer["modifyDisponibility"] = "Warning"
      answer["messages"] = messages
    return answer

  @classmethod
  def forgetPassword(cls, email):
    user = User.objects.filter(username=email)
    if user:
      userProfile = UserProfile.objects.get(userNameInternal=user[0])
      userProfile.token = SmtpConnector(cls.portSmtp).forgetPassword(email)
      userProfile.save()
      return {"forgetPassword":"Warning", "messages":"work in progress"}
    return {"forgetPassword":"Warning", "messages":f"L'adressse du couriel {email} n'est pas reconnue"}

  @classmethod
  def inviteFriend(cls, email, currentUser):
    userProfile = UserProfile.objects.get(userNameInternal=currentUser)
    exists = InviteFriend.objects.filter(emailTarget=email)
    if exists:
      return {"inviteFriend":"Warning", "messages":f"Une invitation a déjà été envoyé"}
    token = secrets.token_urlsafe(10)
    response = SmtpConnector(cls.portSmtp).inviteFriend(email, token, userProfile.firstName, userProfile.lastName, userProfile.Company.name)
    if "status" in response and response["status"]:
      InviteFriend.objects.create(invitationAuthor=userProfile, emailTarget=email, token=token)
      return  {"inviteFriend":"OK", "messages": f"Invitation envoyé"}
    return {"inviteFriend":"Warning", "messages":f"Echec de l'envoi"}


  @classmethod
  def newPassword(cls, data):
    for key in ["token", "password"]:
      if not key in data:
        return {"newPassword":"Error", "messages":f"no {key} in post"}
    userProfile = UserProfile.objects.filter(token=data["token"])
    if userProfile:
      userProfile = userProfile[0]
      userProfile.token = None
      userProfile.save()
      user = userProfile.userNameInternal
      user.set_password(data["password"])
      user.save()
      return {"newPassword":"OK"}
    return {"newPassword":"Warning", "messages":"work in progress"}
    