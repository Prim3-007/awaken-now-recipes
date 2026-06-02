import pypdf
import re

def main():
    reader = pypdf.PdfReader("Awaken_Now_Master_Recipe_Collection.pdf")
    print(f"Total pages in PDF: {len(reader.pages)}")
    
    # Print the text of the first 3 pages to see the format
    for idx in range(min(5, len(reader.pages))):
        print(f"\n--- Page {idx+1} ---")
        text = reader.pages[idx].extract_text()
        print(text[:800]) # print first 800 chars of each page

if __name__ == '__main__':
    main()
