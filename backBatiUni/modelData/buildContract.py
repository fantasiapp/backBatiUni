from fpdf import FPDF
from ..models import *
class BuildContract(FPDF):

  def __init__(self, userProfile):
    self.userProfile = userProfile
    print(self.userProfile.Company.name)
    file = File.objects.filter(nature="userImage", Company=self.userProfile.Company)
    print("buildContract", file)

    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('Times', '', 12)
    pdf.cell(40, 10, 'Hello World!')
    pdf.output('./files/documents/tuto1.pdf', 'F')

  def header(self):
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
  #   self.image()