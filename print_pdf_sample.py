import pypdf

def main():
    reader = pypdf.PdfReader("Awaken_Now_Master_Recipe_Collection.pdf")
    # Print pages 10, 11, 12, 13
    for p_idx in [10, 11, 12, 13]:
        if p_idx < len(reader.pages):
            print(f"\n--- Page {p_idx+1} ---")
            print(reader.pages[p_idx].extract_text())

if __name__ == '__main__':
    main()
