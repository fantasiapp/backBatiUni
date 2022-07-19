import requests
# from ..models import File
import os
import cv2
from bs4 import BeautifulSoup

class TreatFile:
  file = None
  headersKbis = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
  beforeDateKbis = "Document commandé sur infogreffe le :"
  beforeNameKbis = "Dénomination :"
  beforeRcsKbis = "N° d’immatriculation :"

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
      result = self.__computeResultFromQrCode(linkKbis, textInHtml.splitlines())
      return (True, result)
    return (False, "Votre KBis n'est pas reconnu")


  def __computeResultFromQrCode(self, link, lines):
    print("__computeResultFromQrCode", link)
    response = self.__computeResultFromKbisWithLink(link)
    linesStrip = [line.strip() for line in lines if line.strip()]
    beforeDate, beforeName, beforeRcs = False, False, False
    for line in linesStrip:
      if beforeDate:
        response["kBisDate"] = line[0:10]
        beforeDate = False
      if beforeName:
        response["name"] = line
        beforeName = False
      if beforeRcs:
        response["RCS"] = line
        beforeRcs = False
      
      if line == self.beforeDateKbis:
        beforeDate = True
      if line == self.beforeNameKbis:
        beforeName = True
      if line == self.beforeRcsKbis:
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
      html = request.content.decode()
      soup = BeautifulSoup(html, features="html.parser")
      textInHtml = soup.get_text()
      lines = [line.strip() for line in textInHtml.splitlines() if line.strip]
      chunks = "\n".join(lines)
      for line in lines:
        print(line)
    return result
    


  
