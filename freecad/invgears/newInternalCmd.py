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

from PySide2.QtWidgets import QDialogButtonBox

from freecad.invgears import local
from freecad.invgears.featureClasses import InternalGear, SlaveGear, ViewProviderInternalGear, ViewProviderSlaveGear
from freecad.invgears.widgets import GearWidget


class createInvoluteGears4():
    def __init__(self, widget):

        body_internal = App.activeDocument().addObject('PartDesign::Body', 'body_internal')
        fp_internal = App.activeDocument().addObject("PartDesign::FeaturePython", "fp_internal")
        ViewProviderInternalGear(fp_internal.ViewObject)
        InternalGear(fp_internal, body_internal, widget)
        App.activeDocument().recompute()

        list_s_gear = "[" + widget.list_angular_s_Edit.text() + "]"
        if list_s_gear:
            for item in eval(list_s_gear):
                body_slave = App.activeDocument().addObject('PartDesign::Body', 'body_slave')
                fp_slave = App.activeDocument().addObject("PartDesign::FeaturePython", "fp_slave")
                ViewProviderSlaveGear(fp_slave.ViewObject)
                SlaveGear(fp_slave, body_slave, fp_internal, item)
                App.activeDocument().recompute()

        Gui.SendMsgToActiveView("ViewFit")


class InternalGearTaskPanel:
    def __init__(self):
        self.form = GearWidget("Internal")
        print(type(self))

    def accept(self):
        N_m = self.form.N_m_Edit.text()
        N_s = self.form.N_s_Edit.text()
        if N_s >= N_m:
            self.form.print_warnings.setText("Number of master gear teeth must be greater than Number of slave gear teeth")
        else:
            createInvoluteGears4(self.form)
            Gui.Control.closeDialog()

    def reject(self):
        Gui.Control.closeDialog()

    def getStandardButtons(self):
        return QDialogButtonBox.Cancel | QDialogButtonBox.Ok


class makeInternalGearCmd():
    def GetResources(self):
        return {"MenuText": "Create Internal Gear",
                "ToolTip": "Create a new internal gear",
                "Pixmap": local.path() + "/Resources/icons/internal_gear.svg"}

    def IsActive(self):
        if App.activeDocument() is None:
            return False
        else:
            return True

    def Activated(self):
        panel = InternalGearTaskPanel()
        Gui.Control.showDialog(panel)


Gui.addCommand('CreateInternalGear', makeInternalGearCmd())
