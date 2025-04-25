# ***************************************************************************
# *   Copyright (c) 2021 Sebastian Ernesto García <sebasg@outlook.com>      *
# *                                                                         *
# *   newSlaveMasterCmd.py                                                  *
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
import os
from PySide.QtWidgets import QDialogButtonBox

from freecad.invgears.featureClasses import SlaveMasterGear, ViewProviderSlaveMasterGear
from freecad.invgears.observers import SelObserver


class SlaveMasterGearTaskPanel:
    def __init__(self):
        widget1 = Gui.PySideUic.loadUi(f"{os.path.split(__file__)[0]}/Resources/ui/slaves.ui")
        widget1.label.setText("Angular locations of slave-master gears")
        widget2 = Gui.PySideUic.loadUi(f"{os.path.split(__file__)[0]}/Resources/ui/separator.ui")
        widget3 = Gui.PySideUic.loadUi(f"{os.path.split(__file__)[0]}/Resources/ui/gears.ui")
        widget4 = Gui.PySideUic.loadUi(f"{os.path.split(__file__)[0]}/Resources/ui/additional.ui")
        self.form = [widget1, widget2, widget3, widget4]
        self.form[2].comboBox.currentIndexChanged.connect(self.onChanged)
        self.form[2].label_9.hide()
        self.form[2].doubleSpinBox_6.hide()
        self.form[2].label_10.hide()
        self.form[2].lineEdit.hide()
        self.form[2].label_13.hide()
        self.form[2].checkBox.hide()
        self.form[2].label_11.hide()
        self.form[2].doubleSpinBox_7.hide()

        self.sel_o = SelObserver(self.form[0].pushButton, self.form[0].lineEdit, self.form[0].label_2)
        self.attach_master_gear()

    def attach_master_gear(self):
        self.form[0].pushButton.setText("Selecting fp_master...")
        self.form[0].pushButton.setEnabled(False)
        self.sel_o.addSelection(0, 0, 0, 0)

    def accept(self):
        angle_list = self.form[0].lineEdit_2.text()
        if not self.sel_o.sel_flag:
            self.form[0].label_2.setText("First you have to choose a master gear and then click on ok.")
        elif not angle_list:
            self.form[0].label_2.setText("First you have to put angular locations and then click on ok.")
        else:
            self.createInvoluteGears()
            Gui.Selection.removeObserver(self.sel_o)
            Gui.Control.closeDialog()

    def reject(self):
        Gui.Selection.removeObserver(self.sel_o)
        Gui.Control.closeDialog()

    def open(self):
        self.form[3].parent().hide()

    def getStandardButtons(self):
        return QDialogButtonBox.Cancel | QDialogButtonBox.Ok

    def onChanged(self, index):
        if index == 0:
            self.form[2].doubleSpinBox_4.setEnabled(False)
        else:
            self.form[2].doubleSpinBox_4.setEnabled(True)

    def createInvoluteGears(self):
        part_master, body_master, fp_master = self.sel_o.selection
        for part in part_master.InList:
            if part.Type == "Part_Gears":
                part_gears = part
        angle_list = self.form[0].lineEdit_2.text()
        list_s_gear = "[" + angle_list + "]"
        if list_s_gear:
            for angle in eval(list_s_gear):
                part_slave_master = App.activeDocument().addObject('App::Part','Part_Slave_Master')
                part_slave_master.Type = "Part_Slave_Master"
                part_gears.addObject(part_slave_master)
                part_slave_master.addProperty('App::PropertyAngle', 'slaveAngularPosition', 'Gear control', 'Slave angular position')
                body_slave_master = App.activeDocument().addObject('PartDesign::Body', 'Body_Slave_Master')
                part_slave_master.addObject(body_slave_master)
                fp_slave_master = App.activeDocument().addObject("PartDesign::FeaturePython", "FP_Slave_Master")
                body_slave_master.addObject(fp_slave_master)
                ViewProviderSlaveMasterGear(fp_slave_master.ViewObject)
                SlaveMasterGear(fp_slave_master, fp_master, self.form, angle)
                App.activeDocument().recompute()

        Gui.SendMsgToActiveView("ViewFit")


class makeSlaveMasterGearCmd():
    def GetResources(self):
        return {"MenuText": "Add Slave-Master Gear",
                "ToolTip": "Add a new slave-master gear",
                "Pixmap": "slave-master_gear"}

    def IsActive(self):
        if App.activeDocument() is None:
            return False
        else:
            return True

    def Activated(self):
        panel = SlaveMasterGearTaskPanel()
        Gui.Control.showDialog(panel)


Gui.addCommand('AddSlaveMasterGear', makeSlaveMasterGearCmd())
