from datetime import date
import sys
import random
#Python 2.7.12

print """Naam: Brent Maas
Jaar van aankomst: 2016
Studierichting: Natuur- en Sterrenkunde
Studentnummer: sXXXXXXX
Opdracht: opdr1

Dit programma is ontwikkeld in de periode 06/09/2016 - 15/09/2016
-----------------------------------------------------------------

Er volgen een aantal vragen, vul deze met geldige waarden in
"""

vandaag = date.today()

#Jaar
print "Geboortejaar: ",
jaar = 0
try: #Probeer een integer te parsen uit de invoer
    jaar = int(raw_input())
except: #Als dat niet lukt, melden en afsluiten
    print "Ongeldig jaar"
    sys.exit(1)
if jaar > vandaag.year:
    print "Geboortedag kan niet in de toekomst liggen"
    sys.exit(1)
elif vandaag.year - jaar < 10:
    print "Gebruiker is te jong"
    sys.exit(1)
elif vandaag.year - jaar > 100:
    print "Gebruiker is te oud"
    sys.exit(1)

#Maand
print "Geboortemaand: ",
maand = 0
try:
    maand = int(raw_input())
except:
    print "Ongeldige maand"
    sys.exit(1)
if maand < 1 or maand > 12:
    print "Ongeldige maand"
    sys.exit(1)
elif jaar == vandaag.year and maand > vandaag.month:
    print "Geboortedag kan niet in de toekomst liggen"
    sys.exit(1)
elif vandaag.year - jaar == 100 and vandaag.month > maand:
    print "Gebruiker is te oud"
    sys.exit(1)
elif vandaag.year - jaar == 10 and vandaag.month < maand:
    print "Gebruiker is te jong"
    sys.exit(1)

#Dag
print "Geboortedag: ",
dag = 0
try:
    dag = int(raw_input())
except:
    print "Ongeldige dag"
    sys.exit(1)
#   |normale maanden   |     |februari in een schrikkeljaar            |     |andere februaris                        |      
if (dag < 1 or dag > 31) or ((jaar % 4 == 0 and maand == 2 and dag > 29) or (jaar % 4 != 0 and maand == 2 and dag > 28)) or \
    ((maand == 4 or maand == 6 or maand == 9 or maand == 11) and dag > 30):
#   |april, juni, september en november (30 dagen)                       |
    print "Ongeldige dag"
    sys.exit(1)

if vandaag.month == maand and vandaag.day == dag:
    print "Gefeliciteerd met uw verjaardag!"
elif vandaag.day == dag:
    print "Gefeliciteerd met uw vermaanddag!"

if vandaag.year - jaar == 100 and vandaag.month == maand and vandaag.day >= dag:
    print "Gebruiker is te oud"
    sys.exit(1)
elif vandaag.year == jaar and vandaag.month == maand and dag > vandaag.day:
    print "Geboortedag kan niet in de toekomst liggen"
    sys.exit(1)
elif vandaag.year - jaar == 10 and vandaag.month == maand and vandaag.day < dag:
    print "Gebruiker is te jong"
    sys.exit(1)

leeftijdJaren = vandaag.year - jaar
if maand > vandaag.month or (maand == vandaag.month and dag > vandaag.day):
    leeftijdJaren = leeftijdJaren - 1 #Nog niet jarig geweest

leeftijdMaanden = vandaag.month - maand
if dag > vandaag.day:
    leeftijdMaanden = leeftijdMaanden - 1 #Nog niet maandig geweest

print ""
print "Leeftijd:"
print leeftijdJaren, "jaar en", leeftijdMaanden, "maanden"
print leeftijdJaren * 12 + leeftijdMaanden, "maanden"

aanhef = "jij"
aanhefCap = "Jij"
aanhefBezit = "jouw"
aanhefBezitCap = "Jouw"
if leeftijdJaren >= 30:
    aanhef = "u"
    aanhefCap = "U"
    aanhefBezit = "uw"
    aanhefBezitCap = "Uw"


print "Wat was", aanhefBezit, "geboortedag? (z, m, d, w, d, v, z)"
weekdag = raw_input()
if weekdag == "z" or weekdag == "d":
    print "Voer a.u.b. een extra letter in: ",
    sys.stdout.writeEncode(weekdag)
    weekdag = weekdag + raw_input()
weekdagI = -1
if weekdag == "zo":
    weekdagI = 0 #Zondag = 0
elif weekdag == "m":
    weekdagI = 1 #Maandag = 1
elif weekdag == "di":
    weekdagI = 2 #Dinsdag = 2
elif weekdag == "w":
    weekdagI = 3 #Woensdag = 3
elif weekdag == "do":
    weekdagI = 4 #Donderdag = 4
elif weekdag == "v":
    weekdagI = 5 #Vrijdag = 5
elif weekdag == "za":
    weekdagI = 6 #Zaterdag = 6
else:
    print "Ongeldige dag,", aanhefBezit, "aanvraag is geweigerd"
    sys.exit(1)

weekdagJ = 2 #Dinsdag 1 januari 1901

for i in range(0, jaar - 1901):
    if (jaar + i) % 4 == 0:
        weekdagJ = weekdagJ + 2 #Schikkeljaar verspringt 2 weekdagen per jaar (366 % 7 = 2)
    else:
        weekdagJ = weekdagJ + 1 #Normaal jaar verspringt 1 weekdag per jaar (365 % 7 = 1)

for i in range(0, maand):
    if i == 1 or i == 3 or i == 5 or i == 7 or i == 8 or i == 10 or i == 12: #31-dagige maanden
        weekdagJ = weekdagJ + 3 #31-dagige maanden verspringen de weekdag met 3 dagen (31 % 7 = 3)
    elif i == 4 or i == 6 or i == 9 or i == 11: #30-dagige maanden
        weekdagJ = weekdagJ + 2 #30-dagige maande verspringen de weekdag met 2 dagen (30 % 7 = 2)
#februari verspringt de weekdag niet en met schrikkeljaren is al rekening gehouden

weekdagJ = weekdagJ + dag - 1 #Elke dag verspringt de weekdag met 1 dag, totaal eentje minder omdat er gerekend werd vanaf 1/1/1901 en niet 0/1/1901

if (weekdagJ % 7) != weekdagI: #Modulo van weekdagJ om weer op [0, 6] te komen
    print aanhefBezitCap, "antwoord is fout,", aanhefBezit, "aanvraag is geweigerd"
    sys.exit(1)
else:
    print aanhefBezitCap, "antwoord is goed"

eps = float(0.1)
print "Om toegelaten te worden tot een beta-studie moet", aanhef, "het volgend product goed gokken met een marge van", 100 * eps, "%"
term1 = random.randint(0, 19)
term2 = random.randint(0, 19)
antwoord = float(term1 * term2)
print term1, "*", term2, "= ?",
antwoordG = 0
try:
    antwoordG = float(raw_input())
except:
    print "Ongeldige invoer"
    sys.exit(1)
if antwoord == 0 and antwoordG == 0:
    print "Gefeliciteerd,", aanhefBezit, "antwoord was goed en", aanhef, "bent toegelaten voor een beta-studie"
    sys.exit(1)
elif antwoord == 0 and antwoordG != 0:
    print aanhefBezitCap, "antwoord was fout,", aanhef, "kunt nu deze vraag over kunst of literatuur nog proberen voor een alpha-studie"
elif abs(1 - antwoordG / antwoord) <= eps:
    print "Gefeliciteerd,", aanhefBezit, "antwoord was goed en", aanhef, "bent toegelaten voor een beta-studie"
    sys.exit(1)
else:
    print aanhefBezitCap, "antwoord was fout,", aanhef, "kunt nu deze vraag over kunst of literatuur nog proberen voor een alpha-studie"

vraagJ = "VraagJ" #Placeholdervraag voor jonger dan 30
ansesJ = ["GoedJ", "Fout1J", "Fout2J", "Fout3J"] #Placeholderantwoorden voor jonger dan 30
vraagO = "VraagO" #Placeholdervraag voor 30 of ouder
ansesO = ["GoedO", "Fout1O", "Fout2O", "Fout3O"] #Placeholderantwoorden voor 30 of ouder
vraag = ""
anses = ["", "", "", ""]
if leeftijdJaren >= 30:
    anses = ansesO
    vraag = vraagO
else:
    anses = ansesJ
    vraag = vraagJ

volgorde = [-1, -1, -1, -1]
goed = -1
while volgorde.count(-1) > 0:
    num = random.randint(0, 3)
    if volgorde.count(num) == 0:
        if num == 0:
            goed = 4 - volgorde.count(-1)
        volgorde[4 - volgorde.count(-1)] = num

print ""
print vraag
print "A.", anses[volgorde[0]]
print "B.", anses[volgorde[1]]
print "C.", anses[volgorde[2]]
print "D.", anses[volgorde[3]]

#print goed #Debugcode voor antwoorden

posAnses = ["a", "b", "c", "d"]
posAnsesCap = ["A", "B", "C", "D"]

ans = raw_input()
if ans == posAnses[goed] or ans == posAnsesCap[goed]:
    print "Gefeliciteerd,", aanhefBezit, "antwoord was goed en", aanhef, "bent toegelaten voor een alpha-studie"
    sys.exit(1)
else:
    print aanhefBezitCap, "antwoord was fout,", aanhef, "bent niet toegelaten voor de alpha-studie"