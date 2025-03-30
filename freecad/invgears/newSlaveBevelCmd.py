# ***************************************************************************
# *   Copyright (c) 2021 Sebastian Ernesto García <sebasg@outlook.com>      *
# *                                                                         *
# *   newSlaveBevelCmd.py                                                   *
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

from PySide6.QtWidgets import QDialogButtonBox

from freecad.invgears.featureClasses import SlaveBevelGear, ViewProviderSlaveBevelGear
from freecad.invgears.observers import SelObserver


class SlaveBevelGearTaskPanel:
    def __init__(self):
        self.form = [Gui.PySideUic.loadUi(f"{os.path.split(__file__)[0]}/Resources/ui/slaves.ui")]
        self.form[0].pushButton.clicked.connect(self.attach_master_gear)
        self.sel_o = SelObserver(self.form[0].pushButton, self.form[0].lineEdit, self.form[0].label_2, True)
        self.attach_master_gear()
    
    def attach_master_gear(self):
        self.form[0].pushButton.setText("Selecting FP_Master_Bevel...")
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

    def getStandardButtons(self):
        return QDialogButtonBox.Cancel | QDialogButtonBox.Ok

    def createInvoluteGears(self):
        part_master, body_master, fp_master = self.sel_o.selection
        for part in part_master.InList:
            if part.Type == "Part_Bevel_Gears":
                part_gears = part
        angle_list = self.form[0].lineEdit_2.text()
        list_s_gear = "[" + angle_list + "]"
        if list_s_gear:
            for angle in eval(list_s_gear):
                part_slave = App.activeDocument().addObject('App::Part','Part_Slave_Bevel')
                part_slave.Type = "Part_Slave_Bevel"
                part_gears.addObject(part_slave)
                body_slave = App.activeDocument().addObject('PartDesign::Body', 'Body_Slave_Bevel')
                part_slave.addObject(body_slave)
                fp_slave = App.activeDocument().addObject("PartDesign::FeaturePython", "FP_Slave_Bevel")
                body_slave.addObject(fp_slave)
                ViewProviderSlaveBevelGear(fp_slave.ViewObject)
                SlaveBevelGear(fp_slave, fp_master, angle)
                App.activeDocument().recompute()

        Gui.SendMsgToActiveView("ViewFit")


class makeSlaveBevelGearCmd():
    def GetResources(self):
        return {"MenuText": "Create Slave Bevel Gear",
                "ToolTip": "Create a new Slave Bevel gear",
                "Pixmap": "slave_bevel_gear"}

    def IsActive(self):
        if App.activeDocument() is None:
            return False
        else:
            return True

    def Activated(self):
        panel = SlaveBevelGearTaskPanel()
        Gui.Control.showDialog(panel)


Gui.addCommand('AddSlaveBevelGear', makeSlaveBevelGearCmd())
