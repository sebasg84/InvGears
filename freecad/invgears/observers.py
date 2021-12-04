# ***************************************************************************
# *   Copyright (c) 2021 Sebastian Ernesto García <sebasg@outlook.com>      *
# *                                                                         *
# *   observers.py                                                            *
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

import FreeCADGui as Gui


class SelObserver:
    def __init__(self, button, lineEdit, print_warnings, bevel=False):
        self.button = button
        self.lineEdit = lineEdit
        self.print_warnings = print_warnings
        self.sel_flag = False
        self.bevel = bevel

    def addSelection(self, doc, obj, sub, pnt):
        selection = Gui.Selection.getSelection()

        if (len(selection) >= 1):
            if (len(selection) > 1):
                self.print_warnings.setText("Selection error: You must choose only one part")
                self.button.setText("Select a Part")
            else:
                part = selection[0]
                if part.TypeId == 'App::Part':
                    bodies = part.Group
                    for body in bodies:
                        if body.TypeId == 'PartDesign::Body':
                            fps = body.Group
                            for fp in fps:
                                if fp.TypeId == 'PartDesign::FeaturePython':
                                    if (((fp.Proxy.Type == "masterGear" or fp.Proxy.Type == "slaveMasterGear" or fp.Proxy.Type == "internalGear") and not self.bevel)
                                        or (fp.Proxy.Type == "masterBevelGear" and self.bevel)):
                                        self.print_warnings.setText("Selection successfully completed")
                                        self.button.setText("Part selected")
                                        self.lineEdit.setText(fp.Name)
                                        self.selection = [part, body, fp]
                                        self.sel_flag = True
                                    else:
                                        self.print_warnings.setText("Selection error: Choose a part that contains a master gear")
                                        self.button.setText("Select a Part")
                                else:
                                    self.print_warnings.setText("Selection error: Choose a part that contains a master gear")
                                    self.button.setText("Select a Part")

            self.button.setEnabled(True)
            Gui.Selection.removeObserver(self)
        else:
            Gui.Selection.addObserver(self)
