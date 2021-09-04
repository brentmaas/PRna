import sys
import Life as life
import AngryBirds as birds
import Speed as speed

#Python 2.7.12
#Numpy 1.10.4
#Matplotlib 1.5.1
#Pyopencl 2016.2
#Programma met Game of Life, Angry Birds en een snelheidstest
#Gemaakt door Brent Maas (sXXXXXXX)
#Ontwikkeld in de periode 01/11/2016 - 22/11/2016

def infoblok():
    """Het infoblok wordt op het scherm weergeven."""
    print """Naam: Brent Maas
Jaar van aankomst: 2016
Studierichting: Natuur- en Sterrenkunde
Studentnummer: sXXXXXXX
Opdracht: opdr3

Dit programma is ontwikkeld in de periode 01/11/2016 - 22/11/2016
-------------------------------------------------------------------------------
"""

cl = False  #Of OpenCL wel of niet gebruikt wordt voor Game of Life en 
            #snelheidstest

def gameoflife():
    """Start Game of Life"""
    wereld = life.LifeWereld(cl)
    wereld.start()

def angrybirds():
    """Start Angry Birds"""
    b = birds.AngryBirds()
    b.run()

def snelheidstest():
    """Start snelheidstest"""
    st = speed.SpeedTest(cl)
    st.run()

def toggleCL():
    """Schakel OpenCL-gebruik tussen aan en uit"""
    global cl #Anders vind het programma de variabele niet
    cl = not cl

def requestInput(maxIn):
    """Vraag de gebruiker om een integer getal, minimaal 1, maximaal maxIn
    Als het gegeven getal buiten deze limiet is, geef 0 terug"""
    i = raw_input()
    try:
        int(i) #Deze functie geeft een ValueError als i geen integer is
        if int(i) > maxIn or int(i) < 1:
            return 0 #Buiten de limiet
    except:
        print "Dat was geen geheel getal"
        return 0 #Geen integer
    return int(i) #Integer binnen de limiet

def menu():
    """Weergeeft het hoofdmenu voor het programma en vraag invoer uit opties"""
    #Menuopties
    print "1. Game of Life"
    print "2. Angry Birds"
    print "3. Snelheidstest"
    print "4. OpenCL voor Game of Life en Snelheidstest:", \
    int(cl) * "AAN" + (1-int(cl)) * "UIT"   #int(True) = 1, int(False) = 0
                                            #Geeft AAN als cl = True
                                            #Geeft UIT als cl = False
    print "5. Sluiten"
    
    i = requestInput(5) #Vraag integer op
    if i == 1: #Optie 1: start Game of Life
        gameoflife()
    elif i == 2: #Optie 2: start Angry Birds
        angrybirds()
    elif i == 3: #Optie 3: start snelheidstest
        snelheidstest()
    elif i == 4: #Optie 4: schakel OpenCL
        toggleCL()
    elif i == 5: #Optie 5: sluit af
        sys.exit(0)
    else: #Iets anders dan de menuopties
        print "Ongeldige invoer:", i

if __name__ == "__main__":
    infoblok() #Weergeef infoblok
    while True: #Zolang het programma draait
        menu() #Weergeef het menu en probeer een geldige invoer te krijgen