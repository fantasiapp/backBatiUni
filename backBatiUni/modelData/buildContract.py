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
      self.set_xy(-5,-5)
      file = file[0]
      self.image(file.path, 10, 8, 33)
    self.set_font('Arial', 'BI', 15)
    self.set_xy(60,20)
    self.cell(120, 10, "ACCORD - CADRE DE SOUS-TRAITANCE", 1, 0, 'C')
    self.ln(20)

  def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')


class BuildContract:
  Part1Title = "Désignation des parties contractantes"
  Part1SubTitle1 = "ENTRE LES SOUSSIGNÉES :"

  def __init__(self, userProfile):
    pdf = MyPdf('P', 'mm', 'A4')
    pdf.userProfile = userProfile
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_xy(20,0)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(190, 10, self.Part1Title, 0, 1, 'L')
    self.set_xy(10,0)
    pdf.set_font('Arial', 'BU', 12)
    pdf.cell(190, 10, self.Part1SubTitle1, 0, 1, 'L')
    pdf.set_font('Arial', '', 12)
    for i in range(1, 41):
      pdf.cell(0, 6, 'Printing line number ' + str(i), 0, 1)
    pdf.output('./files/documents/tuto1.pdf', 'F')

def specialChar(string):
    latinStr = string.encode('utf-8').decode('iso-8859-1')
    print(latinStr)
    for key, value in {'â':"-"}.items():
      latinStr.replace(key, value)
    print(latinStr)
    return latinStr


