# ***************************************************************************
# *   Copyright (c) 2021 Sebastian Ernesto García <sebasg@outlook.com>      *
# *                                                                         *
# *   newInternalCmd.py                                                     *
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
from PySide2.QtWidgets import QDialogButtonBox

from freecad.invgears.featureClasses import InternalGear, SlaveGear, ViewProviderInternalGear, ViewProviderSlaveGear


class InternalGearTaskPanel:
    def __init__(self):
        widget1 = Gui.PySideUic.loadUi(f"{os.path.split(__file__)[0]}/Resources/ui/gears.ui")
        widget2 = Gui.PySideUic.loadUi(f"{os.path.split(__file__)[0]}/Resources/ui/additional.ui")
        self.form = [widget1, widget2]
        self.form[0].doubleSpinBox_4.setEnabled(False)
        self.form[0].comboBox.currentIndexChanged.connect(self.onChanged)
        self.form[0].label_9.hide()
        self.form[0].doubleSpinBox_6.hide()
        self.form[0].label_13.hide()
        self.form[0].checkBox.hide()
        self.form[0].spinBox.setValue(40)
        self.form[0].spinBox_2.setValue(16)

    def accept(self):
        N_m = self.form[0].spinBox.value()
        N_s = self.form[0].spinBox_2.value()
        if N_s >= N_m:
            self.form[0].label_12.setText("Number of master gear teeth must be greater than Number of slave gear teeth")
        else:
            self.createInvoluteGears()
            Gui.Control.closeDialog()

    def reject(self):
        Gui.Control.closeDialog()
    
    def open(self):
        self.form[1].parent().hide()

    def getStandardButtons(self):
        return QDialogButtonBox.Cancel | QDialogButtonBox.Ok

    def onChanged(self, index):
        if index == 0:
            self.form[0].doubleSpinBox_4.setEnabled(False)
        else:
            self.form[0].doubleSpinBox_4.setEnabled(True)
    
    def createInvoluteGears(self):
        part_gears = App.activeDocument().addObject('App::Part','Part_Gears')
        part_gears.Type = "Part_Gears"
        part_internal = App.activeDocument().addObject('App::Part','Part_Internal')
        part_internal.Type = "Part_Internal"
        part_gears.addObject(part_internal)
        part_internal.addProperty('App::PropertyAngle', 'masterRotation', 'Gear control', 'Master rotation')
        part_internal.setExpression("Placement", f"create(<<placement>>; create(<<vector>>; 0; 0; 0); create(<<rotation>>; create(<<vector>>; 0; 0; 1); {part_internal.Name}.masterRotation))")
        part_internal.addProperty('App::PropertyAngle', 'slaveAngularPosition', 'Gear control', 'Slave angular position')
        body_internal = App.activeDocument().addObject('PartDesign::Body', 'Body_Internal')
        part_internal.addObject(body_internal)
        fp_internal = App.activeDocument().addObject("PartDesign::FeaturePython", "FP_Internal")
        body_internal.addObject(fp_internal)
        ViewProviderInternalGear(fp_internal.ViewObject)
        InternalGear(fp_internal, self.form)
        App.activeDocument().recompute()

        list_s_gear = "[" + self.form[0].lineEdit.text() + "]"
        if list_s_gear:
            for angle in eval(list_s_gear):
                part_slave = App.activeDocument().addObject('App::Part','Part_Slave')
                part_slave.Type = "Part_Slave"
                part_gears.addObject(part_slave)
                body_slave = App.activeDocument().addObject('PartDesign::Body', 'Body_Slave')
                part_slave.addObject(body_slave)
                fp_slave = App.activeDocument().addObject("PartDesign::FeaturePython", "FP_Slave")
                body_slave.addObject(fp_slave)
                ViewProviderSlaveGear(fp_slave.ViewObject)
                SlaveGear(fp_slave, fp_internal, angle)
                App.activeDocument().recompute()

        Gui.SendMsgToActiveView("ViewFit")


class makeInternalGearCmd():
    def GetResources(self):
        return {"MenuText": "Create Internal Gear",
                "ToolTip": "Create a new internal gear",
                "Pixmap": "internal_gear"}

    def IsActive(self):
        if App.activeDocument() is None:
            return False
        else:
            return True

    def Activated(self):
        panel = InternalGearTaskPanel()
        Gui.Control.showDialog(panel)


Gui.addCommand('CreateInternalGear', makeInternalGearCmd())
