import codecs

csvPath = ".\..\data.csv"

print("Welcher Eintrag aus der csv Datei?")
z = int(input())
# Skip seq und Zell Names
z -= 1

print("Welcher Text?")
t = input()

csvFile = open(csvPath, 'r')
textFile = codecs.open('text' + t + '.txt', 'r', "utf-8")

csv = csvFile.readlines()[2:]

l = csv[z]

quoted = False
columns = []
colum = ""
# Read the First Collum
for c in l:
    # Check for Quotes
    if c == '"':
        quoted = not quoted
        
    #Add read Charakter to string
    colum = colum + c
    
    if not quoted and c == ',':
        # add to array and reset
        colum = colum[:-1]
        columns.append(colum)
        colum = ""

columns.append(colum)

# Remove Assci Translation and len
columns = columns[2:]

# Convert to byte array
dataBytes = bytearray()
for c in columns:
    dataBytes.append(int(c, base=2))

# Read Text and Convert to bytes
text = textFile.read()
controlBytes = text.encode('utf-8')

textFile.close()
csvFile.close()

# Reduce control Bytes to correct size
dataBytes = dataBytes[:-(len(dataBytes) - len(controlBytes))]

# Compare Bytearray's for BER
