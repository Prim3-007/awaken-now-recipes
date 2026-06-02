import pypdf

def main():
    reader = pypdf.PdfReader("Allowed Indian Seasonal Produce Master List V2.pdf")
    print(reader.pages[0].extract_text())

if __name__ == '__main__':
    main()
