import requests
# from ..models import File
import os
import cv2
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
import base64
from shutil import rmtree
from pdf2image import convert_from_path

class TreatFile:
  file = None
  headersKbis = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
  beforeDateKbis = "Document commandé sur infogreffe le :"
  beforeNameKbis = "Dénomination :"
  beforeRcsKbis = "N° d’immatriculation :"
  linkElementKbis = "/entreprise-societe/"
  startLinkKbis = "https://www.infogreffe.fr"
  beforeAddressKbis = "Siège social"
  afterAddressKbis = "Voir le plan"
  beforeSiretKbis = "Siret"
  obsoleteKbis = 'La commande est supérieure à 3 mois'
  noDocumentKbis = 'Aucun document trouvé pour ce code de vérification'
  dictPath = {"userImage":"./files/avatars/", "labels":"./files/labels/", "admin":"./files/admin/", "post":"./files/posts/", "supervision":"./files/supervisions/", "contract":"./files/contracts/"}
  authorizedExtention = {"png":"png", "PNG":"png", "jpg":"jpg", "JPG":"jpg", "jpeg":"jpg", "JPEG":"jpg", "svg":"svg", "SVG":"svg", "pdf":"pdf", "PDF":"pdf", "HEIC":"heic", "heic":"heic"}

  def __init__(self, file):
    self.file = file

  @property
  def getPages(self):
    listPage = []
    filePath = self.file.path
    pathSplit = filePath.split('.')
    pathSplit.pop(-1)
    if self.file.ext == "pdf":
      self.encodedStringListForPdf()
      path = '.'.join(pathSplit)+'/'
      listDir = os.listdir('.'.join(pathSplit)+'/')
      for pages in listDir:
        listPage.append(path + pages)
    else :
      listPage = [filePath]
    return listPage

  @classmethod
  def getPathAndName(cls, name, nature, userProfile, ext, post, mission, supervision):
    path= None
    if nature == "userImage":
      path = cls.dictPath[nature] + userProfile.Company.name + '_' + str(userProfile.Company.id) + '.' + ext
    if nature in ["labels", "admin"]:
      path = cls.dictPath[nature] + name + '_' + str(userProfile.Company.id) + '.' + ext
    if nature == "post":
      path = cls.dictPath[nature] + name + '_' + str(post.id) + '.' + ext
    if nature == "supervision":
      endName = '_' + str(mission.id) if mission else '_N'
      endName += '_' + str(supervision.id) if supervision else '_N'
      objectFiles = File.objects.filter(nature=nature, Supervision=supervision)
      endName += "_" + str(len(objectFiles))
      name +=  endName
      path = cls.dictPath[nature] + name + '.' + ext
    if nature == "contract":
      path = cls.dictPath[nature] + name + '_' + str(mission.id) + '.' + ext
    return path, name, mission

  def removeOldFile(self, suppress):
    print("removeOldFile")
    oldPath = self.file.path
    if os.path.exists(oldPath) and suppress:
      os.remove(oldPath)
      if self.file.ext == "pdf":
        pathToRemove = self.file.path.replace(".pdf", "/")
        rmtree(pathToRemove, ignore_errors=True)

  @classmethod
  def createFileWidthb64(cls, objectFile, fileStr, currentUser, queryName):
    file = None
    try:
      file = ContentFile(base64.urlsafe_b64decode(fileStr), name=objectFile.path) if objectFile.ext != "txt" else fileStr
      with open(objectFile.path, "wb") as outfile:
        outfile.write(file.file.getbuffer())
    except:
      if objectFile: objectFile.delete()
      return {queryName:"Warning", "messages":"Le fichier ne peut être sauvegardé"}
    try :
      if objectFile.name == "Kbis":
        detectObject = TreatFile(objectFile)
        status, value = detectObject.__readFromQrCode()
        if not status:
          if objectFile: objectFile.delete()
        return {"uploadFile":"Error", "messages":f"{value}"}
      return {queryName:"OK", objectFile.id:objectFile.computeValues(objectFile.listFields(), currentUser, True)}
    except:
      if objectFile: objectFile.delete()
      return {queryName:"Warning", "messages":"Le fichier ne peut être sauvegardé"}

  """Fonctions associées au formatage d'images"""

  def encodedStringListForPdf(self):
    referencepath = os.getcwd()
    path = self.file.path.replace(".pdf", "/")
    split = self.file.path.split("/")
    nameFile = split[-1]
    localPath = f"./{split[1]}/{split[2]}/"
    if not os.path.isdir(path):
      os.mkdir(path)
      os.chdir(localPath)
      try:
        images = convert_from_path(f"{nameFile}")
        os.chdir(referencepath)
        for index in range(len(images)):
          images[index].save(f'{path}page_{str(index)}.jpg', 'JPEG')
      except:
        print("error : no PDF to convert")
      os.chdir(referencepath)
    listFiles, listEncode  = [os.path.join(path, file) for file in os.listdir(path)], []
    for file in listFiles:
      with open(file, "rb") as fileData:
        listEncode.append(base64.b64encode(fileData.read()))
    return [encodedString.decode("utf-8") for encodedString in listEncode]

  """Fonctions associées au QR Code"""

  def __getUrlFromQrCode (self):
    for page in self.getPages:
      image = cv2.imread(page)
      decoder = cv2.QRCodeDetector()
      url, _, _ = decoder.detectAndDecode(image)
      if url: return url
    return False

  def __readFromQrCode(self):
    url, linkKbis = self.__getUrlFromQrCode(), None
    if url:
      try:
        request = requests.get(url, headers=self.headersKbis)
      except:
        return (False, "unrecognize url")
      html = request.content.decode()
      soup = BeautifulSoup(html, features="html.parser")
      for element in soup.findAll('a'):
        link = element.get('href')
        if self.linkElementKbis in link:
          linkKbis = self.startLinkKbis + link

      textInHtml = soup.get_text()
      lines = [line.strip() for line in textInHtml.splitlines() if line.strip()]
      finalText = "\n".join(lines)

      if self.obsoleteKbis in finalText :
        return False, "Le KBis est obsolette, il date de plus de 3 mois"
      if self.noDocumentKbis in finalText :
        return False, "Le KBis n'est pas reconnu"
      if linkKbis:
        response = self.__computeResultFromQrCode(linkKbis, lines)
        if response:
          return True, response
    return False, "Le KBis n'est pas reconnu"


  def __computeResultFromQrCode(self, link, lines):
    response = self.__computeResultFromKbisWithLink(link)
    if response:
      beforeDate, beforeName, beforeRcs = False, False, False
      for line in lines:
        if beforeDate:
          response["kBisDate"] = line[0:10]
          beforeDate = False
        elif beforeName:
          response["name"] = line
          beforeName = False
        elif beforeRcs:
          response["RCS"] = line
          beforeRcs = False
        
        elif line == self.beforeDateKbis:
          beforeDate = True
        elif line == self.beforeNameKbis:
          beforeName = True
        elif line == self.beforeRcsKbis:
          beforeRcs = True
    return response

  def __computeResultFromKbisWithLink(self, link):
    result = {}
    if link:
      try:
        request = requests.get(link, headers=self.headersKbis)
      except:
        request = None
    if request:
      beforeAddress, address, siretKbis = False, "", False
      html = request.content.decode()
      soup = BeautifulSoup(html, features="html.parser")
      textInHtml = soup.get_text()
      lines = [line.strip() for line in textInHtml.splitlines() if line.strip()]

      for line in lines:
        if self.afterAddressKbis in line:
          beforeAddress = False

        elif beforeAddress:
          address += line + ", "
        elif siretKbis:
          result["Siret"] = line
          siretKbis = False
        
        elif self.beforeAddressKbis in line and not address:
          beforeAddress = True
        elif self.afterAddressKbis in line:
          beforeAddress = False
        elif self.beforeSiretKbis in line:
          siretKbis = True

      if address: result["address"] = address.strip(", ")
    return result
    


  
