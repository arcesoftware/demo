import pandas as pd
# Define a function to convert the content of a PDF into an Excel file
from PyPDF2 import PdfReader
# Load in openpyxl and create a new workbook
import openpyxl

# Extract the file path for the uploaded PDF
pdf_path = "C:/Users/myuser123/Documents/Math/plan1.pdf"
excel_path = "C:/Users/myuser123/Documents/Math/plan1.xlsx"

def pdf_to_excel(pdf_path, excel_path):
    reader = PdfReader(pdf_path)
    data = []

    for page in reader.pages:
        lines = page.extract_text().split('\n')
        data.extend(lines)

    # Simple processing to structure the data (basic splitting and organization)
    rows = []
    for line in data:
        if line.strip():
            rows.append(line.split())  # Split line into columns based on whitespace

    # Create DataFrame and save as Excel
    df = pd.DataFrame(rows)
    df.to_excel(excel_path, index=False, header=False)


pdf_to_excel(pdf_path, excel_path)
excel_path
