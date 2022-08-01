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
    self.set_font('Arial', 'B', 15)
    # Move to the right
    self.cell(80)
    # Title
    self.cell(30, 10, 'Title', 1, 0, 'C')
    # Line break
    self.ln(20)

class BuildContract:

  def __init__(self, userProfile):
    pdf = MyPdf('P', 'mm', 'A4')
    pdf.userProfile = userProfile

    # pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Times', '', 12)
    for i in range(1, 41):
      pdf.cell(0, 10, 'Printing line number ' + str(i), 0, 1)
    pdf.output('./files/documents/tuto1.pdf', 'F')