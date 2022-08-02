import fpdf
from fpdf import FPDF
from ..models import *


class MyPdf(FPDF):

  def header(self):
    print("header")
    file = File.objects.filter(nature="userImage", Company=self.pmeProfile.Company)
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
  __part1ST1Text1 = "La Société $Company$, société par actions simplifié $Capital$, $Address$, $Siret$, $Represent$"
  part1ST1Text2 = "Ci-après dénommée « l'Entrepreneur Principal »"
  part1ST1Text3 = "D'UNE PART"

  def __init__(self, pmeProfile):
    self.pmeProfile = pmeProfile
    pdf = MyPdf('P', 'mm', 'A4')
    pdf.pmeProfile = pmeProfile
    pdf.alias_nb_pages()
    pdf.add_page()
    self.writePart1(pdf)
    for i in range(1, 41):
      pdf.cell(0, 6, 'Printing line number ' + str(i), 0, 1)
    pdf.output('./files/documents/tuto1.pdf', 'F')

  def writePart1(self, pdf):
    pdf.set_font('Arial', 'BU', 14)
    pdf.cell(190, 10, self.part1Title, 0, 1, 'L')
    pdf.set_x(10)
    pdf.set_font('Arial', 'BU', 12)
    pdf.cell(190, 10, self.part1SubTitle1, 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(190, 5, self.part1ST1Text1)
    pdf.ln(5)
    pdf.set_font('Arial', 'I', 12)
    pdf.cell(190, 10, self.part1ST1Text2, 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.cell(190, 10, self.part1ST1Text3, 0, 1, 'R')

  @property
  def part1ST1Text1(self):
    return self.translateText(self.__part1ST1Text1)

  @property
  def __findCompany(self):
    return self.pmeProfile.Company.name

  @property
  def __findCapital(self):
    if self.pmeProfile.Company.capital:
      capital = f"{self.pmeProfile.Company.capital:,}".replace(",", " ")
      return f'au capital de {capital} euros'
    return ""

  @property
  def __findAddress(self):
    return f"ayant son siège social au {self.pmeProfile.Company.address}"

  @property
  def __findSiret(self):
    return f"identifiée par son numéro de Siret : {self.pmeProfile.Company.siret}"

  @property
  def __findRepresent(self):
    represent = f"représentée aux fins des présentes par Monsieur {self.pmeProfile.firstName} {self.pmeProfile.lastName}"
    if self.pmeProfile.function:
      represent += f" agissant en tant que {self.pmeProfile.function}"
    return represent + ", dûment habilité."


  def translateText(self, str):
    translated = str
    listTranslation = {"$Company$": self.__findCompany, "$Capital$":self.__findCapital, "$Address$":self.__findAddress, "$Siret$":self.__findSiret, "$Represent$":self.__findRepresent}
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


