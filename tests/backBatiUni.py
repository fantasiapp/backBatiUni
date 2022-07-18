from email.policy import EmailPolicy
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
from datetime import datetime, timedelta
import stripe

stripe.api_key = 'sk_test_51LI7b7GPflszP2pB2F62OC6fyGjgMOTVhQDI19vVqDYEONZmLdDi9KXlQ3bkdgl23t5HsH0FABc7rMHmINenlwV100GfMpz5ec'

# userName, password = "st@g.com", "pwd"
userName, password = "jlw", "pwd"
# userName, password = "jeanluc.walter@fantasiapp.com", "123456Aa"
address = 'http://localhost:8000'
query = "token"
numberCompanies = 5
emailList, missionList, emailListPME, emailListST, detailedPost, candidateToUnapply, labelList = {}, {}, [], [], {}, None, {}

arguments = sys.argv
if len(arguments) > 1:
    host = arguments[1]
    if host == "local": address = 'http://localhost:8000'
    elif host == "temp": address = 'https://batiuni.fantasiapp.tech:5004'
    elif host == "work": address = 'https://batiuni.fantasiapp.tech:5001'
    elif host == "current": address = 'https://batiuni.fantasiapp.tech:5002'
    elif host == "distrib": address = 'https://batiuni.fantasiapp.tech:5003'
    elif host == "distrib2": address = 'https://batiuni.fantasiapp.tech:5005'
    elif host == "com": address = 'https://batiuni.fantasiapp.com:5004'
if len(arguments) > 2:
  query = arguments[2]

def queryForToken(userName, password):
  tokenUrl = f'{address}/api-token-auth/'
  headers = {'Content-Type': 'application/json'}
  data = json.dumps({"username": userName, "password": password})
  response = requests.post(tokenUrl, headers=headers, data=data)
  dictResponse = json.loads(response.text)
  if "token" in dictResponse:
    return dictResponse['token']
  else:
    return False

def getDocStr(index = 0):
  file = ["./files/documents/Qualibat.jpeg", "./files/documents/Kbis.png", "./files/documents/Plan.png", "./files/documents/IMG_2465.HEIC", "./files/documents/Etex.svg", "./files/documents/batiUni.png", "./files/documents/Fantasiapp.png", "./files/documents/logoFantasiapp.png"]
  with open(file[index], "rb") as fileData:
    encoded_string = base64.b64encode(fileData.read())
  return encoded_string.decode("utf-8")

def executeQuery():
  print()
  print("query", query)
  now, data, response, url , headersStart = datetime.now().strftime("%Y-%m-%d"), None, None, f'{address}/initialize/', {"content-type":"Application/Json"}
  if query in ["emptyDB", "buildDB"]:
      token = queryForToken("jlw", "pwd")
      print("user jlw")
      while customers := stripe.Customer.list(limit=100):
        for customer in customers.data:
            stripe.Customer.delete(customer.id)
      response = requests.get(f'{address}/createBase/', headers= {'Authorization': f'Token {token}'}, params={"action":"reload" if query == "buildDB" else "emptyDB"})
  elif query == "register":
    post1 = {"firstname":"Augustin","lastname":"Alleaume","email":"aa@g.com","password":"pwd","company": 'BATOUNO', 'siret': '85342059400014',"Role":3,"proposer":"","jobs":[1,2,80], "action":"register"}
    post2 = {"firstname":"Théophile","lastname":"Traitant","email":"st@g.com","password":"pwd","company":'Sous-traitant', 'siret': '85342059400014', "Role":2, "proposer":"","jobs":[1,2,80], "action":"register"}
    post3 = {"firstname":"Eric","lastname":"Entreprise","email":"pme@g.com","password":"pwd","company": 'PME', 'siret': '85342059400014',"Role":1,"proposer":"","jobs":[1,2,9], "action":"register"}
    post4 = {"firstname":"a","lastname":"a","email":"both@g.com","password":"pwd","company": 'both', 'siret': '85342059400014', "Role":3,"proposer":"","jobs":[1,2,80], "action":"register"}
    post5 = {"firstname":"Tanguy","lastname":"Traitant","email":"st2@g.com","password":"pwd","company": 'Sous-traitant 2', 'siret': '85342059400014', "Role":2,"proposer":"","jobs":[1,2,80], "action":"register"}
    for post in [post1, post2, post3, post4, post5]:
      response = requests.post(url, headers=headersStart, json=post)

  elif query == "registerConfirm":
    requests.get(f'{address}/initialize/', headers=headersStart, params={"action":"registerConfirm", "token":"A secret code to check 9243672519"})
    requests.get(f'{address}/initialize/', headers=headersStart, params={"action":"registerConfirm", "token":"A secret code to check 9243672519"})
    requests.get(f'{address}/initialize/', headers=headersStart, params={"action":"registerConfirm", "token":"A secret code to check 9243672519"})
    requests.get(f'{address}/initialize/', headers=headersStart, params={"action":"registerConfirm", "token":"A secret code to check 9243672519"})
    response = requests.get(f'{address}/initialize/', headers=headersStart, params={"action":"registerConfirm", "token":"A secret code to check 9243672519"})

  elif query == "getGeneralData":
    response = requests.get(url, headers=headersStart, params={"action":"getGeneralData"})

  elif query == "registerMany" and numberCompanies:
    dateForLabel = (datetime.now() + timedelta(days=100, hours=0)).strftime("%Y-%m-%d")
    id, response, url , headers = 0, None, f'{address}/initialize/', {"content-type":"Application/Json"}

    while id <= numberCompanies:
      companyId = id + 7
      company = ''.join(random.choice(string.ascii_letters) for x in range(5))
      companies = requests.get(f'{address}/initialize/', headers=headers, params={"action":"getEnterpriseDataFrom", "subName":company})
      data = json.loads(companies.text)
      if "EstablishmentsValues" in data and data["EstablishmentsValues"]:
        establishmentValue = data["EstablishmentsValues"]['0']
        firstName = ''.join(random.choice(string.ascii_letters) for x in range(6))
        mail = establishmentValue[0][:3].strip(" ") + "@g.com"
        role = 1 if random.random() < 0.5 else 2
        lastName = "Traitant" if role == 2 else "Entreprise"
        jobs = [math.floor(1 + random.random() * 40), math.floor(41 + random.random() * 40), math.floor(81 + random.random() * 60)]
        company = {"id":companyId, 'name':establishmentValue[0], 'address': establishmentValue[1], 'activity': establishmentValue[2], 'siret': establishmentValue[3], 'ntva': establishmentValue[4]}
        post = {"action":"register", "firstname":firstName, "lastname":lastName, "email":mail, "password":"pwd", "company":company, "Role":role,"proposer":"","jobs":jobs}
        userProfile = requests.post(url, headers=headers, json=post)
        success = json.loads(userProfile.text)
        if success['register'] == "OK":
          emailList[companyId] = mail
          if role == 1:
            emailListPME.append(companyId)
          else:
            emailListST.append(companyId)
          id += 1

    for i in emailListPME + emailListST:
      requests.get(f'{address}/initialize/', headers=headers, params={"action":"registerConfirm", "token":"A secret code to check 9243672519"})

    for companyId, mail in emailList.items():
      token = queryForToken(mail, "pwd")
      if token:
        headers = {'Authorization': f'Token {token}'}
        capital = str(math.floor(10000 + random.random() * 100000))
        revenue = str(math.floor(100000 + random.random() * 1000000))
        amount = math.floor(8 + random.random() * 70)
        webSite = "https://monWebSite.fr"
        JobForCompany = [[math.floor(1 + random.random() * 40), math.floor(1 + random.random() * 4)], [math.floor(41 + random.random() * 40), math.floor(1 + random.random() * 4)], [math.floor(81 + random.random() * 40), math.floor(1 + random.random() * 4)]]
        LabelForCompany = [[math.floor(1 + random.random() * 9), dateForLabel], [math.floor(10 + random.random() * 9), dateForLabel], [math.floor(20 + random.random() * 3), dateForLabel]]
        post = {'action': 'modifyUser', 'UserProfile': {'id': companyId, 'cellPhone': '0629350418', 'Company': {'capital': capital, 'revenue': revenue, "webSite": webSite, "amount":amount, 'companyPhone': '0892976415', "allQualifications":True, 'JobForCompany':JobForCompany, 'LabelForCompany':LabelForCompany}}}
        response = requests.post(f'{address}/data/', headers=headers, json=post)
        if companyId in emailList:
          data = json.loads(response.text)
          labelList[companyId] = data["LabelForCompany"]


    generalData = requests.get(url, headers=headersStart, params={"action":"getGeneralData"})
    generalData = json.loads(generalData.text)

    for companyId, value in labelList.items():
      tokenForImage = queryForToken(emailList[companyId], "pwd")
      headersForImage = {'Authorization': f'Token {tokenForImage}'}
      url = f'{address}/data/'
      for labelValues in value:
        for tupleLabel in labelValues.values():
          fileName = generalData["LabelValues"][str(tupleLabel[0])]
          fileName = fileName[1] if isinstance(fileName, list) else fileName
          file = {'action':"uploadFile", "ext":"png", "name":fileName, "fileBase64":getDocStr(0), "nature":"labels", "expirationDate":tupleLabel[1]}
          data = requests.post(url, headers=headersForImage, json=file)

    for i in emailListST:
      token = queryForToken(emailList[i], "pwd")
      headers = {'Authorization': f'Token {token}'}
      disponibilities = [now, (datetime.now() + timedelta(days=1, hours=0)).strftime("%Y-%m-%d"), (datetime.now() + timedelta(days=2, hours=0)).strftime("%Y-%m-%d"), (datetime.now() + timedelta(days=3, hours=0)).strftime("%Y-%m-%d")]
      dispoNature = [(dispo, "Disponible" if random.random() > 0.33 else "Disponible Sous Conditions") for dispo in disponibilities]
      post = {"action":"modifyDisponibility", "disponibility":dispoNature}
      response = requests.post(f'{address}/data/', headers=headers, json=post)


  elif query == "forgetPassword":
    response = requests.get(url, headers=headersStart, params={"action":"forgetPassword", "email":"walter.jeanluc@gmail.com"})
  else:
    
    if query in ["uploadPost", "deletePost", "modifyPost", "getPost", "switchDraft", "handleCandidateForPost", "modifyMissionDate", "getUserData", "closeMission", "notificationViewed", "boostDuration", "isViewed", "blockCompany", "duplicatePost"]:
      token = queryForToken("pme@g.com", "pwd")
    else:
      token = queryForToken("st@g.com", "pwd")
    url = f'{address}/data/'
    headers = {'Authorization': f'Token {token}'}
    tokenPme = queryForToken("pme@g.com", "pwd")
    headersPme = {'Authorization': f'Token {tokenPme}'}

    if query == "getUserData":
      response = requests.get(url, headers=headers, params={"action":"getUserData"})

    elif query == "removeLabelForCompany":
      for value in labelList.values():
        for dict in value:
          for labelId in dict.keys():
            if random.random() > 0.9:
              response = requests.get(url, headers=headers, params={'action':"removeLabelForCompany", "labelId":labelId})


    elif query == "postModifyPwd":
      post = {"action":"modifyPwd", "oldPwd":"pwd", "newPwd":"pwd"}
      response = requests.post(url, headers=headers, json=post)

    elif query == "modifyUser":
      now = "2022-06-12"
      post1 = {'action': 'modifyUser', 'UserProfile': {'id': 3, 'cellPhone': '0629350418', 'Company': {'capital': '307130', 'companyPhone': '0892976415', "amount":'28', 'JobForCompany':[[4,2], [5,3], [77,4]], 'LabelForCompany':[[1,now], [2,now]]}}}
      post2 = {'action': 'modifyUser', 'UserProfile': {'id': 6, 'cellPhone': '0628340317', 'Company': {'capital': '207130', 'companyPhone': '0891966314', "amount":'52', 'JobForCompany':[[4,2], [5,3], [77,4]], 'LabelForCompany':[[1,now], [2,now]]}}}
      requests.post(url, headers=headers, json=post1)
      response = tokenSt2 = queryForToken("st2@g.com", "pwd")
      headersSt2 = {'Authorization': f'Token {tokenSt2}'}
      response = requests.post(url, headers=headersSt2, json=post2)

    elif query == "changeUserImage":
      tokenPme = queryForToken("pme@g.com", "pwd")
      headersPme = {'Authorization': f'Token {tokenPme}'}
      post = {'action':"changeUserImage", "ext":"png", "name":"image", "imageBase64":getDocStr(5)}
      requests.post(url, headers=headersPme, json=post)
      tokenSt2 = queryForToken("st2@g.com", "pwd")
      headersSt2 = {'Authorization': f'Token {tokenSt2}'}
      post = {'action':"changeUserImage", "ext":"png", "name":"image", "imageBase64":getDocStr(7)}
      response = requests.post(url, headers=headersSt2, json=post)
      post = {'action':"changeUserImage", "ext":"png", "name":"image", "imageBase64":getDocStr(6)}
      requests.post(url, headers=headers, json=post)

    elif query == "uploadPost":
      post1 = {'action':"uploadPost", "longitude":2.237779 , "latitude":48.848776, "address":"128 rue de Paris 92100 Boulogne", "Job":6, "numberOfPeople":3, "dueDate":"2022-07-15", "startDate":"2022-07-16", "endDate":"2022-07-28", "DatePost":["2022-07-26", "2022-07-27", "2022-07-28"], "manPower":True, "counterOffer":True, "hourlyStart":"07:30", "hourlyEnd":"17:30", "currency":"€", "description":"Première description d'un chantier", "amount":65243.10, "DetailedPost":["lavabo", "baignoire"]}
      post2 = {'action':"uploadPost", "longitude":2.324877 , "latitude":48.841625, "address":"106 rue du Cherche-Midi 75006 Paris", "Job":5, "numberOfPeople":1, "dueDate":"2022-07-15", "startDate":"2022-07-16", "endDate":"2022-04-28", "DatePost":["2022-07-16", "2022-07-17", "2022-07-18"], "manPower":False, "counterOffer":True, "hourlyStart":"07:00", "hourlyEnd":"17:00", "currency":"€", "description":"Deuxième description d'un chantier", "amount":23456.10, "DetailedPost":["radiateur", "Chaudière"]}
      post3 = {'action':"uploadPost", "longitude":2.326881 , "latitude":48.841626, "address":"36 rue Dauphine 75006 Paris", "Job":10, "numberOfPeople":1, "dueDate":"2022-07-15", "startDate":"2022-07-15", "endDate":"2022-07-18", "DatePost":["2022-07-15", "2022-07-16", "2022-07-17", "2022-07-18"], "manPower":True, "counterOffer":True, "hourlyStart":"07:00", "hourlyEnd":"17:00", "currency":"€", "description":"troisième description d'un chantier", "amount":12345.10, "DetailedPost":["doublage", "cloison"]}
      post4 = {'action':"uploadPost", "longitude":2.325883 , "latitude":48.841627, "address":"28 rue de Fleurus 75006 Paris", "Job":10, "numberOfPeople":2, "dueDate":"2022-07-18", "startDate":"2022-07-16", "endDate":"2022-07-28", "DatePost":["2022-07-21", "2022-07-22", "2022-07-23"], "manPower":True, "counterOffer":False, "hourlyStart":"07:00", "hourlyEnd":"17:00", "currency":"€", "description":"quatrième description d'un chantier", "amount":1300.10, "DetailedPost":["doublage", "cloison", "pose", "mesure"]}
      post5 = {'action':"uploadPost", "longitude":2.325885 , "latitude":48.841628, "address":"34 rue Guynemer 75006 Paris", "Job":10, "numberOfPeople":1, "dueDate":"2022-07-21", "startDate":"2022-07-16", "endDate":"2022-07-28", "DatePost":["2022-07-16", "2022-07-17", "2022-07-18"], "manPower":True, "counterOffer":False, "hourlyStart":"08:00", "hourlyEnd":"17:00", "currency":"€", "description":"cinquième description d'un chantier", "amount":1300.10, "DetailedPost":["cuisine", "salle de bain", "salon", "Chambre"]}
      post6 = {'action':"uploadPost", "longitude":2.324877 , "latitude":48.841625, "address":"108 rue du Cherche-Midi 75006 Paris", "Job":5, "numberOfPeople":1, "dueDate":"2022-07-15", "startDate":"2022-07-16", "endDate":"2022-07-28", "DatePost":["2022-07-26", "2022-07-27", "2022-07-28"], "manPower":False, "counterOffer":True, "hourlyStart":"07:00", "hourlyEnd":"17:00", "currency":"€", "description":"Sixième description d'un chantier", "amount":23456.10, "DetailedPost":["radiateur", "Chaudière"]}
      for post in [post1, post2, post3, post4, post5, post6]:
        response = requests.post(url, headers=headers, json=post)
      if numberCompanies:
        for id, mail in emailList.items():
          flagMission = False
          token = queryForToken("pme@g.com", "pwd")
          if id in emailListPME:
            token = queryForToken(mail, "pwd")
          elif random.random() < 0.5:
            flagMission = True
          headersNew = {'Authorization': f'Token {token}'}
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
            "dueDate":f"2022-07-{str(startDate - 1)}",
            "startDate":f"2022-07-{str(startDate)}",
            "endDate":f"2022-07-{str(startDate + 3)}",
            "DatePost":[f"2022-07-{str(startDate)}", f"2022-07-{str(startDate + 1)}", f"2022-07-{str(startDate + 2)}", f"2022-07-{str(startDate + 3)}"],
            "manPower":random.random() > .5,
            "counterOffer":counterOffer,
            "hourlyStart":"07:30",
            "hourlyEnd":"17:30",
            "currency":"€",
            "description":"Première description d'un chantier " + str(id),
            "amount":math.floor(1000 + random.random() * 4000),
            "DetailedPost":["salle de bain", "douche", "baignoire"],
            "draft": random.random() < 0.25
            }
          if flagMission:
            missionList[id] = {"mail":mail, "counterOffer":counterOffer, "amount":post["amount"]}
            post["draft"] = False
          requests.post(url, headers=headersNew, json=post)
          

    elif query == "modifyPost":
      post = {'action':"modifyPost", "id":1, "address":"126 rue de Paris 92100 Boulogne", "Job":5, "numberOfPeople":2, "dueDate":"2022-03-15", "startDate":"2022-03-16", "endDate":"2022-04-28", "manPower":False, "counterOffer":False, "hourlyStart":"07:00", "hourlyEnd":"17:00", "currency":"€", "description":"Deuxième description d'un chantier", "amount":24456.10, "DetailedPost":["salle de bain", "douche", "lavabo"], "DatePost":["2022-06-15", "2022-06-16", "2022-06-17"]}
      response = requests.post(url, headers=headers, json=post)
    elif query == "setFavorite":
      requests.get(url, headers=headers, params={'action':"setFavorite", "value":"true", "Post":2})
      response = requests.get(url, headers=headers, params={'action':"setFavorite", "value":"true", "Post":3})
      if numberCompanies:
        for id, mail in emailList.items():
          if id in emailListST:
            token = queryForToken(mail, "pwd")
            headersNew = {'Authorization': f'Token {token}'}
            if random.random() > .6:
              requests.get(url, headers=headers, params={'action':"setFavorite", "value":"true", "Post":id})
              requests.get(url, headers=headersNew, params={'action':"setFavorite", "value":"true", "Post":id})
    elif query == "removeFavorite":
      response = requests.get(url, headers=headers, params={'action':"setFavorite", "value":"false", "Post":3})
    elif query == "deletePost":
      # print("deletePost")
      # post = {'action':"uploadPost", "address":"129 rue de Paris 92100 Boulogne", "Job":9, "numberOfPeople":3, "dueDate":"2022-02-15", "startDate":"2022-02-16", "endDate":"2022-02-28", "manPower":True, "counterOffer":True, "hourlyStart":"7:30", "hourlyEnd":"17:30", "currency":"€", "description":"Première description d'un chantier", "amount":65243.10, "DetailedPost":["lavabo", "baignoire"]}
      # response = requests.post(url, headers=headers, json=post)
      # for key in json.loads(response.text).keys():
      #   if key != "uploadPost":
      #     print(key)
      #     response = requests.get(url, headers=headers, params={"action":"deletePost", "id":key})
      pass
    elif query == "modifyDisponibility":
      post = {'action':"modifyDisponibility", "disponibility":[["2022-06-13", "Disponible"], ["2022-06-14", "Disponible Sous Conditions"], ["2022-06-15", "Non Disponible"]]}
      response = requests.post(url, headers=headers, json=post)
    elif query == "uploadFile":
      file1 = {'action':"uploadFile", "ext":"png", "name":"qualibat", "fileBase64":getDocStr(0), "nature":"labels", "expirationDate":"2022-02-12"}
      file2 = {'action':"uploadFile", "ext":"png", "name":"Kbis", "fileBase64":getDocStr(1), "nature":"admin", "expirationDate":"2022-02-12"}
      file4 = {'action':"uploadFile", "ext":"svg", "name":"Document technique", "fileBase64":getDocStr(4), "nature":"post", "Post":2}
      file5 = {'action':"uploadFile", "ext":"jpg", "name":"Plan", "fileBase64":getDocStr(2), "nature":"post", "Post":2}
      requests.post(url, headers=headersPme, json=file2)
      tokenSt2 = queryForToken("st2@g.com", "pwd")
      headersSt2 = {'Authorization': f'Token {tokenSt2}'}
      requests.post(url, headers=headersSt2, json=file2)
      tokenBoth = queryForToken("both@g.com", "pwd")
      headersBoth = {'Authorization': f'Token {tokenSt2}'}
      requests.post(url, headers=headersBoth, json=file2)
      for file in [file1, file2, file4, file5]:
        response = requests.post(url, headers=headers, json=file)
        data = json.loads(response.text)
    elif query == "modifyFile":
      response = requests.post(url, headers=headers, json={'action':"modifyFile", "fileId":4, "expirationDate":"2022-12-12"})
    elif query == "downloadFile":
      requests.get(url, headers=headers, params={"action":"downloadFile", "id":1})
      response = None
    elif query == "deleteFile":
      response = requests.get(url, headers=headers, params={"action":"deleteFile", "id":3})

    elif query == "switchDraft":
      requests.get(url, headers=headers, params={"action":"switchDraft", "id":2})
      requests.get(url, headers=headers, params={"action":"switchDraft", "id":6})
      requests.get(url, headers=headers, params={"action":"switchDraft", "id":4})
      requests.get(url, headers=headers, params={"action":"switchDraft", "id":5})
      response = requests.get(url, headers=headers, params={"action":"switchDraft", "id":3})

    # elif query == "duplicatePost":
    #   response = requests.get(url, headers=headers, params={"action":"duplicatePost", "id":2})

    elif query == "getPost":
      response = requests.get(url, headers=headers, params={"action":"getPost"})

    elif query == "isViewed":
      response = requests.get(url, headers=headers, params={'action':"isViewed", "Post":4})
      for id in missionList.keys():
        response = requests.get(url, headers=headers, params={'action':"isViewed", "Post":id})


    elif query == "applyPost":
      requests.get(url, headers=headers, params={'action':"applyPost", "Post":2, "amount":800, "devis":"Par Jour"})
      requests.get(url, headers=headers, params={'action':"applyPost", "Post":3, "amount":1000, "devis":"Par Jour"})
      requests.get(url, headers=headers, params={'action':"applyPost", "Post":4})
      requests.get(url, headers=headers, params={'action':"applyPost", "Post":5})
      tokenSt2 = queryForToken("st2@g.com", "pwd")
      headers = {'Authorization': f'Token {tokenSt2}'}
      response = requests.get(url, headers=headers, params={'action':"applyPost", "Post":6, "amount":1500, "devis":"Par Jour"})
      if numberCompanies:  
        headers = {'Authorization': f'Token {token}'}
        for id, values in missionList.items():
          data = requests.get(url, headers=headers, params={'action':"applyPost", "Post":id, "amount":values["amount"] / 2, "devis":"Par Jour"})
          data = json.loads(data.text)
          postDump = list(data["Post"].values())[0]
          if postDump[25]:
            values["candidateId"] = postDump[25][-1]
            print("applyPost", postDump, values)
          else:
            print("no apply post", postDump[0])

    elif query == "unapplyPost" and numberCompanies:
      headersUnapplyPost = {'Authorization': f'Token {token}'}
      for id, values in missionList.items():
        rand = random.random()
        if rand > 0.8 and "candidateId" in values:
          print("unapplyPost post", id, "candidate", values["candidateId"])
          response = requests.get(url, headers=headersUnapplyPost, params={'action':"unapplyPost", "candidateId":values["candidateId"], "postId":id})
          del values["candidateId"]
          
          
    elif query == "handleCandidateForPost":
      requests.get(url, headers=headers, params={'action':"handleCandidateForPost", "Candidate":2, "response":"true"})
      requests.get(url, headers=headers, params={'action':"handleCandidateForPost", "Candidate":3, "response":"true"})
      requests.get(url, headers=headers, params={'action':"handleCandidateForPost", "Candidate":4, "response":"false"})
      requests.get(url, headers=headers, params={'action':"handleCandidateForPost", "Candidate":5, "response":"true"})
      response = requests.get(url, headers=headers, params={'action':"handleCandidateForPost", "Candidate":1, "response":"true"})
      if numberCompanies:
        for id, values in missionList.items():
          if random.random() > 0.5 and "candidateId" in values:
            print("handleCandidateForPost post", id, "candidate", values)
            data = requests.get(url, headers=headers, params={'action':"handleCandidateForPost", "Candidate":values["candidateId"], "response":"true"})
            print("handleCandidateForPost", json.loads(data.text))
            values["mission"] = True

    elif query == "signContract":
      requests.get(url, headers=headers, params={"action":"signContract", "missionId":4, "view":"ST"})
      response = requests.get(url, headers=headersPme, params={"action":"signContract", "missionId":4, "view":"PME"})
      if numberCompanies:
        for id, values in missionList.items():
          if "mission" in values:
            print("mission values", id, values)
            requests.get(url, headers=headers, params={"action":"signContract", "missionId":id, "view":"ST"})
            requests.get(url, headers=headersPme, params={"action":"signContract", "missionId":id, "view":"PME"})
    elif query == "createSupervision":
      post1 = {'action':"createSupervision", "detailedPostId":3, "comment":"J'ai fini."}
      post2 = {'action':"createSupervision", "detailedPostId":4, "comment":"OK pour les tâches du jour."}
      post3 = {'action':"createSupervision", "detailedPostId":5, "comment":"Pas de souci aujourd'hui."}
      post4 = {'action':"createSupervision", "detailedPostId":6, "comment":"Le chantier est terminé."}
      post5 = {'action':"createSupervision", "datePostId":7, "comment":"Voila une tâche difficile."}
      for post in [post1, post2, post3, post4, post5]:
        requests.post(url, headers=headers, json=post)
      post1 = {'action':"createSupervision", "detailedPostId":3, "comment":"Les tâches du jour sont bien faites."}
      post2 = {'action':"createSupervision", "detailedPostId":4, "comment":"Tout est parfait, merci."}
      post3 = {'action':"createSupervision", "detailedPostId":5, "comment":"Attention aux finitions."}
      post4 = {'action':"createSupervision", "detailedPostId":6, "comment":"Le travail est fini, Youpi."}
      post5 = {'action':"createSupervision", "datePostId":7, "comment":"Attention au travail de ce jour."}
      for post in [post1, post2, post3, post4, post5]:
        response = requests.post(url, headers=headersPme, json=post)
    elif query == "uploadImageSupervision":
      post = {'action':"uploadImageSupervision", "supervisionId":7, "ext":"png", "imageBase64":getDocStr(7)}
      response = requests.post(url, headers=headers, json=post)
    elif query == "createDetailedPost":
      post = {"action":"createDetailedPost", "postId":1, "content":"Réparer le lavabo une nouvelle fois", "dateId":21}
      response = requests.post(url, headers=headers, json=post)
    elif query == "modifyDetailedPost":
      post1 = {"action":"modifyDetailedPost", "detailedPost":{"id":9, "content":"Nettoyer le chantier", "validated":True}, "unset":False, "datePostId":11}
      post2 = {"action":"modifyDetailedPost", "detailedPost":{"id":5, "refused":True}, "unset":False, "datePostId":7}
      post3 = {"action":"modifyDetailedPost", "detailedPost":{"id":6, "refused":True}, "unset":False, "datePostId":7}
      post4 = {"action":"modifyDetailedPost", "detailedPost":{"id":15, "validated":True}, "unset":False, "datePostId":17}
      post5 = {"action":"modifyDetailedPost", "detailedPost":{"id":16, "validated":False}, "unset":False, "datePostId":18}
      for post in [post1, post2, post3, post4, post5]:
        response = requests.post(url, headers=headers, json=post)

   
    elif query == "deleteDetailedPost":
      post = {"action":"deleteDetailedPost", "detailedPostId":14}
      response = requests.post(url, headers=headers, json=post)

    elif query == "modifyMissionDate":
      post1 = {"action":"modifyMissionDate", "missionId": 3, "hourlyStart":"06:02", "hourlyEnd":"19:02"}
      post2 = {"action":"modifyMissionDate", "missionId": 3, "calendar":['2022-06-15', '2022-06-16', '2022-06-17', '2022-06-18', '2022-06-19']}
      for post in [post1, post2]:
        response = requests.post(url, headers=headers, json=post)

    elif query == "test":
      # post = {"action":"modifyMissionDate", "missionId": 19, "calendar":['2022-06-19', '2022-06-20', '2022-06-21']}
      # post = {'action':"validateMissionDate", "missionId": 19, "field":"date", "state":False, "date":"2022-06-18"}
      post = {"action":"createSupervision", "datePostId":10, "content":"Réparer le lavabo une nouvelle fois"}
      post = {"action":"createDetailedPost", "postId":3, "content":"Réparer le lavabo une nouvelle fois", "dateId":10}
      url = f'{address}/api-token-auth/'
      post = {}
      print()
      response = requests.post(url, headers={}, json={"username":"pme@g.com", "password":"pwd"})

    elif query == "validateMissionDate":
      post1 = {'action':"validateMissionDate", "missionId": 3, "field":"hourlyStart", "state":True}
      post2 = {'action':"validateMissionDate", "missionId": 3, "field":"hourlyEnd", "state":False}
      post3 = {'action':"validateMissionDate", "missionId": 3, "field":"date", "state":False, "date":"2022-06-16"}
      post4 = {'action':"validateMissionDate", "missionId": 3, "field":"date", "state":True, "date":"2022-06-19"}
      for post in [post1, post2, post3, post4]:
        response = requests.post(url, headers=headers, json=post)
      print(json.loads(response.text))
    elif query == "closeMission":
      post = {"action":"closeMission", "missionId": 4, "qualityStars":4, "qualityComment":"très bon travail", "securityStars":4, "securityComment":"Un vrai sous-traitant qualibat", "organisationStars":5, "organisationComment":"Une organisation parfaite"}
      response = requests.post(url, headers=headers, json=post)
    elif query == "closeMissionST":
      post = {"action":"closeMissionST", "missionId": 4, "vibeSTStars":2, "vibeSTComment":"Ambiance moyenne", "securitySTStars":2, "securitySTComment":"une sécurité faible", "organisationSTStars":2, "organisationSTComment":"Une organisation inexistante"}
      response = requests.post(url, headers=headers, json=post)
    elif query == "notificationViewed":
      post = {"action":"notificationViewed", "companyId": 4, "role":"PME"}
      response = requests.post(url, headers=headers, json=post)
    elif query in ["downloadFile", "uploadSupervision"]:
      print(f"{query}: not checked")
    elif query == "inviteFriend":
      response = requests.get(url, headers=headers, params={"action":"inviteFriend", "mail":"jeanluc.walter@fantasiapp.com"})
    elif query == "boostPost":
        post = {"action":"boostPost", "postId":2, "duration":0}
        response = requests.post(url, headers=headers, json=post)
    elif query == "blockCompany":
        response = requests.get(url, headers=headers, params={"action":"blockCompany", "companyId":1, "status":"true"})
    elif query == "askRecommandation":
      response = requests.get(url, headers=headers, params={"action":"askRecommandation", "email":"jeanluc.walter@fantasiapp.com", "firsrtName":"Théophile", "lastName":"Traitant", "company":"Sous-traitant", "companyId":3, "view":"ST"})
    elif query == "giveRecommandation":
      post1 = {"action":"giveRecommandation", "companyRecommanded":3, "firstNameRecommanding":"Maxime", "lastNameRecommanding":"Baraton", "companyNameRecommanding":"Fantasiapp", "qualityStars":4, "qualityComment":"Un travail remarquable", "securityStars":5, "securityComment":"Une sécurité digne de la Nasa", "organisationStars":4, "organisationComment":"Rien à dire", "view":"ST"}
      post2 = {"action":"giveRecommandation", "companyRecommanded":3, "firstNameRecommanding":"Dyvia", "lastNameRecommanding":"Gaultier", "companyNameRecommanding":"Loreal", "qualityStars":5, "qualityComment":"Un travail bien fait", "securityStars":5, "securityComment":"Une sécurité digne de la Nasa", "organisationStars":4, "organisationComment":"Rien à dire", "view":"ST"}
      post3 = {"action":"giveRecommandation", "companyRecommanded":3, "firstNameRecommanding":"William", "lastNameRecommanding":"Baraton", "companyNameRecommanding":"Carrefour", "qualityStars":4, "qualityComment":"Un travail remarquable", "securityStars":5, "securityComment":"Une sécurité digne de la Nasa", "organisationStars":4, "organisationComment":"Rien à dire", "view":"ST"}
      post4 = {"action":"giveRecommandation", "companyRecommanded":3, "firstNameRecommanding":"Lucas", "lastNameRecommanding":"Gaultier", "companyNameRecommanding":"Microsoft", "qualityStars":5, "qualityComment":"Un travail bien fait", "securityStars":5, "securityComment":"Une sécurité digne de la Nasa", "organisationStars":4, "organisationComment":"Rien à dire", "view":"ST"}
      post5 = {"action":"giveRecommandation", "companyRecommanded":3, "firstNameRecommanding":"Sarah", "lastNameRecommanding":"Baraton", "companyNameRecommanding":"BatiUni", "qualityStars":4, "qualityComment":"Un travail remarquable", "securityStars":5, "securityComment":"Une sécurité digne de la Nasa", "organisationStars":4, "organisationComment":"Rien à dire", "view":"ST"}
      post6 = {"action":"giveRecommandation", "companyRecommanded":3, "firstNameRecommanding":"Cassiopée", "lastNameRecommanding":"Gaultier", "companyNameRecommanding":"Artech", "qualityStars":5, "qualityComment":"Un travail bien fait", "securityStars":5, "securityComment":"Une sécurité digne de la Nasa", "organisationStars":4, "organisationComment":"Rien à dire", "view":"ST"}
      post7 = {"action":"giveRecommandation", "companyRecommanded":3, "firstNameRecommanding":"Jean-Luc", "lastNameRecommanding":"Baraton", "companyNameRecommanding":"Reportive", "qualityStars":4, "qualityComment":"Un travail remarquable", "securityStars":5, "securityComment":"Une sécurité digne de la Nasa", "organisationStars":4, "organisationComment":"Rien à dire", "view":"ST"}
      post8 = {"action":"giveRecommandation", "companyRecommanded":3, "firstNameRecommanding":"Maude", "lastNameRecommanding":"Gaultier", "companyNameRecommanding":"Google", "qualityStars":5, "qualityComment":"Un travail bien fait", "securityStars":5, "securityComment":"Une sécurité digne de la Nasa", "organisationStars":4, "organisationComment":"Rien à dire", "view":"ST"}
      for post in [post1, post2, post3, post4, post5, post6, post7, post8]:
        response = requests.post(f'{address}/initialize/', headers=headers, json=post)
    elif query == "giveNotificationToken":
      response = requests.get(url, headers=headers, params={"action":"giveNotificationToken", "token":"La valeur du token qui devrait être enregistée"})
    elif query == "duplicatePost":
      print("duplicatePost")
      response = requests.get(url, headers=headers, params={"action":"duplicatePost", "id":22})
        # response = requests.get(url, headers=headers, params={"action":"blockCompany", "companyId":1, "status":"true"})
  if response and query != "downloadFile":
    data = json.loads(response.text)
    print("data", data)
  else:
    print("no answer")
if query == "all":
  keys = ["buildDB", "register", "registerConfirm", "getGeneralData", "registerMany", "removeLabelForCompany", "modifyUser", "changeUserImage", "getUserData", "uploadPost", "deletePost", "modifyPost", "getPost", "setFavorite", "removeFavorite", "uploadFile", "modifyFile", "downloadFile", "switchDraft", "isViewed", "applyPost", "unapplyPost", "handleCandidateForPost", "signContract", "modifyMissionDate", "validateMissionDate", "createSupervision", "uploadImageSupervision", "modifyDetailedPost", "modifyDisponibility", "closeMission", "closeMissionST", "boostPost", "blockCompany", "askRecommandation", "giveRecommandation", "giveNotificationToken"]#
  for key in keys:
    query = key
    executeQuery()
else:
  executeQuery()

