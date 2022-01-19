from ..models import *
from django.contrib.auth.models import User, UserManager
from django.contrib.auth.hashers import check_password, make_password
from django.apps import apps
from operator import attrgetter
import sys
import os
from datetime import datetime
import base64
from django.core.files.base import ContentFile
from .smtpConnector import SmtpConnector

from dotenv import load_dotenv

load_dotenv()
if os.getenv('PATH_MIDDLE'):
  sys.path.append(os.getenv('PATH_MIDDLE'))
  from profileScraping import searchUnitesLegalesByDenomination

import json

class DataAccessor():
  loadTables = {"user":[UserProfile, Company, JobForCompany, LabelForCompany, Files], "general":[Job, Role, Label]}
  dictTable = {}
  portSmtp = os.getenv('PORT_SMTP')

  @classmethod
  def getData(cls, profile, user):
    dictAnswer = {}
    for table in cls.loadTables[profile]:
      dictAnswer.update(table.dumpStructure(user))
    with open(f"./backBatiUni/modelData/{profile}Data.json", 'w') as jsonFile:
        json.dump(dictAnswer, jsonFile, indent = 3)
    return dictAnswer

  @classmethod
  def register(cls, jsonString):
    data = json.loads(jsonString)
    message = cls.__registerCheck(data, {})
    if message:
      return {"register":"Warning", "messages":message}
    print("port", cls.portSmtp)
    token = SmtpConnector(cls.portSmtp).register(data["firstname"], data["lastname"], data["email"])
    print("register", jsonString, "token", token)
    if token:
      cls.__registerAction(data, token)
      return {"register":"OK"}
    cls.__registerAction(data, "empty token")
    return {"register":"Error", "messages":"token not received"} 

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
    return message

  @classmethod
  def __registerAction(cls, data, token):
    company = Company.objects.filter(name=data['company'])
    if not company:
      if os.getenv('PATH_MIDDLE'):
        searchSiren = searchUnitesLegalesByDenomination(data['company'])
        if searchSiren["status"] == "OK":
          company = Company.objects.create(name=data['company'], siret=searchSiren["data"]["siren"])
        else:
          company = Company.objects.create(name=data['company'])
      else:
        company = Company.objects.create(name=data['company'])
    else:
      company = company[0]
    role = Role.objects.get(id=data['role'])
    proposer = None
    if data['proposer'] and User.objects.get(id=data['proposer']):
      proposer = User.objects.get(id=data['proposer'])
    userProfile = UserProfile.objects.create(Company=company, firstName=data['firstname'], lastName=data['lastname'], proposer=proposer, role=role, token=token, email=data["email"], password=data["password"])
    if 'jobs' in data:
      for idJob in data['jobs']:
        job = Job.objects.get(id=idJob)
        jobCompany = JobForCompany.objects.filter(Job=job, Company=company)
        if not jobCompany:
          JobForCompany.objects.create(Job=job, Company=company, number=1)
    userProfile.save()

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
      return {"registerConfirm":"OK"}
    return {"registerConfirm":"Error", "messages":"wrong token or email"}


  @classmethod
  def dataPost(cls, jsonString, currentUser):
    data = json.loads(jsonString)
    if "action" in data:
      print("dataPost", data["action"])
      if data["action"] == "modifyUser": print("modify user", data)
      if data["action"] == "modifyPwd": return cls.__modifyPwd(data, currentUser)
      elif data["action"] == "modifyUser": return cls.__updateUserInfo(data, currentUser)
      elif data["action"] == "changeUserImage": return cls.__changeUserImage(data, currentUser)
      elif data["action"] == "loadDocument": return cls.__loadDocument(data, currentUser)
      return {"dataPost":"Error", "messages":f"unknown action in post {data['action']}"}
    return {"dataPost":"Error", "messages":"no action in post"}

  @classmethod
  def __changeUserImage(cls, dictData, currentUser):
    fileStr = dictData["imageBase64"]
    if not dictData["name"]:
      return {"changeUserImage":"Error", "messages":"field name is empty"}
    objectFile = Files.createFile("userImage", dictData["name"], dictData['ext'], currentUser)
    file = ContentFile(base64.b64decode(fileStr), name=objectFile.path + dictData['ext'])
    with open(objectFile.path, "wb") as outfile:
        outfile.write(file.file.getbuffer())
    return {"changeUserImage":"OK", objectFile.id:objectFile.computeValues(objectFile.listFields(), currentUser)[1]}

  @classmethod
  def loadImage(cls, id, currentUser):
    file = Files.objects.get(id=id)
    content = file.getAttr("file")
    listFields = file.listFields()
    fileList = file.computeValues(listFields, currentUser)
    indexContent = listFields.index("content")
    fileList[indexContent] = content
    return {"loadImage":"OK", id:fileList}

  @classmethod
  def __loadDocument(cls, request, data, currentUser):
    print(list(data.keys()))
    return {"loadDocument":"work in progress"}

  @classmethod
  def __modifyPwd(cls, data, currentUser):
    if data['oldPwd'] == data['newPwd']:
      return {"modifyPwd":"Warning", "messages":{"oldPwd", "L'ancien et le nouveau mot de passe sont identiques"}}
    currentUser.set_password(data['newPwd'])
    currentUser.save()
    return {"modifyPwd":"OK"}

  @classmethod
  def __updateUserInfo(cls, data, user):
    message, valueModified, userProfile = {}, {"Userprofile":{}}, UserProfile.objects.get(id=data["Userprofile"]["id"])
    flagModified = cls.__setValues(data["Userprofile"], user, message, valueModified["Userprofile"], userProfile, False)
    if not flagModified:
      message["general"] = "Aucun champ n'a été modifié" 
    if message:
      return {"modifyUser":"Warning", "messages":message, "valueModified": valueModified}
    return {"modifyUser":"OK", "valueModified": valueModified}

  @classmethod
  def __setValues(cls, dictValue, user, message, valueModified, objectInstance, flagModified):
    for fieldName, value in dictValue.items():
      if fieldName != "id":
        fieldObject = None
        try:
          fieldObject = objectInstance._meta.get_field(fieldName)
        except:
          pass
        if fieldObject and isinstance(fieldObject, models.ForeignKey):
          valueModified[fieldName], instance = {}, getattr(objectInstance, fieldName)
          valueModified[fieldName] = {}
          flagModified = cls.__setValues(value, user, message, valueModified[fieldName], instance, flagModified) if not flagModified else True
        elif fieldName in objectInstance.manyToManyObject:
          valueModified[fieldName] = {}
          flagModified = cls.__setValuesLabelJob(fieldName, value, valueModified[fieldName], user) if not flagModified else True
        elif getattr(objectInstance, fieldName, "does not exist") != "does not exist":
          valueToSave = value
          if fieldObject and isinstance(fieldObject, models.DateField):
            valueToSave = value.strftime("%Y/%m/%d") if value else None
          elif fieldObject and isinstance(fieldObject, models.IntegerField):
            valueToSave = int(value) if value else None
          elif fieldObject and isinstance(fieldObject, models.FloatField):
            valueToSave = float(value) if value else None
          if valueToSave != getattr(objectInstance, fieldName):
            print("test 1", fieldName, valueToSave, getattr(objectInstance, fieldName))
            setattr(objectInstance, fieldName, valueToSave)
            objectInstance.save()
            print("test 2", fieldName, valueToSave, getattr(objectInstance, fieldName))
            valueModified[fieldName] = value
            flagModified = True
        else:
          message[fieldName] = "is not an field"
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
    labelForCompany = LabelForCompany.objects.filter(Company=company)
    if labelForCompany:
      labelForCompany.delete()
    for listValue in dictValue:
      label = Label.objects.get(id=listValue[0])
      date = datetime.strptime(listValue[1], "%Y/%m/%d")
      labelForCompany = LabelForCompany.objects.create(Label=label, date=date, Company=company)
      valueModified[labelForCompany.id] = [labelForCompany.Label.id, labelForCompany.date.strftime("%Y/%m/%d")]
    return True
