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

from freecad.invgears import local
from freecad.invgears.svgFile import GearsInSVG
from freecad.invgears.widgets import GearWidget
from freecad.invgears.observers import SelObserver


class createInvoluteGears5():
    def __init__(self, widget, filename):
        GearsInSVG(widget, filename)
        Gui.SendMsgToActiveView("ViewFit")


class GearsInSVGTaskPanel:
    def __init__(self):
        self.form = GearWidget("SVG", self.attach_master_gear, self.load_paramers)
        print(type(self))
        self.master_gear_Button = self.form.master_gear_Button
        self.master_gear_Edit = self.form.master_gear_Edit
        self.print_warnings = self.form.print_warnings
        self.sel_o = SelObserver(self.master_gear_Button, self.master_gear_Edit, self.print_warnings)

        self.master_gear_Button.setText("Press to Select a master gear")

    def attach_master_gear(self):
        self.master_gear_Button.setText("Selecting master gear...")
        self.master_gear_Button.setEnabled(False)
        self.sel_o.addSelection(0, 0, 0, 0)

    def load_paramers(self):
        print("load Parametrs")
        fp_master = self.sel_o.selection
        widget = self.form
        widget.mEdit.setText(str(round(fp_master.m.Value, 4)))
        widget.phi_sEdit.setText(str(round(fp_master.phi_s.Value, 4)))
        widget.N_m_Edit.setText(str(fp_master.m_N))
        widget.N_s_Edit.setText(str(fp_master.s_N))
        widget.cEdit.setText(str(round(fp_master.c, 4)))
        widget.rfEdit.setText(str(round(fp_master.rk, 4)))
        widget.deltaCEdit.setText(str(round(fp_master.deltaCs.Value, 4)))
        widget.deltaTpEdit.setText(str(round(fp_master.deltatp.Value, 4)))
        widget.BnEdit.setText(str(round(fp_master.Bn.Value, 4)))
        widget.interfEdit.setText(str(round(fp_master.iL, 4)))
        widget.numPointsEdit.setText(str(round(fp_master.n, 4)))
        widget.offset_m_Edit.setText(str(round(fp_master.m_offset.Value, 4)))
        widget.offset_s_Edit.setText(str(round(fp_master.s_offset.Value, 4)))
        if fp_master.Proxy.Type == 'internalGear':
            widget.checkBox.setChecked(True)
            widget.thicknessEdit.setText(str(round(fp_master.thickness.Value, 4)))
        else:
            widget.checkBox.setChecked(False)

    def accept(self):
        if self.form.checkBox.isChecked():
            N_m = self.form.N_m_Edit.text()
            N_s = self.form.N_s_Edit.text()
            if N_s >= N_m:
                self.form.print_warnings.setText("Number of master gear teeth must be greater than Number of slave gear teeth")
            else:
                filename, filter = QFileDialog.getSaveFileName(self.form, "Save Gears in SVG file", ".", "SVG files (*.svg)")
                if filename:
                    createInvoluteGears5(self.form, filename)
                    Gui.Selection.removeObserver(self.sel_o)
                    Gui.Control.closeDialog()
        else:
            filename, filter = QFileDialog.getSaveFileName(self.form, "Save Gears in SVG file", ".", "SVG files (*.svg)")
            if filename:
                createInvoluteGears5(self.form, filename)
                Gui.Selection.removeObserver(self.sel_o)
                Gui.Control.closeDialog()

    def reject(self):
        Gui.Selection.removeObserver(self.sel_o)
        Gui.Control.closeDialog()

    def getStandardButtons(self):
        return QDialogButtonBox.Cancel | QDialogButtonBox.Ok


class makeGearsInSVGCmd():
    def GetResources(self):
        return {"MenuText": "Create Gears in SVG file",
                "ToolTip": "Create a new Gears in SVG file",
                "Pixmap": local.path() + "/Resources/icons/SVG_gears.svg"}

    def IsActive(self):
        if App.activeDocument() is None:
            return False
        else:
            return True

    def Activated(self):
        panel = GearsInSVGTaskPanel()
        Gui.Control.showDialog(panel)


Gui.addCommand('CreateGearsInSVG', makeGearsInSVGCmd())
