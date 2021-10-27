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


class InvGears(Workbench):
    def __init__(self):
        import local
        self.__class__.Icon = local.path() + "/Resources/icons/master_gear.svg"
        self.__class__.MenuText = "InvGears"
        self.__class__.ToolTip = "InvGears workbench"

    def Initialize(self):
        import newMasterCmd
        import newSlaveCmd
        import newSlaveMasterCmd
        import newInternalCmd
        import newSVGCmd

        self.list_commands = ["CreateMasterGear", "AddSlaveGear", "AddSlaveMasterGear", "CreateInternalGear", "CreateGearsInSVG"]

        self.appendToolbar("Involute Gears", self.list_commands)  # creates a new toolbar with your commands
        self.appendMenu("Involute Gears", self.list_commands)  # creates a new menu
        # self.appendMenu(["An existing Menu","My submenu"],self.list)  # appends a submenu to an existing menu
        Log("Loading InvGears... done\n")

    def Activated(self):
        Msg("InvGears.Activated()\n")

    def Deactivated(self):
        Msg("InvGears.Deactivated()\n")

    def ContextMenu(self, recipient):
        self.appendContextMenu("Involute Gears", self.list_commands)  # add commands to the context menu

    def GetClassName(self):
        return "Gui::PythonWorkbench"


Gui.addWorkbench(InvGears())
