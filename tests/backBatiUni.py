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
from datetime import datetime, timedelta, date
import stripe

# userName, password = "st@g.com", "pwd"
userName, password = "jlw", "pwd"
# userName, password = "jeanluc.walter@fantasiapp.com", "123456Aa"
address = 'http://localhost:8000'
query = "token"
numberCompanies = 50
emailList, missionList, emailListPME, emailListST, detailedPost, candidateToUnapply, labelList = {}, {}, [], [], {}, None, {}

arguments = sys.argv
if len(arguments) > 1:
    host = arguments[1]
    if host == "local": address = 'http://localhost:8000'
    elif host == "temp":
      address = 'https://batiuni.fantasiapp.tech:5004'
      STRIPE_API_KEY = 'sk_test_51LI7b7GPflszP2pB2F62OC6fyGjgMOTVhQDI19vVqDYEONZmLdDi9KXlQ3bkdgl23t5HsH0FABc7rMHmINenlwV100GfMpz5ec'
    elif host == "work":
      address = 'https://batiuni.fantasiapp.tech:5001'
      STRIPE_API_KEY = 'sk_test_51LI7VAENZMpowJJssQMcAAkmGUHReIGl2Z0dkIJDOoLjYyip1d13vq4bGvdnV2sbvA7qrr0qckP9KoFKLDbCGilm006F7DEDsu'
    elif host == "current":
      address = 'https://batiuni.fantasiapp.tech:5002'
      STRIPE_API_KEY = 'sk_test_51LI7eOIb3fLk25W9wYMYgynWp6o89MQSTB1tQszBqKBw3eIyUoC9nHmmbkjclUa9jb9EN9dvhZbtygqbNjUiLBkH00hKUmT6vS'
    elif host == "distrib":
      address = 'https://batiuni.fantasiapp.tech:5003'
      STRIPE_API_KEY = 'sk_test_51LI7spCFcn8ExoZNimoOdmdBrJYoEICDf38ecRSfammtJaBMKmO2cKkBwcgYJ7cJcjOGKVQgqa1rHh06hFcWjUDt00yGeOpRgK'
    elif host == "distrib2": address = 'https://batiuni.fantasiapp.tech:5005'
    elif host == "com": address = 'https://batiuni.fantasiapp.com:5004'
if len(arguments) > 2:
  query = arguments[2]

if host != "local":
  stripe.api_key = STRIPE_API_KEY

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
  file = ["./files/documents/Qualibat.jpeg", "./files/documents/Kbis.png", "./files/documents/Plan.png", "./files/documents/IMG_2465.HEIC", "./files/documents/Etex.svg", "./files/documents/BatiUni.png", "./files/documents/Fantasiapp.png", "./files/documents/logoFantasiapp.png", "./files/documents/Kbis.pdf"]
  with open(file[index], "rb") as fileData:
    encoded_string = base64.b64encode(fileData.read())
  return encoded_string.decode("utf-8")

def executeQuery():
  print()
  print("query", query)
  now, data, response, url , headersStart = datetime.now().strftime("%Y-%m-%d"), None, None, f'{address}/initialize/', {"content-type":"Application/Json"}
  today = date.today() + timedelta(days=30, hours=0)
  nextMonth = '%02d' % today.month

  if query in ["emptyDB", "buildDB"]:
    token = queryForToken("jlw", "pwd")
    print("user jlw", address)
    if host != "local":
      while customers := stripe.Customer.list(limit=100):
        print("supress 100 customer")
        for customer in customers.data:
            stripe.Customer.delete(customer.id)
    response = requests.get(f'{address}/createBase/', headers= {'Authorization': f'Token {token}'}, params={"action":"reload" if query == "buildDB" else "emptyDB"})

  elif query == "register":
    post1 = {"firstname":"Augustin","lastname":"Alleaume","email":"aa@g.com","password":"pwd","company": 'BATOUNO', 'siret': '85342059400014',"Role":3,"proposer":"","jobs":[1,2,80], "action":"register"}
    post2 = {"firstname":"Th??ophile","lastname":"Traitant","email":"st@g.com","password":"pwd","company":'Sous-traitant', 'siret': '85342059400014', "Role":2, "proposer":"","jobs":[1,2,80], "action":"register"}
    post3 = {"firstname":"Eric","lastname":"Entreprise","email":"pme@g.com","password":"pwd","company": 'PME', 'siret': '85342059400014',"Role":1,"proposer":"","jobs":[1,2,9], "action":"register"}
    post4 = {"firstname":"a","lastname":"a","email":"both@g.com","password":"pwd","company": 'both', 'siret': '85342059400014', "Role":3,"proposer":"","jobs":[1,2,80], "action":"register"}
    post5 = {"firstname":"Tanguy","lastname":"Traitant","email":"st2@g.com","password":"pwd","company": 'Sous-traitant 2', 'siret': '85342059400014', "Role":2,"proposer":"","jobs":[1,2,80], "action":"register"}
    listPost = [post1, post2, post3, post4, post5]
    for post in listPost:
      response = requests.post(url, headers=headersStart, json=post)
      

    requests.get(f'{address}/initialize/', headers=headersStart, params={"action":"registerConfirm", "token":"A secret code to check 9243672519"})
    requests.get(f'{address}/initialize/', headers=headersStart, params={"action":"registerConfirm", "token":"A secret code to check 9243672519"})
    requests.get(f'{address}/initialize/', headers=headersStart, params={"action":"registerConfirm", "token":"A secret code to check 9243672519"})
    requests.get(f'{address}/initialize/', headers=headersStart, params={"action":"registerConfirm", "token":"A secret code to check 9243672519"})
    response = requests.get(f'{address}/initialize/', headers=headersStart, params={"action":"registerConfirm", "token":"A secret code to check 9243672519"})

    url = f'{address}/data/'
    for post in listPost:
      tokenForImage = queryForToken(post["email"], "pwd")
      dateForLabel = (datetime.now() + timedelta(days=100, hours=0)).strftime("%Y-%m-%d")
      headersForImage = {'Authorization': f'Token {tokenForImage}'}
      file1 = {'action':"uploadFile", "ext":"pdf", "name":"Kbis", "fileBase64":getDocStr(8), "nature":"admin"}
      file2 = {'action':"uploadFile", "ext":"pdf", "name":"Trav Dis", "fileBase64":getDocStr(8), "nature":"admin", "expirationDate":now}
      file3 = {'action':"uploadFile", "ext":"pdf", "name":"RC + DC", "fileBase64":getDocStr(8), "nature":"admin", "expirationDate":now}
      file4 = {'action':"uploadFile", "ext":"pdf", "name":"URSSAF", "fileBase64":getDocStr(8), "nature":"admin", "expirationDate":now}
      file5 = {'action':"uploadFile", "ext":"pdf", "name":"Cong??s Pay??s", "fileBase64":getDocStr(8), "nature":"admin", "expirationDate":now}
      file6 = {'action':"uploadFile", "ext":"pdf", "name":"Imp??ts", "fileBase64":getDocStr(8), "nature":"admin", "expirationDate":now}
      file7 = {'action':"uploadFile", "ext":"png", "name":"qualibat", "fileBase64":getDocStr(0), "nature":"labels", "expirationDate":dateForLabel}
      file8 = {'action':"uploadFile", "ext":"png", "name":"qualiElec", "fileBase64":getDocStr(0), "nature":"labels", "expirationDate":dateForLabel}
      file9 = {'action':"uploadFile", "ext":"png", "name":"artisanArt", "fileBase64":getDocStr(0), "nature":"labels", "expirationDate":dateForLabel}
      for file in [file1, file2, file3, file4, file5, file6, file7, file8, file9]:
        requests.post(url, headers=headersForImage, json=file)



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
        # company = {"id":companyId, 'name':establishmentValue[0], 'address': establishmentValue[1], 'activity': establishmentValue[2], 'siret': establishmentValue[3], 'ntva': establishmentValue[4]}
        post = {"action":"register", "firstname":firstName, "lastname":lastName, "email":mail, "password":"pwd", "company":establishmentValue[0], "siret": '85342059400014', "Role":role,"proposer":"","jobs":jobs}
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
        size = math.floor(1 + 20 * random.random())
        webSite = "https://monWebSite.fr"
        JobForCompany = [[math.floor(1 + random.random() * 40), math.floor(1 + random.random() * 4)], [math.floor(41 + random.random() * 40), math.floor(1 + random.random() * 4)], [math.floor(81 + random.random() * 40), math.floor(1 + random.random() * 4)]]
        LabelForCompany = [[math.floor(1 + random.random() * 9), dateForLabel], [math.floor(10 + random.random() * 9), dateForLabel], [math.floor(20 + random.random() * 3), dateForLabel]]
        post = {'action': 'modifyUser', 'UserProfile': {'id': companyId, 'cellPhone': '0629350418', 'Company': {'capital': capital, 'revenue': revenue, "webSite": webSite, "amount":amount, 'companyPhone': '0892976415', "allQualifications":True, 'JobForCompany':JobForCompany, 'LabelForCompany':LabelForCompany, "size":size}}}
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
      file = {'action':"uploadFile", "ext":"pdf", "name":"Kbis", "fileBase64":getDocStr(8), "nature":"admin"}
      data = requests.post(url, headers=headersForImage, json=file)
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
    headersST = headers
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
      data1 = {
        "headers":headers,
        "post":{'action': 'modifyUser', 'UserProfile': {'id': 3, 'cellPhone': '0629350418', "function": "Chef de Chantier", 'Company': {'capital': '307130', 'companyPhone': '0892976415', "revenue":"1200000", "amount":'28', 'JobForCompany':[[4,2], [5,3], [77,4]], 'LabelForCompany':[[1,now], [2,now]], "size":9}}}
      }
      data2 = {
        "headers":{'Authorization': f'Token {queryForToken("pme@g.com", "pwd")}'},
        "post":{'action': 'modifyUser', 'UserProfile': {'id': 4, 'cellPhone': '0629350418', "function": "Chef de Chantier", 'Company': {'capital': '407130', 'companyPhone': '0892976415', "revenue":"1300000", "amount":'28', 'JobForCompany':[[4,2], [5,3], [77,4]], 'LabelForCompany':[[1,now], [2,now]], "size":10}}}
      }
      data3 = {
        "headers":{'Authorization': f'Token {queryForToken("st2@g.com", "pwd")}'},
        "post":{'action': 'modifyUser', 'UserProfile': {'id': 5, 'cellPhone': '0628340317', "function": "Chef de Chantier", 'Company': {'capital': '507130', 'companyPhone': '0891966314', "revenue":"1400000", "amount":'52', 'JobForCompany':[[4,2], [5,3], [77,4]], 'LabelForCompany':[[1,now], [2,now]], "size":11}}}
      }
      data4 = {
        "headers":{'Authorization': f'Token {queryForToken("both@g.com", "pwd")}'},
        "post":{'action': 'modifyUser', 'UserProfile': {'id': 6, 'cellPhone': '0628340317', "function": "Chef de Chantier", 'Company': {'capital': '607130', 'companyPhone': '0891966314', "revenue":"1500000", "amount":'52', 'JobForCompany':[[4,2], [5,3], [77,4]], 'LabelForCompany':[[1,now], [2,now]], "size":12}}}
      }
      data5 = {
        "headers":{'Authorization': f'Token {queryForToken("aa@g.com", "pwd")}'},
        "post":{'action': 'modifyUser', 'UserProfile': {'id': 2, 'cellPhone': '0628340317', "function": "Chef de Chantier", 'Company': {'capital': '707130', 'companyPhone': '0891966314', "revenue":"1600000", "amount":'52', 'JobForCompany':[[4,2], [5,3], [77,4]], 'LabelForCompany':[[1,now], [2,now]], "size":13}}}
      }
      for data in [data1, data2, data3, data4, data5]:
        response = requests.post(url, headers=data["headers"], json=data["post"])

    elif query == "changeUserImage":
      tokenPme = queryForToken("pme@g.com", "pwd")
      headersPme = {'Authorization': f'Token {tokenPme}'}
      post = {'action':"changeUserImage", "ext":"png", "name":"image", "fileBase64":getDocStr(5)}
      requests.post(url, headers=headersPme, json=post)
      tokenSt2 = queryForToken("st2@g.com", "pwd")
      headersSt2 = {'Authorization': f'Token {tokenSt2}'}
      post = {'action':"changeUserImage", "ext":"png", "name":"image", "fileBase64":getDocStr(7)}
      response = requests.post(url, headers=headersSt2, json=post)
      post = {'action':"changeUserImage", "ext":"png", "name":"image", "fileBase64":getDocStr(6)}
      requests.post(url, headers=headers, json=post)
      post = {'action':"changeUserImage", "ext":"png", "name":"image", "fileBase64":getDocStr(5)}
      tokenBoth = queryForToken("both@g.com", "pwd")
      headersBoth = {'Authorization': f'Token {tokenBoth}'}
      requests.post(url, headers=headersBoth, json=post)

    elif query == "deleteUserImage":
      tokenPme = queryForToken("pme@g.com", "pwd")
      headersPme = {'Authorization': f'Token {tokenPme}'}
      response = requests.post(url, headers=headersPme, json={"action":"deleteUserImage"})
      post = {'action':"changeUserImage", "ext":"png", "name":"image", "fileBase64":getDocStr(5)}
      requests.post(url, headers=headersPme, json=post)

    elif query == "uploadPost":
      post1 = {'action':"uploadPost", "longitude":2.237779 , "latitude":48.848776, "address":"128 rue de Paris 92100 Boulogne", "Job":6, "numberOfPeople":3, "dueDate":f"2022-{nextMonth}-15", "startDate":f"2022-{nextMonth}-16", "endDate":f"2022-{nextMonth}-28", "DatePost":[f"2022-{nextMonth}-26", f"2022-{nextMonth}-27", f"2022-{nextMonth}-28"], "manPower":True, "counterOffer":True, "hourlyStart":"07:30", "hourlyEnd":"17:30", "currency":"???", "description":"Premi??re description d'un chantier", "amount":65243.10, "DetailedPost":["lavabo", "baignoire"]}
      post2 = {'action':"uploadPost", "longitude":2.324877 , "latitude":48.841625, "address":"106 rue du Cherche-Midi 75006 Paris", "Job":5, "numberOfPeople":1, "dueDate":f"2022-{nextMonth}-15", "startDate":f"2022-{nextMonth}-16", "endDate":f"2022-04-28", "DatePost":[f"2022-{nextMonth}-16", f"2022-{nextMonth}-17", f"2022-{nextMonth}-18"], "manPower":False, "counterOffer":True, "hourlyStart":"07:00", "hourlyEnd":"17:00", "currency":"???", "description":"Deuxi??me description d'un chantier", "amount":23456.10, "DetailedPost":["radiateur", "Chaudi??re"]}
      post3 = {'action':"uploadPost", "longitude":2.326881 , "latitude":48.841626, "address":"36 rue Dauphine 75006 Paris", "Job":10, "numberOfPeople":1, "dueDate":f"2022-{nextMonth}-15", "startDate":f"2022-{nextMonth}-15", "endDate":f"2022-{nextMonth}-18", "DatePost":[f"2022-{nextMonth}-15", f"2022-{nextMonth}-16", f"2022-{nextMonth}-17", f"2022-{nextMonth}-18"], "manPower":True, "counterOffer":True, "hourlyStart":"07:00", "hourlyEnd":"17:00", "currency":"???", "description":"troisi??me description d'un chantier", "amount":12345.10, "DetailedPost":["doublage", "cloison"]}
      post4 = {'action':"uploadPost", "longitude":2.325883 , "latitude":48.841627, "address":"28 rue de Fleurus 75006 Paris", "Job":10, "numberOfPeople":2, "dueDate":f"2022-{nextMonth}-18", "startDate":f"2022-{nextMonth}-16", "endDate":f"2022-{nextMonth}-28", "DatePost":[f"2022-{nextMonth}-21", f"2022-{nextMonth}-22", f"2022-{nextMonth}-23"], "manPower":True, "counterOffer":False, "hourlyStart":"07:00", "hourlyEnd":"17:00", "currency":"???", "description":"quatri??me description d'un chantier", "amount":1300.10, "DetailedPost":["doublage", "cloison", "pose", "mesure"]}
      post5 = {'action':"uploadPost", "longitude":2.325885 , "latitude":48.841628, "address":"34 rue Guynemer 75006 Paris", "Job":10, "numberOfPeople":1, "dueDate":f"2022-{nextMonth}-21", "startDate":f"2022-{nextMonth}-16", "endDate":f"2022-{nextMonth}-28", "DatePost":[f"2022-{nextMonth}-16", f"2022-{nextMonth}-17", f"2022-{nextMonth}-18"], "manPower":True, "counterOffer":False, "hourlyStart":"08:00", "hourlyEnd":"17:00", "currency":"???", "description":"cinqui??me description d'un chantier", "amount":1300.10, "DetailedPost":["cuisine", "salle de bain", "salon", "Chambre"]}
      post6 = {'action':"uploadPost", "longitude":2.324877 , "latitude":48.841625, "address":"108 rue du Cherche-Midi 75006 Paris", "Job":5, "numberOfPeople":1, "dueDate":f"2022-{nextMonth}-15", "startDate":f"2022-{nextMonth}-16", "endDate":f"2022-{nextMonth}-28", "DatePost":[f"2022-{nextMonth}-26", f"2022-{nextMonth}-27", f"2022-{nextMonth}-28"], "manPower":False, "counterOffer":True, "hourlyStart":"07:00", "hourlyEnd":"17:00", "currency":"???", "description":"Sixi??me description d'un chantier", "amount":23456.10, "DetailedPost":["radiateur", "Chaudi??re"]}
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
            "dueDate":f"2022-{nextMonth}-{str(startDate - 1)}",
            "startDate":f"2022-{nextMonth}-{str(startDate)}",
            "endDate":f"2022-{nextMonth}-{str(startDate + 3)}",
            "DatePost":[f"2022-{nextMonth}-{str(startDate)}", f"2022-{nextMonth}-{str(startDate + 1)}", f"2022-{nextMonth}-{str(startDate + 2)}", f"2022-{nextMonth}-{str(startDate + 3)}"],
            "manPower":random.random() > .5,
            "counterOffer":counterOffer,
            "hourlyStart":"07:30",
            "hourlyEnd":"17:30",
            "currency":"???",
            "description":"Premi??re description d'un chantier " + str(id),
            "amount":math.floor(1000 + random.random() * 4000),
            "DetailedPost":["salle de bain", "douche", "baignoire"],
            "draft": random.random() < 0.25
            }
          if flagMission:
            missionList[id] = {"mail":mail, "counterOffer":counterOffer, "amount":post["amount"]}
            post["draft"] = False
          requests.post(url, headers=headersNew, json=post)
        file1 = {'action':"uploadFile", "ext":"svg", "name":"Document technique", "fileBase64":getDocStr(4), "nature":"post", "Post":2}
        file2 = {'action':"uploadFile", "ext":"jpg", "name":"Plan", "fileBase64":getDocStr(2), "nature":"post", "Post":2}
        for file in [file1, file2]:
          requests.post(url, headers=headers, json=file)
          

    elif query == "modifyPost":
      post = {'action':"modifyPost", "id":1, "address":"126 rue de Paris 92100 Boulogne", "Job":5, "numberOfPeople":2, "dueDate":f"2022-{nextMonth}-15", "startDate":f"2022-{nextMonth}-16", "endDate":f"2022-{nextMonth}-28", "manPower":False, "counterOffer":False, "hourlyStart":"07:00", "hourlyEnd":"17:00", "currency":"???", "description":"Deuxi??me description d'un chantier", "amount":24456.10, "DetailedPost":["salle de bain", "douche", "lavabo"], "DatePost":[f"2022-{nextMonth}-15", f"2022-{nextMonth}-16", f"2022-{nextMonth}-17"]}
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
      post = {'action':"uploadPost", "address":"129 rue de Paris 92100 Boulogne", "Job":9, "numberOfPeople":3, "dueDate":f"2022-{nextMonth}-15", "startDate":f"2022-{nextMonth}-16", "endDate":f"2022-{nextMonth}-28", "manPower":True, "counterOffer":True, "hourlyStart":"7:30", "hourlyEnd":"17:30", "currency":"???", "description":"Premi??re description d'un chantier", "amount":65243.10, "DetailedPost":["lavabo", "baignoire"]}
      response = requests.post(url, headers=headers, json=post)
      for key in json.loads(response.text)["Post"].keys():
        if key != "uploadPost":
          response = requests.get(url, headers=headers, params={"action":"deletePost", "id":key})
    elif query == "modifyDisponibility":
      post = {'action':"modifyDisponibility", "disponibility":[[f"2022-{nextMonth}-13", "Disponible"], [f"2022-{nextMonth}-14", "Disponible Sous Conditions"], [f"2022-{nextMonth}-15", "Non Disponible"]]}
      response = requests.post(url, headers=headers, json=post)
    elif query == "uploadFile":
      file1 = {'action':"uploadFile", "ext":"svg", "name":"Document technique", "fileBase64":getDocStr(4), "nature":"post", "Post":2}
      file2 = {'action':"uploadFile", "ext":"jpg", "name":"Plan", "fileBase64":getDocStr(2), "nature":"post", "Post":2}
      for file in [file1, file2]:
        response = requests.post(url, headers=headers, json=file)
        data = json.loads(response.text)

      
    elif query == "modifyFile":
      response = requests.post(url, headers=headers, json={'action':"modifyFile", "fileId":4, "expirationDate":f"2022-12-12"})
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
      requests.get(url, headers=headers, params={'action':"applyPost", "Post":2, "amount":800})
      requests.get(url, headers=headers, params={'action':"applyPost", "Post":3, "amount":1000})
      requests.get(url, headers=headers, params={'action':"applyPost", "Post":4})
      requests.get(url, headers=headers, params={'action':"applyPost", "Post":5})
      tokenSt2 = queryForToken("st2@g.com", "pwd")
      headers = {'Authorization': f'Token {tokenSt2}'}
      requests.get(url, headers=headers, params={'action':"applyPost", "Post":2, "amount":1200})
      requests.get(url, headers=headers, params={'action':"applyPost", "Post":3, "amount":1400})
      requests.get(url, headers=headers, params={'action':"applyPost", "Post":4})
      requests.get(url, headers=headers, params={'action':"applyPost", "Post":5})
      response = requests.get(url, headers=headers, params={'action':"applyPost", "Post":6, "amount":1500})
      if numberCompanies:  
        headers = {'Authorization': f'Token {token}'}
        for id, values in missionList.items():
          data = requests.get(url, headers=headers, params={'action':"applyPost", "Post":id, "amount":values["amount"] / 2})
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
      requests.get(url, headers=headers, params={'action':"handleCandidateForPost", "Candidate":9, "response":"true"})
      response = requests.get(url, headers=headers, params={'action':"handleCandidateForPost", "Candidate":1, "response":"true"})
      if numberCompanies:
        for id, values in missionList.items():
          if random.random() > 0.5 and "candidateId" in values:
            print("handleCandidateForPost post", id, "candidate", values)
            data = requests.get(url, headers=headers, params={'action':"handleCandidateForPost", "Candidate":values["candidateId"], "response":"true"})
            print("handleCandidateForPost", json.loads(data.text))
            values["mission"] = True

    elif query == "signContract":
      for missionId in [2,3,4,6]:
        requests.get(url, headers=headers, params={"action":"signContract", "missionId":missionId, "view":"ST"})
        response = requests.get(url, headers=headersPme, params={"action":"signContract", "missionId":missionId, "view":"PME"})
      if numberCompanies:
        for id, values in missionList.items():
          if "mission" in values:
            requests.get(url, headers=headers, params={"action":"signContract", "missionId":id, "view":"ST"})
            requests.get(url, headers=headersPme, params={"action":"signContract", "missionId":id, "view":"PME"})
    
    elif query == "modifyDetailedPost":
      supervisionST= ["J'ai fini.", "OK pour les t??ches du jour.", "Pas de souci aujourd'hui.", "Voila une t??che difficile.", "Le chantier est termin??."]
      supervisionPME = ["Les t??ches du jour sont bien faites.", "Tout est parfait, merci.", "Attention aux finitions.", "Voila une t??che difficile."]
      index = 0
      for detailedId, dateId in [(10, 11), (8, 12), (9, 13), (7,13), (3, 4), (4, 5), (6, 5), (5, 7), (5, 8), (6, 9), (6,  10), (15, 17), (16, 18), (16, 19)]:
        post = {"action":"modifyDetailedPost", "detailedPost":{"id":detailedId}, "unset":False, "datePostId":dateId}
        response = requests.post(url, headers=headers, json=post)
        dict = json.loads(response.text)
        detailsId = list(dict['detailedPost'].keys())
        dateId = dict["fatherId"]
        supervision = {'action':"createSupervision", "detailedPostId":detailsId[0], "comment":supervisionPME[index % len(supervisionPME)]}
        requests.post(url, headers=headersPme, json=supervision)
        supervision = {'action':"createSupervision", "datePostId":dateId, "comment":supervisionST[index % len(supervisionST)]}
        data = requests.post(url, headers=headersPme, json=supervision)

        dict = json.loads(data.text)
        supervisionId = list(dict['supervision'].keys())[0]
        image = {'action':"uploadImageSupervision", "supervisionId":supervisionId, "ext":"png", "fileBase64":getDocStr(2)}
        data = requests.post(url, headers=headersPme, json=image)
        index += 1

    elif query == "modifyMissionDate":
      post = {"action":"modifyMissionDate", "missionId": 3, "hourlyStart":"06:02", "hourlyEnd":"19:02"}
      response = requests.post(url, headers=headers, json=post)

    elif query == "validateMissionDate":
      post1 = {'action':"validateMissionDate", "missionId": 3, "field":"hourlyStart", "state":True}
      post2 = {'action':"validateMissionDate", "missionId": 3, "field":"hourlyEnd", "state":False}
      for post in [post1, post2]:
        response = requests.post(url, headers=headers, json=post)

    elif query == "closeMission":
      post = {"action":"closeMission", "missionId": 4, "qualityStars":4, "qualityComment":"tr??s bon travail", "securityStars":4, "securityComment":"Un vrai sous-traitant qualibat", "organisationStars":5, "organisationComment":"Une organisation parfaite"}
      response = requests.post(url, headers=headers, json=post)
    elif query == "closeMissionST":
      post = {"action":"closeMissionST", "missionId": 4, "vibeSTStars":5, "vibeSTComment":"Ambiance excellente", "securitySTStars":5, "securitySTComment":"une s??curit?? parfaite", "organisationSTStars":5, "organisationSTComment":"Une organisation impeccable"}
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
      response = requests.get(url, headers=headers, params={"action":"askRecommandation", "email":"jeanluc.walter@fantasiapp.com", "firsrtName":"Th??ophile", "lastName":"Traitant", "company":"Sous-traitant", "companyId":3, "view":"ST"})
    elif query == "giveRecommandation":
      post1 = {"action":"giveRecommandation", "companyRecommanded":3, "firstNameRecommanding":"Maxime", "lastNameRecommanding":"Baraton", "companyNameRecommanding":"Fantasiapp", "qualityStars":4, "qualityComment":"Un travail remarquable", "securityStars":5, "securityComment":"Une s??curit?? digne de la Nasa", "organisationStars":4, "organisationComment":"Rien ?? dire", "view":"ST"}
      post2 = {"action":"giveRecommandation", "companyRecommanded":3, "firstNameRecommanding":"Dyvia", "lastNameRecommanding":"Gaultier", "companyNameRecommanding":"Loreal", "qualityStars":5, "qualityComment":"Un travail bien fait", "securityStars":5, "securityComment":"Une s??curit?? digne de la Nasa", "organisationStars":4, "organisationComment":"Rien ?? dire", "view":"ST"}
      post3 = {"action":"giveRecommandation", "companyRecommanded":3, "firstNameRecommanding":"William", "lastNameRecommanding":"Baraton", "companyNameRecommanding":"Carrefour", "qualityStars":4, "qualityComment":"Un travail remarquable", "securityStars":5, "securityComment":"Une s??curit?? digne de la Nasa", "organisationStars":4, "organisationComment":"Rien ?? dire", "view":"ST"}
      post4 = {"action":"giveRecommandation", "companyRecommanded":3, "firstNameRecommanding":"Lucas", "lastNameRecommanding":"Gaultier", "companyNameRecommanding":"Microsoft", "qualityStars":5, "qualityComment":"Un travail bien fait", "securityStars":5, "securityComment":"Une s??curit?? digne de la Nasa", "organisationStars":4, "organisationComment":"Rien ?? dire", "view":"ST"}
      post5 = {"action":"giveRecommandation", "companyRecommanded":3, "firstNameRecommanding":"Sarah", "lastNameRecommanding":"Baraton", "companyNameRecommanding":"BatiUni", "qualityStars":4, "qualityComment":"Un travail remarquable", "securityStars":5, "securityComment":"Une s??curit?? digne de la Nasa", "organisationStars":4, "organisationComment":"Rien ?? dire", "view":"ST"}
      post6 = {"action":"giveRecommandation", "companyRecommanded":3, "firstNameRecommanding":"Cassiop??e", "lastNameRecommanding":"Gaultier", "companyNameRecommanding":"Artech", "qualityStars":5, "qualityComment":"Un travail bien fait", "securityStars":5, "securityComment":"Une s??curit?? digne de la Nasa", "organisationStars":4, "organisationComment":"Rien ?? dire", "view":"ST"}
      post7 = {"action":"giveRecommandation", "companyRecommanded":3, "firstNameRecommanding":"Jean-Luc", "lastNameRecommanding":"Baraton", "companyNameRecommanding":"Reportive", "qualityStars":4, "qualityComment":"Un travail remarquable", "securityStars":5, "securityComment":"Une s??curit?? digne de la Nasa", "organisationStars":4, "organisationComment":"Rien ?? dire", "view":"ST"}
      post8 = {"action":"giveRecommandation", "companyRecommanded":3, "firstNameRecommanding":"Maude", "lastNameRecommanding":"Gaultier", "companyNameRecommanding":"Google", "qualityStars":5, "qualityComment":"Un travail bien fait", "securityStars":5, "securityComment":"Une s??curit?? digne de la Nasa", "organisationStars":4, "organisationComment":"Rien ?? dire", "view":"ST"}
      for post in [post1, post2, post3, post4, post5, post6, post7, post8]:
        response = requests.post(f'{address}/initialize/', headers=headers, json=post)
    elif query == "giveNotificationToken":
      response = requests.get(url, headers=headers, params={"action":"giveNotificationToken", "token":"La valeur du token qui devrait ??tre enregist??e"})
    elif query == "duplicatePost":
      print("duplicatePost")
      response = requests.get(url, headers=headers, params={"action":"duplicatePost", "id":22})
        # response = requests.get(url, headers=headers, params={"action":"blockCompany", "companyId":1, "status":"true"})
    elif query == "test":
      response = requests.get(url, headers=headers, params={"action":"test", "missionId":4})
  if response and query != "downloadFile":
    data = json.loads(response.text)
    print("data", data)
  else:
    print("no answer")
if query == "all":
  keys = ["buildDB", "register", "getGeneralData", "registerMany", "removeLabelForCompany", "modifyUser", "changeUserImage", "getUserData", "uploadPost", "deletePost", "modifyPost", "getPost", "setFavorite", "removeFavorite", "uploadFile", "modifyFile", "downloadFile", "switchDraft", "isViewed", "applyPost", "unapplyPost", "handleCandidateForPost", "signContract", "modifyDetailedPost", "modifyMissionDate", "validateMissionDate", "modifyDisponibility", "closeMission", "closeMissionST", "boostPost", "blockCompany", "askRecommandation", "giveRecommandation", "giveNotificationToken"]# 
  for key in keys:
    query = key
    executeQuery()
else:
  executeQuery()

