# ***************************************************************************
# *   Copyright (c) 2021 Sebastian Ernesto García <sebasg@outlook.com>      *
# *                                                                         *
# *   newSVGCmd.py                                                          *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Lesser General Public License for more details.                   *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

import FreeCAD as App
import FreeCADGui as Gui

from PySide2.QtWidgets import QDialogButtonBox, QFileDialog

from freecad.invgears.svgFile import GearsInSVG
from freecad.invgears.observers import SelObserver


class GearsInSVGTaskPanel:
    def __init__(self):
        widget1 = Gui.PySideUic.loadUi(f"{os.path.split(__file__)[0]}/Resources/ui/loadParameters.ui")
        widget2 = Gui.PySideUic.loadUi(f"{os.path.split(__file__)[0]}/Resources/ui/gears.ui")
        widget3 = Gui.PySideUic.loadUi(f"{os.path.split(__file__)[0]}/Resources/ui/additional.ui")
        self.form = [widget1, widget2, widget3]
        self.form[0].pushButton.clicked.connect(self.attach_master_gear)
        self.form[0].pushButton_2.clicked.connect(self.load_paramers)
        self.form[1].checkBox.stateChanged.connect(self.onStatusChanged)
        self.form[1].doubleSpinBox_7.setEnabled(False)
        self.form[1].label_9.hide()
        self.form[1].doubleSpinBox_6.hide()
        self.form[1].label_10.hide()
        self.form[1].lineEdit.hide()
        
        self.sel_o = SelObserver(self.form[0].pushButton, self.form[0].lineEdit, self.form[0].label)

        self.form[0].pushButton.setText("Press to Select a master gear")

    def attach_master_gear(self):
        self.form[0].pushButton.setText("Selecting fp_master...")
        self.form[0].pushButton.setEnabled(False)
        self.sel_o.addSelection(0, 0, 0, 0)

    def load_paramers(self):
        part_master, body_master, fp_master = self.sel_o.selection
        self.form[1].doubleSpinBox.setValue(fp_master.m.Value)
        self.form[1].doubleSpinBox_2.setValue(fp_master.phi_s.Value)
        self.form[1].spinBox.setValue(fp_master.N_m)
        self.form[1].spinBox_2.setValue(fp_master.N_s)
        self.form[1].doubleSpinBox_3.setValue(fp_master.Bl.Value)
        if fp_master.Proxy.Type == 'internalGear':
            self.form[1].checkBox.setChecked(True)
            self.form[1].doubleSpinBox_7.setValue(fp_master.extThickness.Value)
        else:
            self.form[1].checkBox.setChecked(False)

        self.form[2].doubleSpinBox.setValue(fp_master.c)
        self.form[2].doubleSpinBox_2.setValue(fp_master.deltaCs.Value)
        self.form[2].doubleSpinBox_3.setValue(fp_master.deltatp.Value)
        self.form[2].doubleSpinBox_4.setValue(fp_master.offset_m.Value)
        self.form[2].doubleSpinBox_5.setValue(fp_master.offset_s.Value)
        self.form[2].spinBox.setValue(fp_master.n)
        self.form[2].doubleSpinBox_6.setValue(fp_master.iL)

    def accept(self):
        if self.form[1].checkBox.isChecked():
            N_m = self.form[1].spinBox.value()
            N_s = self.form[1].spinBox_2.value()
            if N_s >= N_m:
                self.form[1].label_12.setText("Number of master gear teeth must be greater than Number of slave gear teeth")
            else:
                self.filename, filter = QFileDialog.getSaveFileName(self.form[1], "Save Gears in SVG file", ".", "SVG files (*.svg)")
                if self.filename:
                    self.createInvoluteGears()
                    Gui.Selection.removeObserver(self.sel_o)
                    Gui.Control.closeDialog()
        else:
            self.filename, filter = QFileDialog.getSaveFileName(self.form[1], "Save Gears in SVG file", ".", "SVG files (*.svg)")
            if self.filename:
                self.createInvoluteGears()
                Gui.Selection.removeObserver(self.sel_o)
                Gui.Control.closeDialog()

    def reject(self):
        Gui.Selection.removeObserver(self.sel_o)
        Gui.Control.closeDialog()
    
    def open(self):
        self.form[2].parent().hide()

    def getStandardButtons(self):
        return QDialogButtonBox.Cancel | QDialogButtonBox.Ok

    def onStatusChanged(self, state):
        if state == 0:
            self.form[1].doubleSpinBox_7.setEnabled(False)
        else:
            self.form[1].doubleSpinBox_7.setEnabled(True)

    def createInvoluteGears(self):
        GearsInSVG(self.form, self.filename)
        Gui.SendMsgToActiveView("ViewFit")


class makeGearsInSVGCmd():
    def GetResources(self):
        return {"MenuText": "Create Gears in SVG file",
                "ToolTip": "Create a new Gears in SVG file",
                "Pixmap": "SVG_gears"}

    def IsActive(self):
        if App.activeDocument() is None:
            return False
        else:
            return True

    def Activated(self):
        panel = GearsInSVGTaskPanel()
        Gui.Control.showDialog(panel)


Gui.addCommand('CreateGearsInSVG', makeGearsInSVGCmd())
