# ***************************************************************************
# *   Copyright (c) 2021 Sebastian Ernesto García <sebasg@outlook.com>      *
# *                                                                         *
# *   newMasterCmd.py                                                       *
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
from freecad.invgears.animator import Animator, AnimatorVP
from freecad.invgears.widgets import GearWidget


class makeAnimatorCmd():
    def GetResources(self):
        return {"MenuText": "Create an Animator",
                "ToolTip": "Create a new animator",
                "Pixmap": local.path() + "/Resources/icons/Animator.svg"}

    def IsActive(self):
        if App.activeDocument() is None:
            return False
        else:
            return True

    def Activated(self):
        fp = App.activeDocument().addObject("App::FeaturePython","Animator")
        Animator(fp)
        AnimatorVP(fp.ViewObject)
        fp.Proxy.setupVariables(fp)


Gui.addCommand('Animator', makeAnimatorCmd())
