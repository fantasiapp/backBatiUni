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
  
  art02Title = "ARTICLE II : DURÉE"
  artO2Par1 = "Le Contrat est conclu pour une durée indéterminée. Il entrera en vigueur à compter du jour de sa signature. Il pourra être résilié dans les conditions indiquées à l'article VIII ci-après."
  
  art03Title = "ARTICLE III - DOCUMENTS CONTRACTUELS - HIÉRARCHIE"
  artO3ST = "III.1. Les Parties reconnaissent expressément être liées par les documents contractuels suivants :"
  artO3Par1 = "1. Le Contrat et ses annexes."
  artO3Par2 = "2. Le Bon de Commande comprenant le devis descriptif du Sous-Traitant."
  artO3Par3 = "3. Les plans et tous documents techniques par le Maître d'Ouvrage, l'Entrepreneur Principal, les bureaux techniques, le bureau de contrôle."
  artO3Par4 = "4. Les comptes-rendus de chantier."
  artO3Par5 = "5. Le calendrier d'exécution des travaux."
  artO3Par6 = "6. Tout avenant ou document valant avenant modificatif au Bon de Commande comme une demande d'intervention ou de travaux."
  artO3Par7 = "De convention expresse entre les Parties, les dispositions consignées dans les comptes rendus de chantier transmis au Sous-traitant auront une valeur contractuelle dans la mesure où elles n'auront pas été contestées par le Sous-traitant dans un délai de 48 heures après leur réception dont la preuve pourra être rapportée par tout moyen."
  artO3Par8 = "III.2. Les Parties conviennent qu’en cas de contradiction entre les différents documents contractuels susvisés, l’ordre de priorité s’établira dans l’ordre d’énonciation desdits documents ci-dessus."

  art04Title = "ARTICLE IV – OBLIGATIONS DE L’ENTREPRENEUR PRINCIPAL"
  artO4Par1 = "Avant le début de l’exécution des travaux sous-traités au Sous-Traitant, l’Entrepreneur Principal doit faire savoir au Sous-Traitant si le Maître d’Ouvrage l’a accepté et s’il a agréé ses conditions de paiement ;"
  artO4Par2 = "L’Entrepreneur Principal s’engage à fournir au Sous-traitant en temps utile tous les plans et documents nécessaires à l’exécution de sa mission de sous-traitance ;"
  artO4Par3 = "L’Entrepreneur Principal s’interdit de donner quelque ordre ou directive que ce soit ou d’effectuer quelque contrôle que ce soit vis-à-vis du personnel du Sous-Traitant sur lequel il ne dispose d’aucun pouvoir disciplinaire ni réglementaire."
  
  art05Title = "ARTICLE V - OBLIGATIONS DU SOUS TRAITANT"
  art05SubTitle1 = "V.1. Obligation Générales"
  artO5Par01 = "*   Le Sous-Traitant s’engage à mener à bonne fin l’exécution de ses prestations de sous-traitance, dans le cadre de son obligation de résultat ;"
  artO5Par02 = "*   Le Sous-Traitant s’engage à justifier à première demande de ses compétences professionnelles par tout moyen à sa convenance ;"
  artO5Par03 = "*   Le Sous-Traitant s’engage à faire preuve d’une exigence de qualité maximale dans l’exécution de ses prestations et notamment en matière de matériaux et autres fournitures utilisés."
  artO5Par04 = "*   Le Sous-Traitant s’engage à respecter en toutes circonstances ses obligations de bonne foi et de loyauté vis-à-vis de l’Entrepreneur Principal."
  artO5Par05 = "*   Le Sous-Traitant s’engage à exécuter ses prestations selon les règles de l’art de sa profession, dans le respect des plans et descriptifs fournis par l’Entrepreneur Principal et des spécifications définies dans les cahiers des charges ainsi que suivant les indications résultant des rendez-vous de chantier et réunions de pilotage. De plus, il devra impérativement respecter les délais d’exécution des travaux et le calendrier d’exécution desdits travaux, même recalés ou décalés, ces dispositions formant une condition essentielle du Contrat, ce que le Sous-Traitant reconnait expressément ;"
  artO5Par06 = "*   Le Sous-Traitant s’engage à informer sans délai l’Entrepreneur Principal en cas de retard dans l’exécution de ses prestations ;"
  artO5Par07 = "*   Le Sous-Traitant sera responsable des dommages de toutes natures causés à l’occasion de l’exécution de ses prestations et garantit l’Entrepreneur Principal de tous recours et actions à son encontre de ce chef ;"
  artO5Par08 = "*   Le Sous-Traitant s’engage à faire toutes les observations opportunes au regard des règles de l’art de sa profession sur les documents et instructions qui sont portés à sa connaissance, ainsi que sur la nature des existants ;"
  artO5Par09 = "*   Le Sous-Traitant s’engage à prendre pleine connaissance de l’immeuble existant et le cas échéant, du plan de masse et de tous les plans et documents utiles à la réalisation des travaux, ainsi que des sites, de ses contraintes vis-à-vis des mitoyennetés, de l’influence et de l’état des propriétés avoisinantes, et notamment de tous éléments généraux et locaux en relation avec l’exécution des travaux ;"
  artO5Par10 = "*   Le Sous-Traitant s’engage à apprécier exactement toutes les conditions générales et particulières d’exécution de ses prestations, ainsi que l’incidence des travaux des différents corps d’état sur ses propres travaux. En conséquence, il ne bénéficiera d’aucune indemnité en cas de difficulté d’exécution de ses prestations ultérieure, de quelque ordre que ce soit ; A défaut d’observations portées à la connaissance de l’Entrepreneur Principal sous 48 heures, il sera réputé avoir accepté les conditions d’exécution de ses prestations purement et simplement ;"
  artO5Par11 = "*   Le Sous-Traitant s’engage à fournir l’intégralité des documents à jour demandés par l’Entrepreneur Principal tant aux termes du présent Contrat, de ses annexes qu’à ceux du Bon de Commande, dans les délais impartis, sous peine de résiliation de sa mission de sous-traitance dans les conditions fixées à l’article VIII.3. Ci-après ; Le Sout-Traitant devra fournir lesdits documents en original lors de la signature du Bon de Commande ;"
  artO5Par12 = "Le Sous-Traitant devra remettre régulièrement, tout au long de l’exécution de sa mission de sous-traitance lesdits documents mis à jour aux échéances contractuelles prévues ainsi qu’à la première demande de l’Entrepreneur Principal."
  art05SubTitle2 = "V.2. Indépendance juridique"
  artO5Par13 = "Le Sous-Traitant agit en tant qu’entrepreneur indépendant et assume de ce fait toutes les charges occasionnées par les prestations ou travaux sous-traités, notamment : recrutement de la main d’œuvre, versement des salaires et des charges y afférentes, paiements des taxes, des impôts et des primes d’assurances, la présente énumération n’étant pas limitative."
  art05SubTitle3 = "V.3. Assurances"
  artO5Par13 = "Le Sous-Traitant a l’obligation de souscrire toutes les assurances obligatoires (responsabilité civile professionnelle et assurance de garantie décennale) préalablement au commencement de sa mission et devra être à même d’en justifier à première demande de l’Entrepreneur Principal."
  art05SubTitle3 = "V.4. Indépendance Economique"
# Le Sous-Traitant déclare et garantit que le chiffre d’affaires pouvant être 
# généré par le présent Contrat, cumulé à celui généré par tous les contrats 
# existant avec l’Entrepreneur Principal au jour de la signature des présentes, 
# n’est pas susceptible de représenter une part de son chiffre d’affaires global 
# supérieure à 25 %.
# Si à quelque moment que ce soit, le pourcentage que représente le volume 
# d’affaire réalisé avec l’Entrepreneur Principal, tous contrats et commandes 
# confondus, devait excéder le pourcentage susvisé, le Sous-Traitant s’engage à 
# en informer immédiatement et par écrit l’Entrepreneur Principal.
# Le non-respect de cette hypothèse, le Sous-Traitant s’engage à mettre en 
# œuvre toutes les mesures nécessaires pour diversifier sa clientèle et ainsi ne plus
# dépasser le pourcentage susvisé.
# En tout état de cause, le Sous-Traitant est informé du fait que, quelle que soit 
# la manière dont le dépassement du pourcentage susvisé serait porté à la 
# connaissance de l’Entrepreneur Principal, ce dernier pourra mettre en œuvre 
# un plan de réduction, au fil du temps, de son volume de commandes global 
# auprès du Sous-Traitant.
# V.5. Incessibilité et non délégation des missions de sous-traitance
# Il est précisé que, de convention expresse entre les Parties :
# Sauf accord contraire exprès écrit préalable avec l’Entrepreneur 
# Principal, le Sous-Traitant ne pourra céder, faire apport, co-traiter ou 
# sous-traiter tout ou partie de sa mission de sous-traitance telle que définie 
# dans le Bon de Commande.
# Si le Sous-Traitant viole cette interdiction, l’Entrepreneur Principal 
# sera en droit d’exiger l’exécution complète de ladite mission par le Sous-
# Traitant ou, à défaut, pourra résilier le Contrat en application de l’article 
# VIII.3 du présent Contrat.
# La responsabilité du Contrat de sous-traitance ne peut en aucun cas être 
# déléguée.
# La sous-traitance au-delà du deuxième rang est expressément interdite.
# En cas d’intervention d’un sous-traitant de second rang expressément 
# autorisée par l’Entreprise Principal, le Sous-traitant s’engage à 
# respecter les dispositions de la loi n° 75-1334 du 31 décembre 1975 dans 
# ses rapports avec son sous-traitant, à transmettre à l’Entrepreneur 
# Principal l’intégralité des documents à jour demandés contractuellement 
# par lui au sous-traitant de second rang et à faire respecter par le sous-
# traitant de second rang l’intégralité des obligations générales fixées au 
# présent article.
# A défaut, l’Entrepreneur Principal sera en droit de résilier le Contrat 
# par application de l’article VIII.3 des présentes.
# Dans l’hypothèse où il serait autorisé à sous-traiter une partie de sa 
# mission, le Sous-Traitant demeurera seul responsable envers 
# l’Entrepreneur Principal de l’exécution de tous les travaux qui lui auront
# été confiés. Il ne pourra arguer d’une quelconque faute du sous-traitant de
# second rang pour dégager sa responsabilité.
# V.6   -   Obligations sociales et fiscales du Sous-Traitant   
# Le Sous-Traitant s’engage expressément à respecter l’ensemble des 
# dispositions de la loi n°91-1383 du 31 décembre 1991 concernant la lutte contre 
# le travail dissimulé, de ses décrets d’application et de tous textes législatifs ou 
# réglementaires successifs y afférents.
# Le Sous-Traitant justifie en conséquence de la régularité des conditions de son 
# activité par la fourniture des documents suivants ci-annexés :
# Carte d’identification justifiant l’inscription au répertoire des métiers, 
# Ou Extrait de l’inscription au registre du commerce et des Sociétés 
# (extrait K-Bis) de moins de trois mois,
# Attestation de fourniture de déclaration sociale datant de moins d’un 
# an, émanant de l’URSSAF,
# Attestation sur l’honneur établie selon le modèle joint-en annexe 1 
# certifiant que le travail sera réalisé avec des salariés employés 


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
    self.writeArticle02(pdf)
    self.writeArticle03(pdf)
    self.writeArticle04(pdf)
    self.writeArticle05(pdf)

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

  def writeArticle02(self, pdf):
    dictData = {"title":self.art02Title, "paragraphs":[self.artO2Par1]}
    self.writeArticleGeneric(pdf, dictData)

  def writeArticle03(self, pdf):
    pdf.set_font('Arial', 'BU', 12)
    pdf.multi_cell(190, 10, self.art03Title)
    pdf.ln(5)
    dictData = {"title":self.artO3ST, "paragraphs":[self.artO3Par1, self.artO3Par2, self.artO3Par3, self.artO3Par4, self.artO3Par5, self.artO3Par6, self.artO3Par7, self.artO3Par8]}
    self.writeArticleGeneric(pdf, dictData)

  def writeArticle04(self, pdf):
    dictData = {"title":self.art04Title, "paragraphs":[self.artO4Par1, self.artO4Par2, self.artO4Par3]}
    self.writeArticleGeneric(pdf, dictData)

  def writeArticle05(self, pdf):
    pdf.set_font('Arial', 'BU', 12)
    pdf.multi_cell(190, 10, self.art05Title)
    pdf.ln(5)
    dictData = {"title":self.art05SubTitle1, "paragraphs":[self.artO5Par01, self.artO5Par02, self.artO5Par03, self.artO5Par04, self.artO5Par05, self.artO5Par06, self.artO5Par07, self.artO5Par08, self.artO5Par09, self.artO5Par10, self.artO5Par11, self.artO5Par12]}
    self.writeArticleGeneric(pdf, dictData)

# Utilitaires
  def writeArticleGeneric(self, pdf, dictData):
    pdf.set_font('Arial', 'BU', 12)
    title = dictData["title"].replace("’", "'").replace("–", "-")
    pdf.cell(190, 10, title, 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    for paragraph in dictData["paragraphs"]:
      parClean = paragraph.replace("’", "'").replace("–", "-")
      pdf.multi_cell(190, 5, parClean)
      pdf.ln(2)
    pdf.ln(10)

  def part1ST1Text1(self, nature="pme"):
    return self.translateText(self.__part1ST1Text1, nature)

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


