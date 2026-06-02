import pypdf

def main():
    reader = pypdf.PdfReader("Allowed Indian Seasonal Produce Master List V2.pdf")
    print(f"Total pages: {len(reader.pages)}")
    for idx, page in enumerate(reader.pages):
        text = page.extract_text()
        # Look for headers, seasons or months
        if any(w in text.lower() for w in ["spring", "summer", "monsoon", "winter", "vasanta", "grishma", "varsha", "shishira"]):
            print(f"\n--- Page {idx+1} ---")
            lines = text.split('\n')
            # print first 15 lines
            for line in lines[:25]:
                print(line)

if __name__ == '__main__':
    main()
