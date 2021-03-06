'''
Program : MORE-Web
 Author : Esteban Marin - estebanmarin@gmx.ch
 Version    : 2.1
 Release Date   : 2013-05-30
'''
import ROOT, Helper.HtmlParser, os
class TestResultEnvironment:
    # Configuration attributes
    Configuration = {
        'Database':{
            'UseGlobal':False,
            'Type':'',
            'Host':'',
            'User':'',
            'Password':'',
            'DatabaseName':'',
        },
        'DefaultValues':{
            'CanvasWidth': 300,
            'CanvasHeight': 300,
        },
        'ParameterFile':'',
        'GzipSVG':True,
        'DefaultImageFormat':'svg',
        'AbsoluteOverviewPage': None,
    }

    GradingParameters = {
        'noiseMin':50,
        'noiseMax':400,
        'tthrTol':10,
        'gainMin':1.,
        'gainMax': 4.5,
        'par1Min':0.,
        'par1Max':7.,
        'noiseB':500,
        'noiseC':1000,
        'noiseDistribution': 1.0,
        'trimmingB':200,
        'trimmingC':400,
        'trmDistribution':1.0,
        'gainB': 0.1,
        'gainC': 0.2,
        'gainDistribution': 1.0,
        'pedestalB':2500,
        'pedestalC':5000,
        'pedDistribution': 0.96,
        'par1B':1000.,
        'par1C':2000.,
        'par1Distribution': 1.0,
        'defectsB':42,
        'defectsC':168,
        'currentB':2,
        'currentBm10':3,
        'currentC':10,
        'currentCm10':15,
        'slopeivB': 2,
        # check
        'minThrDiff':-5,
        'maxThrDiff':5,
        'BumpBondThr': 150,
        'StandardVcal2ElectronConversionFactor':50,
        'IVCurrentFactor':-1e6,
        'TrimBitDifference':2.,
        'excludeTrimBit14':1,
        'PixelMapMaxValue':10,
        'PixelMapMinValue':0,
        'PixelMapMaskDefectUpperThreshold': 0,
        'BumpBondingProblemsNSigma': 5
    }


    # Database connection
    GlobalDBConnection = None
    GlobalDBConnectionCursor = None

    # Database connection
    LocalDBConnection = None
    LocalDBConnectionCursor = None

    # Path to the test results
    ModuleDataDirectory = '';

    # path to folder with all test results
    GlobalDataDirectory = ''

    TestResultHTMLTemplate = ''

    TestResultStylesheetPath = ''

    # Path to temporary folder
    TempPath = '/tmp'

    # Path to the SQLite Database File for storing the test result
    SQLiteDBPath = ''

    # Path to the Overview
    GlobalOverviewPath = ''

    LastUniqueIDCounter = 0;

    #Error Handling
    ErrorList = []

    def __init__(self, Configuration = None):
        if Configuration:
            self.Configuration['Database'] = {
                'UseGlobal':int(Configuration.get('SystemConfiguration', 'UseGlobalDatabase')),
                'Type':Configuration.get('SystemConfiguration', 'DatabaseType'),
                'Host':Configuration.get('SystemConfiguration', 'DatabaseHost'),
                'User':Configuration.get('SystemConfiguration', 'DatabaseUser'),
                'Password':Configuration.get('SystemConfiguration', 'DatabasePassword'),
                'DatabaseName':Configuration.get('SystemConfiguration', 'DatabaseName'),
            }
            refit = True
            if Configuration.has_option('Fitting','refit'):
                refit = Configuration.getboolean('Fitting','refit')
            self.Configuration['Fitting'] = {
                'refit': refit
            }
            self.Configuration['GzipSVG'] = int(Configuration.get('SystemConfiguration', 'GzipSVG'))
            self.Configuration['DefaultImageFormat'] = Configuration.get('SystemConfiguration', 'DefaultImageFormat')
            for i in self.GradingParameters:
                self.GradingParameters[i] = float(Configuration.get('GradingParameters', i))


        self.MainStylesheet = open('HTML/Main.css').read()

        self.TestResultHTMLTemplate = open('HTML/TestResult/TestResultTemplate.html').read()
        self.TestResultStylesheet = open('HTML/TestResult/TestResultTemplate.css').read()

        self.OverviewHTMLTemplate = open('HTML/Overview/OverviewTemplate.html').read()
        self.OverviewStylesheet = open('HTML/Overview/OverviewTemplate.css').read()
        self.HtmlParser = Helper.HtmlParser.HtmlParser()

        ROOT.gEnv.GetValue("Canvas.SavePrecision", -1)
        ROOT.gEnv.SetValue('Canvas.SavePrecision', "30")
        self.Canvas = ROOT.TCanvas()#'c1', '', 900, 700

        # Prevent garbage collection
        ROOT.SetOwnership(self.Canvas,False)

    def OpenDBConnection(self):
        if self.Configuration['Database']['UseGlobal']:
            import MySQLdb
            try:
                self.GlobalDBConnection = MySQLdb.connect(self.Configuration['Database']['Host'], self.Configuration['Database']['User'], self.Configuration['Database']['Password'], self.Configuration['Database']['DatabaseName'])
                self.GlobalDBConnectionCursor = GlobalDBConnection.cursor()
            except:
                self.GlobalDBConnection = None;
        else:
            CreateDBStructure = False
            import sqlite3
            if not os.path.exists(self.SQLiteDBPath):
                Head, Tail = os.path.split(self.SQLiteDBPath)
                if not os.path.exists(Head):
                    os.makedirs(Head)

                f = open(self.SQLiteDBPath, 'w')
                f.close()
                CreateDBStructure = True

            self.LocalDBConnection = sqlite3.connect(self.SQLiteDBPath)
            self.LocalDBConnection.row_factory = sqlite3.Row
            self.LocalDBConnectionCursor =  self.LocalDBConnection.cursor()
            self.LocalDBConnection.text_factory = str

            if CreateDBStructure:
                self.LocalDBConnectionCursor.executescript('''
                     CREATE TABLE ModuleTestResults(
                        ModuleID TEXT,
                        TestDate INT,
                        TestType TEXT,
                        QualificationType TEXT,
                        Grade TEXT,
                        PixelDefects TEXT,
                        ROCsMoreThanOnePercent INT,
                        Noise INT,
                        Trimming INT,
                        PHCalibration INT,
                        CurrentAtVoltage150 FLOAT,
                        IVSlope FLOAT,
                        Temperature TEXT,
                        RelativeModuleFinalResultsPath TEXT,
                        FulltestSubfolder TEXT,
                        initialCurrent FLOAT,
                        Comments TEXT,
                        nCycles INT,
                        CycleTempLow FLOAT,
                        CycleTempHigh FLOAT
                    );
                ''')


    def GetUniqueID(self, Prefix = ''):
        self.LastUniqueIDCounter += 1
        return Prefix + '_' + str(self.LastUniqueIDCounter)

    def FetchOneAssoc(cursor) :
        data = cursor.fetchone()
        if data == None :
            return None
        desc = cursor.description

        retDict = {}

        for (name, value) in zip(desc, data) :
            retDict[name[0]] = value

        return retDict

    def __del__(self):
        if self.Configuration['Database']['UseGlobal']:
            pass
        else:
            self.LocalDBConnection.close()

    def existInDB(self,moduleID,QualificationType):
        print 'check wheather module %s with QualificationType %s exists in DB: '%(moduleID,QualificationType)
        AdditionalWhere =""
        AdditionalWhere += ' AND ModuleID=:ModuleID '
        AdditionalWhere += ' AND QualificationType=:QualificationType '
        if self.LocalDBConnectionCursor:
            self.LocalDBConnectionCursor.execute(
                'SELECT * FROM ModuleTestResults '+
                'WHERE 1=1 '+
                AdditionalWhere+
                'ORDER BY ModuleID ASC,TestType ASC, TestDate ASC ',
                {
                    'ModuleID':moduleID,
                    'QualificationType':QualificationType
                }
            )
            Rows = self.LocalDBConnectionCursor.fetchall()
            return len(Rows)>0
        return False

