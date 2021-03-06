#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#Author: Read AUTHORS file.
#License: Read COPYING file.



from PyQt4 import *
import os
from ui_mainwindow import Ui_MainWindow
from engine import lib
from pasoinfo import pasoInfo
from pasopackages import pasoPackages
from isopackagesource import isoPackageSource
from preferencesdialog import preferences
from progressdialog import progress
from aboutdialog import about
from engine.pasobuilder import buildFromPath, savePaso, loadPaso
from engine.isobuilder import builder
from engine.lib import ratioCalc
from constants import const






class mainWindow(QtGui.QMainWindow, Ui_MainWindow):


    def __init__(self):
        #
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        self.i18n()

        QtCore.QObject.connect(self.actionNew,  QtCore.SIGNAL("triggered (bool)"),  self.new)
        QtCore.QObject.connect(self.actionOpen,  QtCore.SIGNAL("triggered (bool)"),  self.open)
        QtCore.QObject.connect(self.actionSave,  QtCore.SIGNAL("triggered (bool)"),  self.save)
        QtCore.QObject.connect(self.actionSave_as,  QtCore.SIGNAL("triggered (bool)"),  self.saveas)
        QtCore.QObject.connect(self.actionExit,  QtCore.SIGNAL("triggered (bool)"),  self.exit)
        QtCore.QObject.connect(self.actionBuild_from_Installation,  QtCore.SIGNAL("triggered (bool)"),  self.pasoBuildfromIns)
        QtCore.QObject.connect(self.actionBuild_installation_image,  QtCore.SIGNAL("triggered (bool)"),  self.isoBuild)
        QtCore.QObject.connect(self.actionPreferences,  QtCore.SIGNAL("triggered (bool)"),  self.openPreferences)
        QtCore.QObject.connect(self.actionAbout,  QtCore.SIGNAL("triggered (bool)"),  self.openAbout)
        QtCore.QObject.connect(self.actionExport, QtCore.SIGNAL("triggered (bool)"), self.export)

        self.preferences = preferences()
        if not self.preferences.load():
            self.message(self.msg[0])
            self.preferences.exec_()

        self.pasoFName = ""
        self.setWindowTitle("%s   -   %s" %(const.NAME, self.pasoFName))

        self.move(( (QtGui.QApplication.desktop().width()- self.width()) / 2 ),
            ( (QtGui.QApplication.desktop().height()- self.height()) / 2 ))





    def new(self):
        if not self.saveQuestion(): return()
        try:
            self.pasoinfo.hide()
            self.pasopackages.hide()
            self.horizontalLayout.removeWidget(self.pasoinfo)
            self.horizontalLayout.removeWidget(self.pasopackages)
        except:
            pass
        self.pasoinfo = pasoInfo()
        header = self.pasoinfo.getHeader()
        header.pn = self.preferences.config.name
        header.pm = self.preferences.config.email
        self.pasoinfo.setHeader(header)
        self.horizontalLayout.addWidget(self.pasoinfo)
        self.actionBuild_from_Installation.setEnabled(True)
        self.pasoFName = ""
        self.actionSave.setEnabled(False)
        self.actionBuild_installation_image.setEnabled(False)
        self.actionSave_as.setEnabled(False)
        self.actionExport.setEnabled(False)
        self.setWindowTitle(const.NAME)







    def open(self):
        if not self.saveQuestion(): return()
        try:
            self.pasoinfo.hide()
            self.pasopackages.hide()
            self.horizontalLayout.removeWidget(self.pasoinfo)
            self.horizontalLayout.removeWidget(self.pasopackages)
        except:
            pass
        fileName = QtGui.QFileDialog.getOpenFileName(self, "",self.preferences.config.workspace, "Paso (*%s)" %const.PASO_EXT)
        if fileName:
            data = loadPaso(unicode(fileName))
            if data:
                self.pasoFName = os.path.basename(unicode(fileName))
                self.pasoinfo = pasoInfo()
                self.pasopackages = pasoPackages()
                self.pasoinfo.setHeader(data.header)
                self.pasoinfo.setTitle(self.pasoFName)
                self.pasopackages.setFromList(data.packages.files.keys())
                self.horizontalLayout.addWidget(self.pasoinfo)
                self.horizontalLayout.addWidget(self.pasopackages)
                self.actionBuild_from_Installation.setEnabled(True)
                self.actionSave.setEnabled(True)
                self.actionSave_as.setEnabled(True)
                self.actionExport.setEnabled(False)
                self.actionBuild_installation_image.setEnabled(True)
                self.setWindowTitle("%s   -   %s" %(const.NAME, self.pasoFName))
            else:
                self.message(self.msg[23])




    def save(self):
        if not self.pasoFName:
            fileName = QtGui.QFileDialog.getSaveFileName(self, "", self.preferences.config.workspace, "Paso (*%s)" %const.PASO_EXT)
            if fileName:
                self.pasoFName = unicode(fileName)
                if self.pasoFName[len(self.pasoFName)-5:] != const.PASO_EXT:
                    self.pasoFName = self.pasoFName+const.PASO_EXT
        if self.pasoFName:
            if savePaso(self.pasoinfo.getHeader(), self.pasopackages.getPackages(), self.pasoFName):
                self.pasoinfo.changed = False
                self.pasopackages.changed = False
                self.pasoinfo.setTitle(os.path.basename(self.pasoFName))
                self.setWindowTitle("%s   -   %s" %(const.NAME, unicode(self.pasoFName)))
            else:
                self.message(self.msg[24])




    def saveas(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self, "", self.preferences.config.workspace, "Paso (*%s)" %const.PASO_EXT)
        if fileName:
            self.pasoFName = unicode(fileName)
            if self.pasoFName[len(self.pasoFName)-5:] != const.PASO_EXT:
                self.pasoFName = self.pasoFName+const.PASO_EXT
            self.save()






    def pasoBuildfromIns(self):
        self.message(self.msg[25], self.msg[26])
        dirName = QtGui.QFileDialog.getExistingDirectory(self, "", "/", QtGui.QFileDialog.ShowDirsOnly )
        if dirName:
            packages = buildFromPath()
            pkgList = packages.loadList(unicode(dirName))
            if not pkgList:
                self.message(self.msg[3])
                return()
            prg = progress()
            prg.show()
            total = len(pkgList)
            current = 0
            for pkg in pkgList:
                self.setProgress(prg, self.msg[4], pkg, ratioCalc(total, current))
                if not packages.loadPackageInfo(pkg):
                    self.message(self.msg[5], pkg)
                    return()
                current += 1
            if const.INSTALLER_NAME not in packages.getNameList():
                self.message(self.msg[27], self.msg[28])
                return()
            try:
                self.pasopackages.hide()
                self.horizontalLayout.removeWidget(self.pasopackages)
            except:
                pass
            header = self.pasoinfo.getHeader()
            header.r = lib.getPardusRelease(unicode(dirName))
            header.d = lib.getDate()
            header.a = packages.getArch()
            header.ds = packages.getDist()
            header.pn = self.preferences.config.name
            header.pm = self.preferences.config.email
            self.pasoinfo.setHeader(header)
            self.pasopackages = pasoPackages()
            self.pasopackages.setFromList(packages.getFileList(), packages.getNameList())
            self.pasopackages.changed = True
            self.horizontalLayout.addWidget(self.pasopackages)
            self.actionSave.setEnabled(True)
            self.actionBuild_installation_image.setEnabled(True)
            self.actionSave_as.setEnabled(True)
            self.actionExport.setEnabled(True)





    def isoBuild(self):
        iso = builder()
        iso.loadSources()
        if not iso.pisiconfLoaded:
            self.message(self.msg[6])
            return()
        if not iso.repoUrlsLoaded:
            self.message(self.msg[7])
            return()
        remoteSources = iso.getRemoteSources() + self.preferences.getRemoteSources()
        localSources = iso.getLocalSources() + self.preferences.getLocalSources()
        isoDialog = isoPackageSource()
        isoDialog.setRemoteSources(remoteSources)
        isoDialog.setLocalSources(localSources)
        isoDialog.setWorkspace(self.preferences.config.workspace)
        if self.pasoFName:
            isoDialog.setProjectName( unicode(os.path.basename(self.pasoFName)[:len(os.path.basename(self.pasoFName))-len(const.PASO_EXT)]) )
        else:
            isoDialog.setProjectName( self.pasoinfo.getHeader().n.__str__() )
        isoDialog.setPIMPath(self.preferences.config.pim)
        if not isoDialog.exec_():
            return()
        iso.setSources(isoDialog.getLocalSources(), isoDialog.getRemoteSources())
        iso.setTarget(isoDialog.getWorkspace(), isoDialog.getProjectName()+"-"+self.pasoinfo.getHeader().a)
        iso.setPIMPath(isoDialog.getPIMPath())
        self.preferences.config.pim = isoDialog.getPIMPath()
        self.preferences.save()
        prg = progress()
        self.setProgress(prg, self.msg[22], isoDialog.getProjectName() )
        prg.show()
        if not iso.makeDirs():
            self.message(self.msg[8])
            return()
        total = len( self.pasopackages.getFileList() )
        current = 0
        for pkg in self.pasopackages.getFileList():
            if prg.stop:
                return()
            self.setProgress(prg, self.msg[9] , pkg, ratioCalc(total, current, 5, 1))
            pkgInfo = iso.searchPackage(pkg)
            if not pkgInfo:
                self.message(self.msg[10], pkg)
                return()
            elif not pkgInfo.path:
                pass    #already on repo
            else:
                self.setProgress(prg, self.msg[11] , os.path.join(pkgInfo.path, pkg), ratioCalc(total, current, 5, 1))
                if not iso.bringPackage(pkgInfo):
                    self.message(self.msg[29], pkg)
                    return()
            current += 1
        self.setProgress(prg, self.msg[12],self.msg[13], ratioCalc(100, 50, 5, 2))
        if not iso.buildIndex():
            self.message(self.msg[14])
            return()
        self.setProgress(prg, self.msg[15] , self.msg[13], ratioCalc(100, 50, 5, 3) )
        if not iso.transferInstallationSystem():
            self.message(self.msg[16])
            return()
        self.setProgress(prg, self.msg[17] , self.msg[13], ratioCalc(100, 50, 5, 4) )
        if not iso.createISO():
            self.message(self.msg[18])
            return()
        self.setProgress(prg, self.msg[19] , self.msg[13], ratioCalc(100, 50, 5, 5))
        if not iso.calcSUM():
            self.message(self.msg[20])
            return()
        prg.hide()
        self.message(self.msg[21], iso.getTargetName() )







    def openPreferences(self):
        self.preferences.update()
        self.preferences.exec_()






    def openAbout(self):
        aDialog = about()
        aDialog.exec_()




    def export(self):
        fileName = unicode( QtGui.QFileDialog.getSaveFileName(self, "", self.preferences.config.workspace,
                const.EXPORT_TYPES %(self.msg[30], self.msg[31]) ) )
        if fileName[len(fileName)-3:].lower() == "txt":
            if not lib.savefile(fileName, str().join(map(lambda x: x+"\n", self.pasopackages.getNameList())) ):
                self.message(self.msg[32], fileName)
        if fileName[len(fileName)-3:].lower() == "xml":
            pass





    def setProgress(self, prg,  name, action="", value=0):
        prg.show()
        prg.setName(name)
        prg.setAction(action)
        prg.setValue(value)
        prg.repaint()
        QtGui.QApplication.processEvents()





    def exit(self):
        self.close()








    def saveQuestion(self):
        state = False
        try:               state = self.pasoinfo.changed + self.pasopackages.changed
        except:            pass

        if state:
            msgBox = QtGui.QMessageBox()
            msgBox.setText( self.msg[1] )
            msgBox.setInformativeText( self.msg[2] )
            msgBox.setStandardButtons(QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel)
            msgBox.setDefaultButton(QtGui.QMessageBox.Save)
            rep = msgBox.exec_()
            if rep == QtGui.QMessageBox.Save:
                self.save()
            if rep == QtGui.QMessageBox.Cancel:
                return(False)
        return(True)




    def message(self, msg, inf=""):
        msgBox = QtGui.QMessageBox()
        msgBox.setText(msg)
        msgBox.setInformativeText( inf )
        msgBox.exec_()





    def i18n(self):
        self.msg = range(40)
        self.msg[0] = QtGui.QApplication.translate("MainDialog", "Welcome, Paso needs your personal information, please continue and create your profile.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[1] = QtGui.QApplication.translate("MainDialog", "The project has been modified.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[2] = QtGui.QApplication.translate("MainDialog", "Do you want to save your changes?", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[3] = QtGui.QApplication.translate("MainDialog", "Package list could not be read.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[4] = QtGui.QApplication.translate("MainDialog", "Loading information of packages.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[5] = QtGui.QApplication.translate("MainDialog", "Package could not be read.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[6] = QtGui.QApplication.translate("MainDialog", "Pisi configuration could not be read.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[7] = QtGui.QApplication.translate("MainDialog", "Pisi repository information could not be read.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[8] = QtGui.QApplication.translate("MainDialog", "Directories could not be created on workspace.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[9] = QtGui.QApplication.translate("MainDialog", "Searching package...", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[10] = QtGui.QApplication.translate("MainDialog", "Pisi package could not be found.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[11] = QtGui.QApplication.translate("MainDialog", "Downloading or copying package...", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[12] = QtGui.QApplication.translate("MainDialog", "Building repository index.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[13] = QtGui.QApplication.translate("MainDialog", "Please wait...", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[14] = QtGui.QApplication.translate("MainDialog", "Installation repository index could not be created.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[15] = QtGui.QApplication.translate("MainDialog", "Copying installation system.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[16] = QtGui.QApplication.translate("MainDialog", "Pardus installation system could not be copied from installation media.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[17] = QtGui.QApplication.translate("MainDialog", "Creating installation image.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[18] = QtGui.QApplication.translate("MainDialog", "Installation image could not be created.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[19] = QtGui.QApplication.translate("MainDialog", "Calculating verification code (SHA1SUM).", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[20] = QtGui.QApplication.translate("MainDialog", "Verification code could not be created.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[21] = QtGui.QApplication.translate("MainDialog", "Image successfully created.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[22] = QtGui.QApplication.translate("MainDialog", "Project directories are creating on workspace.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[23] = QtGui.QApplication.translate("MainDialog", "Paso file could not be opened.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[24] = QtGui.QApplication.translate("MainDialog", "Paso file could not be saved.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[25] = QtGui.QApplication.translate("MainDialog", "Please select root directory of Pardus installation which you want to build.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[26] = QtGui.QApplication.translate("MainDialog", "Current root directory will be opened. If you want to build from current system, just click Ok button on the next dialog.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[27] = QtGui.QApplication.translate("MainDialog", "Pardus installer application could not be found in packages.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[28] = QtGui.QApplication.translate("MainDialog", "Please install Yali by this command 'pisi it -c system.installer' and try again.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[29] = QtGui.QApplication.translate("MainDialog", "Pisi package could not be copied.", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[30] = QtGui.QApplication.translate("MainDialog", "Text file for pisi", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[31] = QtGui.QApplication.translate("MainDialog", "XML File for Pardusman", None, QtGui.QApplication.UnicodeUTF8)
        self.msg[32] = QtGui.QApplication.translate("MainDialog", "File could not be saved.", None, QtGui.QApplication.UnicodeUTF8)
