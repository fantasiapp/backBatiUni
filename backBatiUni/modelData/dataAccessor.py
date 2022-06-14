from email.headerregistry import ContentTransferEncodingHeader
from lib2to3.pgen2 import token
from this import d
from django.forms import EmailInput
from ..models import *
from django.contrib.auth.models import User
from django.utils import timezone
from django.apps import apps
import sys
import os
import shutil
from datetime import datetime, timedelta
import base64
from django.core.files.base import ContentFile
from ..smtpConnector import SmtpConnector
import json
import secrets
from pathlib import Path
from dotenv import load_dotenv
from copy import copy


load_dotenv()
if os.getenv('PATH_MIDDLE'):
  sys.path.append(os.getenv('PATH_MIDDLE'))
  from profileScraping import getEnterpriseDataFrom
  from geocoding import getCoordinatesFrom # argument str address


class DataAccessor():
  loadTables = {"user":[UserProfile, Company, JobForCompany, LabelForCompany, File, Post, Candidate, DetailedPost, DatePost, Mission, Disponibility, Supervision, Notification, BlockedCandidate, Recommandation], "general":[Job, Role, Label]}
  dictTable = {}
  portSmtp = os.getenv('PORT_SMTP')

  @classmethod
  def getData(cls, profile, user):
    if not UserProfile.objects.filter(userNameInternal=user) and profile == "user":
      {"register":"Error", "messages":"currentUser does not exist"}
    dictAnswer = {"currentUser":UserProfile.objects.get(userNameInternal=user).id} if profile == "user" else {}
    t0 = time()
    if profile == "user":
      # RamData.isUsed = False
      RamData.fillUpRamStructure()
    t1 = time()
    # print(f"queries executed in {(t1-t0):.4f}s")
    for table in cls.loadTables[profile]:
      t1 = time()
      dictAnswer.update(table.dumpStructure(user))
      t2 = time()
      # print(f'Function {table} executed in {(t2-t1):.4f}s')
    print(f"total executed in {(t2-t0):.4f}s")
    dictAnswer["timestamp"] = datetime.now().timestamp()
    with open(f"./backBatiUni/modelData/{profile}Data.json", 'w') as jsonFile:
      json.dump(dictAnswer, jsonFile, indent = 3)
    # RamData.isUsed = True
    return dictAnswer

  @classmethod
  def register(cls, data):
    if "again" in data and data["again"]:
      return cls.registerAgain(data)
    message = cls.__registerCheck(data, {})
    if message:
      return {"register":"Warning", "messages":message}
    token = SmtpConnector(cls.portSmtp).register(data["firstname"], data["lastname"], data["email"])
    if token != "token not received" or data["email"] == "jeanluc":
      userProfile = cls.__registerAction(data, token)
      cls.__checkIfHaveBeenInvited(userProfile, data['proposer'], data['email'])
      print("register", "OK")
      return {"register":"OK"}
    cls.__registerAction(data, "empty token")
    return {"register":"Error", "messages":"token not received"}


  @classmethod
  def registerAgain(cls, data):
    userProfile = UserProfile.objects.filter(email=data["email"])
    if userProfile:
      userProfile = userProfile[0]
      token = SmtpConnector(cls.portSmtp).register(data["firstname"], data["lastname"], data["email"])
      if token != "token not received":
        userProfile.token = token
        userProfile.save()
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
    if userProfile:
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
    company = Company.objects.create(name=companyData['name'], address=companyData['address'], companyMail=data["email"], activity=companyData['activity'], ntva=companyData['ntva'], siret=companyData['siret'])
    cls.__getGeoCoordinates(company)
    company.Role = Role.objects.get(id=data['Role'])
    company.save()
    proposer = None
    # if data['proposer'] and UserProfile.objects.get(tokenFriend=data['proposer']):
    #   idProposer = UserProfile.objects.get(tokenFriend=data['proposer'])
    #   proposer = UserProfile.objects.get(id=idProposer)
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
        Notification.createAndSend(Company=company, title="Parrainage", nature="alert", Role=role, content=f"{userProfile.firstName} {userProfile.lastName} de la société {userProfile.Company.name} s'est inscrit sur BatiUni. Vous êtes son parrain.", timestamp=datetime.now().timestamp())
        Notification.createAndSend(Company=userProfile.Company, title="Parrainage", nature="alert", Role=role, content=f"{userProfile.firstName} {userProfile.lastName} de la société {userProfile.Company.name} s'est inscrit sur BatiUni. Vous êtes son parrain.", timestamp=datetime.now().timestamp())
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
      elif data["action"] == "modifyFile": return cls.__modifyFile(data, currentUser)
      elif data["action"] == "modifyDisponibility": return cls.__modifyDisponibility(data["disponibility"], currentUser)
      elif data["action"] == "uploadImageSupervision": return cls.__uploadImageSupervision(data, currentUser)
      elif data["action"] == "modifyMissionDate": return cls.__modifyMissionDate(data, currentUser)
      elif data["action"] == "validateMissionDate": return cls.__validateMissionDate(data, currentUser)
      elif data["action"] == "closeMission": return cls.__closeMission(data, currentUser)
      elif data["action"] == "closeMissionST": return cls.__closeMissionST(data, currentUser)
      elif data["action"] == "notificationViewed": return cls.__notificationViewed(data, currentUser)
      elif data["action"] == "boostPost": return cls.__boostPost(data, currentUser)
      return {"dataPost":"Error", "messages":f"unknown action in post {data['action']}"}
    return {"dataPost":"Error", "messages":"no action in post"}

  @classmethod
  def __changeUserImage(cls, dictData, currentUser):
    if not dictData['ext'] in File.authorizedExtention:
      return {"changeUserImage":"Warning", "messages":f"L'extention {dictData['ext']} n'est pas traitée"}
    else:
      dictData['ext'] = File.authorizedExtention[dictData['ext']]
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
    postDump = {objectPost.id:objectPost.computeValues(objectPost.listFields(), currentUser, True)}
    datePostDump = [{date.id:date.computeValues(date.listFields(), currentUser, True) for date in DatePost.objects.filter(Post = objectPost)}]
    detailedPostDump = [{detailedPost.id:detailedPost.computeValues(detailedPost.listFields(), currentUser, True) for detailedPost in DetailedPost.objects.filter(Post = objectPost)}]
    return {"uploadPost":"OK", "Post":postDump, "DatePost":datePostDump, "DetailedPost":detailedPostDump}

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
          try:
            date = datetime.strptime(dictData[fieldName], "%Y-%m-%d") if dictData[fieldName] else None
          except ValueError:
            return {"uploadPost":"Error", "messages":f"{dictData[fieldName]} is not properly formated"}, False
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
            if fieldName == "DatePost":
              cls.__computeStartEndDate(kwargs, content)
              listObject.append(modelObject.objects.create(date=content))
            else:
              listObject.append(modelObject.objects.create(content=content))
    kwargs["contactName"] = f"{userProfile.firstName} {userProfile.lastName}"
    return kwargs, listObject


  @classmethod
  def __computeStartEndDate(cls, limitDate, strDate):
    if strDate:
      date = datetime.strptime(strDate, "%Y-%m-%d")
      if not limitDate["startDate"] or limitDate["startDate"] > date:
        limitDate["startDate"] = date
      if not limitDate["endDate"] or limitDate["endDate"] < date:
        limitDate["endDate"] = date
    else:
      print("__computeStartEndDate pb date null")
    


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
      postDump = {post.id:post.computeValues(post.listFields(), currentUser, True)}
      datePostDump = [{date.id:date.computeValues(date.listFields(), currentUser, True) for date in DatePost.objects.filter(Post = post)}]
      detailedPostDump = [{detailedPost.id:detailedPost.computeValues(detailedPost.listFields(), currentUser, True) for detailedPost in DetailedPost.objects.filter(Post = post)}]
      return {"modifyPost":"OK", "Post":postDump, "DatePost":datePostDump, "DetailedPost":detailedPostDump}
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
    amount = 0.0 if amount == "undefined" else amount
    candidate = Candidate.objects.create(Post=post, Company=subContractor, amount=amount, contact=contact, unitOfTime=unitOfTime)
    Notification.createAndSend(Post=post, Company=company, title="Nouveau candidat", subContractor=subContractor, nature="ST", Role="PME", content=f"Un nouveau sous traitant : {subContractor.name} pour le chantier du {post.address} a postulé.", timestamp=datetime.now().timestamp())
    postDump = {post.id:post.computeValues(post.listFields(), currentUser, True)}
    candidateDump = {candidate.id:candidate.computeValues(candidate.listFields(), currentUser, True)}
    return {"applyPost":"OK", "Post":postDump, "Candidate":candidateDump}

  @classmethod
  def unapplyPost(cls, postId, candidateId, currentUser):
    print("unapplyPost", postId, candidateId)
    candidate = Candidate.objects.get(id=candidateId)
    post = Post.objects.get(id=postId)
    candidate.delete()
    postDump = {post.id:post.computeValues(post.listFields(), currentUser, True)}
    return {"unapplyPost":"OK", "Candidate":candidateId, "Post":postDump}


  @classmethod
  def candidateViewed(cls, candidateId, currentUser):
    print("candidateViewed", candidateId)
    candidate = Candidate.objects.get(id=candidateId)
    candidate.isViewed = True
    candidate.save()
    post = candidate.Post
    if post:
      return {"candidateViewed":"OK", post.id:post.computeValues(post.listFields(), currentUser, True)}
    else:
      return {"candidateViewed":"Error", "messages":f"Candidate of id {candidate.id} has no post."}



  @classmethod
  def __createDetailedPost(cls, data, currentUser):
    print("createDetailedPost", data)
    kwargs, post, mission, detailedPost2 = {"Post":None, "Mission":None, "content":None}, None, None, None
    if "postId" in data:
      post = Post.objects.get(id=data["postId"])
      kwargs["Post"] = post
    if "missionId" in data:
      mission = Mission.objects.get(id=data["missionId"])
      kwargs["Mission"] = mission
    if "content" in data:
      kwargs["content"] = data["content"]
    detailedPost2 = DetailedPost.objects.create(**kwargs)
    kwargs["DatePost"] = DatePost.objects.get(id=data["dateId"])
    del kwargs["Mission"]
    detailedPost = DetailedPost.objects.create(**kwargs)
    return cls.__detailedPostComputeAnswer(detailedPost, currentUser, "createDetailedPost", detailedPost2)
    # return {"createDetailedPost":"Warning", "messages":"La tâche n'a pas été créée"}

  @classmethod
  def __modifyDetailedPost(cls, data, currentUser):
    print("modifyDetailedPost", data)
    datePostId = data["datePostId"] if "datePostId" in data and data["datePostId"] else None
    unset = data["unset"] if "unset" in data else False
    data = data["detailedPost"]
    datePost = DatePost.objects.get(id=datePostId) if datePostId else None
    detailedPost = DetailedPost.objects.get(id=data["id"])
    if not unset:
      if not detailedPost.DatePost or datePost.id != detailedPost.DatePost.id:
        detailedPost = DetailedPost.objects.create(
          content=detailedPost.content,
          DatePost=datePost,
        )
      """Une fois que le datePost existe surement, on peut mettre à jour"""
      for field in ["content", "validated", "refused"]:
        if field in data:
            setattr(detailedPost, field, data[field])
      detailedPost.save()
      return cls.__detailedPostComputeAnswer(detailedPost, currentUser)
    else:
      """retrait d'une detailed post"""
      if detailedPost.Mission:
        return {"modifyDetailedPost":"Warning", "messages":f"Not yet implemented"}
      if Supervision.objects.filter(DetailedPost=detailedPost):
        return {"modifyDetailedPost":"Warning", "messages":f"Cette tâche est commentée"}
      if detailedPost.validated or detailedPost.refused :
        return {"modifyDetailedPost":"Warning", "messages":f"Cette tâche est évaluée"}
      detailPostId = detailedPost.id
      datePostId = detailedPost.DatePost.id
      detailedPost.delete()
      datePost = DatePost.objects.get(id=datePostId)
      datePostDump = {datePost.id:datePost.computeValues(datePost.listFields(), currentUser, True)}
      return {"modifyDetailedPost":"OK", "deleted":"yes", "detailedPostId":detailPostId, "datePost":datePostDump}

  @classmethod
  def __detailedPostComputeAnswer(cls, detailedPost, currentUser, functionName="modifyDetailedPost", detailedPost2=None):
    typeDetailedPost = "Post" if detailedPost.Post else "Mission"
    if detailedPost.DatePost:
      fatherId = detailedPost.DatePost.id
      typeDetailedPost = "DatePost"
    elif typeDetailedPost == "Post": fatherId = detailedPost.Post.id
    elif typeDetailedPost == "Mission": fatherId = detailedPost.Mission.id
    answer = {
      functionName:"OK",
      "type":typeDetailedPost,
      "fatherId":fatherId,
      "detailedPost":{detailedPost.id:detailedPost.computeValues(detailedPost.listFields(), currentUser, True)}
    }
    if detailedPost2:
      answer["detailedPost2"] = {detailedPost2.id:detailedPost2.computeValues(detailedPost2.listFields(), currentUser, True)}
      answer["missionId"] = detailedPost2.Mission.id
    return answer



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
    datePost, detailedPost, mission = None, None, None
    kwargs = {"DetailedPost":None, "author":author, "companyId":userProfile.Company.id,"comment":""}
    if "detailedPostId" in data and data["detailedPostId"]:
      detailedPost = DetailedPost.objects.get(id=data["detailedPostId"])
      kwargs["DetailedPost"] = detailedPost
      mission = detailedPost.Mission
    if "datePostId" in data and data["datePostId"]:
      datePost = DatePost.objects.get(id=data["datePostId"]) 
      kwargs["DatePost"] = datePost
      mission = detailedPost.Mission
    if "comment" in data:
      kwargs["comment"] = data["comment"]
    if "date" in data and data["date"]:
      kwargs["date"] = datetime.strptime(data["date"], "%Y-%m-%d")
    supervision = Supervision.objects.create(**kwargs)
    candidate = Candidate.objects.get(Mission=mission, isChoosen=True)
    message = f"Un nouveau sous message pour le chantier du {mission.address} vous attend."
    if userProfile.Company.id == candidate.Company.id:
      company = mission.Company
      subContractor = candidate.Company
      nature = "PME"
      role = "ST"
    else:
      company = candidate.Company
      subContractor = mission.Company
      nature = "ST"
      role = "PME"
    Notification.createAndSend(Mission=mission, Company=company, title="Nouveau message", category="supervision", subContractor=subContractor, nature=nature, Role=role, content=message, timestamp=datetime.now().timestamp())
    if supervision:
      return  cls.__supervisionAnswer(supervision, currentUser)
    return {"createSupervision":"Warning", "messages":"La supervision n'a pas été créée"}

  @classmethod
  def __supervisionAnswer(cls, supervision, currentUser):
    answer = {
      "createSupervision":"OK",
      "type":"DetailedPost" if supervision.DetailedPost else "DatePost",
      "fatherId":supervision.DetailedPost.id if supervision.DetailedPost else supervision.DatePost.id,
      "supervision":{supervision.id:supervision.computeValues(supervision.listFields(), currentUser, True)}}
    return answer


  @classmethod
  def __modifySupervision(cls, data, currentUser):
    print("modifySupervision", data, currentUser.id)
    return {"modifySupervision":"Warning", "messages":"Work in progress"}

  @classmethod
  def __deleteSupervision(cls, data, currentUser):
    """A mettre à jour si nécessaire"""
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
        print("favoritePost deleted", postId, value, UserProfile.id)
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
      post = post[0]
      for candidate in Candidate.objects.filter(Post=post):
        Notification.objects.create(nature="PME", Company=candidate.Company, Role="ST", content=f"L'annonce sur le chantier du {candidate.Post.address} de la société { post.Company.name } a été supprimé.", timestamp=datetime.now().timestamp())
        candidate.delete()
      for notification in Notification.objects.filter(Post=post):
        notification.Post = None
        notification.save()
      for classObject in [DetailedPost, DatePost, DetailedPost, File]:
        for object in classObject.objects.filter(Post=post):
          object.delete()
      post.delete()
      return {"deletePost":"OK", "id":id}
    return {"deletePost":"Error", "messages":f"{id} does not exist"}

  @classmethod
  def handleCandidateForPost(cls, candidateId, status, currentUser):
    userProfile = UserProfile.objects.get(userNameInternal=currentUser)
    candidate = Candidate.objects.get(id=candidateId)
    if candidate.Mission:
      return {"handleCandidateForPost":"Error", "messages":f"The post of id {candidate.Mission.id} is allready a mission"}
    postId = candidate.Post.id
    addressWithNoNumber = cls.removefirstNumber(list(candidate.Post.address))
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
      Notification.createAndSend(Mission=candidate.Mission, Company=candidate.Company, title="Candidature retenue", subContractor=userProfile.Company, nature="PME", Role="ST", content=f"Votre candidature pour le chantier du {candidate.Mission.address} a été retenue.", timestamp=datetime.now().timestamp())
      for otherCandidate in Candidate.objects.filter(Post=mission, isRefused=False):
        if otherCandidate.id != candidate.id:
          Notification.createAndSend(Mission=otherCandidate.Post, Company=otherCandidate.Company, title="Candidature non retenue", subContractor=userProfile.Company, nature="PME", Role="ST", content=f"Une autre candidature que la vôtre a été retenue pour le chantier du {addressWithNoNumber}.", timestamp=datetime.now().timestamp())
          otherCandidate.isRefused = True
          otherCandidate.save()
      return {"handleCandidateForPost":"OK", mission.id:mission.computeValues(mission.listFields(), currentUser, dictFormat=True)}
    candidate.save()
    Notification.createAndSend(Post=candidate.Post, Company=candidate.Company, title="Candidature refusée", subContractor=userProfile.Company, nature="PME", Role="ST", content=f"Votre candidature pour le chantier du {addressWithNoNumber} a été refusée.", timestamp=datetime.now().timestamp())
    candidate.isRefused = True
    candidate.save()
    post = candidate.Post
    return {"handleCandidateForPost":"OK", post.id:post.computeValues(post.listFields(), currentUser, dictFormat=True)}

  @classmethod
  def removefirstNumber(cls, listChar):
    firstLetter = listChar.pop(0)
    if firstLetter.isdigit() or firstLetter == " ":
      return cls.removefirstNumber(listChar)
    return firstLetter + "".join(listChar)

  @classmethod
  def blockCompany(cls, companyId, status, currentUser):
    userProfile = UserProfile.objects.get(userNameInternal=currentUser)
    blockedCompany = Company.objects.get(id=companyId)
    blockingCompany = userProfile.Company
    blockData = BlockedCandidate.objects.filter(blocker=blockingCompany, blocked=blockedCompany)
    status = True if status == "true" else False
    if blockData:
      blockData[0].status = status
      blockData[0].save()
      blockedCandidate = blockData[0]
    else:
      blockedCandidate = BlockedCandidate.objects.create(blocker=blockingCompany, blocked=blockedCompany, status=status, date=timezone.now())
    return {"blockCompany":"OK", blockedCandidate.id:blockedCandidate.computeValues(blockedCandidate.listFields(), currentUser, dictFormat=True)}


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
    print("signContract", missionId)
    mission = Mission.objects.get(id=missionId)
    print("signContract contractId", mission.contract)
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
      Notification.createAndSend(Mission=mission, Company=candidate.Company, title="Signature de contrat", subContractor=mission.Company, nature="PME", Role="ST", content=f"Le contrat pour le chantier du {mission.address}  a été signé.", timestamp=datetime.now().timestamp())
      mission.signedByCompany = True
    else:
      Notification.createAndSend(Mission=mission, subContractor=candidate.Company, title="Signature de contrat", nature="ST", Company=mission.Company, Role="PME", content=f"Le contrat pour le chantier du {mission.address}  a été signé.", timestamp=datetime.now().timestamp())
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
    data["calendar"] = [date for date in data["calendar"] if date] if "calendar" in data else []
    existingDateMission = DatePost.objects.filter(Mission=mission)
    datePostList = {}
    for task in existingDateMission:
      if task.date:
        strDate = task.date.strftime("%Y-%m-%d")
        if not strDate in data["calendar"]:
          date = datetime.strptime(strDate, "%Y-%m-%d")
          datePost = DatePost.objects.get(Mission=mission, date=date)
          if DetailedPost.objects.filter(DatePost=datePost):
            return {"modifyMissionDate":"Error", "messages":"DatePost contains detailedPost"}
          if Supervision.objects.filter(DatePost=datePost):
            return {"modifyMissionDate":"Error", "messages":"DatePost contains Supervision"}
          Notification.createAndSend(Mission=mission, nature="alert", title="Modification de la mission", Company=subContractor, Role="ST", content=f"Votre journée de travail du {strDate} pour le chantier du {mission.address} est proposée à la suppression, à vous de valider la modification.", timestamp=datetime.now().timestamp())
          datePost.deleted = True
          datePost.validated = False
          datePost.save()
          datePostList[datePost.id] = datePost
        else:
          data["calendar"].remove(strDate)
    for strDate in data["calendar"]:
      date = datetime.strptime(strDate, "%Y-%m-%d")
      datePost = DatePost.objects.create(Mission=mission, date=date, validated=False)
      datePostList[datePost.id] = datePost
      Notification.createAndSend(Mission=mission, nature="alert", title="Modification de la mission", Company=subContractor, Role="ST", content=f"Une journée de travail pour le chantier du {mission.address} vous est proposée {strDate}, à vous de valider la proposition.", timestamp=datetime.now().timestamp())
    return {"modifyMissionDate":"OK", "mission":{mission.id:mission.computeValues(mission.listFields(), currentUser, dictFormat=True)} , "datePost":{id:datePost.computeValues(datePost.listFields(), currentUser, dictFormat=True) for id, datePost in datePostList.items()}}

  @classmethod
  def __modifyMissionTimeTable(cls, data):
    mission = Mission.objects.get(id=data["missionId"])
    candidate = Candidate.objects.get(Mission=mission, isChoosen=True)
    subContractor = candidate.Company
    roleST = "ST"
    if "hourlyStart" in data and mission.hourlyStart != data["hourlyStart"]:
      mission.hourlyStartChange = data["hourlyStart"]
      Notification.createAndSend(Mission=mission, nature="alert", title="Modification de la mission", Company=subContractor, Role=roleST, content=f"Votre horaire de départ pour le chantier du {mission.address} va changé et pour {mission.hourlyStart}, à vous de valider la modification.", timestamp=datetime.now().timestamp())
    if "hourlyEnd" in data and mission.hourlyEnd != data["hourlyEnd"]:
      mission.hourlyEndChange = data["hourlyEnd"]
      Notification.createAndSend(Mission=mission, nature="alert", title="Modification de la mission", Company=subContractor, Role=roleST, content=f"Votre horaire de fin de journée pour le chantier du {mission.address} va changer et pour {mission.hourlyEnd}, à vous de valider la modification.", timestamp=datetime.now().timestamp())
    mission.save()
    return mission, subContractor

  @classmethod
  def __validateMissionDate(cls, data, currentUser):
    print("validateMissionDate", data)
    mission, answer = cls.__validateMissionTimeTable(data)
    if answer:
      return {"validateMissionDate":"OK", "update":"yes", "type":"Mission", "Mission":{mission.id:mission.computeValues(mission.listFields(), currentUser, dictFormat=True)}}
    return cls.__validateMissionDateAction(data, currentUser, mission)
    
  @classmethod
  def __validateMissionTimeTable(cls, data):
    mission = Mission.objects.get(id=data["missionId"])
    answer = False
    if data["field"] == "hourly":
      answer = True
      if data["state"]:
        Notification.createAndSend(Mission=mission, nature="alert", title="Modification de la mission", Company=mission.Company, Role="PME", content=f"Vos horaires pour le chantier du {mission.address} sont maintenant validées.", timestamp=datetime.now().timestamp())
        if mission.hourlyStartChange:
          mission.hourlyStart = mission.hourlyStartChange
        if mission.hourlyEndChange:
          mission.hourlyEnd = mission.hourlyEndChange
      else:
        Notification.createAndSend(Mission=mission, nature="alert", title="Modification de la mission", Company=mission.Company, Role="PME", content=f"Vos modifications d'horaire pour le chantier du {mission.address} a été refusée.", timestamp=datetime.now().timestamp())
      mission.hourlyStartChange = ''
      mission.hourlyEndChange = ''
    mission.save()
    return mission, answer

  @classmethod
  def __validateMissionDateAction(cls, data, currentUser, mission):
    if data["field"] == "date":
      date = datetime.strptime(data["date"], "%Y-%m-%d")
      datePost = DatePost.objects.get(Mission=mission, date=date)
      datePostId = datePost.id
      stillExist = True
      if data["state"]:
        if datePost.deleted:
          if DetailedPost.objects.filter(DatePost=datePost):
            return {"validateMissionDate":"Error", "messages":"DatePost contains detailedPost"}
          if Supervision.objects.filter(DatePost=datePost):
            return {"validateMissionDate":"Error", "messages":"DatePost contains Supervision"}
          stillExist = False
          datePost.delete()
          Notification.createAndSend(Mission=mission, nature="alert", Company=mission.Company, title="Modification de la mission", Role="PME", content=f"La journée de travail du {data['date']} pour le chantier du {mission.address} a été refusée.", timestamp=datetime.now().timestamp())
        else:
          Notification.createAndSend(Mission=mission, nature="alert", Company=mission.Company, title="Modification de la mission", Role="PME", content=f"La journée de travail du {data['date']} pour le chantier du {mission.address} est maintenant validée.", timestamp=datetime.now().timestamp())
      else:
        if datePost.deleted:
          datePost.deleted = False
          Notification.createAndSend(Mission=mission, nature="alert", Company=mission.Company, title="Modification de la mission", Role="PME", content=f"Le retrait de la journée de travail du {data['date']} pour le chantier du {mission.address} a été refusé.", timestamp=datetime.now().timestamp())
        else:
          stillExist = False
          datePost.delete()
          Notification.createAndSend(Mission=mission, nature="alert", Company=mission.Company, title="Modification de la mission", Role="PME", content=f"La journée supplémentaire de travail du {data['date']} pour le chantier du {mission.address} a été refusé.", timestamp=datetime.now().timestamp())
      if stillExist:
        datePost.validated = True
        datePost.save()
      if stillExist:
        return {"validateMissionDate":"OK", "type":"Mission", "fatherId":mission.id, "datePost":{datePost.id:datePost.computeValues(datePost.listFields(), currentUser, dictFormat=True)}}
      return {"validateMissionDate":"OK", "fatherId":datePostId, "deleted":"yes","mission":{mission.id:mission.computeValues(mission.listFields(), currentUser, dictFormat=True)}}
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
    Notification.createAndSend(Mission=mission, subContractor=subContractor, title="Modification de la mission", nature="ST", Company=mission.Company, Role="PME", content=f"La mission du {mission.address} a été notée.", timestamp=datetime.now().timestamp())
    return {"closeMissionST":"OK", mission.id:mission.computeValues(mission.listFields(), currentUser, dictFormat=True)}

  @classmethod
  def __notificationViewed(cls, data, currentUser):
    print("__notificationViewed", data)
    company = Company.objects.filter(id=data["companyId"])
    if not company:
      return {"notificationViewed":"Error", "messages":f"{data['companyId']} does not exist"}
    company = company[0]
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
        kwargs["boostTimestamp"] = 0
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
  def deleteFile(cls, id, currentUser):
    print("deleteFile", id)
    file = File.objects.filter(id=id)
    if file:
      file = file[0]
      isCompany = file.nature in ["admin", "labels"]
      if not Path(file.path).is_file():
        return {"deleteFile":"Error", "messages":f"No file with path {file.path}"}
      os.remove(file.path)
      file.delete()
      response = {"deleteFile":"OK", "id":id}
      if isCompany:
        company = UserProfile.objects.get(userNameInternal=currentUser).Company
        response["Company"] = {company.id:company.computeValues(company.listFields(), currentUser, True)}
        print("deleteFile", response)
      return response
    return {"deleteFile":"Error", "messages":f"No file width id {id}"}

  @classmethod
  def __uploadFile(cls, data, currentUser):
    print("uploadFile", list(data.keys()))
    if not "ext" in data or not "fileBase64" in data:
      return {"uploadFile":"Warning", "messages":f"Le fichier n'est pas conforme"}
    if not data['ext'] in File.authorizedExtention:
      return {"changeUserImage":"Warning", "messages":f"L'extention {data['ext']} n'est pas traitée"}
    else:
      data['ext'] = File.authorizedExtention[data['ext']]
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
        return {"uploadFile":"Error", "messages":f"no post with id {data['Post']} for Post"}
      else:
        post = post[0]
    objectFile = File.createFile(data["nature"], data["name"], data['ext'], currentUser, expirationDate=expirationDate, post=post)
    file = None
    try:
      file = ContentFile(base64.urlsafe_b64decode(fileStr), name=objectFile.path) if data['ext'] != "txt" else fileStr
      with open(objectFile.path, "wb") as outfile:
        outfile.write(file.file.getbuffer())
      return {"uploadFile":"OK", objectFile.id:objectFile.computeValues(objectFile.listFields(), currentUser, True)}
    except:
      if file: file.delete()
      return {"uploadFile":"Warning", "messages":"Le fichier ne peut être sauvegardé"}


  @classmethod
  def __modifyFile(cls, data, currentUser):
    print("modifyFile", list(data.keys()))
    objectFile = File.objects.get(id=data["fileId"])
    expirationDate = datetime.strptime(data["expirationDate"], "%Y-%m-%d") if "expirationDate" in data and data["expirationDate"] else None
    post, mission = objectFile.Post, objectFile.Mission
    nature = data["nature"] if "nature" in data else objectFile.nature
    name = data["name"] if "name" in data else objectFile.name
    ext = data["ext"] if "ext" in data and data["ext"] != "???" else objectFile.ext
    suppress = "fileBase64" in data and len(data["fileBase64"]) != 0
    objectFile = File.createFile(nature, name, ext, currentUser, expirationDate=expirationDate, post=post, mission=mission, detailedPost=None, suppress=suppress)
    if "fileBase64" in data and data["fileBase64"]:
      try:
        file = ContentFile(base64.urlsafe_b64decode(data["fileBase64"]), name=objectFile.path) if data['ext'] != "txt" else data["fileBase64"]
        with open(objectFile.path, "wb") as outfile:
          outfile.write(file.file.getbuffer())
      except ValueError:
        return {"modifyFile":"Error", "messages":f"File of id {file.id} has not been saved"}
    return {"modifyFile":"OK", objectFile.id:objectFile.computeValues(objectFile.listFields(), currentUser, True)}
      

  @classmethod
  def __uploadImageSupervision(cls, data, currentUser):
    print("uploadImageSupervision")
    if not data['ext'] in File.authorizedExtention:
      return {"uploadImageSupervision":"Warning", "messages":f"L'extention {data['ext']} n'est pas traitée"}
    else:
      data['ext'] = File.authorizedExtention[data['ext']]
    fileStr = data["imageBase64"]
    if not fileStr:
      return {"uploadImageSupervision":"Error", "messages":"field fileBase64 is empty"}
    supervision = Supervision.objects.get(id=data["supervisionId"])
    objectFile = File.createFile("supervision", "supervision", data['ext'], currentUser, supervision=supervision)
    file = None
    try:
      file = ContentFile(base64.urlsafe_b64decode(fileStr), name=objectFile.path + data['ext']) if data['ext'] != "txt" else fileStr
      with open(objectFile.path, "wb") as outfile:
          outfile.write(file.file.getbuffer())
      return {"uploadImageSupervision":"OK", objectFile.id:objectFile.computeValues(objectFile.listFields(), currentUser, True), "supervisionId":supervision.id}
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
    print("__updateUserInfo", user, data)
    valuesSaved = {"JobForCompany":{}, "LabelForCompany":{}}
    message, userProfile = {}, UserProfile.objects.get(userNameInternal=user)
    if "UserProfile" in data and data["UserProfile"]:
      valuesSaved = cls.__setValuesForUser(data["UserProfile"], user, message, userProfile, valuesSaved)
      if message:
        return {"modifyUser":"Warning", "messages":message}
      company = userProfile.Company
      userProfileDump = {userProfile.id:userProfile.computeValues(userProfile.listFields(), user, True)}
      companyDump = {company.id:company.computeValues(company.listFields(), user, True)}
      response = {"modifyUser":"OK","UserProfile":userProfileDump, "Company":companyDump}
      for fieldName in ['JobForCompany', 'LabelForCompany']:
        response[fieldName] = valuesSaved[fieldName]
      return response
    return {"modifyUser":"Warning", "messages":"Pas de valeur à mettre à jour"}
    
  @classmethod
  def __setValuesForUser(cls, dictValue, user, message, objectInstance, valuesSaved):
    for fieldName, value in dictValue.items():
      valueToSave = value
      if fieldName != "id" and fieldName != 'userName':
        fieldObject = None
        try:
          fieldObject = objectInstance._meta.get_field(fieldName)
        except:
          message = f"{fieldName} is not a field"
        if fieldObject and isinstance(fieldObject, models.ForeignKey):
          cls.__setValuesForUser(value, user, message, getattr(objectInstance, fieldName), valuesSaved)
        elif fieldName in objectInstance.manyToManyObject:
          valuesSaved[fieldName] = cls.__setValuesLabelJob(fieldName, value, user)
        elif getattr(objectInstance, fieldName, "does not exist") != "does not exist":
          if fieldObject and isinstance(fieldObject, models.DateField):
            valueToSave = value.strftime("%Y-%m-%d") if value else None
          elif fieldObject and isinstance(fieldObject, models.IntegerField):
            valueToSave = int(value) if value else None
          elif fieldObject and isinstance(fieldObject, models.FloatField):
            valueToSave = float(value) if value else None
          if valueToSave != objectInstance.getAttr(fieldName):
            objectInstance.setAttr(fieldName, valueToSave)
            objectInstance.save()
    return valuesSaved

  @classmethod
  def __setValuesLabelJob(cls, modelName, dictValue, user):
    if modelName == "JobForCompany":
      return cls.__setValuesJob(dictValue, user)
    else:
      return cls.__setValuesLabel(dictValue, user)

  @classmethod
  def __setValuesJob(cls, dictValue, user):
    company, listJobForCompany = UserProfile.objects.get(userNameInternal=user).Company, []
    jobForCompany = JobForCompany.objects.filter(Company=company)
    if jobForCompany:
      jobForCompany.delete()
    for listValue in dictValue:
      if listValue[1]:
        job = Job.objects.get(id=listValue[0])
        jobForCompany = JobForCompany.objects.create(Job=job, number=listValue[1], Company=company)
        if jobForCompany.number != 0:
          listJobForCompany.append({jobForCompany.id:[jobForCompany.Job.id, jobForCompany.number]})
    return listJobForCompany

  @classmethod
  def __setValuesLabel(cls, dictValue, user):
    company, listLabelForCompany = UserProfile.objects.get(userNameInternal=user).Company, []
    LabelForCompany.objects.filter(Company=company).delete()
    for listValue in dictValue:
      label = Label.objects.get(id=listValue[0])
      date = datetime.strptime(listValue[1], "%Y-%m-%d") if listValue[1] else None
      labelForCompany = LabelForCompany.objects.create(Label=label, date=date, Company=company)
      date = labelForCompany.date.strftime("%Y-%m-%d") if labelForCompany.date else ""
      listLabelForCompany.append({labelForCompany.id:[labelForCompany.Label.id, date]})
    return listLabelForCompany

  @classmethod
  def removeLabelForCompany(cls, labelId, user):
    company = UserProfile.objects.get(userNameInternal=user).Company
    label = LabelForCompany.objects.get(id=labelId)
    file = File.objects.filter(nature="labels", Company=company, name=label.Label.name)
    response = {"removeLabelForCompany":"OK", "LabelForCompany":label.id}
    if file:
      response["File":file[0].id]
      file[0].delete()
    label.delete()
    response["Company"] = {company.id:company.computeValues(company.listFields(), user, True)}
    return response

  @classmethod
  def __modifyDisponibility(cls, listValue, user):
    print("modifyDisponibility", listValue)
    company, messages = UserProfile.objects.get(userNameInternal=user).Company, {}
    if company.Role.id == 1:
      return {"modifyDisponibility":"Error", "messages":f"User company is not sub contractor {company.name}"}
    Disponibility.objects.filter(Company=company).delete()
    for date, nature in listValue:
      if not nature in ["Disponible", "Disponible Sous Conditions"]:
        messages[date] = f"nature incorrect: {nature} replaced by Disponible"
        nature = "Disponible"
      if date and not Disponibility.objects.filter(Company=company, date=datetime.strptime(date, "%Y-%m-%d")):
        Disponibility.objects.create(Company=company, date=datetime.strptime(date, "%Y-%m-%d"), nature=nature)
    answer = {"modifyDisponibility":"OK"}
    answer.update({disponibility.id:[disponibility.date.strftime("%Y-%m-%d"), disponibility.nature] for disponibility in Disponibility.objects.filter(Company=company)})
    if messages:
      answer["modifyDisponibility"] = "Warning"
      answer["messages"] = messages
    return answer

  @classmethod
  def __boostPost(cls, dictValue, user):
    print("boostPost")
    post = Post.objects.filter(id=dictValue["postId"])
    if post:
      post = post[0]
      if dictValue["duration"]:
        date = datetime.now() + timedelta(days=dictValue["duration"], hours=0)
      else:
        date = None
        endDate = post.endDate
        strEndDate = post.endDate.strftime("%m/%d/%Y" "%H:%M:%S")
        date = datetime.strptime(strEndDate, "%m/%d/%Y" "%H:%M:%S")
      post.boostTimestamp = date.timestamp()
      post.save()
      return {"boostPost":"OK","UserProfile":{post.id:post.computeValues(post.listFields(), user, True)}}
    return {"boostPost":"Error", "messages":f"No post with id {'postId'}"}
    


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
  def inviteFriend(cls, email, register, currentUser):
    userProfile = UserProfile.objects.get(userNameInternal=currentUser)
    if register == "false":
      userProfile.tokenFriend = ''
      userProfile.save()
      return  {"inviteFriend":"OK"}
    exists = InviteFriend.objects.filter(emailTarget=email)
    if exists:
      return {"inviteFriend":"Warning", "messages":f"Une invitation a déjà été envoyé"}
    token = secrets.token_urlsafe(10)
    response = SmtpConnector(cls.portSmtp).inviteFriend(email, token, userProfile.firstName, userProfile.lastName, userProfile.Company.name)
    if "status" in response and response["status"]:
      InviteFriend.objects.create(invitationAuthor=userProfile, emailTarget=email, token=token)
      userProfile.tokenFriend = token
      userProfile.save()
      return  {"inviteFriend":"OK", "messages": f"Invitation envoyé", "token":token}
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

  @classmethod
  def askRecommandation(cls, mail, currentUser):
    userProfile = UserProfile.objects.get(userNameInternal=currentUser)
    response = SmtpConnector(cls.portSmtp).askRecomandation(mail, userProfile.firstName, userProfile.lastName, userProfile.Company.name, userProfile.Company.id)
    print("askRecommandation dataAccessor", response)

    if "status" in response and response["status"]:
      return  {"askRecommandation":"OK", "messages": f"Demande de recommandation envoyée"}
    return {"askRecommandation":"Warning", "messages":f"Echec de l'envoi"}

  @classmethod
  def giveRecommandation(cls, data):
    del data["action"]
    print("giveRecommandation", data)
    company = Company.objects.get(id=data["companyRecommanded"])
    if Recommandation.objects.filter(companyRecommanded=company, companyNameRecommanding=data['companyNameRecommanding']):
      return {"giveRecommandation":"Warning", "messages":"La recommandation existe déjà"}
    kwargs = {"date":timezone.now()}
    for key, value in data.items():
      if key == "companyRecommanded":
        company = Company.objects.get(id=value)
        kwargs[key] = company
      else:
        kwargs[key] = value
    Recommandation.objects.create(**kwargs)
    return {"giveRecommandation":"OK", "messages":"Recommandation recorded"}

  @classmethod
  def giveNotificationToken(cls, token, currentUser):
    print("giveNotificationToken", token, currentUser.id)
    userProfile = UserProfile.objects.get(userNameInternal=currentUser)
    userProfile.tokenNotification = token
    userProfile.save()
    return {"giveNotificationToken":"OK"}





    

      
    