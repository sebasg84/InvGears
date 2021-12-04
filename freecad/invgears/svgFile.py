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
    def __init__(self, form, filename):
        m = form[1].doubleSpinBox.value()
        phi_s = form[1].doubleSpinBox_2.value()
        N_m = form[1].spinBox.value()
        N_s = form[1].spinBox_2.value()
        Bl = form[1].doubleSpinBox_3.value()

        c = form[2].doubleSpinBox.value()
        deltaCs = form[2].doubleSpinBox_2.value()
        deltatp = form[2].doubleSpinBox_3.value()
        offset_m = form[2].doubleSpinBox_4.value()
        offset_s = form[2].doubleSpinBox_5.value()
        n = form[2].spinBox.value()
        iL = form[2].doubleSpinBox_6.value()

        inputData = inputDataClass(m, phi_s, N_m, N_s, Bl, c, deltaCs, deltatp, offset_m, offset_s, n, iL)
        cD = commonData()
        master = gearData()
        slave = gearData()

        
        if form[1].checkBox.isChecked():
            mainCalculations(inputData, cD, master, slave, True)
            cD.C = abs(master.Rp - slave.Rp)
            angle = slave.beta0 - pi + pi / N_s
        else:
            mainCalculations(inputData, cD, master, slave)
            angle = slave.beta0

        if not master.FirstCond:
            App.Console.PrintWarning("WARNING: Undercutting en 1 \n")
        if not slave.FirstCond:
            App.Console.PrintWarning("WARNING: Undercutting en 2 \n")

        if not master.SecondCond and master.FirstCond:
            App.Console.PrintWarning("WARNING: Interference en 1(Second Condition). Reducir rf, Incrementar deltaC o Cambiar valores \n")
        if not slave.SecondCond and slave.FirstCond:
            App.Console.PrintWarning("WARNING: Interference en 2(Second Condition). Reducir rf, Incrementar deltaC o Cambiar valores \n")

        if not master.ThirdCond:
            App.Console.PrintWarning("WARNING: Third Condition. master.tita_Tc = {}. Reducir rf o Cambiar valores \n".format(master.tita_Tc))
        if not slave.ThirdCond:
            App.Console.PrintWarning("WARNING: Third Condition. slave.tita_Tc = {}. Reducir rf o Cambiar valores \n".format(slave.tita_Tc))

        if not cD.fourthCond:
            App.Console.PrintWarning("WARNING: Fourth Condition. mc = {} < 1.4 \n".format(cD.mc))

        x = 0
        y = 0
        if form[1].checkBox.isChecked():
            getProfile(master, slave, cD, True)
            r = master.RTc + form[1].doubleSpinBox_7.value()
            x = r
            y = r
            circle_svg_path = "M{},{} m{},0 a{},{},0,0,1,{},0 a{},{},0,0,1,{},0\n".format(x, y, -r, r, r, 2 * r, r, r, - 2 * r)
        else:
            getProfile(master, slave, cD)
            x = master.RT
            y = master.RT
            circle_svg_path = ""

        getProfile(slave, master, cD)

        ###############################################################
        ##################Master Gear Shape Creation###################
        ###############################################################
        index = 1
        master_svg_path = "M{},{}".format(master.profile[0][0, 0] + x, -master.profile[0][1, 0] + y)
        for profile in master.profile:
            if index % 3 == 0:
                master_svg_path = master_svg_path + drawArc(profile, x, y)
            else:
                master_svg_path = master_svg_path + drawBezierCurve(profile, x, y)
            index = index + 1
        ##############################################################################

        ###############################################################
        ##################Slave Gear Shape Creation####################
        ###############################################################
        index = 1
        x = x + cD.C
        M = array([[cos(angle), -sin(angle)], [sin(angle), cos(angle)]])
        slave_profile = list(map(lambda x: dot(M, x), slave.profile))
        slave_svg_path = "M{},{}".format(slave_profile[0][0, 0] + x, -slave_profile[0][1, 0] + y)
        for profile in slave_profile:
            if index % 3 == 0:
                slave_svg_path = slave_svg_path + drawArc(profile, x, y)
            else:
                slave_svg_path = slave_svg_path + drawBezierCurve(profile, x, y)
            index = index + 1
        ###############################################################
        if form[1].checkBox.isChecked():
            height = 2 * y
            width = height
        else:
            width = cD.C + master.RT + slave.RT
            height = 2 * master.RT
        svg_string = '<?xml version="1.0" standalone="no"?>\n' +\
                    '<svg xmlns="http://www.w3.org/2000/svg"\n' +\
                    'version="1.1" width="{}mm" height="{}mm">\n'.format(width, height) +\
                    '<g transform="scale(3.78)">\n' +\
                    '<path d="' + circle_svg_path + master_svg_path + '" style="fill:none;fill-opacity:1;stroke-width:0.2;stroke:#000000;stroke-opacity:1;stroke-miterlimit:4" />\n' +\
                    '<path d="' + slave_svg_path + '" style="fill:none;fill-opacity:1;stroke-width:0.2;stroke:#000000;stroke-opacity:1;stroke-miterlimit:4" />\n' +\
                    '</g>' +\
                    '</svg>\n'

        f = open(filename, "w")
        f.write(svg_string)
        f.close()
