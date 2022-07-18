import requests
# from ..models import File
import os

class DetectQrCode:
  file = None

  def __init__(self, file):
    print("create detectQrCode")
    self.file = file

  @property
  def getPages(self):
    print("getPages")
    listPage = []
    filePath = self.file.path
    pathSplit = filePath.split('.')
    pathSplit.pop(-1)
    print("before")
    if self.ext == "pdf":
      print("pdf loop")
      self.file.encodedStringListForPdf()
      print("encode done")
      path = '.'.join(pathSplit)+'/'
      listDir = os.listdir('.'.join(pathSplit)+'/')
      for pages in listDir:
        listPage.append(path + pages)
      print("finished")
    else :
      print("second linge")
      listPage = [filePath]
    return listPage