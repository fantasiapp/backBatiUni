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
  part1SubTitle2 = "ET :"
  __part1ST1Text1 = "La Société $Company$, société par actions simplifié $Capital$, $Address$, $Siret$, $Represent$"
  part1ST1Text2 = "Ci-après dénommée « l'Entrepreneur Principal »"
  part1ST2Text2 = "Ci-après dénommée « le Sous-Traitant »"
  part1ST1Text3 = "D'UNE PART"
  part1ST2Text3 = "L'entrepreneur Principal et le Sous-Traitant étant ci-après dénommés ensemble les « Parties » ou individuellement une « Partie »."
  part1ST2Text4 = "D'AUTRE PART"

  part2Title = "EXPOSÉ PRÉALABLE"
  __part2Text1 = "La société $Company$, dans le cadre de son activité de Contractant Général, ci-après l'Entrepreneur Principal, se voit confier par des maîtres d'ouvrages, des missions de conception - réalisation de l'aménagement de locaux à usage de bureaux, activités ou commerce, ci-après le « Contrat Principal »."
  part2Text2 = "Pour mener à bien ses missions, la société $Company$ sous-traite tout ou partie des prestations et/ou des travaux à des sous-traitants."
  __part2Text3 = "La société $Company$, ci-après le Sous-Traitant, est une société spécialisée et dispose à ce titre des compétences, moyens et installations techniques, de la logistique et de l'expérience nécessaire à la réalisation de missions de sous-traitance pour le compte de l'Entrepreneur Principal."
  part2Text4 = "L'Entrepreneur Principal et le Sous-Traitant se sont rapprochés et ont défini les conditions générales de leur collaboration aux termes du présent accord - cadre de sous-traitance, ci-après « le Contrat »."
  part2Title2 = "IL A AINSI ETE ARRETE ET CONVENU CE QUI SUIT :"

  art01Title = "ARTICLE I : OBJET DU CONTRAT"
  artO1Par1 = "I.1. Le présent accord - cadre de sous-traitance, ci-après « le Contrat », définit les conditions générales de la collaboration entre les Parties donnant lieu à des missions de sous-traitance que l'Entrepreneur Principal confie au Sous-Traitant, opération par opération, et que ce dernier s'engage à exécuter, pour mener à bien l'exécution de tout Contrat Principal confié par un maître d'ouvrage ci-après « le Maître d'Ouvrage » à l'Entrepreneur Principal. A ce titre, il est expressément convenu entre les Parties que l'Entrepreneur Principal n'est en aucun cas lié au Sous-Traitant par une obligation d'exclusivité et quil pourra confier des missions de sous-traitance pour l'exécution de tout Contrat Principal à tout sous-traitant de sons choix."
  artO1Par2 = "I.2. Les conditions particulières de chaque mission de sous-traitance confiée par l'Entrepreneur Principal au Sous-Traitant seront quant à elles précisées sur les bons de commande écrits établis pour chaque mission, ci-après « le Bon de Commande » qui complétera les présentes conditions générales. Chaque Bon de Commande, communiqué par l'Entrepreneur Principal avant le démarrage de chaque mission, comprendra obligatoirement le devis descriptif du Sous-Traitant, la mention de la date de démarrage et de la date de réception des travaux sous-traités le montant et les modalités de paiement du prix de la mission de sous-traitance."
  artO1Par3 = "I.3. Les Parties reconnaissent expressément que le sort de toute mission de sous-traitance sera dépendant du sort du Contrat Principal ; en conséquence, la prise d'effet du Contrat Principal conditionnera la prise d'effet de la mission de sous-traitance. De la même façon, toute évolution du Contrat Principal, pour quelque motif que ce soit, entraînera celle de la mission de sous-traitance, ce que le Sous-traitant accepte expressément."
  artO1Par4 = "I.4. Il est rappelé que chaque mission de sous-traitance est soumise, notamment aux dispositions de la loi n° 71-584 du 16 juillet 1971 et à celles de la loi n°75-1334 du 31 décembre 1975, et plus généralement aux dispositions légales et réglementaires applicables à la sous-traitance."
# ARTICLE II      : DUREE   
# Le Contrat est conclu pour une durée indéterminée. Il entrera en vigueur à 
# compter du jour de sa signature. Il pourra être résilié dans les conditions 
# indiquées à l'article VIII ci-après.
# ARTICLE III - DOCUMENTS CONTRACTUELS - HIERARCHIE 
# III.1. Les Parties reconnaissent expressément être liées par les 
# documents contractuels suivants      :  
# 1. Le Contrat et ses annexes,
# 2. Le Bon de Commande comprenant le devis descriptif du Sous-
# Traitant,
# 3. Les plans et tous documents techniques par le Maître d'Ouvrage, 
# l'Entrepreneur Principal, les bureaux techniques, le bureau de 
# contrôle,
# 4. Les comptes-rendus de chantier,
# 5. Le calendrier d'exécution des travaux,
# 6. Tout avenant ou document valant avenant modificatif au Bon de 
# Commande comme une demande d'intervention ou de travaux.

# De convention expresse entre les Parties, les dispositions consignées dans les 
# comptes rendus de chantier transmis au Sous-traitant auront une valeur 
# contractuelle dans la mesure où elles n'auront pas été contestées par le Sous-
# traitant dans un délai de 48 heures après leur réception dont la preuve pourra 
# être rapportée par tout moyen.



  def __init__(self, pmeProfile, stProfile):
    self.pmeProfile = pmeProfile
    self.stProfile = stProfile
    pdf = MyPdf('P', 'mm', 'A4')
    pdf.pmeProfile = pmeProfile
    pdf.alias_nb_pages()
    pdf.add_page()
    self.writePart1Text1(pdf)
    self.writePart1Text2(pdf)
    self.writePart2(pdf)
    self.writeArticle01(pdf)

    for i in range(1, 41):
      pdf.cell(0, 6, 'Printing line number ' + str(i), 0, 1)
    pdf.output('./files/documents/tuto1.pdf', 'F')

  def writePart1Text1(self, pdf):
    pdf.set_font('Arial', 'BU', 14)
    pdf.cell(190, 10, self.part1Title, 0, 1, 'L')
    pdf.set_font('Arial', 'BU', 12)
    pdf.cell(190, 10, self.part1SubTitle1, 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(190, 5, self.part1ST1Text1("pme"))
    pdf.ln(5)
    pdf.set_font('Arial', 'I', 12)
    pdf.cell(190, 10, self.part1ST1Text2, 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.cell(190, 10, self.part1ST1Text3, 0, 1, 'R')

  def writePart1Text2(self, pdf):
    pdf.set_font('Arial', 'BU', 12)
    pdf.cell(190, 10, self.part1SubTitle2, 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(190, 5, self.part1ST1Text1("st"))
    pdf.ln(5)
    pdf.set_font('Arial', 'I', 12)
    pdf.cell(190, 10, self.part1ST2Text2, 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(190, 5, self.part1ST2Text3)
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    pdf.cell(190, 5, self.part1ST2Text4, 0, 1, 'R')
    pdf.ln(20)

  def writePart2(self, pdf):
    pdf.set_font('Arial', 'BU', 12)
    pdf.cell(190, 10, self.part2Title, 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(190, 5, self.part2Text1)
    pdf.ln(2)
    pdf.multi_cell(190, 5, self.part2Text2)
    pdf.ln(2)
    pdf.multi_cell(190, 5, self.part2Text3)
    pdf.ln(2)
    pdf.multi_cell(190, 5, self.part2Text4)
    pdf.ln(5)
    pdf.set_font('Arial', 'BU', 12)
    pdf.cell(190, 10, self.part2Title2, 0, 1, 'L')
    pdf.ln(10)

  def writeArticle01(self, pdf):
    dictData = {"title":self.art01Title, "paragraphs":[self.artO1Par1, self.artO1Par2, self.artO1Par3, self.artO1Par4]}
    self.writeArticleGeneric(pdf, dictData)

  def writeArticleGeneric(self, pdf, dictData):
    pdf.set_font('Arial', 'BU', 12)
    pdf.cell(190, 10, dictData["title"], 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    for paragraph in dictData["paragraphs"]:
      pdf.multi_cell(190, 5, paragraph)
      pdf.ln(2)
    pdf.ln(10)

# Utilitaires
  def part1ST1Text1(self, nature="pme"):
    return self.translateText(self.__part2Text1, nature)

  @property
  def part2Text1(self):
    return self.translateText(self.__part2Text1, "pme")

  @property
  def part2Text3(self):
    return self.translateText(self.__part2Text3, "st")

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


