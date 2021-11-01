# ***************************************************************************
# *   Copyright (c) 2021 Sebastian Ernesto García <sebasg@outlook.com>      *
# *                                                                         *
# *   InitGui.py                                                            *
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
import FreeCAD as App
from . import InvGears_rc


class InvGears(Gui.Workbench):
    def __init__(self):
        from freecad.invgears import local
        self.__class__.Icon = local.path() + "/Resources/icons/master_gear.svg"
        self.__class__.MenuText = "InvGears"
        self.__class__.ToolTip = "InvGears workbench"

    def Initialize(self):
        from freecad.invgears import newMasterCmd
        from freecad.invgears import newSlaveCmd
        from freecad.invgears import newSlaveMasterCmd
        from freecad.invgears import newInternalCmd
        from freecad.invgears import newSVGCmd
        from freecad.invgears import newAnimatorCmd

        self.list_commands = ["CreateMasterGear", "AddSlaveGear", "AddSlaveMasterGear", "CreateInternalGear", "CreateGearsInSVG", "Animator"]

        self.appendToolbar("Involute Gears", self.list_commands)  # creates a new toolbar with your commands
        self.appendMenu("Involute Gears", self.list_commands)  # creates a new menu
        # self.appendMenu(["An existing Menu","My submenu"],self.list)  # appends a submenu to an existing menu
        App.Console.PrintLog("Loading InvGears... done\n")

    def Activated(self):
        App.Console.PrintMessage("InvGears.Activated()\n")

    def Deactivated(self):
        App.Console.PrintMessage("InvGears.Deactivated()\n")

    def ContextMenu(self, recipient):
        self.appendContextMenu("Involute Gears", self.list_commands)  # add commands to the context menu

    def GetClassName(self):
        return "Gui::PythonWorkbench"


Gui.addWorkbench(InvGears())
