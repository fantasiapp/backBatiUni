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

  def __init__(self, pmeProfile, stProfile):
    self.pmeProfile = pmeProfile
    pdf = MyPdf('P', 'mm', 'A4')
    pdf.pmeProfile = pmeProfile
    pdf.stProfile = stProfile
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
    pdf.multi_cell(190, 5, self.part1ST1Text1("pme"))
    pdf.ln(5)
    pdf.set_font('Arial', 'I', 12)
    pdf.cell(190, 10, self.part1ST1Text2, 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.cell(190, 10, self.part1ST1Text3, 0, 1, 'R')

  def part1ST1Text1(self, nature="pme"):
    print("part1ST1Text1", self.__part1ST1Text1, nature)
    return self.translateText(self.__part1ST1Text1, nature)

  def __findCompany(self, nature):
    return self.pmeProfile.Company.name if nature == "pme" else self.stProfile.Company.name

  def __findCapital(self, nature):
    profile = self.pmeProfile if nature == "pme" else self.stProfile
    if profile.Company.capital:
      capital = f"{profile.Company.capital:,}".replace(",", " ").replace(".", ",")
      return f'au capital de {capital} euros'
    return ""

  def __findAddress(self, nature):
    profile = self.pmeProfile if nature == "pme" else self.stProfile
    return f"ayant son siège social au {profile.Company.address}"

  def __findSiret(self, nature):
    profile = self.pmeProfile if nature == "pme" else self.stProfile
    return f"identifiée par son numéro de Siret : {profile.Company.siret}"

  def __findRepresent(self, nature):
    profile = self.pmeProfile if nature == "pme" else self.stProfile
    represent = f"représentée aux fins des présentes par Monsieur {profile.firstName} {profile.lastName}"
    if self.pmeProfile.function:
      represent += f" agissant en tant que {profile.function}"
    return represent + ", dûment habilité."


  def translateText(self, str, nature):
    translated = str
    listTranslation = {"$Company$": self.__findCompany(nature), "$Capital$":self.__findCapital(nature), "$Address$":self.__findAddress(nature), "$Siret$":self.__findSiret(nature), "$Represent$":self.__findRepresent(nature)}
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


