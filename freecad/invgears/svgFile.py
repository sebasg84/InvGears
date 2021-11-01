# ***************************************************************************
# *   Copyright (c) 2021 Sebastian Ernesto García <sebasg@outlook.com>      *
# *                                                                         *
# *   svgFile.py                                                            *
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

from numpy import zeros, linalg, array, sin, cos, dot, pi
from freecad.invgears.gears import inputDataClass, commonData, gearData, mainCalculations, getProfile


def controlPoints(p, t):
    # given the points array p calculate the control points for the cubic Bezier curves
    cp = zeros((2, 2, p.shape[1] - 2))
    for i in range(p.shape[1] - 2):
        diff = p[:, i + 2] - p[:, i]
        # // the left control point
        cpl = p[:, i + 1] - t * diff
        # // the right control point
        cpr = p[:, i + 1] + t * diff
        # // building the control points array
        cp[0, :, i] = cpl
        cp[1, :, i] = cpr
    return cp


def drawBezierCurve(p, x=0.0, y=0.0):
    # size of the tangent
    t = 1 / 5
    cp = controlPoints(p, t)  # // the control points array
    # p[x_or_y, index_point] cp[l_or_r, x_or_y, index_point]
    d = " Q{},{},{},{}\n".format(cp[0, 0, 0] + x, -cp[0, 1, 0] + y, p[0, 1] + x, -p[1, 1] + y)

    if p.shape[1] > 3:
        # // central curves are cubic Bezier
        for i in range(1, p.shape[1] - 2):
            d = d + " C{},{},{},{},{},{}\n".format(cp[1, 0, i - 1] + x, -cp[1, 1, i - 1] + y, cp[0, 0, i] + x, -cp[0, 1, i] + y, p[0, i + 1] + x, -p[1, i + 1] + y)

    #  the first & the last curve are quadratic Bezier
    d = d + " Q{},{},{},{}\n".format(cp[1, 0, -1] + x, -cp[1, 1, -1] + y, p[0, -1] + x, -p[1, -1] + y)

    return d


def drawArc(p, x=0.0, y=0.0):
    r = linalg.norm(p[:, 1])
    d = " A{},{},0,0,1,{},{}\n".format(r, r, p[0, 2] + x, -p[1, 2] + y)
    return d


class GearsInSVG():
    def __init__(self, widget, filename):
        self.m = float(widget.mEdit.text())
        self.phi_s = float(widget.phi_sEdit.text())
        self.N_m = int(widget.N_m_Edit.text())
        self.N_s = int(widget.N_s_Edit.text())
        self.c = float(widget.cEdit.text())
        self.rk = float(widget.rfEdit.text())
        self.deltaCs = float(widget.deltaCEdit.text())
        self.deltatp = float(widget.deltaTpEdit.text())
        self.Bn = float(widget.BnEdit.text())
        self.iL = float(widget.interfEdit.text())
        self.n = int(widget.numPointsEdit.text())
        self.offset_m = float(widget.offset_m_Edit.text())
        self.offset_s = float(widget.offset_s_Edit.text())

        inputData = inputDataClass(self.m, self.phi_s, self.deltaCs, self.c, self.rk, self.Bn, self.iL, self.N_m, self.N_s, self.deltatp, self.n, self.offset_m, self.offset_s)
        cD = commonData()
        gear = gearData()
        pinion = gearData()

        if widget.checkBox.isChecked():
            mainCalculations(inputData, cD, gear, pinion, True)
            cD.C = abs(gear.Rp - pinion.Rp)
            angle = pinion.beta0 - pi + pi / self.N_s
        else:
            mainCalculations(inputData, cD, gear, pinion)
            angle = pinion.beta0

        if not gear.FirstCond:
            App.Console.PrintWarning("WARNING: Undercutting en 1 \n")
        if not pinion.FirstCond:
            App.Console.PrintWarning("WARNING: Undercutting en 2 \n")

        if not gear.SecondCond and gear.FirstCond:
            App.Console.PrintWarning("WARNING: Interference en 1(Second Condition). Reducir rf, Incrementar deltaC o Cambiar valores \n")
        if not pinion.SecondCond and pinion.FirstCond:
            App.Console.PrintWarning("WARNING: Interference en 2(Second Condition). Reducir rf, Incrementar deltaC o Cambiar valores \n")

        if not gear.ThirdCond:
            App.Console.PrintWarning("WARNING: Third Condition. yc1_p = {}. Reducir rf o Cambiar valores \n".format(gear.yc_a))
        if not pinion.ThirdCond:
            App.Console.PrintWarning("WARNING: Third Condition. yc2_p = {}. Reducir rf o Cambiar valores \n".format(pinion.yc_a))

        if not cD.fourthCond:
            App.Console.PrintWarning("WARNING: Fourth Condition. mc = {} < 1.4 \n".format(cD.mc))

        x = 0
        y = 0
        if widget.checkBox.isChecked():
            getProfile(gear, pinion, cD, True)
            r = gear.RTc + float(widget.thicknessEdit.text())
            x = r
            y = r
            circle_svg_path = "M{},{} m{},0 a{},{},0,0,1,{},0 a{},{},0,0,1,{},0\n".format(x, y, -r, r, r, 2 * r, r, r, - 2 * r)
        else:
            getProfile(gear, pinion, cD)
            x = gear.RT
            y = gear.RT
            circle_svg_path = ""

        getProfile(pinion, gear, cD)

        ###############################################################
        ##################Master Gear Shape Creation###################
        ###############################################################
        index = 1
        gear_svg_path = "M{},{}".format(gear.profile[0][0, 0] + x, -gear.profile[0][1, 0] + y)
        for profile in gear.profile:
            if index % 3 == 0:
                gear_svg_path = gear_svg_path + drawArc(profile, x, y)
            else:
                gear_svg_path = gear_svg_path + drawBezierCurve(profile, x, y)
            index = index + 1
        ##############################################################################

        ###############################################################
        ##################Slave Gear Shape Creation####################
        ###############################################################
        index = 1
        x = x + cD.C
        M = array([[cos(angle), -sin(angle)], [sin(angle), cos(angle)]])
        pinion_profile = list(map(lambda x: dot(M, x), pinion.profile))
        pinion_svg_path = "M{},{}".format(pinion_profile[0][0, 0] + x, -pinion_profile[0][1, 0] + y)
        for profile in pinion_profile:
            if index % 3 == 0:
                pinion_svg_path = pinion_svg_path + drawArc(profile, x, y)
            else:
                pinion_svg_path = pinion_svg_path + drawBezierCurve(profile, x, y)
            index = index + 1
        ###############################################################
        if widget.checkBox.isChecked():
            height = 2 * y
            width = height
        else:
            width = cD.C + gear.RT + pinion.RT
            height = 2 * gear.RT
        svg_string = '<?xml version="1.0" standalone="no"?>\n' +\
                    '<svg xmlns="http://www.w3.org/2000/svg"\n' +\
                    'version="1.1" width="{}mm" height="{}mm">\n'.format(width, height) +\
                    '<g transform="scale(3.78)">\n' +\
                    '<path d="' + circle_svg_path + gear_svg_path + '" fill="rgb(210, 130, 50)" />\n' +\
                    '<path d="' + pinion_svg_path + '" fill="rgb(50, 130, 210)" />\n' +\
                    '</g>' +\
                    '</svg>\n'

        f = open(filename, "w")
        f.write(svg_string)
        f.close()
