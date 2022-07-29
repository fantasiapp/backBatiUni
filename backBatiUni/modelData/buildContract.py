from fpdf import FPDF

class BuildContract(FPDF):

  def __init__(self, userProfile):
    self.userProfile = userProfile
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('Times', '', 12)
    pdf.cell(40, 10, 'Hello World!')
    pdf.output('./files/documents/tuto1.pdf', 'F')

  # def header(self):
  #   self.image()