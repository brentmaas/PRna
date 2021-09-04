import numpy as np
import time
import sys

#Python 2.7.12
#Numpy 1.10.4
#Matplotlib 1.5.1
#Pyopencl 2016.2
#Module voor Game of Life
#Gemaakt door Brent Maas (sXXXXXXX)
#Ontwikkeld in de periode 01/11/2016 - 22/11/2016

class LifeWereld:
    cl = False #Gebruik van OpenCL
    clInitialized = False #Is OpenCL geinitialiseerd
    clPrgBuild = False #Is het OpenCL-programma succesvol gecompileerd
    gen = 0 #Generatie
    levend = "#" #Karakter voor levende cel
    dood = " " #Karakter voor dode cel
    fps = 10 #Beelden per seconde
    clFailed = False #Is het starten van OpenCL mislukt
    averageDT = 0.0 #Gemiddelde berekeningstijd per beeld
    
    width = 80 #Breedte
    height = 20 #Hoogte
    
    #De kernel (programmabroncode) voor het OpenCL-programma
    clKernel = """//Comment in OpenCL-code
//*a_g: pointer (soort array) naar de werelddata
//*width: pointer van lengte 1 naar de breedte van de wereld
//*res_g: resultaatpointer
__kernel void gameoflife(__global const float *a_g, __global const int *width, 
__global float *res_g){
    int gid = get_global_id(0); //Vraag het ID van deze instantie op
    
    //Teller voor omgevende levende cellen, met meteen boven en onder opgeteld
    //Als een cel leeft is zijn waarde 1, anders 0
    //In geval van IndexErrors geven deze pointers de waarde 0
    float n = a_g[gid-width[0]] + a_g[gid+width[0]];
    if(gid % width[0] != 0) //Als de huidige cel niet aan de linkerrand zit
    {
        //Voeg de waarden van linksboven, links en linksonder toe
        n = n + a_g[gid-width[0]-1] + a_g[gid-1] + a_g[gid+width[0]-1];
    }
    //Als de huidige cel niet aan de rechterrand zit
    if(gid % width[0] != width[0]-1)
    {
        //Voeg de waarden van rechtsboven, rechts en rechtsonder toe
        n = n + a_g[gid-width[0]+1] + a_g[gid+1] + a_g[gid+width[0]+1];
    }
    res_g[gid] = n; //Schrijf de uitkomst naar de resultaatpointer
}"""
    
    def __init__(self, cl):
        """Initialisatiefunctie
cl: of het programma wel of niet OpenCL gebruikt"""
        self.cl = cl #Kopieer de waarde van cl
        #Genereer een lege wereld
        self.wereld = np.zeros(self.width * self.height)\
        .reshape((self.height, self.width)).astype(np.bool8)
        
        #Wanneer OpenCL gebruikt wordt, maar nog niet geinitialiseerd is
        if self.cl and not self.clInitialized:
            try:
                global ocl #Moet helaas om andere functies toegang te geven
                import pyopencl as ocl
            except ImportError: #Als het importeren fout gaat
                print "Pyopencl kon niet worden geimporteerd,",
                print "schakel het a.u.b. uit"
                self.clFailed = True #Starten van Pyopencl is niet gelukt
            if not self.clFailed: #Als alles goed ging
                try:
                    print "Mogelijk wordt er gevraagd om een platform/device."
                    print "Voer bij voorkeur een grafische kaart (GPU) in."
                    #Deze functie laat de gebruiker zelf een platform/device
                    #gevraagd om te gebruiken. Dit wordt gebruikt om een
                    #context te maken, een referentie naar platform en device
                    self.ctx = ocl.create_some_context(interactive=True)
                    #Naar een commandqueue worden de opdrachten gestuurd
                    self.queue = ocl.CommandQueue(self.ctx)
                    #Een kopie van de 'memory flags' die rechten voor
                    #buffers regelen
                    self.mf = ocl.mem_flags
                    self.clInitialized = True #Pyopencl is geinitialiseerd
                except: #Iets ging ergens fout
                    print "Pyopencl kon niet worden geinitialiseerd, schakel het a.u.b. uit"
                    self.clFailed = True #Pyopencl kon niet goed worden gestart
    
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
    
    def clean(self):
        """Ruim de wereld op en reset variabelen"""
        #Nieuwe, lege wereld
        self.wereld = np.zeros(self.width * self.height)\
        .reshape((self.height, self.width)).astype(np.bool8)
        self.gen = 0 #Terug naar generatie 0
        self.averageDT = 0 #Reset de tijdsberekening
    
    def random(self):
        """Genereer een nieuwe, willekeurige wereld"""
        #Nieuwe, willekeurige wereld, float met bereik [0;1]
        self.wereld = np.random.rand(self.width * self.height)\
        .reshape((self.height, self.width))
        self.wereld += 0.5 #Verschuif het bereik naar [0,5;1,5]
        #Converteer naar integer, < 1 wordt 0, >= 1 wordt 1
        self.wereld = self.wereld.astype(np.int32).astype(np.bool8)
    
    def iterate(self, n):
        """Voer n iteraties (= n generaties) uit"""
        for i in range(0, n): #For-loop voor elke iteratie
            tStart = time.time() #Begintijd
            if not self.cl: #De normale iteratieberekening
                #Maak een reservekopie van de wereld
                copy = self.wereld.astype(np.int32).copy()
                for x in range(0, self.height): #x-bereik
                    for y in range(0, self.width): #y-bereik
                        m = 0 #Teller voor omgevende levende cellen
                        for v in range(0, 3): #dx-bereik, xCel = x + v - 1
                            for w in range(0, 3): #dy-bereik yCel = y + w - 1
                                #Als de cel die bekeken wordt niet de huidige
                                #cel is, en de bekeken cel niet buiten
                                #de wereld valt
                                if (v != 1 or w != 1) and x + v - 1 >= 0 \
                                and x + v - 1 < self.height and y + w - 1 >= 0\
                                and y + w - 1 < self.width:
                                    #+1 levende buur
                                    m += copy[x + v - 1][y + w - 1]
                        #Als de cel leeft en het aantal levende buren
                        #kleiner dan 2 of groter dan 3 is (de cel sterft)
                        if copy[x][y] and (m < 2 or m > 3):
                            self.wereld[x][y] = False
                        #Als de cel niet leeft en het aantal levende buren
                        #gelijk is aan 3 (de cel wordt geboren)
                        elif not copy[x][y] and m == 3:
                            self.wereld[x][y] = True
                        #Met andere cellen gebeurt niets
            else: #Een iteratieberekning met OpenCL
                global ocl #Wederom een zonde om de import te laten werken
                #Kopie van de wereld
                copy = self.wereld.astype(np.int32).copy()
                #Maak een 1D-array van de kopie
                copy = copy.reshape(self.width * self.height)
                #Lengte 1 array met de breedte van de wereld
                width_a = np.array([self.width])
                #Buffer-instantie met de wereld
                a_g = ocl.Buffer(self.ctx, self.mf.READ_ONLY | \
                self.mf.COPY_HOST_PTR, hostbuf=copy)
                #Buffer-instantie met de breedte
                width_g = ocl.Buffer(self.ctx, self.mf.READ_ONLY | \
                self.mf.COPY_HOST_PTR, hostbuf=width_a)
                if not self.clPrgBuild: #Als het programma nog niet gemaakt is
                    #Maak een nieuw programma-instantie met de kernel-broncode
                    #en compileer deze
                    self.prg = ocl.Program(self.ctx, self.clKernel).build()
                #Buffer-instantie voor het resultaat
                res_g = ocl.Buffer(self.ctx, self.mf.WRITE_ONLY,\
                copy.size * copy.itemsize)
                #Voer het programma uit
                self.prg.gameoflife(self.queue, copy.shape, None, a_g,\
                width_g, res_g)
                #Maak een lege array om het resultaat naar te kopieren
                res = np.empty_like(copy)
                #Kopieer het resultaat van de buffer naar de array
                ocl.enqueue_copy(self.queue, res, res_g)
                #Maak weer een 2D array met de dimensies van de wereld
                res = res.reshape((self.height, self.width))
                #Zelfde voor de kopie
                copy = copy.reshape((self.height, self.width)).astype(np.bool8)
                for x in range(0, self.height): #x-bereik
                    for y in range(0, self.width): #y-bereik
                        m = res[x][y]   #Teller voor omgevende levende buren
                                        #uit de resultaatarray
                        #Als de cel leeft en het aantal levende buren
                        #kleiner dan 2 of groter dan 3 is (de cel sterft)
                        if copy[x][y] and (m < 2 or m > 3):
                            self.wereld[x][y] = False
                        #Als de cel niet leeft en het aantal levende buren
                        #gelijk is aan 3 (de cel wordt geboren)
                        elif not copy[x][y] and m == 3:
                            self.wereld[x][y] = True
            tEnd = time.time() #Eindtijd
            dt = tEnd - tStart #Het verschil in begin- en eindtijd
            if self.averageDT == 0: #Als er nog geen tijdsdata was
                self.averageDT = dt #De eerste tijdsmeting is zover de enige
            else: #Als er al data was
                #Update de gemiddelde tijd
                self.averageDT = (self.averageDT * self.gen + dt)\
                / (self.gen + 1)
            #Als het aantal beelden per seconde niet ongelimiteerd is
            if self.fps != 0:
                tPerFrame = 1.0 / abs(self.fps) #Bereken tijd per beeld
                self.disp() #Weergeef de geitereerde wereld
                #Als er nog tijd over is dit beeld en het niet het laatste
                #beeld is
                if tPerFrame > dt and i != n - 1:
                    time.sleep(tPerFrame - dt)
            else: #Bij ongelimiteerde beelden per seconde
                self.disp() #Weergeef de geitereerde wereld
            self.gen += 1 #Een generatie is uitgevoerd
    
    def insertPos(self, xLim = sys.maxint, yLim = sys.maxint):
        """Vraag de positie aan waar een object wordt ingevoegd"""
        x = -1 #Initialiseer buiten de limiet
        y = -1 #Initialiseer buiten de limiet
        while True: #Zolang geen zinnig antwoord voor x is gegeven
            print "X ( 0 -", xLim, "):",
            i = raw_input() #Vraag een getal aan
            try:
                x = int(i) #Schrijf naar x
            except ValueError: #Als de invoer geen integer was
                print "Dat was geen geheel getal"
            if x >= 0 and x <= xLim: #Als de waarde binnen de limiet ligt
                break #Stop de eerste whileloop
            else: #Buiten de limiet, geef aan en laat de loop opnieuw vragen
                print "Ingevoerde getal was buiten de gegeven limiet"
        while True: #Zolang geen zinnig antwoord voor y is gegeven
            print "Y ( 0 -", yLim, "):",
            i = raw_input() #Vraag een getal aan
            try:
                y = int(i) #Schrijf naar y
            except ValueError: #Als de invoer geen integer was
                print "Dat was geen geheel getal"
            if y >= 0 and y <= yLim: #Als de waarde binnen de limiet ligt
                break #Stop de tweede whileloop
            else: #Buiten de limiet, geef aan en laat de loop opnieuw vragen
                print "Ingevoerde getal was buiten de gegeven limiet"
        return [x, y] #Geef de positie terug
    
    def insertObject(self, ob):
        """Voeg een object in"""
        o = ob.copy() #Maak een kopie van het gegeven object
        backup = self.wereld.copy() #Maak een backup van de wereld
        #Vraag een positie aan
        pos = self.insertPos(self.width - o.shape[1], self.height - o.shape[0])
        while True: #Start een loop voor een menu
            self.wereld = backup.copy() #Kopieer de backup naar de wereld
            for x in range(0, o.shape[0]):
                for y in range(0, o.shape[1]):
                    #Kopieer het object naar de wereld
                    self.wereld[pos[1] + x][pos[0] + y] = o[x][y]
            self.disp() #Weergeef de tijdelijke wereld
            print "1. OK"
            print "2. Verplaatsen"
            print "3. Draai links"
            print "4. Draai rechts"
            print "5. Annuleer"
            j = self.requestInput(5)
            if j == 1: #Accepteer en ga terug naar het Game of Life menu
                break
            if j == 2: #Vraag een nieuwe positie aan
                pos = self.insertPos(self.width - o.shape[1],\
                self.height - o.shape[0])
            if j == 3: #Draai naar links
                o2 = o.copy() #Maak een kopie van het object
                try:
                    #Nieuwe dimensies aannemen
                    o = o.reshape(o.shape[1], o.shape[0])
                    for x in range(0, o.shape[0]):
                        for y in range(0, o.shape[1]):
                            #Transponeer en spiegel over de x-as
                            #(gelijk aan rotatie naar links)
                            o[x][y] = o2[y][o.shape[0] - x - 1]
                except IndexError:  #Als het niet lukte (geroteerde object
                                    #komt buiten de wereld)
                    o = o2.copy() #Val terug op de kopie
                    print "Draaien is niet gelukt"
            if j == 4: #Draai naar rechts
                o2 = o.copy() #Maak een kopie van het object
                try:
                    #Nieuwe dimensies aannemen
                    o = o.reshape(o.shape[1], o.shape[0])
                    for x in range(0, o.shape[0]):
                        for y in range(0, o.shape[1]):
                            #Transponeer en spiegel over de y-as
                            #(gelijk aan rotatie naar rechts)
                            o[x][y] = o2[o.shape[1] - y - 1][x]
                except IndexError:  #Als het niet lukte (geroteerde object
                                    #komt buiten de wereld)
                    o = o2.copy() #Val terug op de kopie
                    print "Draaien is niet gelukt"
            if j == 5: #Annuleren
                self.wereld = backup.copy() #Overschrijf de tijdelijke
                                            #wereld met de oude
                break #Stop het menu
    
    def insert(self):
        """Open een menu om een object in te voegen"""
        #Ruwe data voor een glider
        glider = np.array([1, 1, 0,  1, 0, 1,  1, 0, 0]).astype(np.bool8)\
        .reshape(3, 3)
        #Ruwe data voor een glidergun
        glidergun = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
            0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 
            1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
            0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
            0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 
            0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 
            0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 
            0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 
            0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
            0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])\
            .astype(np.bool8).reshape(9, 36)
        #Ruwe data voor een Light Weight Space Ship
        lwss = np.array([0, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 
        1, 0]).astype(np.bool8).reshape((4, 5))
        while True: #While-loop voor een menu
            print "1. Glider"
            print "2. Glidergun"
            print "3. Light Weight Space Ship"
            print "4. Ga terug"
            i = self.requestInput(4)
            if i == 1: #Glider invoegen
                self.insertObject(glider)
            if i == 2: #Glidergun invoegen
                self.insertObject(glidergun)
            if i == 3:
                self.insertObject(lwss)
            if i == 4: #Annuleren
                return #Stop het menu en de functie
    
    def disp(self):
        """Weergeef de wereld"""
        s = "" #String om de wereld in op te bouwen
        for x in range(0, self.height):
            for y in range(0, self.width):
                if self.wereld[x][y]: #Als de cel op (x, y) leeft
                    #Voeg een karakter voor een levende cel
                    #aan de wereld-string toe
                    s += self.levend
                else: #Als die cel niet leeft
                    #Voeg een karakter voor een dode cel
                    #aan de wereld-string toe
                    s += self.dood
            #Als we de laatste cel in een rij gehad hebben
            if x < self.height - 1:
                s += "\n" #Voeg een newline toe aan de wereld-string
        print "Generatie:", self.gen #Print de generatie
        print "-" * self.width #Print een lijn streepjes
        print s #Print de wereld-string
        print "-" * self.width #Print nog een lijn streepjes
        #Tip van een vriend om de beelden vloeiender te laten verlopen
        sys.stdout.flush()
    
    def start(self):
        """Start het Game of Life-programma"""
        if self.clFailed: #Als OpenCL niet goed gestart is
            return #Stop het programma voor we beginnen
        
        while True: #Een while-loop voor een menu
            self.disp() #Weergeef de wereld
            
            #Gemiddelde tijd per beeldtje/generatie
            print "Gemiddelde tijd per generatie:", self.averageDT
            print "-" * self.width #Lijn streepjes
            #Menuopties
            print "1. Start 100 generaties"
            print "2. Start X generaties"
            print "3. Random"
            print "4. Opschonen"
            print "5. Invoegen"
            print "6. Beelden per seconde:", self.fps
            print "7. Resolutie:", self.width, "x", self.height
            print "8. Stop"
            
            i = self.requestInput(8)
            if i == 1: #Start 100 generaties
                self.iterate(100)
            elif i == 2: #Start X generaties, X ingevoerd door de gebruiker
                print "X:",
                j = raw_input()
                try:
                    self.iterate(int(j)) #Voer X iteraties uit
                except ValueError:
                    print "Dat was geen geheel getal,",
                    print "klik enter om door te gaan..."
                    raw_input() #Blokkeer totdat enter is ingeklikt
                    continue #Sla de rest over en begin de loop opnieuw
            elif i == 3: #Genereer een willekeurige wereld
                self.random()
            elif i == 4: #Opschonen
                self.clean()
            elif i == 5: #Voeg een object in
                self.insert()
            elif i == 6: #Voer een aantal beeldjes per seconde in
                print "Het programma probeert maximaal zoveel beeldjes",
                print "per seconde te laten zien."
                print "Beelden per seconde (0 voor ongelimiteerd):",
                j = raw_input() #Vraag een getal aan
                try:
                    self.fps = int(j)   #Zet het aantal beelden per seconde
                                        #gelijk aan het ingevoerde getal
                except ValueError:
                    print "Dat was geen geheel getal, klik enter om door te",
                    print "gaan..."
                    raw_input() #Blokkeer totdat enter is ingeklikt
                    continue #Sla de rest over en begin de loop opnieuw
            elif i == 7: #Nieuwe resolutie voor de wereld
                print "Het veranderen van de resolutie reset de wereld, wilt",
                print "u doorgaan?"
                print "N voor nee, niks of een ander karakter voor Ja:",
                j = raw_input() #Vraag een getal aan
                if j == "N": #Nee
                    continue #Sla de rest over en begin de loop opnieuw
                print "De terminal ondersteunt mogelijk geen breedte groter",
                print "dan 80"
                print "Breedte (beginwaarde: 80):",
                k = raw_input() #Vraag een getal aan
                try:
                    int(k) #Geeft een ValueError als k geen integer is
                except ValueError:
                    print "Dat was geen geheel getal, klik enter om door te",
                    print "gaan..."
                    raw_input() #Blokkeer totdat enter is ingeklikt
                    continue #Sla de rest over en begin de loop opnieuw
                print "Hoogte (beginwaarde: 20):",
                l = raw_input() #Vraag een getal aan
                try:
                    int(l) #Geeft een ValueError als l geen integer is
                except ValueError:
                    print "Dat was geen geheel getal, klik enter om door te",
                    print "gaan..."
                    raw_input() #Blokkeer totdat enter is ingeklikt
                    continue #Sla de rest over en begin de loop opnieuw
                self.width = int(k) #Schrijf de nieuwe breedte
                self.height = int(l) #Schrijf de nieuwe hoogte
                #De oude wereld werkt niet met de nieuwe, ruim hem op
                self.clean()
            elif i == 8: #Sluiten
                return #Stop het menu en het Game of Life-programma