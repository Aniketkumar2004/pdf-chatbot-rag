

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_sample_pdf(filename="tests/sample.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Page 1
    c.drawString(100, 750, "Sample PDF Document")
    c.drawString(100, 730, "This is a test document for PDF chatbot.")
    c.drawString(100, 700, "Machine learning is a subset of artificial intelligence.")
    c.showPage()
    
    # Page 2
    c.drawString(100, 750, "Page 2: More Content")
    c.drawString(100, 730, "RAG combines retrieval and generation for better LLM responses.")
    c.showPage()
    
    c.save()
    print(f"Created {filename}")

if __name__ == "__main__":
    create_sample_pdf()