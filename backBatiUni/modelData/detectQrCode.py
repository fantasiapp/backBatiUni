import requests
# from ..models import File
import os
import cv2

class DetectQrCode:
  file = None

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

  def readQrCode (self):
    print("readQrCodeStart")
    print("readQrCodeStart", self.getPages)
    for page in self.getPages:
      image = cv2.imread(page)
      print("image")
      decoder = cv2.QRCodeDetector()
      print("decoder")
      data, _, _ = decoder.detectAndDecode(image)
      print("data")
      if data: return data
      print()
    return False
