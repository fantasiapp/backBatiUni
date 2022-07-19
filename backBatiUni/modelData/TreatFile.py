import requests
# from ..models import File
import os
import cv2
from bs4 import BeautifulSoup

class TreatFile:
  file = None
  headersKbis = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
  beforeDateKbis = "Document commandé sur infogreffe le :"
  beforeNameKbis = "Dénomination"
  beforeRcsKbis = "N° d’immatriculation :"

  def __init__(self, file):
    self.file = file

  @property
  def getPages(self):
    print("getPages")
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
    print("getPages", listPage)
    return listPage

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
    print("readFromQrCode")
    url, linkKbis = self.__getUrlFromQrCode(), None
    if url:
      try:
        request = requests.get(url, headers=self.headersKbis)
      except:
        return (False, "unrecognize url")
      html = request.content.decode()
      soup = BeautifulSoup(html, features="html.parser")
      for link in soup.findAll('a'):
        if "/entreprise-societe/" in link:
          linkKbis = "https:/"+link

      textInHtml = soup.get_text()
      lines = (line.strip() for line in textInHtml.splitlines())
      chunks = (phrase.strip() for line in lines for phrase in line.split("  ") if line.strip())
      finalText = '\n'.join(chunk for chunk in chunks if chunk)

      if 'La commande est supérieure à 3 mois' in finalText :
        return (False, "Le KBis est obsolette, il date de plus de 3 mois")
      if 'Aucun document trouvé pour ce code de vérification' in finalText :
        return (False, "Le KBis n'est pas reconnu")
      print("result")
      result = self.__computeResultFromQrCode(linkKbis, textInHtml.splitlines())
      return (True, result)
    return (False, "Votre KBis n'est pas reconnu")


  def __computeResultFromQrCode(self, link, lines):
    print("__computeResultFromQrCode")
    response = {"link":link}
    linesStrip = [line.strip() for line in lines if line]
    beforeDate, beforeName, beforeRcs = False, False, False
    for line in linesStrip:
      print("line", line)
      if line == self.beforeDateKbis:
        beforeDate = True
        print("beforeDate")
      if beforeDate:
        response["kBisDate"] = line[0:11]
        print("kBisDate", line)
        beforeDate = False
      if line == self.beforeNameKbis:
        beforeName = True
        print("beforeNameKbis")
      if beforeName:
        response["name"] = line
        print("beforeNameKbis", line)
        beforeName = False
      if line == self.beforeRcsKbis:
        beforeRcs = True
        print("beforeRcsKbis")
      if beforeRcs:
        response["RCS"] = line
        print("beforeRcsKbis", line)
        beforeRcs = False

    print("lines", linesStrip)
    return response
    


  
