import requests
# from ..models import File
import os
import cv2
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
import base64

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

  def __init__(self, file):
    self.file = file

  @property
  def getPages(self):
    listPage = []
    filePath = self.file.path
    pathSplit = filePath.split('.')
    pathSplit.pop(-1)
    if self.file.ext == "pdf":
      self.file.encodedStringListForPdf()
      path = '.'.join(pathSplit)+'/'
      listDir = os.listdir('.'.join(pathSplit)+'/')
      for pages in listDir:
        listPage.append(path + pages)
    else :
      listPage = [filePath]
    return listPage


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
      print("le nom a testé (censé être Kbis) : ", objectFile.name, objectFile.name == "Kbis")
      if objectFile.name == "Kbis":
        detectObject = TreatFile(objectFile)
        status, value = detectObject.readFromQrCode()
        if status:
          print("__createFileWidthb64 Kbis", value)
        else:
          if objectFile: objectFile.delete()
          return {"uploadFile":"Error", "messages":f"{value}"}
      return {queryName:"OK", objectFile.id:objectFile.computeValues(objectFile.listFields(), currentUser, True)}
    except:
      if objectFile: objectFile.delete()
      return {queryName:"Warning", "messages":"Le fichier ne peut être sauvegardé"}

  """Fonctions associées au QR Code"""

  def __getUrlFromQrCode (self):
    for page in self.getPages:
      image = cv2.imread(page)
      decoder = cv2.QRCodeDetector()
      url, _, _ = decoder.detectAndDecode(image)
      if url:
        print("url", url)
        return url
    return False

  def readFromQrCode(self):
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
          linkKbis = "https://www.infogreffe.fr" + link

      textInHtml = soup.get_text()
      lines = [line.strip() for line in textInHtml.splitlines() if line.strip()]
      finalText = "\n".join(lines)

      if 'La commande est supérieure à 3 mois' in finalText :
        return (False, "Le KBis est obsolette, il date de plus de 3 mois")
      if 'Aucun document trouvé pour ce code de vérification' in finalText :
        return (False, "Le KBis n'est pas reconnu")
      result = self.__computeResultFromQrCode(linkKbis, lines)
      return (True, result)
    return (False, "Votre KBis n'est pas reconnu")


  def __computeResultFromQrCode(self, link, lines):
    response = self.__computeResultFromKbisWithLink(link)
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
      print(link, self.headersKbis)
      try:
        request = requests.get(link, headers=self.headersKbis)
      except:
        request = None
    print("request", request)
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
    


  
