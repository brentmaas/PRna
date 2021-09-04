import numpy as np
import time
import matplotlib.pyplot as plt

#Python 2.7.12
#Numpy 1.10.4
#Matplotlib 1.5.1
#Pyopencl 2016.2
#Module voor snelheidstest
#Gemaakt door Brent Maas (sXXXXXXX)
#Ontwikkeld in de periode 01/11/2016 - 22/11/2016

class SpeedTest:
    cl = False #Of OpenCL gebruikt wordt
    maxN = 10 #Maximale n in een nxn-matrix
    limit = 100 #Grootste waarde in een matrix
    repeat = 10 #Aantal herhalingen per n in een nxn-matrix
    
    clInitialized = False #Is OpenCL geinitialiseerd
    clPrgBuild = False #Is het OpenCL-programma gecompileerd
    clFailed = False #Is OpenCL niet goed gestart
    #De broncode voor het OpenCL programma (kernel)
    clKernel = """//OpenCL comment
//Een enkele matrixvermenigvuldiging
//*a: pointer met data voor de eerste matrix
//*b: pointer met data voor de tweede matrix
//*c: pointer voor de resulterende matrix
//n: grootte van de matrix (nxn)
void mMult(__global int *a, __global int *b, __global int *c, int n){
    for(int i = 0;i < n;i++){ //Voor elke i-index
        for(int j = 0;j < n;j++){ //Voor elke j-index
            int d = 0; //Teller voor het dot-product
            for(int k = 0;k < n;k++){ //Nog een loop langs de matrix
                //Een gedeelte van het dotproduct
                d += a[i * n + k] * b[k * n + j];
            }
            c[i * n + j] = d; //Schrijf dotproduct naar resultaat
        }
    }
}

//Kernel (main-functie)
//*a: pointer met data naar alle eerste matrices
//*b: pointer met data naar alle tweede matrices
//*c: pointer voor data naar alle resulterende matrices
//*n: pointer met n
//*size: pointer met het aantal matrices dat berekent wordt
__kernel void matrixMult(__global const int *a, __global const int *b, 
__global int *c, __global int *n, __global int *size){
    //Vraag het ID van deze instantie op
    //(wordt hier gebruikt als index voor de matrix die berekent wordt)
    int gid = get_global_id(0);
    if(gid < size[0]){ //Als de index binnen het maximum valt
        //&a[b] geeft een pointer die hetzelfde is als a, maar met een offset b
        __global float *mA = &a[n[0] * n[0] * gid]; //Vind eerste matrix
        __global float *mB = &b[n[0] * n[0] * gid]; //Vind tweede matrix
        __global float *mC = &c[n[0] * n[0] * gid]; //Vind resulterende matrix
        mMult(mA, mB, mC, n[0]); //Voer de vermenigvuldiging uit
    }
}"""
    
    def __init__(self, cl):
        """Initialisatiefunctie
        cl: of het programma wel of niet OpenCL gebruikt"""
        self.cl = cl #Kopier het argument cl
        
        #Als OpenCL wordt gebruikt, maar nog niet is geinitialiseerd
        if self.cl and not self.clInitialized:
            try:
                global ocl #Kleine zonde om de import te laten werken
                import pyopencl as ocl #Importeer pyopencl
            except ImportError: #Als pyopencl niet kon worden geimporteerd
                print "Pyopencl kon niet worden geimporteerd,",
                print "schakel het a.u.b. uit"
                self.clFailed = True #OpenCL kon niet goed worden gestart
            if not self.clFailed: #Als OpenCL goed gestart is
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
                    self.prg = ocl.Program(self.ctx, self.clKernel).build()
                    self.clInitialized = True #Pyopencl is geinitialiseerd
                    self.clPrgBuild = True #Het programma is gecompileerd
                except: #Als er iets fout ging tijdens de initialisatie
                    print "Pyopencl kon niet worden geinitialiseerd,",
                    print "schakel het a.u.b. uit"
                    self.clFailed = True #OpenCL kon niet goed worden gestart
    
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
    
    def genMatrix(self, n):
        """Genereer een nxn matrix met willekeurige integers"""
        a = np.random.rand(n * n) #Genereer een random array, floats [0;1]
        a *= self.limit #Vermenigvuldig met de maximale waarde
        a += 0.5 #Voeg een half toe om goed af te ronden (round(i)=int(i+0.5))
        a = a.reshape((n, n)).astype(np.int32) #Maak er integers van
        return np.matrix(a) #Geeft terug als matrix
    
    def matrixMultNpIntegrated(self, matricesA, matricesB, n, repeat=1):
        """Vermenigvuldig repeat nxn-matrices in matricesA en matricesB
        met behulp van Numpy's geintegreerde matrixvermenigvuldiging"""
        matricesC = [] #Lege lijst voor resultaat
        for i in range(0, repeat): #Voor elke matrixvermenigvuldiging
            #Vermenigvuldig matrix A en B en voeg het resultaat achter in C
            matricesC.append(matricesA[i] * matricesB[i])
        return matricesC #Geef de resultaatmatrices terug
    
    def dot(self, a, b):
        """Dotproduct tussen vectors a en b"""
        n = len(a) #Indices in een vector
        c = 0 #Teller 
        for i in range(0, n): #Voor elke index
            c += a[i] * b[i] #Voeg het product van die indices toe aan c
        return c #Geef c terug
    
    def matrixMultNpPython(self, matricesA, matricesB, n, repeat=1):
        """Vermenigvuldig repeat nxn-matrices in matricesA en matricesB
        met behulp van Numpy-arrays en een eigen implementatie"""
        matricesC = [] #Lege lijst voor resultaten
        for i in range(0, repeat): #Voor elke matrixvermenigvuldiging
            a = np.asarray(matricesA[i]) #Matrix A als array
            b = np.asarray(matricesB[i]) #Matrix B als array
            c = np.empty_like(matricesA[i]) #Lege resulterende matrix C
            for j in range(0, n): #Voor elke i-index
                for k in range(0, n): #Voor elke j-index
                    #Voer een dotproduct uit voor element (i,j) (= [j,k]) van C
                    c[j,k] = self.dot(a[j,:], b[:,k])
            #Voeg resultaatmatrix c toe aan de resultaten
            matricesC.append(np.matrix(c))
        return matricesC #Geef de resultaatmatrices terug
    
    def matrixMultCL(self, matricesA, matricesB, n, repeat=1):
        """Vermenigvuldig repeat nxn-matrices in matricesA en matricesB
        met behulp van een eigen OpenCL-implementatie"""
        global ocl #Wederom een zonde om de import te laten werken
        matricesC = [] #Lege lijst voor resultaten
        #Lege array voor matrices A
        a_np = np.zeros(n * n * repeat, dtype=np.int32)
        #Lege array voor matrices B
        b_np = np.zeros(n * n * repeat, dtype=np.int32)
        for i in range(0, repeat): #Voor elke matrixvermenigvuldiging
            #Voeg matrix A in in de lege array
            a_np[i * n**2:i * n**2 + n**2] = np.asarray(matricesA[i])\
            .reshape(n * n)
            #Voeg matrix B in in de lege array
            b_np[i * n**2:i * n**2 + n**2] = np.asarray(matricesB[i])\
            .reshape(n * n)
        #De matrices A als buffer
        a_g = ocl.Buffer(self.ctx, self.mf.READ_ONLY | self.mf.COPY_HOST_PTR,\
        hostbuf=a_np)
        #De matrices B als buffer
        b_g = ocl.Buffer(self.ctx, self.mf.READ_ONLY | self.mf.COPY_HOST_PTR,\
        hostbuf=b_np)
        #n als buffer
        n_g = ocl.Buffer(self.ctx, self.mf.READ_ONLY | self.mf.COPY_HOST_PTR,\
        hostbuf=np.array([n]))
        #repeat als buffer
        size_g = ocl.Buffer(self.ctx, self.mf.READ_ONLY |\
        self.mf.COPY_HOST_PTR, hostbuf=np.array([repeat]))
        #De resultaatmatrices als buffer
        res_g = ocl.Buffer(self.ctx, self.mf.WRITE_ONLY,\
        a_np.size * a_np.itemsize)
        
        #Voer de berekning uit
        self.prg.matrixMult(self.queue, (repeat,), None, a_g,\
        b_g, res_g, n_g, size_g)
        
        #Lege array om resultaten naar te kopieren
        res_np = np.empty_like(a_np)
        #Kopieer resultaten van de buffer naar de array
        ocl.enqueue_copy(self.queue, res_np, res_g)
        for i in range(0, repeat): #Voor elke matrix in de resultatenarray
            #Voeg de matrix achter aan de resultatenlijst
            matricesC.append(np.matrix(res_np[n**2 * i:n**2 * i + n**2]\
            .reshape((n, n))))
        
        return matricesC #Geef de lijst met resultaten terug
    
    def matrixMultNestedList(self, matricesA, matricesB, n, repeat=1):
        """Vermenigvuldig repeat nxn-matrices uit matricesA en matricesB
        met behulp van geneste Python-lijsten"""
        matricesC = [] #Lege lijst voor resultaten
        for i in range(0, repeat): #Voor elke vermenigvuldiging
            a = matricesA[i].tolist() #Pak matrix A en maak er een lijst van
            b = matricesB[i].tolist() #Pak matrix B en maak er een lijst van
            c = [[0] * n] * n #Maak een 2D geneste lijst met nullen
            for j in range(0, n): #Voor elke i-index
                for k in range(0, n): #Voor elke j-index
                    #Voor elke index van de kolom- en rijvectoren van (i,j)
                    for l in range(0, n):
                        #Voeg een gedeelte van het dotproduct toe aan (i,j)
                        c[j][k] += a[j][l] * b[l][k]
            #Voeg de resulterende matrix toe aan
            #het einde van de resultatenlijst
            matricesC.append(np.matrix(c))
        return matricesC #Geef de lijst met resultaten terug
    
    def go(self):
        """Voer alle matrixvermenigvuldigingen uit"""
        #Lege lijst voor tijdsmetingen voor
        #de geintegreerde Numpy-vermenigvuldiging
        self.resNpIntegrated = []
        #Lege lijst voor tijdsmetingen voor
        #eigen implementatie met Numpy arrays
        self.resNpPython = []
        #Lege lijst voor tijdsmetingen voor eigen implementatie met OpenCL
        self.resCl = []
        #Lege lijst voor tijdsmetingen voor
        #eigen implementatie met geneste Pythonlijsten
        self.resNested = []
        for n in range(1, self.maxN + 1): #Voor elke n
            print "n:", n
            #Genereer de eerste matrices
            matricesA = [self.genMatrix(n) for i in range(0, self.repeat)]
            #Genereer de tweede matrices
            matricesB = [self.genMatrix(n) for i in range(0, self.repeat)]
            t = time.clock() #Begintijd geintegreerde Numpy-vermenigvuldiging
            #Voor berekening uit en sla resultaten op
            cNpIntegrated = self.matrixMultNpIntegrated(matricesA, matricesB,\
            n, repeat=self.repeat)
            #Eindtijd geintegreerde Numpy-vermenigvuldiging
            dtNpIntegrated = (time.clock() - t) / self.repeat * 1000
            #Voeg tijdsmeting toe aan lijst
            self.resNpIntegrated.append(dtNpIntegrated)
            t = time.clock() #Begintijd implementatie met Numpy-arrays
            #Voor berekening uit en sla resultaten op
            cNpPython = self.matrixMultNpPython(matricesA, matricesB, n,\
            repeat=self.repeat)
            dtNpPython = (time.clock() - t) / self.repeat * 1000
            #Voeg tijdsmeting toe aan lijst
            self.resNpPython.append(dtNpPython)
            if self.cl: #Als OpenCL gebruikt wordt
                t = time.clock() #Begintijd OpenCL-implementatie
                #Voor berekening uit en sla resultaten op
                cCl = self.matrixMultCL(matricesA, matricesB, n,\
                repeat=self.repeat)
                #Eindtijd OpenCL
                dtCl = (time.clock() - t) / self.repeat * 1000
            #Voeg tijdsmeting toe aan lijst
                self.resCl.append(dtCl)
            t = time.clock() #Begintijd implementatie geneste Pythonlijsten
            #Voor berekening uit en sla resultaten op
            cNested = self.matrixMultNestedList(matricesA, matricesB, n,\
            repeat=self.repeat)
            #Eindtijd implementatie geneste Pythonlijsten
            dtNestedList = (time.clock() - t) / self.repeat * 1000
            #Voeg tijdsmeting toe aan lijst
            self.resNested.append(dtNestedList)
            
            #De geintegreerde Numpy-vermenigvuldiging wordt als juist beschouwt
            #Lege controlelijst implementatie met Numpy-arrays
            checkNpPython = [None] * self.repeat
            if self.cl: #Als OpenCL gebruikt wordt
                checkCl = [None] * self.repeat #Lege lijst OpenCL-implementatie
            #Lege lijst implementatie met geneste Pythonlijsten
            checkNested = [None] * self.repeat
            for i in range(0, self.repeat): #Voor elke vermenigvuldiging
                #Controleer implementatie met Numpy-arrays
                checkNpPython[i] = cNpIntegrated[i] == cNpPython[i]
                if self.cl: #Als OpenCL gebruikt wordt
                    #Controleer implementatie met OpenCL
                    checkCl[i] = cNpIntegrated[i] == cCl[i]
                #Contorleer implementatie met geneste Pythonlijsten
                checkNested[i] = cNpIntegrated[i] == cNested[i]
            
            #Als er een fout zit in de implementatie met Numpy-arrays
            if np.any(checkNpPython == False):
                print "Numpy array + Python had een foutief resultaat!"
            if self.cl: #Als OpenCL gebruikt wordt
                #Als er een fout zit in de OpenCL-implementatie
                if np.any(checkCl == False):
                    print "OpenCl had een foutief resultaat!"
            #Als er een fout zit in de implementatie met geneste Pythonlijsten
            if np.any(checkNested == False):
                print "Python geneste lijsten had een foutief resultaat!"
        
        #Lijst met alle gebruikte n
        ns = [n for n in range(1, self.maxN + 1)]
        
        #Array met gebruikte n-waarden als x-waarden
        x = np.array(ns)
        #Array met y-waarden geintegreerde Numpy-vermenigvuldiging
        yNpIntegrated = np.array(self.resNpIntegrated)
        #Array met y-waarden implementatie met Numpy-arrays
        yNpPython = np.array(self.resNpPython)
        if self.cl: #Als OpenCL gebruikt is
            #Array met y-waarden OpenCL-implementatie
            yCl = np.array(self.resCl)
        #Array met y-waarden implementatie met geneste Pythonlijsten
        yNested = np.array(self.resNested)
        
        w = 2 #Lijndikte
        #Zet de title
        plt.title("Matrixvermenigvuldiging benchmark")
        plt.xlim(1, self.maxN) #Zet de bounds van de x-as
        plt.xlabel("n") #Zet de naam van de x-as
        plt.ylabel("t (ms)") #Zet de naam van de y-as
        #Plot de tijdsmetingen van de geintegreerde Numpy-vermenigvuldiging
        plt.plot(x, yNpIntegrated, label="Numpy geintegreerd", linewidth=w)
        #Plot de tijdsmetingen van de implementatie met Numpy-arrays
        plt.plot(x, yNpPython, label="Numpy array + Python", linewidth=w)
        if self.cl: #Als OpenCL gebruikt is
            #Plot de tijdsmetingen van de OpenCL-implementatie
            plt.plot(x, yCl, label="OpenCL", linewidth=w)
        #Plot de tijdsmetingen van de implementatie met geneste Pythonlijsten
        plt.plot(x, yNested, label="Python geneste lijst", linewidth=w)
        plt.legend(loc=2) #Maak een legend linksboven
        fig = plt.gcf() #Krijg de referentie naar de plot
        plt.show() #Laat de plot zien
        
        print "Kies een locatie om de plot op te slaan,",
        print "laat leeg voor niet opslaan."
        print "Locatie:",
        i = raw_input() #Vraag een locatie
        if not i == "": #Als de invoer niet leeg is
            fig.savefig(i) #Sla de figuur op
            print "Opgeslagen in", i
    
    def run(self):
        """Start het snelheidstestprogramma"""
        if self.clFailed: #Als OpenCL niet goed gestart is
            return #Stop het programma
        
        while True: #Een whileloop voor een menu
            #Menuopties
            print "1. Start"
            print "2. Max n:", self.maxN
            print "3. Maximale waarde:", self.limit
            print "4. Herhalingen:", self.repeat
            print "5. Terug"
            
            i = self.requestInput(5)
            
            if i == 1: #Start
                self.go() #Start de berekeningen
                return #Stop het programma en ga terug naar het hoofdmenu
            elif i == 2: #Maximale n
                print "De maximale waarde voor n in een nxn-matrix,",
                print "er wordt getest van 1 tot en met n"
                j = raw_input() #Vraag een getal
                try:
                    int(j) #Geeft een ValueError als j geen integer is
                except ValueError: #j geen integer
                    print "Dat was geen geheel getal"
                    continue #Herstart de loop
                if int(j) < 1: #Als de invoer kleiner is dan 1
                    print "n kan niet kleiner zijn dan 1"
                    continue #Herstart de loop
                self.maxN = int(j) #Als alles goed is, sla de invoer op
            elif i == 3: #Maximale waarde
                print "De grootste waarde die, groter dan 0,",
                print "in een matrix kan voorkomen"
                j = raw_input() #Vraag een getal
                try:
                    int(j) #Geeft een ValueError als j geen integer is
                except ValueError: #j geen integer
                    print "Dat was geen geheel getal"
                    continue #Herstart de loop
                if int(j) < 0: #Als de invoer kleiner is dan 0
                    print "Deze waarde kan niet kleiner dan 0 zijn"
                    continue #Herstart de loop
                self.limit = int(j) #Als alles goed is, sla de invoer op
            elif i == 4: #Herhalingen
                print "Het aantal keer dat de tests worden uitgevoerd per n"
                j = raw_input() #Vraag een getal
                try:
                    int(j) #Geeft een ValueError als j geen integer is
                except ValueError: #j geen integer
                    print "Dat was geen geheel getal"
                    continue #Herstart de loop
                if int(j) < 1: #Als de invoer kleiner is dan 1
                    print "Er kunnen geen nul of minder tests worden gedraaid"
                    continue #Herstart de loop
                self.repeat = int(j) #Als alles goed is, sla de invoer op
            elif i == 5: #Sluiten
                return #Sluit het programma en ga terug naar het hoofdmenu