
csvPath = "F:\\Schule\\WSeminar\\code\\MicroPython\\Analyse\\data.csv"
csvFile = open(csvPath, 'r')
csv = csvFile.readlines()[2:]
csvFile.close()

print("Welcher Eintrag aus der csv Datei?")
z = int(input())
# Skip seq und Zell Names
z -= 1

print("Welcher Text?")
t = input()


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
textFile = open("text" + t + ".txt", "r")
text = textFile.read()
textFile.close()
controlBytes = text.encode('utf-8')

correctBits = 0
correctBytes = 0

# Compare Bytearray's for BER
for i in range(len(controlBytes)):
    cb = controlBytes[i]
    db = dataBytes[i]

    # Count same Bit's
    for m in range(8):
        if ((cb & 1<<(7 - m)) != 0) == ((db & 1<<(7 - m)) != 0):
            correctBits += 1

    # Check if Bytes are the same
    if db == cb:
        correctBytes += 1

# Calculate BER
ber = correctBits/(len(controlBytes * 8))

print("BER ist " + str(ber))
print("Korrekt übertragene Zeichen: " + str(correctBytes) + " von insgesamt " + str(len(dataBytes)))