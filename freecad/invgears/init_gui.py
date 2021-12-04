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
from . import rc_invGears

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
        from freecad.invgears import newMasterBevelCmd
        from freecad.invgears import newSlaveBevelCmd
        from freecad.invgears import newAnimatorCmd
        from freecad.invgears import newSVGCmd

        self.list_commands = ["CreateMasterGear", "AddSlaveGear", "AddSlaveMasterGear", "CreateInternalGear", "CreateMasterBevelGear", "AddSlaveBevelGear", "Animator", "CreateGearsInSVG"]

        self.appendToolbar("Involute Gears", self.list_commands)
        self.appendMenu("Involute Gears", self.list_commands)
        App.Console.PrintLog("Loading InvGears... done\n")

    def Activated(self):
        App.Console.PrintMessage("InvGears.Activated()\n")

    def Deactivated(self):
        App.Console.PrintMessage("InvGears.Deactivated()\n")

    def ContextMenu(self, recipient):
        self.appendContextMenu("Involute Gears", self.list_commands)

    def GetClassName(self):
        return "Gui::PythonWorkbench"


Gui.addWorkbench(InvGears())
