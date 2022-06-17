from ast import DictComp
from fileinput import isstdin
from this import d
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os
import base64
import datetime
from django.apps import apps
from pdf2image import convert_from_path
import requests

import whatimage
import pyheif
from PIL import Image
from cairosvg import svg2png
from time import sleep, time
from copy import deepcopy
import json
import shutil



class RamData():
  ramStructure = {}
  lastTimeStamp = 0
  ramStructureComplete = {}
  allPost = {}
  allMission = {}
  allCompany = {}
  isUsed = False

  @classmethod
  def fillUpRamStructure(cls):
    if not cls.isUsed or datetime.datetime.now().timestamp() - cls.isUsed > 30:
      # print("compute fillUpRamStructure", RamData.isUsed)
      cls.isUsed = datetime.datetime.now().timestamp()
      # print("fillUpRamStructure", cls.isUsed)
      cls.allPost = {int(post.id):[] for post in Post.objects.all() if post.subContractorName == None}
      cls.allMission = {mission.id:[] for mission in Mission.objects.all() if mission.subContractorName}
      cls.allCompany = {company.id:[] for company in Company.objects.all()}
      cls.allDatePost = {datePost.id:[] for datePost in DatePost.objects.all()}
      cls.allDetailedPost = {detailPost.id:[] for detailPost in DetailedPost.objects.all()}
      cls.ramStructure = {"Company":{}, "Post":{}, "Mission":{}, "DetailedPost":{}, "DatePost":{}}
      # print("ramStructure", cls.ramStructure)
      for classObject in [Supervision, DatePost, DetailedPost, File, JobForCompany, LabelForCompany, Disponibility, Post, Mission, Notification, Candidate]:
        if cls.ramStructureComplete:
          print("generateRamStructure", classObject, cls.isUsed)
        classObject.generateRamStructure()
      cls.ramStructureComplete = deepcopy(cls.ramStructure)
      cls.timestamp = cls.isUsed
      cls.isUsed = False
    #   print("deepCopy", cls.isUsed)
    # else:
    #   print("isBlocked", datetime.datetime.now().timestamp() - cls.isUsed if cls.isUsed else cls.isUsed)


class CommonModel(models.Model):
  manyToManyObject = []

  class Meta:
    abstract = True

  @classmethod
  def fillupRamObjects(cls, user):
    pass

  @classmethod
  def dumpStructure(cls, user):
    dictAnswer = {}
    tableName = cls._meta.verbose_name
    if len(cls.listFields()) > 1:
      if cls == UserProfile:
        newKey = {"FavoritePost":"favoritePosts", "ViewPost":"viewedPosts"}
        listF = [key if not key in newKey else newKey[key] for key in cls.listFields()]
        dictAnswer[tableName + "Fields"] = listF
      elif cls == Mission:
        dictAnswer[tableName + "Fields"] = cls.listFields() + ["subContractor"]
      else:
        dictAnswer[tableName + "Fields"] = cls.listFields()
      if len(cls.listIndices()) >= 1:
        if cls == Mission:
          dictAnswer[tableName + "Indices"] = cls.listIndices() + [len(cls.listFields())]
        else:
          dictAnswer[tableName + "Indices"] = cls.listIndices()
    dictAnswer[tableName + "Values"] = cls.dictValues(user)
    return dictAnswer

  @classmethod
  def listFields(cls):
    return [field.name.replace("Internal", "") for field in cls._meta.fields][1:] + cls.manyToManyObject

  @classmethod
  def listIndices(cls):
    listName = cls.listFields()
    listMetaFields = [field.name for field in cls._meta.fields]
    listNameF = [name for name in listName if cls.testListIndices(name, listMetaFields)]
    return [listName.index(name) for name in listNameF]

  @classmethod
  def testListIndices(cls, name, listMetaFields):
    if name + "Internal" in listMetaFields: return False
    if name in cls.manyToManyObject: return True
    if hasattr(cls, name) and isinstance(cls._meta.get_field(name), models.ForeignKey): return True
    # if hasattr(cls, name) and isinstance(cls._meta.get_field(name), models.ManyToManyField): return True
    return False

  @classmethod
  def dictValues(cls, user):
    listFields, dictResult = cls.listFields(), {}
    for instance in cls.filter(user):
        dictResult[instance.id] = instance.computeValues(listFields, user)
        if len(listFields) == 1:
          dictResult[instance.id] = dictResult[instance.id][0]
    return dictResult

  def computeValues(self, listFields, user, dictFormat=False):
    values, listIndices = [], self.listIndices()
    for index in range(len(listFields)):
      field = listFields[index]
      fieldObject = None
      try:
        fieldObject = self._meta.get_field(field)
      except:
        pass
      if index in listIndices and isinstance(fieldObject, models.ForeignKey):
        values.append(getattr(self, field).id if getattr(self, field, None) else "")
      # elif index in listIndices and isinstance(fieldObject, models.ManyToManyField):
      #   values.append([element.id for element in getattr(self, field).all()])
      elif isinstance(fieldObject, models.DateField):
        values.append(getattr(self, field).strftime("%Y-%m-%d") if getattr(self, field) else "")
      elif isinstance(fieldObject, models.BooleanField):
        values.append(getattr(self, field))
      elif field in self.manyToManyObject:
        model = apps.get_model(app_label='backBatiUni', model_name=field)
        listFieldsModel = model.listFields()
        if field == "ViewPost":
          listModel = [view.id for view in ViewPost.objects.filter(UserProfile=self)]
        elif field == "FavoritePost":
          listModel = [favorite.postId for favorite in FavoritePost.objects.filter(UserProfile=self)]
        elif field in ["DatePost", "DetailedPost"] and (isinstance(self, Post) or isinstance(self, Mission)) : #, "Candidate"]
          objectsClass = {"DatePost":DatePost, "DetailedPost":DetailedPost}
          objects = objectsClass[field].objects.filter(Mission = self) if isinstance(self, Mission) else  objectsClass[field].objects.filter(Post = self)
          if dictFormat:
            listModel = {objectModel.id:objectModel.computeValues(listFieldsModel, user, dictFormat=True) for objectModel in objects}
          else:
            listModel = [objectModel.id for objectModel in objects]
        elif dictFormat:
          listModel = {objectModel.id:objectModel.computeValues(listFieldsModel, user, dictFormat=True) for objectModel in model.filter(user) if getattr(objectModel, self.__class__.__name__, False) == self}
          listModel = {key:valueList if len(valueList) != 1 else valueList[0] for key, valueList in listModel.items()}
        else:
          listModel = [objectModel.id for objectModel in model.filter(user) if getattr(objectModel, self.__class__.__name__, False) == self]
        values.append(listModel)
      else:
        value = getattr(self, field, "") if getattr(self, field, None) else ""
        values.append(value)
    return values

  @classmethod
  def filter(cls, user):
    return cls.objects.all()

  def setAttr(self, fieldName, value):
    listMetaFields = [field.name for field in self._meta.fields]
    if fieldName + "Internal" in listMetaFields:
      self.setAttr(fieldName, value)
    elif isinstance(self._meta.get_field(fieldName), models.ForeignKey):
      foreign = self._meta.get_field(fieldName).remote_field.model
      newValue = foreign.objects.get(id=value)
      setattr(self, fieldName, newValue)
    # elif isinstance(self._meta.get_field(fieldName), models.ManyToManyField):
    #   foreign = self._meta.get_field(fieldName).remote_field.model
    #   for index in value:
    #     newValue = foreign.objects.get(id=index)
    else:
      setattr(self, fieldName, value)

  def getAttr(self, fieldName, answer=False):
    return getattr(self, fieldName, answer)

class Label(CommonModel):
  name = models.CharField('Nom du label', unique=True, max_length=128, null=False, default=False, blank=False)
  # description = models.CharField('Description du métier', unique=False, null=True, max_length=2048, default=None)
  # site = models.CharField('Site internet', unique=False, null=True, max_length=256, default=None)

  class Meta:
    verbose_name = "Label"

class Role(CommonModel):
  name = models.CharField('Profil du compte', unique=True, max_length=128)

  class Meta:
    verbose_name = "Role"

class Job(CommonModel):
  name = models.CharField('Nom du métier', unique=True, max_length=128)

  class Meta:
    verbose_name = "Job"

class Company(CommonModel):
  name = models.CharField('Nom de la société', unique=True, max_length=128, null=False, blank=False)
  Role = models.ForeignKey(Role, on_delete=models.PROTECT, blank=False, null=False, default=3)
  siret = models.CharField('Numéro de Siret', unique=True, max_length=32, null=True, default=None)
  address = models.CharField("Adresse de l'entreprise", unique=False, max_length=256, null=True, default=None)
  activity = models.CharField("Activite principale de l'entreprise", unique=False, max_length=256, null=False, default="")
  ntva = models.CharField("Numéro de TVA intra communautaire", unique=True, max_length=32, null=True, default=None)
  capital = models.FloatField("Capital de l'entreprise", null=True, default=None)
  revenue = models.FloatField("Capital de l'entreprise", null=True, default=None)
  logo = models.CharField("Path du logo de l'entreprise", max_length=256, null=True, default=None)
  webSite = models.CharField("Url du site Web", max_length=256, null=True, default=None)
  starsST = models.IntegerField("Notation sous forme d'étoile", null=False, default=0.0)
  starsPME = models.IntegerField("Notation sous forme d'étoile", null=False, default=0.0)
  companyPhone = models.CharField("Téléphone du standard", max_length=128, blank=False, null=True, default=None)
  companyMail = models.CharField("mail de la company", max_length=256, null=True, default=None)
  amount = models.FloatField("Montant sous-traitant", null=True, default=None)
  unity = models.CharField("Unité du montant", max_length=64, null=True, default=None)
  latitude = models.FloatField("Latitude", null=True, default=None)
  longitude = models.FloatField("Longitude", null=True, default=None)
  saturdayDisponibility = models.BooleanField("Disponibilité le Samedi", null=False, default=False)
  allQualifications = models.BooleanField("Tous corps d'état", null=False, default=False)
  manyToManyObject = ["JobForCompany", "LabelForCompany", "File", "Post", "Mission", "Disponibility", "Notification"]

  class Meta:
    verbose_name = "Company"

  @property
  def jobs(self):
    return [jobForCompany.Job for jobForCompany in JobForCompany.objects.filter(Company=self)]

  def computeValues(self, listFields, user, dictFormat=False):
    values = []
    manyToMany = {"LabelForCompany":LabelForCompany, "JobForCompany":JobForCompany, "Disponibility":Disponibility, "Post":Post, "Mission":Mission, "File":File, "Notification":Notification}
    postMission = {"Post":Post, "Mission":Mission}
    for index in range(len(listFields)):
      field = listFields[index]
      
      if field == "Role": values.append(self.Role.id if self.Role else "")
      elif field == "name": values.append(self.name if self.name else "")
      elif field == "siret": values.append(self.siret if self.siret else "")
      elif field == "address": values.append(self.address if self.address else "")
      elif field == "ntva": values.append(self.ntva if self.ntva else "")
      elif field == "activity": values.append(self.activity if self.activity else "")
      elif field == "capital": values.append(self.capital if self.capital else "")
      elif field == "revenue": values.append(self.revenue if self.revenue else "")
      elif field == "logo": values.append(self.logo if self.logo else "")
      elif field == "webSite": values.append(self.webSite if self.webSite else "")
      elif field == "starsST": values.append(self.starsST if self.starsST else "")
      elif field == "starsPME": values.append(self.starsPME if self.starsPME else "")
      elif field == "companyPhone": values.append(self.companyPhone if self.companyPhone else "")
      elif field == "amount": values.append(self.amount if self.amount else "")
      elif field == "unity": values.append(self.unity if self.unity else "")
      elif field == "latitude": values.append(self.latitude if self.latitude else "")
      elif field == "longitude": values.append(self.longitude if self.longitude else "")
      elif field == "saturdayDisponibility": values.append(self.saturdayDisponibility if self.saturdayDisponibility else "")
      elif field == "allQualifications": values.append(self.allQualifications if self.allQualifications else "")
  
      elif field in self.manyToManyObject:
        if dictFormat or not self.id in RamData.ramStructureComplete["Company"][field]:
          listModel = [objectModel.id for objectModel in manyToMany[field].objects.filter(Company=self)]
        else:
          listModel = RamData.ramStructureComplete["Company"][field][self.id]
        values.append(listModel)
      else:
        value = getattr(self, field, "") if getattr(self, field, None) else ""
        values.append(value)
    return values

class Disponibility(CommonModel):
  Company = models.ForeignKey(Company, related_name='CompanyDisponible', on_delete=models.PROTECT, blank=False, null=True, default=None)
  date = models.DateField(verbose_name="Date de disponibilité", null=True, default=None)
  nature = models.CharField('Disponibilité', unique=False, max_length=32, null=True, default="Disponible")

  class Meta:
    verbose_name = "Disponibility"
    unique_together = ('Company', 'date')

  @classmethod
  def generateRamStructure(cls):
    RamData.ramStructure["Company"]["Disponibility"] = deepcopy(RamData.allCompany)
    RamData.ramStructure["Company"]["Notification"] = deepcopy(RamData.allCompany)
    RamData.ramStructure["Company"]["Post"] = deepcopy(RamData.allCompany)
    RamData.ramStructure["Company"]["Mission"] = deepcopy(RamData.allCompany)
    for disponibility in Disponibility.objects.all():
      if not "Disponibility" in RamData.ramStructure["Company"]:
        print("bug 285", RamData.ramStructure["Company"])
      RamData.ramStructure["Company"]["Disponibility"][disponibility.Company.id].append(disponibility.id)
    for notification in Notification.objects.all():
      RamData.ramStructure["Company"]["Notification"][notification.Company.id].append(notification.id)
    

  @classmethod
  def listFields(cls):
    superList = super().listFields()
    superList.remove("Company")
    return superList

  def dump(self): return [self.date.strftime("%Y-%m-%d") if self.date else "", self.nature]

class JobForCompany(CommonModel):
  Job = models.ForeignKey(Job, on_delete=models.PROTECT, blank=False, null=False)
  number = models.IntegerField("Nombre de profils ayant ce metier", null=False, default=1)
  Company = models.ForeignKey(Company, related_name='CompanyJob', on_delete=models.PROTECT, blank=False, null=False)

  @classmethod
  def generateRamStructure(cls):
    RamData.ramStructure["Company"]["JobForCompany"] = deepcopy(RamData.allCompany)
    for jobForCompany in JobForCompany.objects.all():
      if jobForCompany.Company:
        RamData.ramStructure["Company"]["JobForCompany"][jobForCompany.Company.id].append(jobForCompany.id)

  def computeValues(self, listFields, user, dictFormat=False): return [self.Job.id, self.number]

  class Meta:
    unique_together = ('Job', 'Company')
    verbose_name = "JobForCompany"

  @classmethod
  def listFields(cls):
    superList = super().listFields()
    superList.remove("Company")
    return superList

  def dump(self):
    return [self.Job.id, self.number]

class LabelForCompany(CommonModel):
  Label = models.ForeignKey(Label, on_delete=models.PROTECT, blank=False, null=False)
  date = models.DateField(verbose_name="Date de péremption", null=True, default=None)
  Company = models.ForeignKey(Company, related_name='CompanyLabel', on_delete=models.PROTECT, blank=False, null=False)

  class Meta:
    unique_together = ('Label', 'Company')
    verbose_name = "LabelForCompany"

  def computeValues(self, listFields, user, dictFormat=False): return [self.Label.id, self.date.strftime("%Y-%m-%d") if self.date else ""]

  @classmethod
  def generateRamStructure(cls):
    RamData.ramStructure["Company"]["LabelForCompany"] = deepcopy(RamData.allCompany)
    for labelForCompany in LabelForCompany.objects.all():
      RamData.ramStructure["Company"]["LabelForCompany"][labelForCompany.Company.id].append(labelForCompany.id)

  def dump(self):
    return [self.Label.id, self.date.strftime("%Y-%m-%d") if self.date else ""]

  @classmethod
  def listFields(cls):
    superList = super().listFields()
    superList.remove("Company")
    return superList

  # @classmethod
  # def filter(cls, user):
  #   userProfile = UserProfile.objects.get(userNameInternal=user)
  #   company = userProfile.Company
  #   return cls.objects.filter(Company=company)

class UserProfile(CommonModel):
  userNameInternal = models.ForeignKey(User, on_delete=models.PROTECT, null=True, default=None)
  Company = models.ForeignKey(Company, related_name='CompanyProfile', on_delete=models.PROTECT, blank=False, null=False)
  firstName = models.CharField("Prénom", max_length=128, blank=False, default="Inconnu")
  lastName = models.CharField("Nom de famille", max_length=128, blank=False, default="Inconnu")
  proposer = models.IntegerField(blank=False, null=True, default=None)
  cellPhone = models.CharField("Téléphone mobile", max_length=128, blank=False, null=True, default=None)
  token = models.CharField("Token de validation", max_length=512, blank=True, null=True, default="empty token")
  tokenNotification = models.CharField("Token de validation", max_length=512, blank=True, null=True, default="empty token")
  email = models.CharField("Email", max_length=128, blank=True, null=True, default="Inconnu")
  password = models.CharField("Mot de passe", max_length=128, blank=True, null=True, default="Inconnu")
  function = models.CharField("Fonction dans l'entreprise", max_length=128, blank=True, null=True, default="")
  tokenFriend = models.CharField("Token pour invitation d'ami", max_length=128, blank=True, null=True, default="")
  manyToManyObject = ["FavoritePost", "ViewPost"]

  class Meta:
    verbose_name = "UserProfile"

  @classmethod
  def listFields(cls):
    superList = super().listFields()
    superList.remove("token")
    superList.remove("password")
    return superList

  @property
  def userName(self):
    return self.userNameInternal.username

  def getAttr(self, fieldName, answer=False):
    if fieldName == "userName":
      user = self.userNameInternal
      return user.username
    return getattr(self, fieldName, answer)

  def setAttr(self, fieldName, value):
    if fieldName == "userName":
      user = self.userNameInternal
      user.username = value
      user.save()
    else:
      super().setAttr(fieldName, value) 
  
  @classmethod
  def filter(cls, user):
    return [UserProfile.objects.get(userNameInternal=user)]

class FavoritePost(CommonModel):
  UserProfile = models.ForeignKey(UserProfile, related_name='UserProfileforFavorite', on_delete=models.PROTECT, null=True, default=None)
  postId = models.IntegerField("id du Post", blank=True, null=True, default=None)

  class Meta:
    verbose_name = "FavoritePost"
    unique_together = ('UserProfile', 'postId')

  @classmethod
  def listFields(cls):
    return ["Post"]

  @classmethod
  def dictValues(cls, user):
    return [favorite.postId for favorite in cls.filter(user)]

  @classmethod
  def filter(cls, user):
    userProfile = UserProfile.objects.get(userNameInternal=user)
    return [favorite for favorite in cls.objects.filter(UserProfile=userProfile)]



class ViewPost(CommonModel):
  UserProfile = models.ForeignKey(UserProfile, related_name='UserProfileforView', on_delete=models.PROTECT, null=True, default=None)
  postId = models.IntegerField("id du Post", blank=True, null=True, default=None)

  class Meta:
    verbose_name = "ViewPost"
    unique_together = ('UserProfile', 'postId')

  @classmethod
  def listFields(cls):
    return ["Post"]

  @classmethod
  def dictValues(cls, user):
    return [favorite.postId for favorite in cls.filter(user)]

  @classmethod
  def filter(cls, user):
    userProfile = UserProfile.objects.get(userNameInternal=user)
    return [favorite for favorite in cls.objects.filter(UserProfile=userProfile)]

class Post(CommonModel):
  Company = models.ForeignKey(Company, related_name='CompanyOfPost', verbose_name='Société demandeuse', on_delete=models.PROTECT, null=True, default=None) 
  Job = models.ForeignKey(Job, verbose_name='Métier', on_delete=models.PROTECT, null=True, default=None) 
  numberOfPeople = models.IntegerField("Nombre de personne(s) demandées", blank=False, null=False, default=1)
  address = models.CharField("Adresse du chantier", max_length=1024, null=True, default=None)
  latitude = models.FloatField("Latitude", null=True, default=None)
  longitude = models.FloatField("Longitude", null=True, default=None)
  contactName = models.CharField("Nom du contact responsable de la mission", max_length=256, null=True, default=None)
  draft = models.BooleanField("Brouillon ou validé", null=False, default=True)
  manPower = models.BooleanField("Main d'oeuvre ou fourniture et pose", null=False, default=True)
  creationDate = models.DateField(verbose_name="Date de creation de l'annonce", null=False, default=timezone.now)
  dueDate = models.DateField(verbose_name="Date de d'échéance de l'annonce", null=True, default=None)
  startDate = models.DateField(verbose_name="Date de début de chantier", null=True, default=None)
  endDate = models.DateField(verbose_name="Date de fin de chantier", null=True, default=None)
  hourlyStart = models.CharField("Horaire de début de chantier", max_length=128, null=True, default=None)
  hourlyEnd = models.CharField("Horaire de fin de chantier", max_length=128, null=True, default=None)
  hourlyStartChange = models.CharField("Horaire de début de chantier proposé en modification", max_length=128, null=True, default=None)
  hourlyEndChange = models.CharField("Horaire de fin de chantier proposé en modificatio", max_length=128, null=True, default=None)
  amount = models.FloatField("Montant du chantier", null=False, default=0.0)
  currency = models.CharField("Unité monétaire", max_length=128, null=True, default="€")
  unitOfTime = models.CharField("Unité de temps", max_length=128, null=True, default="Prix Journalier")
  counterOffer = models.BooleanField("Autoriser une contre offre", null=False, default=False)
  description = models.CharField("Description du chantier", max_length=4096, null=True, default=None)
  signedByCompany = models.BooleanField("Signature de la PME", null=False, default=False)
  signedBySubContractor = models.BooleanField("Signature du ST", null=False, default=False)
  subContractorContact = models.CharField("Contact chez le sous traitant", max_length=128, null=True, default=None)
  subContractorName = models.CharField("Nom du sous traitant", max_length=128, null=True, default=None)
  quality = models.IntegerField("Qualité du travail fourni", blank=False, null=False, default=0)
  qualityComment = models.TextField("Qualité du travail fourni Commentaire", blank=False, null=False, default="")
  security = models.IntegerField("Respect de la sécurité et de la propreté du chantier", blank=False, null=False, default=0)
  securityComment = models.TextField("Respect de la sécurité et de la propreté du chantier Commentaire", blank=False, null=False, default="")
  organisation = models.IntegerField("Organisation", blank=False, null=False, default=0)
  organisationComment = models.TextField("Organisation Commentaire", blank=False, null=False, default="")
  boostTimestamp = models.FloatField(verbose_name="Timestamp de mise à jour", null=False, default=0.0)

  vibeST = models.IntegerField("Ambiance sur le chantier ST", blank=False, null=False, default=0)
  vibeCommentST = models.TextField("Ambiance sur le chantier ST Commentaire", blank=False, null=False, default="")
  securityST = models.IntegerField("Respect de la sécurité et de la propreté du chantier ST", blank=False, null=False, default=0)
  securityCommentST = models.TextField("Respect de la sécurité et de la propreté du chantier ST Commentaire", blank=False, null=False, default="")
  organisationST = models.IntegerField("Organisation", blank=False, null=False, default=0)
  organisationCommentST = models.TextField("Organisation Commentaire", blank=False, null=False, default="")

  isClosed = models.BooleanField("Fin de la mission", null=False, default=False)

  contract = models.IntegerField("Image du contrat", blank=False, null=True, default=None)
  manyToManyObject = ["DetailedPost", "File", "Candidate", "DatePost"]

  class Meta:
    verbose_name = "Post"

  @classmethod
  def listFields(cls):
      superList = super().listFields()
      for fieldName in ["signedByCompany", "signedBySubContractor", "contract", "subContractorContact", "subContractorName", "quality", "qualityComment", "security", "securityComment", "organisation", "organisationComment", "vibeST", "vibeCommentST", "securityST", "securityCommentST", "organisationST", "organisationCommentST", "isClosed"]:
        index = superList.index(fieldName)
        del superList[index]
      return superList

  @classmethod
  def generateRamStructure(cls):
    RamData.ramStructure["Company"]["Post"] = deepcopy(RamData.allCompany)
    for post in Post.objects.all():
      if not post.subContractorName:
        RamData.ramStructure["Company"]["Post"][post.Company.id].append(post.id)


  @classmethod
  def filter(cls, user):
    listMission = {candidate.Mission.id for candidate in Candidate.objects.all() if candidate.Mission != None}
    company = UserProfile.objects.get(userNameInternal=user).Company
    listBlocked = [block.blocker.id for block in BlockedCandidate.objects.filter(blocked=company, status=True)]
    return [post for post in Post.objects.all() if not post.id in listMission and not post.Company.id in listBlocked]

  def computeValues(self, listFields, user, dictFormat=False):
    values = []
    manyToMany = {"DetailedPost":DetailedPost, "File":File, "Candidate":Candidate, "DatePost":DatePost} #, "DatePost":DatePost
    for field in listFields:
      if field == "Company": values.append(self.Company.id if self.Company else "")
      elif field == "Job": values.append(self.Job.id if self.Job else "")

      elif field == "numberOfPeople": values.append(self.numberOfPeople)
      elif field == "draft": values.append(self.draft)
      elif field == "manPower": values.append(self.manPower)
      elif field == "amount": values.append(self.amount)
      elif field == "currency": values.append(self.currency)
      elif field == "unitOfTime": values.append(self.unitOfTime)
      elif field == "counterOffer": values.append(self.counterOffer)
      elif field == "signedByCompany": values.append(self.signedByCompany)
      elif field == "signedBySubContractor": values.append(self.signedBySubContractor)
      elif field == "quality": values.append(self.quality)
      elif field == "qualityComment": values.append(self.qualityComment)
      elif field == "security": values.append(self.security)
      elif field == "securityComment": values.append(self.securityComment)
      elif field == "organisation": values.append(self.organisation)
      elif field == "organisationComment": values.append(self.organisationComment)
      elif field == "boostTimestamp": values.append(self.boostTimestamp)
      elif field == "vibeST": values.append(self.vibeST)
      elif field == "vibeCommentST": values.append(self.vibeCommentST)
      elif field == "securityST": values.append(self.securityST)
      elif field == "securityCommentST": values.append(self.securityCommentST)
      elif field == "organisationST": values.append(self.organisationST)
      elif field == "organisationCommentST": values.append(self.organisationCommentST)
      elif field == "isClosed": values.append(self.isClosed)

      elif field == "address": values.append(self.address if self.address else "")
      elif field == "latitude": values.append(self.latitude if self.latitude else "")
      elif field == "longitude": values.append(self.longitude if self.longitude else "")
      elif field == "contactName": values.append(self.contactName if self.contactName else "")
      elif field == "hourlyStart": values.append(self.hourlyStart if self.hourlyStart else "")
      elif field == "hourlyEnd": values.append(self.hourlyEnd if self.hourlyEnd else "")
      elif field == "starsST": values.append(self.starsST if self.starsST else "")
      elif field == "starsPME": values.append(self.starsPME if self.starsPME else "")
      elif field == "hourlyStartChange": values.append(self.hourlyStartChange if self.hourlyStartChange else "")
      elif field == "hourlyEndChange": values.append(self.hourlyEndChange if self.hourlyEndChange else "")
      elif field == "description": values.append(self.description if self.description else "")
      elif field == "subContractorContact": values.append(self.subContractorContact if self.subContractorContact else "")
      elif field == "subContractorName": values.append(self.subContractorName if self.subContractorName else "")
      elif field == "contract": values.append(self.contract if self.contract else "")
      
      elif field == "creationDate": values.append(self.dueDate.strftime("%Y-%m-%d") if self.dueDate else "")
      elif field == "dueDate": values.append(self.dueDate.strftime("%Y-%m-%d") if self.dueDate else "")
      elif field == "startDate": values.append(self.startDate.strftime("%Y-%m-%d") if self.startDate else "")
      elif field == "endDate": values.append(self.endDate.strftime("%Y-%m-%d") if self.endDate else "")

      elif field in self.manyToManyObject:
        if self.subContractorName:
          if dictFormat or not self.id in RamData.ramStructureComplete["Mission"][field]:
            listModel = [objectModel.id for objectModel in manyToMany[field].objects.filter(Mission=self)]
          else:
            listModel = RamData.ramStructureComplete["Mission"][field][self.id]
        else:
          if dictFormat or not self.id in RamData.ramStructureComplete["Post"][field]:
            listModel = [objectModel.id for objectModel in manyToMany[field].objects.filter(Post=self)]
          else:
            listModel = RamData.ramStructureComplete["Post"][field][self.id]
        values.append(listModel)
    return values

class Mission(Post):
  class Meta:
    proxy = True
    verbose_name = "Mission"

  @classmethod
  def generateRamStructure(cls):
    RamData.ramStructure["Company"]["Mission"] = deepcopy(RamData.allCompany)
    RamData.ramStructure["Company"]["Post"] = deepcopy(RamData.allCompany)
    for post in Post.objects.all():
      if post.subContractorName:
        RamData.ramStructure["Company"]["Mission"][post.Company.id].append(post.id)
      else:
        RamData.ramStructure["Company"]["Post"][post.Company.id].append(post.id)

  @classmethod
  def listFields(cls):
      superList = [field.name.replace("Internal", "") for field in cls._meta.fields][1:] + cls.manyToManyObject
      for fieldName in ["Candidate", "boostTimestamp"]: #"Company", 
        index = superList.index(fieldName)
        del superList[index]
      return superList

  @classmethod
  def listIndices(cls):
    parentList = super().listIndices()
    listFields = cls.listFields()
    index = listFields.index("contract")
    parentList.append(index)
    parentList.sort()
    return parentList

  def computeValues(self, listFields, user, dictFormat=False):
    listV = super().computeValues(listFields, user, dictFormat)
    cd = [candidate for candidate in Candidate.objects.filter(Mission=self) if candidate.isChoosen][0]
    return listV + [cd.Company.id]

  @classmethod
  def filter(cls, user):
    company = UserProfile.objects.get(userNameInternal=user).Company
    listBlocked = [block.blocker.id for block in BlockedCandidate.objects.filter(blocked=company)]
    return [candidate.Mission for candidate in Candidate.objects.all() if candidate.Mission != None and not candidate.Mission.id in listBlocked]


  # @classmethod
  # def filter(cls, user):
  #   userProfile = UserProfile.objects.get(userNameInternal=user)
  #   jobList = [jobForCompany.Job for jobForCompany in JobForCompany.objects.filter(Company = userProfile.Company)]
  #   if userProfile.Company.allQualifications:
  #     return [candidate.Mission for candidate in Candidate.objects.all() if candidate.Mission != None]
  #   else:
  #     return [candidate.Mission for candidate in Candidate.objects.all() if candidate.Mission != None and (candidate.Company == userProfile.Company or candidate.Mission.Job in jobList)]

class DatePost(CommonModel):
  Post = models.ForeignKey(Post, verbose_name='Annonce associée', related_name='PostDate', on_delete=models.CASCADE, null=True, default=None)
  Mission = models.ForeignKey(Mission, verbose_name='Mission associée', related_name='MissionDate', on_delete=models.CASCADE, null=True, default=None)
  date = models.DateField(verbose_name="Date du chantier", null=False, default=timezone.now)
  deleted = models.BooleanField("A été effacé", null=False, default=False)
  validated = models.BooleanField("A été effacé", null=False, default=True)
  manyToManyObject = ["Supervision", "DetailedPost"]

  class Meta:
    unique_together = ('Post', 'Mission', 'date')
    verbose_name = "DatePost"

  @classmethod
  def listFields(cls):
    superList= super().listFields()
    for fieldName in ["Post", "Mission"]: #"Company", 
        index = superList.index(fieldName)
        del superList[index]
    return superList
  
  @classmethod
  def generateRamStructure(cls):
    RamData.ramStructure["Post"]["DatePost"] = deepcopy(RamData.allPost)
    RamData.ramStructure["Mission"]["DatePost"] = deepcopy(RamData.allMission)
    if not "DatePost" in RamData.ramStructure["Post"]: print("warning bug 820", RamData.ramStructure["Post"])
    if not "DatePost" in RamData.ramStructure["Mission"]: print("warning bug 820", RamData.ramStructure["Mission"])
    for datePost in DatePost.objects.all():
      if datePost.Post:
        RamData.ramStructure["Post"]["DatePost"][datePost.Post.id].append(datePost.id)
        if not "DatePost" in RamData.ramStructure["Post"]:
          print("bug ramStructure 634", RamData.ramStructure["Post"], datePost.Mission.id, datePost.id)
      elif datePost.Mission:
        if not "DatePost" in RamData.ramStructure["Mission"]:
          print("bug ramStructure 636", RamData.ramStructure["Mission"], datePost.Mission.id, datePost.id)
        RamData.ramStructure["Mission"]["DatePost"][datePost.Mission.id].append(datePost.id)

  def computeValues(self, listFields, user, dictFormat=False):
    values = []
    manyToMany = {"Supervision":Supervision, "DetailedPost":DetailedPost}
    for index in range(len(listFields)):
      field = listFields[index]

      if field == "date": values.append(self.date.strftime("%Y-%m-%d") if self.date else "")
      elif field == "deleted": values.append(self.deleted)
      elif field == "validated": values.append(self.validated)
      elif field == "refused": values.append(self.refused)
      else:
        values.append([objectModel.id for objectModel in manyToMany[field].objects.filter(DatePost=self)])
    return values

  def dump(self):
    date = self.date.strftime("%Y-%m-%d") if self.date else ""
    supervisions = [supervision.id for supervision in Supervision.objects.filter(DatePost=self)]

    return [date, self.deleted, self.validated, supervisions]

class Notification(CommonModel):
  Post = models.ForeignKey(Post, verbose_name='Annonce associée', related_name='PostNotification', on_delete=models.PROTECT, null=True, default=None)
  Mission = models.ForeignKey(Mission, verbose_name='Mission associée', related_name='MissionNotification', on_delete=models.PROTECT, null=True, default=None)
  subContractor = models.ForeignKey(Company, verbose_name="Société destinatrice", related_name='SubContractorAuthor', on_delete=models.PROTECT, null=True, default=None)
  Company = models.ForeignKey(Company, verbose_name="Sous traitant associé", related_name='CompanyNotification', on_delete=models.PROTECT, null=True, default=None)
  Role = models.CharField("Rôle effectif durant la notation", max_length=64, null=False, default="PME")
  timestamp = models.FloatField(verbose_name="Timestamp de mise à jour", null=False, default=datetime.datetime.now().timestamp())
  content = models.CharField("Contenu du Post", max_length=1024, null=False, default="")
  hasBeenViewed = models.BooleanField("A été vu", null=False, default=False)
  nature = models.CharField("Nature de la notification", max_length=64, null=False, default="other")
  category = models.CharField("Catégorie de la notification", max_length=64, null=False, default="other")
  title = models.CharField("Nature de la notification", max_length=128, null=False, default="Titre par défaut")
  url = "https://fcm.googleapis.com/fcm/send"
  key = "AAAABTLuxMI:APA91bFfnZnDEzRqfuoZNfhaWH6BtbREG0OdWWxVirhbSoxZkHzJcweXrS5_yREwPI9lZmtFk7Qvht3mi9KkWBVOfjCNsyCUzIwhLMiL5kcEuBgxVZ09E5mDSrSHV-M_0CdZvFoJ56Qn"

  @classmethod
  def generateRamStructure(cls):
    RamData.ramStructure["Company"]["Notification"] = deepcopy(RamData.allCompany)
    for notification in Notification.objects.all():
      RamData.ramStructure["Company"]["Notification"][notification.Company.id].append(notification.id)

  # def computeValues(copy
  # self, listFields, user, dictFormat=False):
  #   print("computeValue, notifications", [notification.id for notification in self.filter(user)])
  #   return [notification.id for notification in self.filter(user)]

  class Meta:
    verbose_name = "Notification"
  
  @classmethod
  def listFields(cls):
    superList= super().listFields()
    for fieldName in ["Company"]:
        index = superList.index(fieldName)
        del superList[index]
    return superList

  @classmethod
  def filter(cls, user):
    userProfile = UserProfile.objects.get(userNameInternal=user)
    notifications = list(Notification.objects.filter(Company=userProfile.Company))
    notifications.sort(key=lambda notification: notification.timestamp, reverse=True)
    return notifications

  def dump(self):
    postId = self.Post.id if self.Post else ""
    missionId = self.Mission.id if self.Mission else ""
    subContractorId = self.subContractor.id if self.subContractor else ""
    return [postId, missionId, subContractorId, self.Role, self.timestamp, self.content, self.content, self.hasBeenViewed, self.nature]

  @classmethod
  def createAndSend(cls, **kwargs):
    notification = cls.objects.create(**kwargs)
    company = notification.Company
    tokenList = [userProfile.tokenNotification for userProfile in UserProfile.objects.filter(Company=company)]
    headers= {'Content-Type': 'application/json', 'Authorization': f'key = {cls.key}'}
    for token in tokenList:
      post = {"notification":{"title":notification.title, "body":notification.content}, "to":token}
      requests.post(cls.url, headers=headers, json=post)



class Candidate(CommonModel):
  Post = models.ForeignKey(Post, verbose_name='Annonce associée', on_delete=models.CASCADE, null=True, default=None)
  Mission = models.ForeignKey(Mission, verbose_name='Mission associée', related_name='selectedMission', on_delete=models.CASCADE, null=True, default=None)
  Company = models.ForeignKey(Company, verbose_name='Sous-Traitant', related_name='selecteCompany', on_delete=models.PROTECT, null=True, default=None)
  contact = models.CharField("Le nom du contact", max_length=128, null=False, default="")
  isChoosen = models.BooleanField("Sous traitant selectionné", null=True, default=False)
  isRefused = models.BooleanField("Sous traitant refusé", null=True, default=False)
  isViewed = models.BooleanField("Candidature vue", null=True, default=False)
  date = models.DateField(verbose_name="Date de candidature ou date d'acceptation", null=False, default=timezone.now)
  amount = models.FloatField("Prix unitaire", null=False, default=0.0)
  unitOfTime = models.CharField("Unité de temps", max_length=128, null=True, default="Prix Total")

  def computeValues(self, listFields, user, dictFormat=False):
    values = []
    for field in listFields:
      if field == "Company": values.append(self.Company.id if self.Company else "")
      elif field == "contact": values.append(self.contact)
      elif field == "isChoosen": values.append(self.isChoosen)
      elif field == "isRefused": values.append(self.isRefused)
      elif field == "isViewed": values.append(self.isViewed)
      elif field == "date": values.append(self.date.strftime("%Y-%m-%d") if self.date else "")
      elif field == "amount": values.append(self.amount)
      elif field == "unitOfTime": values.append(self.unitOfTime)
    return values

  class Meta:
    unique_together = ('Post', 'Mission', 'Company')
    verbose_name = "Candidate"

  @classmethod
  def generateRamStructure(cls):
    RamData.ramStructure["Post"]["Candidate"] = deepcopy(RamData.allPost)
    RamData.ramStructure["Mission"]["Candidate"] = deepcopy(RamData.allMission)
    for candidate in Candidate.objects.all():
      if candidate.Post and candidate.Post.id in RamData.ramStructure["Post"]["Candidate"]:
        RamData.ramStructure["Post"]["Candidate"][candidate.Post.id].append(candidate.id)
      if candidate.Mission and candidate.Mission.id in RamData.ramStructure["Mission"]["Candidate"]:
        RamData.ramStructure["Mission"]["Candidate"][candidate.Mission.id].append(candidate.id)

  @classmethod
  def listFields(cls):
      superList = super().listFields()
      for fieldName in ["Post", "Mission", "unitOfTime"]:
        index = superList.index(fieldName)
        del superList[index]
      return superList

  def dump(self):
    date = self.date.strftime("%Y-%m-%d") if self.date else ""
    return [self.Company.id, self.contact, self.isChoosen, self.isRefused, self.isViewed, date, self.amount, self.unitOfTime]

class DetailedPost(CommonModel):
  Post = models.ForeignKey(Post, related_name='Post', verbose_name='Annonce associée', on_delete=models.PROTECT, null=True, default=None)
  Mission = models.ForeignKey(Mission, related_name='Mission', verbose_name='Mission associée', on_delete=models.PROTECT, null=True, default=None)
  DatePost = models.ForeignKey(DatePost, related_name='DateOfDetail', verbose_name='Date associée', on_delete=models.PROTECT, null=True, default=None)
  content = models.CharField("Détail de la prescription", max_length=256, null=True, default=None)
  validated = models.BooleanField("Validation de la tache", null=False, default=False)
  refused = models.BooleanField("Refus de validation de la tache", null=False, default=False)
  manyToManyObject = ["Supervision"]

  class Meta:
    verbose_name = "DetailedPost"
    unique_together = ('Post', 'Mission', 'DatePost')


  @classmethod
  def listFields(cls):
      superList = super().listFields()
      for fieldName in ["Post", "Mission", 'DatePost']:
        index = superList.index(fieldName)
        del superList[index]
      return superList

  @classmethod
  def generateRamStructure(cls):
    RamData.ramStructure["Post"]["DetailedPost"] = deepcopy(RamData.allPost)
    RamData.ramStructure["Mission"]["DetailedPost"] = deepcopy(RamData.allMission)
    RamData.ramStructure["DatePost"]["DetailedPost"] = deepcopy(RamData.allDatePost)
    for detailed in DetailedPost.objects.all():
      if detailed.Post:
        if not detailed.Post.id in RamData.ramStructure["Post"]["DetailedPost"]:
          print(RamData.ramStructure["Post"]["DetailedPost"])
        RamData.ramStructure["Post"]["DetailedPost"][detailed.Post.id].append(detailed.id)
      if detailed.Mission:
        RamData.ramStructure["Mission"]["DetailedPost"][detailed.Mission.id].append(detailed.id)
      if detailed.DatePost:
        RamData.ramStructure["DatePost"]["DetailedPost"][detailed.DatePost.id].append(detailed.id)

    
  def computeValues(self, listFields, user, dictFormat=False):
    values = []
    for index in range(len(listFields)):
      field = listFields[index]

      if field == "content": values.append(self.content if self.content else "")
      elif field == "date": values.append(self.date.strftime("%Y-%m-%d") if self.date else "")
      elif field == "validated": values.append(self.validated)
      elif field == "refused": values.append(self.refused)

      else:
        if dictFormat or not self.id in RamData.ramStructureComplete["DetailedPost"][field]:
          values.append([objectModel.id for objectModel in Supervision.objects.filter(DetailedPost=self)])
        else:
          values.append(RamData.ramStructureComplete["DetailedPost"][field][self.id])
    return values

  def dump(self):
    return self.computeValues(self.listFields(), None, dictFormat=True)


class Supervision(CommonModel):
  DetailedPost = models.ForeignKey(DetailedPost, verbose_name='Tâche associée', on_delete=models.PROTECT, null=True, default=None)
  DatePost = models.ForeignKey(DatePost, verbose_name='Tâche associée', on_delete=models.PROTECT, null=True, default=None)
  author = models.CharField("Nom de l'auteur du message", max_length=256, null=True, default=None)
  companyId = models.IntegerField("Id de la companie emettrice", blank=True, null=False, default=None)
  date = models.DateField(verbose_name="Date du suivi", null=False, default=timezone.now)
  comment = models.CharField("Commentaire sur le suivi", max_length=4906, null=True, default=None)
  manyToManyObject = ["File"]

  class Meta:
    verbose_name = "Supervision"

  @classmethod
  def listFields(cls):
      superList = super().listFields()
      for fieldName in ["DatePost", "DetailedPost"]:
        index = superList.index(fieldName)
        del superList[index]
      return superList

  @classmethod
  def generateRamStructure(cls):
    RamData.ramStructure["DetailedPost"]["Supervision"] = {detailed.id:[] for detailed in DetailedPost.objects.all()}
    RamData.ramStructure["DatePost"]["Supervision"] = deepcopy(RamData.allDatePost)
    for supervision in Supervision.objects.all():
      if supervision.DetailedPost:
        RamData.ramStructure["DetailedPost"]["Supervision"][supervision.DetailedPost.id].append(supervision.id)
      elif supervision.DatePost:
        RamData.ramStructure["DatePost"]["Supervision"][supervision.DatePost.id].append(supervision.id)

  def computeValues(self, listFields, user, dictFormat=False):
    return self.dump()

  def dump(self):
    files = [file.id for file in File.objects.filter(Supervision = self)]
    return [self.author, self.companyId, self.date.strftime("%Y-%m-%d") if self.date else "", self.comment, files]


class InviteFriend(CommonModel):
  invitationAuthor = models.ForeignKey(UserProfile, related_name='Author', on_delete=models.PROTECT, null=True, default=None)
  emailTarget = models.CharField('email du destinataire', max_length=256, null=False, default="")
  token = models.CharField('token', max_length=64, null=False, default="")
  invitedUser = models.ForeignKey(UserProfile, related_name='Invited', on_delete=models.PROTECT, null=True, default=None)
  date = models.DateField(verbose_name="Date de l'inscription", null=True, default=None)


  class Meta:
    verbose_name = "InviteFriend"

class File(CommonModel):
  nature = models.CharField('nature du fichier', max_length=128, null=False, default=False, blank=False)
  name = models.CharField('Nom du fichier pour le front', max_length=128, null=False, default=False, blank=False)
  path = models.CharField('path', max_length=256, null=False, default=False, blank=False)
  ext = models.CharField('extension', max_length=8, null=False, default=False, blank=False)
  Company = models.ForeignKey(Company, on_delete=models.PROTECT, null=True, default=None)
  expirationDate = models.DateField(verbose_name="Date de péremption", null=True, default=None)
  timestamp = models.FloatField(verbose_name="Timestamp de mise à jour", null=False, default=datetime.datetime.now().timestamp())
  Post = models.ForeignKey(Post, verbose_name="Annonce associée", related_name='selectPost', on_delete=models.PROTECT, null=True, default=None)
  Mission = models.ForeignKey(Mission, verbose_name="Mission associée", related_name='selectMission', on_delete=models.PROTECT, null=True, default=None)
  Supervision = models.ForeignKey(Supervision, verbose_name="Suivi associé", on_delete=models.PROTECT, null=True, default=None)
  dictPath = {"userImage":"./files/avatars/", "labels":"./files/labels/", "admin":"./files/admin/", "post":"./files/posts/", "supervision":"./files/supervisions/", "contract":"./files/contracts/"}
  authorizedExtention = {"png":"png", "PNG":"png", "jpg":"jpg", "JPG":"jpg", "jpeg":"jpg", "JPEG":"jpg", "svg":"svg", "SVG":"svg", "pdf":"pdf", "PDF":"pdf", "HEIC":"heic", "heic":"heic"}

  class Meta:
    unique_together = ('nature', 'name', 'Company', "Post", "Mission", "Supervision")
    verbose_name = "File"

  @classmethod
  def generateRamStructure(cls):
    RamData.ramStructure["Post"]["File"] = deepcopy(RamData.allPost)
    RamData.ramStructure["Mission"]["File"] = deepcopy(RamData.allMission)
    RamData.ramStructure["Company"]["File"] = deepcopy(RamData.allCompany)
    for file in File.objects.all():
      if file.Company:
        RamData.ramStructure["Company"]["File"][file.Company.id].append(file.id)
      if file.Post:
        RamData.ramStructure["Post"]["File"][file.Post.id].append(file.id)
      if file.Mission:
        RamData.ramStructure["Mission"]["File"][file.Mission.id].append(file.id)


  @classmethod
  def listFields(cls):
    superList = super().listFields()
    for fieldName in ["path", "Company", "Post", "Mission", "Supervision"]:
      index = superList.index(fieldName)
      del superList[index]
    superList.append("content")
    return superList

  def dump(self):
    expirationDate = self.expirationDate.strftime("%Y-%m-%d") if self.expirationDate else ""
    return [self.nature, self.name, self.ext, expirationDate, self.timestamp, ""]

  def getAttr(self, fieldName, answer=False):
    if fieldName == "ext":
      if self.ext == "pdf":
        return "jpg"
    if fieldName == "file":
      if self.ext == "pdf":
        return self.encodedStringListForPdf()
      if self.ext.lower() == "heic":
        return [self.decodeHeic()]
      if self.ext.lower() == "svg":
        return [self.decodeSvg()]
      return [self.readFile(self.path)]
    return getattr(self, fieldName, answer)

  def readFile(self, path):
    try:
      with open(path, "rb") as fileData:
          encoded_string = base64.b64encode(fileData.read())
          return encoded_string.decode("utf-8")
    except ValueError:
      print("readFile", os.getcwd(), os.listdir('files/avatars'))
      return None


  def encodedStringListForPdf(self):
    path = self.path.replace(".pdf", "/")
    split = self.path.split("/")
    nameFile = split[-1]
    localPath = f"./{split[1]}/{split[2]}/"
    if not os.path.isdir(path):
      os.mkdir(path)
      os.chdir(localPath)
      images = convert_from_path(f"{nameFile}")
      os.chdir('../../.')
      for index in range(len(images)):
        images[index].save(f'{path}page_{str(index)}.jpg', 'JPEG')
    listFiles, listEncode  = [os.path.join(path, file) for file in os.listdir(path)], []
    for file in listFiles:
      with open(file, "rb") as fileData:
        listEncode.append(base64.b64encode(fileData.read()))
    return [encodedString.decode("utf-8") for encodedString in listEncode]

  def decodeHeic(self):
    equivJpg = self.path.replace(f"{self.ext}", "jpg")
    if not os.path.exists(equivJpg):
      with open(self.path, "rb") as fileData:
        bytesIo = fileData.read()
        imageType = whatimage.identify_image(bytesIo)
        if imageType in ['heic', 'avif']:
          image = pyheif.read_heif(bytesIo)
          picture = Image.frombytes(mode=image.mode, size=image.size, data=image.data)
          picture.save(equivJpg, format="jpeg")
    return self.readFile(equivJpg)

  def decodeSvg(self):
    equivJpg = self.path.replace(f"{self.ext}", "png")
    if not os.path.exists(equivJpg):
      with open(self.path, "rb") as fileData:
        bytesIo = fileData.read()
        svg2png(bytestring=bytesIo, write_to=equivJpg)
    return self.readFile(equivJpg)

  @classmethod
  def findAvatar(cls, user):
    userProfile = UserProfile.objects.get(userNameInternal=user)
    file = cls.objects.filter(nature="userImage", Company=userProfile.Company)
    if file:
      return file[0].getAttr("file")
    return {}

  @classmethod
  def createFile(cls, nature, name, ext, user, expirationDate = None, post=None, mission=None, detailedPost=None, supervision=None, suppress = False):
    userProfile = UserProfile.objects.get(userNameInternal=user)
    objectFile, mission = None, None
    if nature == "userImage":
      path = cls.dictPath[nature] + userProfile.Company.name + '_' + str(userProfile.Company.id) + '.' + ext
    if nature in ["labels", "admin"]:
      path = cls.dictPath[nature] + name + '_' + str(userProfile.Company.id) + '.' + ext
    if nature == "post":
      path = cls.dictPath[nature] + name + '_' + str(post.id) + '.' + ext
    if nature == "supervision":
      endName = '_' + str(mission.id) if mission else '_N'
      endName += '_' + str(detailedPost.id) if detailedPost else '_N'
      endName += '_' + str(supervision.id) if supervision else '_N'
      objectFiles = File.objects.filter(nature=nature, Supervision=supervision)
      endName += "_" + str(len(objectFiles))
      name +=  endName
      path = cls.dictPath[nature] + name + '.' + ext
    if nature == "contract":
      mission = post
      post = None
      path = cls.dictPath[nature] + name + '_' + str(mission.id) + '.' + ext
    company = userProfile.Company if not post and not supervision else None
    objectFile = File.objects.filter(nature=nature, name=name, Company=company, Post=post, Mission=mission, Supervision=supervision)
    if objectFile:
      objectFile = objectFile[0]
      oldPath = objectFile.path
      if os.path.exists(oldPath) and suppress:
        os.remove(oldPath)
        if objectFile.ext == "pdf":
          pathToRemove = objectFile.path.replace(".pdf", "/")
          shutil.rmtree(pathToRemove, ignore_errors=True)
      objectFile.path = path
      objectFile.timestamp = datetime.datetime.now().timestamp()
      objectFile.ext = ext
      if expirationDate:
        objectFile.expirationDate = expirationDate
      objectFile.save()
    else:
      objectFile = cls.objects.create(nature=nature, name=name, path=path, ext=ext, Company=company, expirationDate=expirationDate, Post=post, Mission=mission, Supervision=supervision)
    return objectFile

class BlockedCandidate(CommonModel):
  blocker = models.ForeignKey(Company, verbose_name='Company who is blocking', related_name='blocking', on_delete=models.PROTECT, null=True, default=None)
  blocked = models.ForeignKey(Company, verbose_name='Company who is blocked', related_name='blocked', on_delete=models.PROTECT, null=True, default=None)
  status= models.BooleanField("Status du bloqué", null=False, default=False)
  date = models.DateField(verbose_name="Date de l'inscription", null=True, default=None)

  class Meta:
    verbose_name = "BlockedCandidate"
    unique_together = ('blocker', 'blocked')

class Recommandation(CommonModel):
  companyRecommanded =  models.ForeignKey(Company, verbose_name='Company who is recommanded', related_name='recommanded', on_delete=models.PROTECT, null=True, default=None)
  firstNameRecommanding = models.CharField('first name of recommander', max_length=128, null=False, default="", blank=True)
  lastNameRecommanding = models.CharField('last name of recommander', max_length=128, null=False, default="", blank=True)
  companyNameRecommanding = models.CharField('company name of recommander', max_length=128, null=False, default="", blank=True)
  qualityStars = models.IntegerField("Notation sous forme d'étoile", null=False, default=0.0)
  qualityComment = models.CharField('company name of recommander', max_length=3000, null=False, default="", blank=True)
  securityStars = models.IntegerField("Notation sous forme d'étoile", null=False, default=0.0)
  securityComment = models.CharField('company name of recommander', max_length=3000, null=False, default="", blank=True)
  organisationStars = models.IntegerField("Notation sous forme d'étoile", null=False, default=0.0)
  organisationComment = models.CharField('company name of recommander', max_length=3000, null=False, default="", blank=True)
  date = models.DateField(verbose_name="Date de l'inscription", null=True, default=None)

  class Meta:
    verbose_name = "Recommandation"
    unique_together = ('companyRecommanded', 'companyNameRecommanding')



