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
      print("header", file.path)
    self.set_font('Arial', 'BI', 15)
    # Move to the right
    self.set_x(-1)
    self.cell(120, 20)
    self.cell(120, 20, "ACCORD - CADRE DE SOUS-TRAITANCE", 1, 0, 'C')
    # Line break
    self.ln(20)

  def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')


class BuildContract:
  def __init__(self, userProfile):
    pdf = MyPdf('P', 'mm', 'A4')
    pdf.userProfile = userProfile

    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Times', '', 12)
    for i in range(1, 41):
      pdf.cell(0, 10, 'Printing line number ' + str(i), 0, 1)
    pdf.output('./files/documents/tuto1.pdf', 'F')

def specialChar(string):
    latinStr = string.encode('utf-8').decode('iso-8859-1')
    print(latinStr)
    for key, value in {'â':"-"}.items():
      latinStr.replace(key, value)
    print(latinStr)
    return latinStr


