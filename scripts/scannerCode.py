from bs4 import BeautifulSoup as bs
content = []
# Read the XML file
with open("scanners.txt", "r", encoding='cp932', errors='ignore') as file:
    # Read each line in the file, readlines() returns a list of lines
    content = file.readlines()
    # Combine the lines in the list into a string
    content = "".join(content)
    bs_content = bs(content, "xml")
    #print(bs_content)

    scanCodes = bs_content.find_all("scanCode")

    for scanCode in scanCodes:
        print(scanCode.text)

# python scannerCode.py > scannerCode.txt