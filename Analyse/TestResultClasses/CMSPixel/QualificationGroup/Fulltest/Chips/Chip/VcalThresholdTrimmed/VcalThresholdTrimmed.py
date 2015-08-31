# -*- coding: utf-8 -*-
import ROOT
import AbstractClasses
import AbstractClasses.Helper.HistoGetter as HistoGetter

class TestResult(AbstractClasses.GeneralTestResult.GeneralTestResult):
    def CustomInit(self):
        self.Name='CMSPixel_QualificationGroup_Fulltest_Chips_Chip_VcalThresholdTrimmed_TestResult'
        self.NameSingle='VcalThresholdTrimmed'
        self.Attributes['TestedObjectType'] = 'CMSPixel_QualificationGroup_Fulltest_ROC'
        self.ThrDefectList = set()
        self.chipNo = self.ParentObject.Attributes['ChipNo']

    def PopulateResultData(self):

        ROOT.gPad.SetLogy(1);
        ROOT.gStyle.SetOptStat(1);
        ChipNo=self.ParentObject.Attributes['ChipNo']
        try:
            DeadPixelList = self.ParentObject.ResultData['SubTestResults']['PixelMap'].ResultData['KeyValueDictPairs']['DeadPixels']['Value']
        except:
            DeadPixelList = ()
            print "warning: could not find pixel alive map, cannot distinguish threshold defects from dead pixels!"

        # TH1D
        HistoDict = self.ParentObject.ParentObject.ParentObject.HistoDict
        histname = HistoDict.get(self.NameSingle, 'ThresholdMap')
        ThresholdMap = HistoGetter.get_histo(self.ParentObject.ParentObject.FileHandle, histname, rocNo = ChipNo)
        self.ResultData['Plot']['ROOTObject'] = ROOT.TH1F(self.GetUniqueID(),'ThresholdDist',256,-.5,255.5)

        for col in range(0, ThresholdMap.GetNbinsX()):
            for row in range(0, ThresholdMap.GetNbinsY()):
                threshold = ThresholdMap.GetBinContent(col + 1, row + 1)
                if (ChipNo, col, row) not in DeadPixelList:
                    self.ResultData['Plot']['ROOTObject'].Fill(threshold)

        bin_min = self.ResultData['Plot']['ROOTObject'].FindFirstBinAbove()
        bin_max = self.ResultData['Plot']['ROOTObject'].FindLastBinAbove()
        self.ResultData['Plot']['ROOTObject'].GetXaxis().SetRange(bin_min-1,bin_max+1)

        self.ResultData['Plot']['ROOTObject_Map'] = ThresholdMap.Clone(self.GetUniqueID())
        gaus = ROOT.TF1('gaus', 'gaus(0)', 0, 255)
        gaus.SetParameters(1600., 
                           self.ResultData['Plot']['ROOTObject'].GetMean(),
                           self.ResultData['Plot']['ROOTObject'].GetRMS())
        gaus.SetParLimits(0, 0., 4160.)
        gaus.SetParLimits(1, 0., 2.*self.ResultData['Plot']['ROOTObject'].GetMean())
        gaus.SetParLimits(2, 0., 2.*self.ResultData['Plot']['ROOTObject'].GetRMS())
        #mG
        self.ResultData['Plot']['ROOTObject'].Fit(gaus, 'QBR', '', 0., 255.)
        #MeanVcalThr = self.ResultData['Plot']['ROOTObject'].GetMean()
        MeanVcalThr = gaus.GetParameter(1)
        #sG
        #RMSVcalThr = self.ResultData['Plot']['ROOTObject'].GetRMS()
        RMSVcalThr = gaus.GetParameter(2)
        #nG
        first = self.ResultData['Plot']['ROOTObject'].GetXaxis().GetFirst()
        last = self.ResultData['Plot']['ROOTObject'].GetXaxis().GetLast()
        IntegralVcalThr = self.ResultData['Plot']['ROOTObject'].Integral(first,last)
        #nG_entries
        IntegralVcalThr_Entries = self.ResultData['Plot']['ROOTObject'].GetEntries()

        under = self.ResultData['Plot']['ROOTObject'].GetBinContent(0)
        over = self.ResultData['Plot']['ROOTObject'].GetBinContent(self.ResultData['Plot']['ROOTObject'].GetNbinsX()+1)

        if self.ParentObject.ResultData['SubTestResults']['OpParameters'].ResultData['HiddenData'].has_key('vcalTrim'):
            self.vcalTrim = self.ParentObject.ResultData['SubTestResults']['OpParameters'].ResultData['HiddenData']['vcalTrim']
        else:
            self.vcalTrim = 0
        if self.vcalTrim < 0:
            self.vcalTrim = 0
        maxDiff = self.TestResultEnvironmentObject.GradingParameters['tthrTol']
        self.ResultData['KeyValueDictPairs'] = {
            'N': {
                'Value':'{0:1.0f}'.format(IntegralVcalThr),
                'Label':'N'
            },
            'mu': {
                'Value':'{0:1.2f}'.format(MeanVcalThr),
                'Label':'μ'
            },
            'sigma':{
                'Value':'{0:1.2f}'.format(RMSVcalThr),
                'Label':'σ'
            },
            'vcal':{
                'Value':'{0:1.2f}'.format(self.vcalTrim),
                'Label':'vcal'
            },
            'maxDiff':{
                'Value':'{0:1.2f}'.format(maxDiff),
                'Label':'Max Delta'
            }
        }
        self.ResultData['KeyList'] = ['N','mu','sigma']
        if under:
            self.ResultData['KeyValueDictPairs']['under'] = {'Value':'{0:1.2f}'.format(under), 'Label':'Underflow'}
            self.ResultData['KeyList'].append('under')
        if over:
            self.ResultData['KeyValueDictPairs']['over'] = {'Value':'{0:1.2f}'.format(over), 'Label':'Overflow'}
            self.ResultData['KeyList'].append('over')


        if self.ResultData['Plot']['ROOTObject']:
            self.ResultData['Plot']['ROOTObject'].SetTitle("")
            self.ResultData['Plot']['ROOTObject'].SetAxisRange(0, 100)
            self.ResultData['Plot']['ROOTObject'].GetXaxis().SetTitle("Vcal Threshold")
            self.ResultData['Plot']['ROOTObject'].GetYaxis().SetTitle("No. of Entries")
            self.ResultData['Plot']['ROOTObject'].GetXaxis().CenterTitle()
            self.ResultData['Plot']['ROOTObject'].GetYaxis().SetTitleOffset(1.5)
            self.ResultData['Plot']['ROOTObject'].GetYaxis().CenterTitle()
            self.ResultData['Plot']['ROOTObject'].Draw()
        self.ResultData['Plot']['ROOTObject_LowEdge'] = ROOT.TCutG('lLower', 2)
        self.ResultData['Plot']['ROOTObject_LowEdge'].SetPoint(0, self.vcalTrim - maxDiff, -1e6)
        self.ResultData['Plot']['ROOTObject_LowEdge'].SetPoint(1, self.vcalTrim - maxDiff, +1e6)
        self.ResultData['Plot']['ROOTObject_LowEdge'].SetLineColor(ROOT.kRed)
        self.ResultData['Plot']['ROOTObject_LowEdge'].SetLineStyle(2)
        self.ResultData['Plot']['ROOTObject_LowEdge'].Draw('same')

        self.ResultData['Plot']['ROOTObject_UpEdge'] = ROOT.TCutG('lUpper', 2)
        self.ResultData['Plot']['ROOTObject_UpEdge'].SetPoint(0, self.vcalTrim + maxDiff, -1e6)
        self.ResultData['Plot']['ROOTObject_UpEdge'].SetPoint(1, self.vcalTrim + maxDiff, +1e6)
        self.ResultData['Plot']['ROOTObject_UpEdge'].SetLineColor(ROOT.kRed)
        self.ResultData['Plot']['ROOTObject_UpEdge'].SetLineStyle(2)
        self.ResultData['Plot']['ROOTObject_UpEdge'].Draw('same')
        if self.ResultData['Plot']['ROOTObject_Map']:
            for column in range(self.nCols):  # Column
                for row in range(self.nRows):  # Row
                    if (ChipNo, column, row) not in DeadPixelList:
                        self.HasThresholdDefect(column, row)

        self.Title = 'Vcal Threshold Trimmed'
        self.SaveCanvas()
        self.ResultData['KeyValueDictPairs']['TrimProblems'] = { 'Value':self.ThrDefectList, 'Label':'Trim Problems'}
        self.ResultData['KeyValueDictPairs']['NTrimProblems'] = { 'Value':len(self.ThrDefectList), 'Label':'N Trim Problems'}
        self.ResultData['KeyList'].append('NTrimProblems')


    def HasThresholdDefect(self, column, row):
        if self.vcalTrim > 0:
            binContent = self.ResultData['Plot']['ROOTObject_Map'].GetBinContent(column + 1, row + 1)
            delta = abs(binContent - self.vcalTrim)
            if  delta > self.TestResultEnvironmentObject.GradingParameters['tthrTol']:
                self.ThrDefectList.add((self.chipNo, column, row))
                print 'ThresholdDefect %2d %2d %2d ' % (self.chipNo, column, row), self.vcalTrim, delta, self.TestResultEnvironmentObject.GradingParameters['tthrTol']
                return True
        return False
