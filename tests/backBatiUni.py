import requests
import json
import sys
from PIL import Image
import os
import base64
from io import BytesIO
import random
import string
import math

userName, password = "st", "pwd"
# userName, password = "jlw", "pwd"
# userName, password = "jeanluc.walter@fantasiapp.com", "123456Aa"
address = 'http://localhost:8000'
query = "token"

arguments = sys.argv
if len(arguments) > 1:
    host = arguments[1]
    if host == "local": address = 'http://localhost:8000'
    elif host == "temp": address = 'https://batiuni.fantasiapp.tech:5004'
    elif host == "work": address = 'https://batiuni.fantasiapp.tech:5001'
    elif host == "current": address = 'https://batiuni.fantasiapp.tech:5002'
    elif host == "distrib": address = 'https://batiuni.fantasiapp.tech:5003'
    elif host == "distrib2": address = 'https://batiuni.fantasiapp.tech:5005'
if len(arguments) > 2:
  query = arguments[2]

def queryForToken(userName, password):
  print("queryForToken", userName, password)
  tokenUrl = f'{address}/api-token-auth/'
  headers = {'Content-Type': 'application/json'}
  data = json.dumps({"username": userName, "password": password})
  response = requests.post(tokenUrl, headers=headers, data=data)
  dictResponse = json.loads(response.text)
  print(dictResponse)
  return dictResponse['token']

def getDocStr(index = 0):
  file = ["./files/documents/Qualibat.jpeg", "./files/documents/Kbis.png", "./files/documents/Plan.png", "./files/documents/IMG_2465.HEIC", "./files/documents/etex.svg", "./files/documents/batiUni.png", "./files/documents/Fantasiapp.png", "./files/documents/logoFantasiapp.png"]
  with open(file[index], "rb") as fileData:
    encoded_string = base64.b64encode(fileData.read())
  return encoded_string.decode("utf-8")

def executeQuery():
  print()
  print("query", query)
  now, data, response, url , headers = "2022/01/12", None, None, f'{address}/initialize/', {"content-type":"Application/Json"}
  if query == "register":
    headers = {}
    post1 = {"firstname":"Augustin","lastname":"Alleaume","email":"aa","password":"pwd","company":{'id': 2, 'name': 'BATIUNI', 'address': '9 rue Vintimille Paris 75009', 'activity': 'Activité inconnue', 'siret': '40422352100018', 'ntva': 'FR49404223521'},"Role":3,"proposer":"","jobs":[1,2,80]}
    post2 = {"firstname":"Théophile","lastname":"Traitant","email":"st","password":"pwd","company":{'id': 3, 'name': 'Sous-traitant', 'address': '74 ave des Sous-traitants Paris 75008', 'activity': 'Activité inconnue', 'siret': '40422352100021', 'ntva': 'FR49404223522'},"Role":2,"proposer":"","jobs":[1,2,80]}
    post3 = {"firstname":"Eric","lastname":"Entreprise","email":"pme","password":"pwd","company":{'id': 4, 'name': 'PME', 'address': '74 ave des PME Paris 75008', 'activity': 'Activité inconnue', 'siret': '40422352100019', 'ntva': 'FR49404223523'},"Role":1,"proposer":"","jobs":[1,2,9]}
    post4 = {"firstname":"a","lastname":"a","email":"both","password":"pwd","company":{'id': 5, 'name': 'both', 'address': '74 ave des deux Paris 75008', 'activity': 'Activité inconnue', 'siret': '40422352100020', 'ntva': 'FR4940422352'},"Role":3,"proposer":"","jobs":[1,2,80]}
    post5 = {"firstname":"Tanguy","lastname":"Traitant","email":"st2","password":"pwd","company":{'id': 6, 'name': 'Sous-traitant 2', 'address': '78 rue des Sous-traitants Paris 75008', 'activity': 'Activité inconnue', 'siret': '40422352100048', 'ntva': 'FR49404223553'},"Role":2,"proposer":"","jobs":[1,2,80]}
    for post in [post1, post2, post3, post4, post5]:
      response = requests.post(url, headers=headers, json=post)
  elif query == "registerMany":
    company = ''.join(random.choice(string.ascii_letters) for x in range(3))
    companies = requests.get(f'{address}/initialize/', headers=headers, params={"action":"getEnterpriseDataFrom", "subName":company})
    data = json.loads(companies.text)
    establishmentsFields = data["EstablishmentsFields"]
    establishmentsValues = data["EstablishmentsValues"]
    for i in range(len(establishmentsValues)):
      establishmentValue = establishmentsValues[str(i)]
      print(establishmentValue)
    print(establishmentsFields, len(establishmentsValues))
  elif query == "registerConfirm":
      print("registerConfirm", url)
      requests.get(f'{address}/initialize/', headers=headers, params={"action":"registerConfirm", "token":"A secret code to check 9243672519"})
      requests.get(f'{address}/initialize/', headers=headers, params={"action":"registerConfirm", "token":"A secret code to check 9243672519"})
      requests.get(f'{address}/initialize/', headers=headers, params={"action":"registerConfirm", "token":"A secret code to check 9243672519"})
      requests.get(f'{address}/initialize/', headers=headers, params={"action":"registerConfirm", "token":"A secret code to check 9243672519"})
      response = requests.get(f'{address}/initialize/', headers=headers, params={"action":"registerConfirm", "token":"A secret code to check 9243672519"})
  elif query == "getGeneralData":
    response = requests.get(url, headers=headers, params={"action":"getGeneralData"})
  elif query == "forgetPassword":
      response = requests.get(url, headers=headers, params={"action":"forgetPassword", "email":"walter.jeanluc@gmail.com"})
  else:
    if query in ["emptyDB", "buildDB"]:
      token = queryForToken("jlw", "pwd")
      print("user jlw")
    elif query in ["uploadPost" , "modifyPost", "getPost", "switchDraft", "handleCandidateForPost", "modifyMissionDate", "getUserData", "closeMission", "notificationViewed", "boostDuration"]:
      print("user pme")
      token = queryForToken("pme", "pwd")
    else:
      token = queryForToken("st", "pwd")
    if query == "token":
      print("token", token)
    url = f'{address}/data/'
    headers = {'Authorization': f'Token {token}'}
    if query == "getUserData":
      # token = queryForToken("st", "pwd")
      # headers = {'Authorization': f'Token {token}'}
      # print("user = st")
      response = requests.get(url, headers=headers, params={"action":"getUserData"})
    elif query == "postModifyPwd":
      post = {"action":"modifyPwd", "oldPwd":"pwd", "newPwd":"pwd"}
      response = requests.post(url, headers=headers, json=post)
    elif query == "modifyUser":
      now = "2022-01-12"
      post1 = {'action': 'modifyUser', 'UserProfile': {'id': 3, 'cellPhone': '06 29 35 04 18', 'Company': {'capital': '307130', 'companyPhone': '08 92 97 64 15', "allQualifications":True, 'JobForCompany':[[4,2], [5,3], [77,4]], 'LabelForCompany':[[1,now], [2,now]]}}}
      post2 = {'action': 'modifyUser', 'UserProfile': {'id': 6, 'cellPhone': '06 28 34 03 17', 'Company': {'capital': '207130', 'companyPhone': '08 91 96 63 14', "allQualifications":True, 'JobForCompany':[[4,2], [5,3], [77,4]], 'LabelForCompany':[[1,now], [2,now]]}}}
      requests.post(url, headers=headers, json=post1)
      response = requests.post(url, headers=headers, json=post2)
    elif query == "changeUserImage":
      tokenPme = queryForToken("pme", "pwd")
      headersPme = {'Authorization': f'Token {tokenPme}'}
      post = {'action':"changeUserImage", "ext":"png", "name":"BatiUni_1", "imageBase64":getDocStr(5)}
      requests.post(url, headers=headersPme, json=post)
      tokenPme = queryForToken("st2", "pwd")
      headersSt2 = {'Authorization': f'Token {tokenPme}'}
      post = {'action':"changeUserImage", "ext":"png", "name":"SousTtraitant2_1", "imageBase64":getDocStr(7)}
      response = requests.post(url, headers=headersSt2, json=post)
      post = {'action':"changeUserImage", "ext":"png", "name":"Fantasiapp_1", "imageBase64":getDocStr(6)}
      requests.post(url, headers=headers, json=post)
    elif query == "uploadPost":
      post1 = {'action':"uploadPost", "longitude":2.237779 , "latitude":48.848776, "address":"128 rue de Paris 92100 Boulogne", "Job":6, "numberOfPeople":3, "dueDate":"2022-04-15", "startDate":"2022-02-16", "endDate":"2022-02-28", "DatePost":["2022-04-26", "2022-04-27", "2022-04-28"], "manPower":True, "counterOffer":True, "hourlyStart":"07:30", "hourlyEnd":"17:30", "currency":"€", "description":"Première description d'un chantier", "amount":65243.10, "DetailedPost":["lavabo", "baignoire"]}
      post2 = {'action':"uploadPost", "longitude":2.324877 , "latitude":48.841625, "address":"106 rue du Cherche-Midi 75006 Paris", "Job":5, "numberOfPeople":1, "dueDate":"2022-04-15", "startDate":"2022-03-16", "endDate":"2022-04-28", "DatePost":["2022-05-16", "2022-05-17", "2022-05-18"], "manPower":False, "counterOffer":True, "hourlyStart":"07:00", "hourlyEnd":"17:00", "currency":"€", "description":"Deuxième description d'un chantier", "amount":23456.10, "DetailedPost":["radiateur", "Chaudière"]}
      post3 = {'action':"uploadPost", "longitude":2.326881 , "latitude":48.841626, "address":"36 rue Dauphine 75006 Paris", "Job":10, "numberOfPeople":1, "dueDate":"2022-04-15", "startDate":"2022-03-16", "endDate":"2022-04-28", "DatePost":["2022-04-15", "2022-04-16", "2022-04-17", "2022-04-18"], "manPower":True, "counterOffer":True, "hourlyStart":"07:00", "hourlyEnd":"17:00", "currency":"€", "description":"troisième description d'un chantier", "amount":12345.10, "DetailedPost":["doublage", "cloison"]}
      post4 = {'action':"uploadPost", "longitude":2.325883 , "latitude":48.841627, "address":"28 rue de Fleurus 75006 Paris", "Job":10, "numberOfPeople":2, "dueDate":"2022-04-18", "startDate":"2022-03-16", "endDate":"2022-04-28", "DatePost":["2022-04-21", "2022-04-22", "2022-04-23"], "manPower":True, "counterOffer":False, "hourlyStart":"07:00", "hourlyEnd":"17:00", "currency":"€", "description":"quatrième description d'un chantier", "amount":1300.10, "DetailedPost":["doublage", "cloison", "pose", "mesure"]}
      post5 = {'action':"uploadPost", "longitude":2.325885 , "latitude":48.841628, "address":"34 rue Guynemer 75006 Paris", "Job":10, "numberOfPeople":1, "dueDate":"2022-04-21", "startDate":"2022-04-16", "endDate":"2022-04-28", "DatePost":["2022-04-16", "2022-04-17", "2022-04-18"], "manPower":True, "counterOffer":False, "hourlyStart":"08:00", "hourlyEnd":"17:00", "currency":"€", "description":"cinquième description d'un chantier", "amount":1300.10, "DetailedPost":["cuisine", "salle de bain", "salon", "Chambre"]}
      post6 = {'action':"uploadPost", "longitude":2.324877 , "latitude":48.841625, "address":"108 rue du Cherche-Midi 75006 Paris", "Job":5, "numberOfPeople":1, "dueDate":"2022-04-15", "startDate":"2022-04-16", "endDate":"2022-04-28", "DatePost":["2022-04-26", "2022-04-27", "2022-04-28"], "manPower":False, "counterOffer":True, "hourlyStart":"07:00", "hourlyEnd":"17:00", "currency":"€", "description":"Sixième description d'un chantier", "amount":23456.10, "DetailedPost":["radiateur", "Chaudière"]}
      for post in [post1, post2, post3, post4, post5, post6]:
        response = requests.post(url, headers=headers, json=post)

      for i in range(50):
        street = ''.join(random.choice(string.ascii_letters) for x in range(8))
        city = ''.join(random.choice(string.ascii_letters) for x in range(8))
        counterOffer = random.random() > .5
        startDate = math.floor(5 + random.random() * 20)
        post = {
          'action':"uploadPost",
          "longitude":2.237779 + random.random() / 10000 ,
          "latitude":48.848776 + random.random() / 10000,
          "address":f"{math.floor(1 + random.random() * 50)} rue de {street} {city}",
          "Job":math.floor(1 + random.random() * 140),
          "numberOfPeople":math.floor(1 + random.random() * 10),
          "dueDate":f"2022-06-{str(startDate - 1)}",
          "startDate":f"2022-06-{str(startDate)}",
          "endDate":f"2022-06-{str(startDate + 3)}",
          "DatePost":[f"2022-06-{str(startDate)}", f"2022-06-{str(startDate + 1)}", f"2022-06-{str(startDate + 2)}", f"2022-06-{str(startDate + 3)}"],
          "manPower":random.random() > .5,
          "counterOffer":counterOffer,
          "hourlyStart":"07:30",
          "hourlyEnd":"17:30",
          "currency":"€",
          "description":"Première description d'un chantier",
          "amount":math.floor(1000 + random.random() * 4000),
          "DetailedPost":["salle de bain", "douche"],
          "draft": random.random() < 0.2
          }
        requests.post(url, headers=headers, json=post)

    elif query == "modifyPost":
      post = {'action':"modifyPost", "id":1, "address":"126 rue de Paris 92100 Boulogne", "Job":5, "numberOfPeople":2, "dueDate":"2022-03-15", "startDate":"2022-03-16", "endDate":"2022-04-28", "manPower":False, "counterOffer":False, "hourlyStart":"07:00", "hourlyEnd":"17:00", "currency":"€", "description":"Deuxième description d'un chantier", "amount":24456.10, "DetailedPost":["salle de bain", "douche", "lavabo"], "DatePost":["2022-03-15", "2022-03-16", "2022-03-17"]}
      response = requests.post(url, headers=headers, json=post)
    elif query == "setFavorite":
      requests.get(url, headers=headers, params={'action':"setFavorite", "value":"true", "Post":2})
      response = requests.get(url, headers=headers, params={'action':"setFavorite", "value":"true", "Post":3})
    elif query == "removeFavorite":
      response = requests.get(url, headers=headers, params={'action':"removeFavorite", "value":"false", "Post":3})
    elif query == "isViewed":
      response = requests.get(url, headers=headers, params={'action':"isViewed", "Post":1})
      print("response", response)
    # elif query == "deletePost":
    #   print("deletePost")
    #   post = {'action':"uploadPost", "address":"129 rue de Paris 92100 Boulogne", "Job":9, "numberOfPeople":3, "dueDate":"2022-02-15", "startDate":"2022-02-16", "endDate":"2022-02-28", "manPower":True, "counterOffer":True, "hourlyStart":"7:30", "hourlyEnd":"17:30", "currency":"€", "description":"Première description d'un chantier", "amount":65243.10, "DetailedPost":["lavabo", "baignoire"]}
    #   response = requests.post(url, headers=headers, json=post)
    #   id = None
    #   for key, value in json.loads(response.text).items():
    #     if key != "action":
    #       id = key
    #     response = requests.get(url, headers=headers, params={"action":"deletePost", "id":id})
    elif query == "modifyDisponibility":
      post = {'action':"modifyDisponibility", "disponibility":[["2022-02-13", "Disponible"], ["2022-02-14", "Disponible Sous Conditions"], ["2022-02-15", "Non Disponible"]]}
      response = requests.post(url, headers=headers, json=post)
    elif query == "uploadFile":
      file1 = {'action':"uploadFile", "ext":"png", "name":"Qualibat", "fileBase64":getDocStr(0), "nature":"labels", "expirationDate":"2022-02-12"}
      file2 = {'action':"uploadFile", "ext":"png", "name":"Kbis", "fileBase64":getDocStr(1), "nature":"admin", "expirationDate":"2022-02-12"}
      file4 = {'action':"uploadFile", "ext":"svg", "name":"Document technique", "fileBase64":getDocStr(4), "nature":"post", "Post":2}
      file5 = {'action':"uploadFile", "ext":"jpg", "name":"Plan", "fileBase64":getDocStr(2), "nature":"post", "Post":2}
      for file in [file1, file2, file4, file5]:
        response = requests.post(url, headers=headers, json=file)
        data = json.loads(response.text)
        print("uploadFile", data.keys())
    elif query == "downloadFile":
      requests.get(url, headers=headers, params={"action":"downloadFile", "id":1})
      response = None
    elif query == "deleteFile":
      response = requests.get(url, headers=headers, params={"action":"deleteFile", "id":3})
    elif query == "applyPost":
      requests.get(url, headers=headers, params={'action':"applyPost", "Post":2, "amount":800, "devis":"Par Jour"})
      requests.get(url, headers=headers, params={'action':"applyPost", "Post":3, "amount":1000, "devis":"Par Jour"})
      requests.get(url, headers=headers, params={'action':"applyPost", "Post":4, "amount":1200, "devis":"Par Jour"})
      requests.get(url, headers=headers, params={'action':"applyPost", "Post":5})
      tokenSt2 = queryForToken("st2", "pwd")
      headers = {'Authorization': f'Token {tokenSt2}'}
      response = requests.get(url, headers=headers, params={'action':"applyPost", "Post":2, "amount":1500, "devis":"Par Jour"})
    elif query == "handleCandidateForPost":
      requests.get(url, headers=headers, params={'action':"handleCandidateForPost", "Candidate":2, "response":"true"})
      requests.get(url, headers=headers, params={'action':"handleCandidateForPost", "Candidate":5, "response":"false"})
      response = requests.get(url, headers=headers, params={'action':"handleCandidateForPost", "Candidate":3, "response":"true"})
    elif query == "signContract":
      requests.get(url, headers=headers, params={"action":"signContract", "missionId":4, "view":"ST"})
      print("user pme")
      tokenPme = queryForToken("pme", "pwd")
      headersPme = {'Authorization': f'Token {tokenPme}'}
      response = requests.get(url, headers=headersPme, params={"action":"signContract", "missionId":4, "view":"PME"})
    elif query == "createSupervision":
      post1 = {'action':"createSupervision", "detailedPostId":7, "comment":"J'ai fini."}
      post2 = {'action':"createSupervision", "detailedPostId":8, "comment":"OK pour les tâches du jour."}
      post3 = {'action':"createSupervision", "detailedPostId":10, "comment":"Pas de souci aujourd'hui."}
      post4 = {'action':"createSupervision", "detailedPostId":9, "comment":"Le chantier est terminé."}
      for post in [post1, post2, post3, post4]:
        response = requests.post(url, headers=headers, json=post)
      tokenPme = queryForToken("pme", "pwd")
      headersPme = {'Authorization': f'Token {tokenPme}'}
      post1 = {'action':"createSupervision", "detailedPostId":7, "comment":"Les tâches du jour sont bien faites."}
      post2 = {'action':"createSupervision", "detailedPostId":8, "comment":"Tout est parfait, merci."}
      post3 = {'action':"createSupervision", "detailedPostId":10, "comment":"Attention aux finitions."}
      post4 = {'action':"createSupervision", "detailedPostId":9, "comment":"Le travail est fini, Youpi."}
      post4 = {'action':"createSupervision", "missionId":3, "date":"2022-04-16", "comment":"Attention au travail de ce jour."}
      for post in [post1, post2, post3, post4]:
        response = requests.post(url, headers=headersPme, json=post)
    elif query == "uploadImageSupervision":
      post = {'action':"uploadImageSupervision", "supervisionId":7, "ext":"png", "imageBase64":getDocStr(7)}
      response = requests.post(url, headers=headers, json=post)
    elif query == "switchDraft":
      requests.get(url, headers=headers, params={"action":"switchDraft", "id":2})
      response = requests.get(url, headers=headers, params={"action":"switchDraft", "id":3})
      requests.get(url, headers=headers, params={"action":"switchDraft", "id":6})
      requests.get(url, headers=headers, params={"action":"switchDraft", "id":4})
      requests.get(url, headers=headers, params={"action":"switchDraft", "id":5})
    elif query == "duplicatePost":
      response = requests.get(url, headers=headers, params={"action":"duplicatePost", "id":1})
    elif query == "getPost":
      response = requests.get(url, headers=headers, params={"action":"getPost"})
    elif query == "buildDB":
      url = f'{address}/createBase/'
      response = requests.get(url, headers=headers, params={"action":"reload"})
    elif query == "emptyDB":
      url = f'{address}/createBase/'
      response = requests.get(url, headers=headers, params={"action":"emptyDB"})
    elif query == "createDetailedPost":
      post = {"action":"createDetailedPost", "missionId":1, "content":"Réparer le lavabo une nouvelle fois", "date":"2022-03-17"}
      response = requests.post(url, headers=headers, json=post)
    elif query == "modifyDetailedPost":
      post1 = {"action":"modifyDetailedPost", "detailedPost":{"id":9, "date":"2022-03-18", "content":"Nettoyer le chantier", "validated":True, "unset":False}}
      post2 = {"action":"modifyDetailedPost", "detailedPost":{"id":7, "date":"2022-03-17", "validated":True, "unset":False}}
      post3 = {"action":"modifyDetailedPost", "detailedPost":{"id":8, "date":"2022-03-17", "validated":True, "unset":False}}
      post4 = {"action":"modifyDetailedPost", "detailedPost":{"id":10, "date":"2022-03-16", "validated":True, "unset":False}}
      post5 = {"action":"modifyDetailedPost", "detailedPost":{"id":5, "date":"2022-04-16", "validated":False, "unset":False}}
      post6 = {"action":"modifyDetailedPost", "detailedPost":{"id":6, "date":"2022-04-16", "validated":False, "unset":False}}
      post6 = {"action":"modifyDetailedPost", "detailedPost":{"id":6, "date":"2022-04-16", "validated":False, "unset":True}}
      post6 = {"action":"modifyDetailedPost", "detailedPost":{"id":6, "date":"2022-04-17", "validated":False, "unset":False}}
      for post in [post4, post2, post3, post1, post5, post6]:
        response = requests.post(url, headers=headers, json=post)
      data = json.loads(response.text)
      response = requests.post(url, headers=headers, json=post2)
    elif query == "deleteDetailedPost":
      post = {"action":"deleteDetailedPost", "detailedPostId":9}
      response = requests.post(url, headers=headers, json=post)
    elif query == "modifyMissionDate":
      post = {"action":"modifyMissionDate", "missionId": 3, "hourlyStart":"06:02", "hourlyEnd":"19:02", "calendar":['2022-04-16', '2022-04-17', '2022-04-18', '2022-04-19']}
      response = requests.post(url, headers=headers, json=post)
    elif query == "validateMissionDate":
      post1 = {'action':"validateMissionDate", "missionId": 3, "field":"hourlyStart", "state":True, "date":""}
      post2 = {'action':"validateMissionDate", "missionId": 3, "field":"hourlyEnd", "state":False, "date":""}
      post3 = {'action':"validateMissionDate", "missionId": 3, "field":"date", "state":False, "date":"2022-04-15"}
      post4 = {'action':"validateMissionDate", "missionId": 3, "field":"date", "state":True, "date":"2022-04-19"}
      for post in [post1, post2, post3, post4]:
        response = requests.post(url, headers=headers, json=post)
    elif query == "closeMission":
      post = {"action":"closeMission", "missionId": 4, "qualityStars":4, "qualityComment":"très bon travail", "securityStars":4, "securityComment":"Un vrai sous-traitant qualibat", "organisationStars":5, "organisationComment":"Une organisation parfaite"}
      response = requests.post(url, headers=headers, json=post)
    elif query == "closeMissionST":
      post = {"action":"closeMissionST", "missionId": 4, "vibeSTStars":2, "vibeSTComment":"Ambiance moyenne", "securitySTStars":2, "securitySTComment":"une sécurité faible", "organisationSTStars":2, "organisationSTComment":"Une organisation inexistante"}
      response = requests.post(url, headers=headers, json=post)
    elif query == "notificationViewed":
      post = {"action":"notificationViewed", "companyId": 4, "role":"PME"}
      response = requests.post(url, headers=headers, json=post)
  if response and query != "downloadFile":
    data = json.loads(response.text)
    print("data", data)
  elif query == "downloadFile":
    print("downloadFile: not checked")
  elif query == "inviteFriend":
    response = requests.get(url, headers=headers, params={"action":"inviteFriend", "mail":"jeanluc.walter@fantasiapp.com"})
  elif query == "boostPost":
      post = {"action":"boostPost", "postId":2, "duration":0}
      response = requests.post(url, headers=headers, json=post)
  else:
    print("no answer")
if query == "all":
  keys = ["buildDB", "register", "registerConfirm", "modifyUser", "changeUserImage", "getUserData", "uploadPost", "modifyPost", "getPost", "uploadFile", "downloadFile", "applyPost", "switchDraft", "handleCandidateForPost", "signContract", "modifyDetailedPost", "createSupervision", "modifyMissionDate", "validateMissionDate", "uploadImageSupervision", "closeMission", "closeMissionST", "boostPost"]
  for key in keys: #, "modifyPost"
    query = key
    executeQuery()
else:
  executeQuery()

