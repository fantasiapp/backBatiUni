from ..models import *
import mysql.connector as db
import os
from dotenv import load_dotenv

class CreateNewDataBase:
  listTable = {"UserProfile":UserProfile, "JobForCompany":JobForCompany, "LabelForCompany":LabelForCompany, "Job":Job, "Role":Role, "Label":Label, "Company":Company}

  def __init__(self):
    load_dotenv()
    self.connection = db.connect(
      user = os.getenv('DB_USERNAME'),
      password = os.getenv('DB_PASSWORD'),
      host = os.getenv('DB_HOST'),
      database = os.getenv('DB_NAME'),
    )
    self.cursor = self.connection.cursor()

  def reloadDataBase(self):
    print("reloadDataBase")
    answer = self.emptyDataBase()
    return self.fillupDataBase(answer)

  def emptyDataBase (self):
    for table in CreateNewDataBase.listTable.values():
      table.objects.all().delete()
      tableName = table.objects.model._meta.db_table
      self.cursor.execute(f"ALTER TABLE {tableName} AUTO_INCREMENT=1;")
    for user in User.objects.all():
      if user.username != "jlw":
        user.delete()
    self.cursor.execute("ALTER TABLE auth_user AUTO_INCREMENT=1;")
    return {"emptyDataBase":"OK"}

  def fillupDataBase (self, response= {}):
    for function, table in CreateNewDataBase.listTable.items():
      for key, value in getattr(self, "fillup" + function)(table).items():
        response[key] = value
    self.connection.close() 
    return response

  def fillupUserProfile(self, table): return {} 
  def fillupCompany(self, table):return {}
  def fillupLabelForCompany(self, table): return {} 
  def fillupJobForCompany(self, table):return {}

  def fillupJob(self, table):
    listJobs = ['TCE', 'Cuisiniste', 'Ingénieur en Aménagement et Urbanisme', "Ingénieur d'affaires du BTP", 'Economiste de la construction', 'Dessinateur technique', 'Conducteur de travaux bâtiment', "Chef d'équipe BTP", 'Calculateur projeteur en béton armé', 'Technicien Expert VRD', 'Métreur', 'Maître d’œuvre', 'Ingénieur en Génie Civil', 'Géomètre topographe', 'Assistant d’entrepreneur du BTP', 'Aide-conducteur de travaux', 'Acousticien', 'Ingénieur études de prix', 'Peintre décorateur', 'Chef de chantier', 'Conducteur d’engins', 'Agenceur de cuisines et de salles de bains', 'Vitrier', 'Vitrailliste', 'Restaurateur d’art', 'Menuisier', 'Terrassier', 'Maçon', 'Dessinateur-Projeteur', 'Couvreur-zingueur', 'Serrurier', 'Plombier', 'Electricien', 'Chauffagiste', 'Carreleur faïenceur', 'Câbleur', 'Bainiste', 'Collaborateur d’architecte', 'Charpentier', 'Designer', 'Ferronnier d’art']
    for job in listJobs:
      table.objects.create(name=job)
    return {"fillupJob":"OK"}

  def fillupRole(self, table):
    listRole = ["Une entreprise à la recherche de sous-traitances", "Un sous-traitant à la recherche d'une entreprise", "Les deux"]
    for role in listRole:
      table.objects.create(name=role)
    return {"fillupRole":"OK"}

  def fillupLabel(self, table):
    listLabel = ['Qualibat', 'RGE', 'RGE Eco Artisan', 'NF', 'Effinergie', 'Handibat', 'Qualifelec', 'Qualit’EnR', 'Quali’Sol', 'Quali’Bois', 'Quali’PV', 'Quali’Pac', 'Certibat', 'CERQUAL Qualitel Certification', 'Autres...']
    for label in listLabel:
      table.objects.create(name=label)
    return {"fillupLabel":"OK"}




