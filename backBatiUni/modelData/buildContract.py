from fpdf import FPDF

class BuildContract:

  def __init__():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Hello World!')
    pdf.output('./files/documents/tuto1.pdf', 'F')