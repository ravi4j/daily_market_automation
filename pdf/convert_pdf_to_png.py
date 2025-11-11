from pdf2image import convert_from_path

pdf_path = "/pdf/investments-webinar-getting-started-technical-analysis.pdf"   # replace with your PDF name
pages = convert_from_path(pdf_path, dpi=300)  # high quality

for i, page in enumerate(pages, start=1):
    filename = f"page_{i}.png"
    page.save(filename, "PNG")
    print(f"Saved {filename}")