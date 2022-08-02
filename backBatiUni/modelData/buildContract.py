import fpdf
from fpdf import FPDF
from ..models import *


class MyPdf(FPDF):

  # def __init__(self):
  #   self.userProfile = None
  #   print(self.userProfile.Company.name)
  #   file = File.objects.filter(nature="userImage", Company=self.userProfile.Company)
  #   print("buildContract", file)

  def header(self):
    print("header")
    file = File.objects.filter(nature="userImage", Company=self.userProfile.Company)
    if file:
      file = file[0]
      self.image(file.path, 10, 8, 33)
    self.set_font('Arial', 'BI', 15)
    self.set_xy(60,20)
    self.cell(120, 10, "ACCORD - CADRE DE SOUS-TRAITANCE", 1, 1, 'C')
    self.ln(30)

  def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')


class BuildContract:
  part1Title = "Désignation des parties contractantes"
  part1SubTitle1 = "ENTRE LES SOUSSIGNÉES :"
  __part1ST1Text1 = "La Société ALLEAUME ET GOULART, société par actions simplifié au capital 100 000,00 euros, ayant son siège social au 9-11 rue Vintimille 75009 Paris, immatriculée au RCS de Paris et identifiée sous le numéro 732 039 417, représentée aux fins des présentes par Monsieur Hubert ALLEAUME agissant en tant que Président, dûment habilité,"

  def __init__(self, userProfile):
    self.userProfile = userProfile
    pdf = MyPdf('P', 'mm', 'A4')
    pdf.userProfile = userProfile
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial', 'BU', 14)
    pdf.cell(190, 10, self.part1Title, 0, 1, 'L')
    pdf.set_x(10)
    pdf.set_font('Arial', 'BU', 12)
    pdf.cell(190, 10, self.part1SubTitle1, 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(190, 5, self.part1ST1Text1)
    pdf.ln(5)

    for i in range(1, 41):
      pdf.cell(0, 6, 'Printing line number ' + str(i), 0, 1)
    pdf.output('./files/documents/tuto1.pdf', 'F')

  @property
  def part1ST1Text1(self):
    return self.translateText(self.__part1ST1Text1)

  @property
  def __findCompany(self):
    return self.userProfile.Company.name

  def translateText(self, str):
    translated = str
    listTranslation = {"$Company$": self.__findCompany}
    for key, value in listTranslation.items():
      translated = translated.replace(key, value)
    return translated

def specialChar(string):
    latinStr = string.encode('utf-8').decode('iso-8859-1')
    print(latinStr)
    for key, value in {'â':"-"}.items():
      latinStr.replace(key, value)
    print(latinStr)
    return latinStr


