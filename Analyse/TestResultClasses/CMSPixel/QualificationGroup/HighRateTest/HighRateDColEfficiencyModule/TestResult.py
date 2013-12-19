import AbstractClasses
import ROOT

class TestResult(AbstractClasses.GeneralTestResult.GeneralTestResult):
    def CustomInit(self):
        self.Name = "CMSPixel_ModuleTestGroup_HighRateTest_HighRateDColEfficiencyModule_TestResult"
        self.NameSingle = "HighRateDColEfficiencyModule"
        self.Title = "Double column efficiency"
        self.verbose = True
        if self.verbose:
            tag = self.Name + ": Custom Init"
            print "".ljust(len(tag), '=')
            print tag

        self.ResultData["SubTestResultDictList"] = [
            {
                "Key": "Chips",
                "InitialAttributes": {
                    "StorageKey": "Chips",
                    "TestResultSubDirectory": ".",
                    "IncludeIVCurve": False,
                    "ModuleID": self.Attributes["ModuleID"],
                    "ModuleVersion": self.Attributes["ModuleVersion"],
                    "ModuleType": self.Attributes["ModuleType"],
                    "ModuleNRocs": self.Attributes["ModuleNRocs"],
                    "TestType": "HighRateTest",
                    "TestTemperature": self.Attributes["TestTemperature"],
                    "PixelMapA": self.Attributes["PixelMapA"],
                    "PixelMapB": self.Attributes["PixelMapB"],
                },
                "DisplayOptions":{
                    "Order": 1,
                    "Width": 5
                }
            }, {
                "Key": "ModuleSigma",
                "InitialAttributes": {
                    "StorageKey": "ModuleSigma",
                    "TestResultSubDirectory": ".",
                    "IncludeIVCurve": False,
                    "ModuleID": self.Attributes["ModuleID"],
                    "ModuleVersion": self.Attributes["ModuleVersion"],
                    "ModuleType": self.Attributes["ModuleType"],
                    "ModuleNRocs": self.Attributes["ModuleNRocs"],
                    "TestType": "HighRateTest",
                    "TestTemperature": self.Attributes["TestTemperature"],
                },
                "DisplayOptions":{
                    "Order": 2,
                    "Width": 1
                }
            }
        ]
        self.Attributes['TestedObjectType'] = 'HighRateDColEfficiencyModule'

    def PopulateResultData(self):
        if self.verbose:
            tag = self.Name + ": Populate"
            print "".ljust(len(tag), '=')
            print tag
