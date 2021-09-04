import sys

#Python 2.7.12
#Programma om bestanden te coderen en te decoderen
#Gemaakt door Brent Maas (sXXXXXXX)

#Referentielijst voor de karakters waar een backslash voor moeten
refBackslash = ["\\", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
#Referentielijst voor de getallen
refNums = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
#Referentielijst voor de lowercase letters
refLowercaseAbc = [chr(x + ord("a")) for x in range(0, 26)]
#Opslag van aantal keer dat een letter voorkomt
storeAbc = [0] * 26

def infoblok():
    """Het infoblok wordt op het scherm weergeven."""
    print """Naam: Brent Maas
Jaar van aankomst: 2016
Studierichting: Natuur- en Sterrenkunde
Studentnummer: sXXXXXXX
Opdracht: opdr2

Dit programma is ontwikkeld in de periode 27/09/2016 - 07/10/2016
-----------------------------------------------------------------
"""

def reverseString(string):
    return str(string)[::-1]

def isNum(char):
    return char in refNums

def toInt(string):
    i = 0
    for char in str(string):
        if char not in refNums:
            return i
        i = 10 * i + ord(char) - ord("0")
    return i

def isLowercaseChar(char):
    return char in refLowercaseAbc

def iterateLychrel(num):
    """Voert een iteratie voor een Lychrel-getal uit op num en returnt het 
    resultaat"""
    numReverse = reverseString(num) #String wordt omgedraaid
    som = toInt(num) + toInt(numReverse)
    return som

def isLychrel(num):
    """Evalueert of het argument num een Lychrel-getal is en geeft een boolean 
    terug."""
    numReverse = reverseString(num) #String wordt omgedraaid
    return toInt(num) == toInt(numReverse)

def testLychrel(num):
    """Test of het gegeven getal num een Lychrel-getal is print het aantal 
    iteraties totdat het getal een Lychrel-getal is en geeft aan wanneer een 
    iteratie boven sys.maxint komt"""
    i = 0 #Iteratie
    n = num
    while isLychrel(n) == False: #Zolang we geen Lychrel-getal hebben
        i += 1
        n = iterateLychrel(n)
        if n > sys.maxint:  #Als het getal groter wordt dan sys.maxint,
                            #dit melden en stoppen
            print "Controle voor Lychrel-getal op getal", num, \
                "is buiten de limiet gekomen"
            return
    print "Lychrel-getal:", num, "in", i, "iteraties"

def writeEncode(o, char, n):
    """Schrijft het karakter char, eventueel met backslash, en het getal 
    n naar de uitvoerfile o. Returnt het aantal karakters dat geschreven is"""
    writtenChars = 0 #Aantal geschreven karakters
    if char == "\n":    #Als het karakter een newline is, 
                        #schrijf n keer een newline en stop direct
        o.write("\n" * n)
        writtenChars += n
        return writtenChars
    if char in refBackslash:    #Als voor het karakter een backslash moet
                                #komen, schrijf deze
        writtenChars += 1
        o.write("\\")
    o.write(char)
    writtenChars += 1
    if n > 1:   #Schrijf het aantal keer dat het karakter voorkomt achter het
                #karakter, maar alleen als dit meer dan een keer is
        o.write(str(n))
        writtenChars += len(str(n)) #De lengte van het getal optellen
                                    #i.p.v. het getal zelf
    
    if isLowercaseChar(char): #Als het karakter lowercase is, 
                                #vul de data voor het histogram bij
        index = refLowercaseAbc.index(char, 0)
        storeAbc[index] = storeAbc[index] + 1
    return writtenChars

def encode():
    """De hoofdroutine voor het coderen"""
    #Invoerfile aanvragen
    while True:
        print "Voer het pad van het te comprimeren bestand in:",
        pathIn = raw_input()
        try:
            i = open(pathIn, "r")
            break
        except IOError:
            print "Het bestand", pathIn, \
                "bestaat niet of kan niet worden geopend."
    
    #Uitvoerfile aanvragen
    print "Voer het pad van het doelbestand in", \
        "(bestaande bestanden worden overschreven!):",
    pathOut = raw_input()
    try:
        o = open(pathOut, "w")
    except IOError:
        print "Het bestand", pathOut, "kon niet worden aangemaakt", \
        "of overschreven."
        sys.exit(1)
    
    char = i.read(1)
    
    n = 0 #Aantal keer dat een karakter voorkomt
    totalChars = 0 #Aantal karakters in de invoerfile
    totalCharsComp = 0 #Totale karakters na compressie
    lychreltest = 0 #Het getal dat te controleren valt voor een Lychrel-getal
    currChar = ""   #Huidige karakter (wordt gebruikt om vorige
                    #karakter op te slaan)
    lines = 1 #Aantal regels, alvast eerste regel optellen
    
    while char:
        if char == "\n": #Bij een newline, een bij het aantal regels optellen
            lines += 1
        if char == currChar:    #Eentje optellen bij het aantal keer dat het
                                #karakter voorkomt
            n += 1
        elif n > 0: #Als het karakter niet gelijk is aan het vorige karakter,
                    #schrijven
            totalCharsComp += writeEncode(o, currChar, n)
            if currChar in refNums: #Als het vorige karakter een getal was,
                                    #voeg deze achter het zover opgebouwde getal
                lychreltest = 10 ** (n) * lychreltest + toInt(currChar * n)
                
                if char not in refNums: #Maar als het huidige karakter geen
                                        #getal is, controleer of het opgebouwde
                                        #getal een Lychrel-getal is
                    testLychrel(lychreltest)
                    lychreltest = 0
            currChar = char
            n = 1
        else:
            currChar = char
            n = 1
        char = i.read(1)
        totalChars += 1
    totalCharsComp += writeEncode(o, currChar, n)
    if currChar in refNums: #Voor de laatste keer controleren of het vorige
                            #karakter een getal was en het opgebouwde getal
                            #bijwerken en controleren
        lychreltest = 10 ** (n) * lychreltest + toInt(currChar * n)
        testLychrel(lychreltest)
    
    
    compressie = toInt(100 * float(totalCharsComp) / float(totalChars) \
                      + 0.5) #int(n + 0.5) staat gelijk aan round(n)
    print "Compressieverhouding:", compressie, "%"
    print "Regels:", lines
    
    maxLength = 40
    largest = max(storeAbc) #Zoek het meest voorkomende lowercase karakter op
    
    #Print het histogram
    for i in range(0, 26):
        if storeAbc[i] > 0:
            chars = min(toInt(float(storeAbc[i]) / largest * maxLength) + 1, \
                maxLength)
            spaces = maxLength - chars
            letter = refLowercaseAbc[i]
            print letter, "|", "=" * chars + " " * spaces, "|", storeAbc[i]

def writeDecode(o, char, n=1):
    """Schrijft het karakter char n keer naar de uitvoerfile o"""
    if n == 0:
        o.write(char)
    else:
        o.write(char * n)

def decode():
    """De hoofdroutine voor het decoderen"""
    #Invoerfile aanvragen
    while True:
        print "Voer het pad van het te comprimeren bestand in:",
        pathIn = raw_input()
        try:
            i = open(pathIn, "r")
            break
        except IOError:
            print "Het bestand", pathIn, \
                "bestaat niet of kan niet worden geopend."
    
    #Uitvoerfile aanvragen
    print "Voer het pad van het doelbestand in", \
        "(bestaande bestanden worden overschreven!):",
    pathOut = raw_input()
    try:
        o = open(pathOut, "w")
    except IOError:
        print "Het bestand", pathOut, \
            "kon niet worden aangemaakt of overschreven."
        sys.exit(1)
    
    count = False   #Of er gekeken moet worden voor getallen die het aantal keer
                    #het karakter aangeven (True), of er gekeken moet worden
                    #naar karakters (False)
    n = 0 #Het aantal keer dat een karakter geschreven moet worden
    currChar = "" #Het vorige karakter
    
    char = i.read(1)
    while char:
        if not count: #Kijk voor karakters
            if char == "\n":    #Bij een newline,
                                #schrijf deze een keer naar de uitvoerfile
                writeDecode(o, "\n")
            elif char == "\\" and currChar != "\\": #Als het huidige karakter
                                                    #een backslash is, maar de
                                                    #vorige niet, zet het
                                                    #huidige karakter voorlopig
                                                    #als vorige karakter
                currChar = char
            else: #Sla het huidige karakter op en ga tellen
                currChar = char
                count = True
        else: #Tellen
            if char in refNums: #Als het een getal is, het aantal keer dat
                                #geschreven moet worden bijwerken en doorgaan
                n = 10 * n + toInt(char)
            else: #Als het geen getal is, schrijven en stoppen met tellen
                writeDecode(o, currChar, n)
                n = 0
                count = False
                if currChar == "\\":    #Als het vorige karakter een backslash
                                        #was, overschrijf deze, zodat deze niet
                                        #opnieuw meegerekend wordt
                    currChar = ""
                continue    #Herstart de loop voordat een nieuw karakter
                            #gelezen wordt, zodat ook het nieuwe karakter
                            #verwerkt wordt
        char = i.read(1)
    writeDecode(o, currChar, n)

def wantEncode():
    """Vraagt aan de gebruiker of deze een bestand wil coderen of decoderen 
        en returnt True als de gebruiker wilt coderen, False als de gebruiker 
        wilt decoderen"""
    while True: #Oneindige loop die alleen verbroken wordt als de routine
                #wordt beeindigd
        print "Wilt u coderen of decoderen?\n1. Coderen\n2. Decoderen"
        i = raw_input()
        try:
            if toInt(i) == 1: #1 komt overeen met coderen
                return True
            elif toInt(i) == 2: #2 komt overeen met decoderen
                return False
            raise ValueError    #Doen alsof de invoer niet geldig was om
                                #dezelfde tekst op het scherm te krijgen
        except ValueError: #Wanneer we geen geldige invoer kregen
            print "Ongeldige invoer"

def main():
    """De hoofdroutine"""
    infoblok()
    if wantEncode():
        encode()
    else:
        decode()

#Roep de hoofdroutine aan
if __name__ == "__main__":
    main()