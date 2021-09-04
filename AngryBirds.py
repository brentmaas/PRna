import numpy as np
import matplotlib.pyplot as plt
import sys

#Python 2.7.12
#Numpy 1.10.4
#Matplotlib 1.5.1
#Pyopencl 2016.2
#Module voor Angry Birds
#Gemaakt door Brent Maas (sXXXXXXX)
#Ontwikkeld in de periode 01/11/2016 - 22/11/2016

class AngryBirds:
    g = 0 #Zwaartekrachtsversnelling
    name = "" #Naam van de planeet
    startHeight = 5 #De beginhoogte
    useTimeFit = False #Of het programma wel of niet een tijd probeer te fitten
    dataPoints = 50 #Aantal datapunten
    endTime = 20.0 #Eindtijd
    animated = False #Of de plot geanimeerd wordt of niet
    
    def getG(self, m, r):
        """Bereken de gravitatieversnelling uit massa en straal"""
        return 6.67384e-11 * m / (r ** 2)
    
    def __init__(self):
        """Initialisatiefunctie"""
        self.pNames = [] #Array met planeetnamen
        self.gs = [] #Array met gravitatieversnellingen van planeten
        self.bNames = [] #Array met vogelnamen
        self.bData = [] #Array met vogeldata
        f = open("planeten.txt", "r") #Open planeten.txt om te lezen
        temp = [] #Tijdelijke array voor het lezen
        line = f.readline() #Lees de eerste regel
        while line: #Zolang de regel niet leeg is
            if line[0] == "#": #Als de regel begint met '#', negeer de regel
                line = f.readline() #Lees een nieuwe regel
                continue #Herstart de loop
            else: #Zo niet, verwerk de regel
                #Array met elementen van de regel
                elements = line.rstrip("\n").split("\t")
                #Voeg het datapunt toe aan de tijdelijke array
                #(naam, massa, straal)
                temp.append([elements[0], elements[1], elements[2]])
            line = f.readline() #Lees een nieuwe regel
        
        for i in range(0, len(temp)): #Voor elke element in de tijdelijke array
            self.pNames.append(temp[i][0]) #Voeg de naam toe
            m = float(temp[i][1]) #De massa
            r = float(temp[i][2]) * 1000 #De straal (in meter ipv kilometer)
            grav = self.getG(m, r) #Bereken de gravitatieversnelling
            self.gs.append(grav) #Voeg de gravitatieversnelling toe
        f.close() #Sluit het bestand
        
        f = open("vogels.txt", "r") #Open vogels.txt om te lezen
        temp = [] #Leeg de tijdelijke array
        temp2 = [] #Nog een tijdelijke array
        line = f.readline() #Lees de eerste regel
        while line: #Zolang de regel niet leeg is
            if line[0] == "#": #Als de regel begint met '#', negeer de regel
                line = f.readline() #Lees een nieuwe regel
                continue #Herstart de loop
            else: #Zo niet, verwerk de regel
                #Array met elementen van de regel
                elements = line.rstrip("\n").split("\t")
                #Voeg de naam toe aan de tijdelijke array
                temp.append(elements[0])
                #Voeg de data toe aan de tweede tijdelijke array
                #(beginsnelheid, hoek)
                temp2.append([float(elements[1]) / 3.6,\
                np.deg2rad(float(elements[2]))])
            line = f.readline() #Lees een nieuwe regel
        f.close() #Sluit het bestand
        self.bNames = np.array(temp) #Schrijf de namen
        self.bData = np.array(temp2) #Schrijf de beginsnelheid en hoek
    
    def requestInput(self, maxIn):
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
    
    def x(self, t):
        """Bereken de x-waarde op tijd t"""
        return self.bData[:,0] * np.cos(self.bData[:,1]) * t
    
    def y(self, t):
        """Bereken de y-waarde op tijd t"""
        return self.bData[:,0] * np.sin(self.bData[:,1]) * t\
        - 0.5 * self.g * t ** 2 + self.startHeight
    
    def disp(self):
        """Weergeef de plot"""
        vY = self.bData[:,0] * np.sin(self.bData[:,1])
        if self.useTimeFit: #Als dde tijd gefit moet worden
            #Bereken de tijd dat alle vogels onder de y-as zijn
            tZero = (vY + np.sqrt(vY ** 2 + 2 * self.g *\
            self.startHeight))/(self.g)
            #Vind de waarde waar de laatste vogel onder de y-as is
            maxT = int(np.amax(tZero) + 1)
            #Zet de tijd-array op
            t = np.linspace(0, maxT, self.dataPoints)\
            .reshape((self.dataPoints, 1))
        else: #Zo niet, zet de tijd-array op met de gegeven eindtijd
            t = np.linspace(0, self.endTime, self.dataPoints)\
            .reshape((self.dataPoints, 1))
        x = self.x(t) #Bereken de x-array
        y = self.y(t) #Bereken de y-array
        #Zet de x-limiet op 110% de maximale x-waarde
        plt.xlim(0, np.amax(x[y>0]) * 1.1)
        #Zet de y-limiet op 110% de maximale y-waarde
        plt.ylim(0, np.amax(y) * 1.1)
        plt.xlabel("Afstand (m)") #Zet het label voor de x-as
        plt.ylabel("Hoogte (m)") #Zet het label voor de y-as
        plt.title(self.name) #Zet de naam van de planeet als titel
        #Plot de beginhoogte
        plt.plot(np.array([0, np.amax(x[y>0]) * 1.1]),\
        np.array([self.startHeight] * 2), linestyle="dotted")
        if self.animated: #Als de plot geanimeerd moet zijn
            #Schakel wat gezeur van matplotlib uit
            import warnings as w
            w.simplefilter("ignore")
            #Zorg ervoor dat de plot niet verwijdert wordt met elke nieuwe plot
            plt.hold(True)
            #Wacht een halve seconde voor het scherm om goed zichtbaar te zijn
            plt.pause(0.5)
            #Plot het eerste segment en vang de handles af
            handles = plt.plot(x[0:2], y[0:2])
            plt.legend(handles, self.bNames) #Maak een legenda
            stop = False #Of er gestopt moet worden met plotten
            for i in range(1, len(t)): #Voor elk segment, behalve de eerste
                plt.pause(0.05) #Wacht 50ms tussen elk segment
                for j in range(0, len(self.bNames)):
                    #Als er geen scherm meer in beeld is of
                    #als er moet worden gestopt
                    #(len(plt.get_fignums()) geeft het aantal actieve schermen)
                    if len(plt.get_fignums()) == 0 or stop:
                        stop = True #Stoppen
                        break #Stop de forloop
                    #Plot een segment als er niet gestopt wordt
                    plt.plot(x[i:i+2, j], y[i:i+2, j], color=handles[j]\
                    .get_color())
                if stop: #Als er gestopt moet worden
                    break #Stop ook deze forloop
                #Dit plot niks, maar update het scherm
                plt.plot(x[0:1], y[0:1])
        else: #Wanneer er niet geanimeerd moet worden
            handles = plt.plot(x, y) #Plot alles en vang handles af
            plt.legend(handles, self.bNames) #Maak een legenda
        plt.show() #Weergeef de plot
    
    def settings(self):
        """Een menu voor instellingen"""
        while True: #Een while-loop voor een menu
            #Menuopties
            print "1. Fit de tijd i.p.v. 0 s -", self.endTime, "s:",\
            int(self.useTimeFit) * "AAN" + (1 - int(self.useTimeFit)) * "UIT"
            print "2. Datapunten (beginwaarde: 50):", self.dataPoints
            print "3. Eindtijd (beginwaarde: 20,0):", self.endTime
            print "4. Animatie:", int(self.animated) * "AAN" +\
            (1 - int(self.animated)) * "UIT"
            print "5. Terug"
            
            i = self.requestInput(5)
            
            if i == 1: #Wissel gebruik van tijdsfitting
                print "Het programma probeert hiermee de tijd de berekenen",
                print "waarbij alle vogels op de grond zijn en gebruikt deze",
                print "als eindtijd"
                self.useTimeFit = not self.useTimeFit #Wissel tijdsfitting
            elif i == 2: #Datapunten
                print "Het aantal datapunten dat gegenereerd moet worden"
                j = raw_input() #Vraag getal op
                try:
                    int(j) #Geeft een ValueError als het geen integer is
                except ValueError: #ALs j geen integer is
                    print "Dat was geen geheel getal"
                    continue #Herstart de loop
                if int(j) < 2: #Minder dan 2 datapunten levert niks op
                    print "Er kunnen geen een of minder datapunten worden gegenereerd"
                    continue #Herstart loop
                self.dataPoints = int(j) #Als alles goed is, sla de invoer op
            elif i == 3: #Eindtijd
                print "De eindtijd die het programma gebruikt"
                j = raw_input() #Vraag getal op
                try:
                    float(j) #Geeft ValueError als j geen reeel getal is
                except ValueError: #j geen reeel getal
                    print "Dat was geen reeel getal"
                    continue #Herstart loop
                if float(j) <= 0: #De eindtijd kan niet 0s of minder zijn
                    print "De eindtijd kan niet minder of gelijk aan nul zijn"
                    continue #Herstart loop
                self.endTime = float(j) #Als alles goed is, sla de invoer op
            elif i == 4: #Animatie
                self.animated = not self.animated #Wissel animatie-gebruik
            elif i == 5: #Terug
                #Sluit menu en stop functie, gaat terug naar Angry Birds menu
                return
            else: #Gegeven getal is geen menuoptie
                print "Ongeldige invoer"
    
    def run(self):
        """Voer Angry Birds uit"""
        while True: #While-loop voor een menu
            print "Op welke planeet wilt u spelen?"
            for i in range(0, len(self.pNames)): #Voor elke planeet
                #Schrijf de index van de planeet + 1 (ZONDER extra spatie)
                sys.stdout.write(str(i + 1))
                #Schrijf de rest van de optie (naam + gravitatieversnelling)
                print ".", self.pNames[i], "-", self.gs[i]
            #Menuoptiegetal na de laatste planeet (zonder spatie)
            sys.stdout.write(str(len(self.pNames) + 1))
            print ". Opties"
            #Menuoptiegetal na vorige menuoptie (zonder spatie)
            sys.stdout.write(str(len(self.pNames) + 2))
            print ". Terug"
            
            j = raw_input() #Vraag een getal
            try:
                int(j) #Geeft ValueError als j geen integer is
            except ValueError: #j geen integer
                print "Dat was geen geheel getal"
                continue #Herstart loop
            if int(j) == len(self.pNames) + 1: #Opties
                self.settings() #Start optiesmenu
                continue #Herstart loop (als optiesmenu gesloten is)
            if int(j) == len(self.pNames) + 2: #Terug
                return #Sluit menu en ga terug naar Angry Birds menu
            #Als j buiten de indices van de planeten ligt
            elif int(j) < 1 or int(j) > len(self.pNames):
                print "Ongeldige invoer"
                continue #Herstart loop
            #Hierna: j - 1 is een index van een planeet
            self.g = self.gs[int(j) - 1] #Pak een gravitatieversnelling
            self.name = self.pNames[int(j) - 1] #Pak de planeetnaam
            self.disp() #Weergeef de plot
            return #Stop Angry Birds en ga terug naar het hoofdmenu