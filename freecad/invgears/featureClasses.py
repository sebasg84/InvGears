# ***************************************************************************
# *   Copyright (c) 2021 Sebastian Ernesto García <sebasg@outlook.com>      *
# *                                                                         *
# *   featureClasses.py                                                     *
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
from Part import BSplineCurve, Wire, Arc, Face, makeShell, makeSolid, makeCylinder
from freecad.invgears import local
from numpy import pi, sin, cos
from freecad.invgears.gears import inputDataClass, commonData, gearData, mainCalculations, getProfile
from freecad.invgears.functions import loadProperties, commonextrusion, helicalextrusion, doblehelicalextrusion


def getInternalShape(fp, W, z=0.0, tita=0.0):
    height = fp.height.Value
    if fp.gearType == "Spur":
        Solid = commonextrusion(W, height, App.Vector(0, 0, z), tita)
    if fp.gearType == "Helical":
        helicalAngle = - fp.helicalPortion * (2 * pi / fp.m_N)
        Solid = helicalextrusion(W, height, helicalAngle, App.Vector(0, 0, z), tita)
    if fp.gearType == "DobleHelical":
        helicalAngle = - fp.helicalPortion * (2 * pi / fp.m_N)
        Solid = doblehelicalextrusion(W, height, helicalAngle, App.Vector(0, 0, z), tita)
    return Solid


def getMasterShape(fp, W, z=0.0, tita=0.0):
    height = fp.height.Value
    if fp.gearType == "Spur":
        Solid = commonextrusion(W, height, App.Vector(0, 0, z), tita)
    if fp.gearType == "Helical":
        helicalAngle = fp.helicalPortion * (2 * pi / fp.m_N)
        Solid = helicalextrusion(W, height, helicalAngle, App.Vector(0, 0, z), tita)
    if fp.gearType == "DobleHelical":
        helicalAngle = fp.helicalPortion * (2 * pi / fp.m_N)
        Solid = doblehelicalextrusion(W, height, helicalAngle, App.Vector(0, 0, z), tita)
    return Solid


def getSlaveShape(fp_master):
    height = fp_master.height.Value
    W = fp_master.W_p.copy()
    if fp_master.gearType == "Spur":
        Solid = commonextrusion(W, height)
    if fp_master.gearType == "Helical":
        helicalAngle = -fp_master.helicalPortion * (2 * pi / fp_master.s_N)
        Solid = helicalextrusion(W, height, helicalAngle)
    if fp_master.gearType == "DobleHelical":
        helicalAngle = -fp_master.helicalPortion * (2 * pi / fp_master.s_N)
        Solid = doblehelicalextrusion(W, height, helicalAngle)
    return Solid


def getWire(gear):
    S = []
    index = 1
    for profile in gear.profile:
        if index % 3 == 0:
            arc = Arc(*list(map(lambda x, y: App.Vector(x, y, 0.0), profile[0, :], profile[1, :])))
            S.append(arc.toShape())
        else:
            curve = BSplineCurve()
            curve.interpolate(list(map(lambda x, y: App.Vector(x, y, 0.0), profile[0, :], profile[1, :])))
            S.append(curve.toShape())
        index = index + 1
    W = Wire(S)
    return W


def updatePosition(fp):
    fp_master = fp.fp_master
    C = fp_master.C.Value
    Base = fp.body_master.Placement.Base
    positionAngle = fp.positionAngle.Value
    Angle = fp.body_master.Placement.Rotation.Angle * 180 / pi
    s_angle = fp_master.s_angle.Value

    x = Base.x + C * cos(positionAngle * pi / 180)
    y = Base.y + C * sin(positionAngle * pi / 180)
    if hasattr(fp_master, "hseparator"):
        slave_height = fp_master.fp_master.height.Value
        if fp_master.hseparator.Value < 0.0:
            verticalPosition = fp_master.hseparator.Value - fp_master.height.Value
        else:
            verticalPosition = slave_height + fp_master.hseparator.Value
        z = Base.z + verticalPosition
    else:
        z = Base.z

    if fp_master.Proxy.Type == "internalGear":
        if hasattr(fp_master, "tita"):
            angle = s_angle + positionAngle + (- positionAngle - fp_master.tita.Value + Angle) * (fp_master.m_N / fp_master.s_N)
        else:
            angle = s_angle + positionAngle + (- positionAngle + Angle) * (fp_master.m_N / fp_master.s_N)
    else:
        if hasattr(fp_master, "tita"):
            angle = s_angle + positionAngle + (positionAngle - fp_master.tita.Value - Angle) * (fp_master.m_N / fp_master.s_N)
        else:
            angle = s_angle + positionAngle + (positionAngle - Angle) * (fp_master.m_N / fp_master.s_N)

    fp._Body.Placement = App.Placement(App.Vector(x, y, z), App.Rotation(App.Vector(0, 0, 1), angle))


class ViewProviderInternalGear():
    def __init__(self, obj):
        ''' Set this object to the proxy object of the actual view provider '''
        obj.Proxy = self

    def attach(self, vobj):
        self.vobj = vobj

    def getIcon(self):
        return ":/icons/internal_gear.svg"

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


class InternalGear():

    def __init__(self, fp, body, widget):
        self.Type = 'internalGear'
        fp.Proxy = self

        body.addObject(fp)

        if widget.indexComboBox == 0:
            gearType = "Spur"
        if widget.indexComboBox == 1:
            gearType = "Helical"
        if widget.indexComboBox == 2:
            gearType = "DobleHelical"

        fp.addProperty('App::PropertyLength', 'height', '1 - Common input data', 'Height').height = widget.heightEdit.text()
        fp.addProperty('App::PropertyFloat', 'helicalPortion', '1 - Common input data', 'Helical portion').helicalPortion = float(widget.helicalAngleEdit.text())
        fp.addProperty('App::PropertyEnumeration', 'gearType', '1 - Common input data', 'Type of Gear').gearType = ["Spur", "Helical", "DobleHelical"]
        fp.gearType = gearType
        fp.addProperty('App::PropertyLength', 'm', '1 - Common input data', 'Module').m = widget.mEdit.text()
        fp.addProperty('App::PropertyAngle', 'phi_s', '1 - Common input data', 'Standard pressure angle').phi_s = widget.phi_sEdit.text()
        fp.addProperty('App::PropertyDistance', 'deltaCs', '1 - Common input data', 'Center distance offset').deltaCs = widget.deltaCEdit.text()
        fp.addProperty('App::PropertyDistance', 'deltatp', '1 - Common input data', 'Delta Thickness').deltatp = widget.deltaTpEdit.text()
        fp.addProperty('App::PropertyFloat', 'c', '1 - Common input data', 'Clearance constant').c = float(widget.cEdit.text())
        fp.addProperty('App::PropertyFloat', 'rk', '1 - Common input data', 'Cutter Tip Corner Radius Constant').rk = float(widget.rfEdit.text())
        fp.addProperty('App::PropertyLength', 'Bn', '1 - Common input data', 'Backlash along the common normal').Bn = widget.BnEdit.text()
        fp.addProperty('App::PropertyFloat', 'iL', '1 - Common input data', 'Limit of second Interference').iL = float(widget.interfEdit.text())
        fp.addProperty('App::PropertyInteger', 'n', '1 - Common input data', 'Number of Point on curves').n = int(widget.numPointsEdit.text())
        fp.addProperty('App::PropertyAngle', 'phi_p', '4 - Common data', 'Pressure angle', 1)
        fp.addProperty('App::PropertyAngle', 'inv_phi_s', '4 - Common data', 'Involute function of phi_s', 1)
        fp.addProperty('App::PropertyAngle', 'inv_phi_p', '4 - Common data', 'Involute function of phi', 1)
        fp.addProperty('App::PropertyLength', 'Cs', '4 - Common data', 'Standard center distance', 1)
        fp.addProperty('App::PropertyLength', 'C', '4 - Common data', 'Center distance', 1)
        fp.addProperty('App::PropertyLength', 'ps', '4 - Common data', 'Standard Circular pitch', 1)
        fp.addProperty('App::PropertyLength', 'pp', '4 - Common data', 'Circular pitch', 1)
        fp.addProperty('App::PropertyLength', 'pb', '4 - Common data', 'Base Circular pitch', 1)
        fp.addProperty('App::PropertyLength', 'pd', '4 - Common data', 'Diametral pitch', 1)
        fp.addProperty('App::PropertyLength', 'rcT', '4 - Common data', 'Cutter Tip Corner Radius', 1)
        fp.addProperty('App::PropertyLength', 'B', '4 - Common data', 'Circular Backlash', 1)
        fp.addProperty('App::PropertyFloat', 'mc', '4 - Common data', 'Contact Ratio', 1)
        fp.addProperty('App::PropertyBool', 'FourthCond', '4 - Common data', 'Fourth Condition', 1)
        fp.addProperty('App::PropertyInteger', 'm_N', '2 - Internal gear input data', 'Number of Teeth').m_N = int(widget.N_m_Edit.text())
        fp.addProperty('App::PropertyDistance', 'm_offset', '2 - Internal gear input data', '3D printer offset').m_offset = widget.offset_m_Edit.text()
        fp.addProperty('App::PropertyLength', 'thickness', '2 - Internal gear input data', 'Thickness').thickness = widget.thicknessEdit.text()
        fp.addProperty('App::PropertyLength', 'm_Rs', '5 - Internal gear data', 'Standard Pitch Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_Rp', '5 - Internal gear data', 'Pitch Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_Rb', '5 - Internal gear data', 'Base Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_RT', '5 - Internal gear data', 'Tip Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_Rroot', '5 - Internal gear data', 'Root Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_RL', '5 - Internal gear data', 'Limit Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_Rf', '5 - Internal gear data', 'Fillet Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_Ru', '5 - Internal gear data', 'Undercut Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_ts', '5 - Internal gear data', 'Tooth thickness at the standard pitch circle', 1)
        fp.addProperty('App::PropertyLength', 'm_tp', '5 - Internal gear data', 'Tooth thickness at the pitch circle', 1)
        fp.addProperty('App::PropertyLength', 'm_tb', '5 - Internal gear data', 'Tooth thickness at the base circle', 1)
        fp.addProperty('App::PropertyLength', 'm_tT', '5 - Internal gear data', 'Tooth thickness at the tip circle', 1)
        fp.addProperty('App::PropertyDistance', 'm_e', '5 - Internal gear data', 'Profile Shift', 1)
        fp.addProperty('App::PropertyLength', 'm_as', '5 - Internal gear data', 'Standard Pitch Circle Addendum', 1)
        fp.addProperty('App::PropertyLength', 'm_ap', '5 - Internal gear data', 'Pitch Circle Addendum', 1)
        fp.addProperty('App::PropertyLength', 'm_bs', '5 - Internal gear data', 'Standard Pitch Circle Dedendum', 1)
        fp.addProperty('App::PropertyLength', 'm_bp', '5 - Internal gear data', 'Pitch Circle Dedendum', 1)
        fp.addProperty('App::PropertyBool', 'm_FirstCond', '5 - Internal gear data', 'First Condition', 1)
        fp.addProperty('App::PropertyBool', 'm_SecondCond', '5 - Internal gear data', 'Second Condition', 1)
        fp.addProperty('App::PropertyBool', 'm_ThirdCond', '5 - Internal gear data', 'Third Condition', 1)
        fp.addProperty('App::PropertyInteger', 's_N', '3 - Slave gear input data', 'Number of Teeth').s_N = int(widget.N_s_Edit.text())
        fp.addProperty('App::PropertyDistance', 's_offset', '3 - Slave gear input data', '3D printer offset').s_offset = widget.offset_s_Edit.text()
        fp.addProperty('App::PropertyLength', 's_Rs', '6 - Slave gear data', 'Standard Pitch Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_Rp', '6 - Slave gear data', 'Pitch Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_Rb', '6 - Slave gear data', 'Base Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_RT', '6 - Slave gear data', 'Tip Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_Rroot', '6 - Slave gear data', 'Root Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_RL', '6 - Slave gear data', 'Limit Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_Rf', '6 - Slave gear data', 'Fillet Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_Ru', '6 - Slave gear data', 'Undercut Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_ts', '6 - Slave gear data', 'Tooth thickness at the standard pitch circle', 1)
        fp.addProperty('App::PropertyLength', 's_tp', '6 - Slave gear data', 'Tooth thickness at the pitch circle', 1)
        fp.addProperty('App::PropertyLength', 's_tb', '6 - Slave gear data', 'Tooth thickness at the base circle', 1)
        fp.addProperty('App::PropertyLength', 's_tT', '6 - Slave gear data', 'Tooth thickness at the tip circle', 1)
        fp.addProperty('App::PropertyDistance', 's_e', '6 - Slave gear data', 'Profile Shift', 1)
        fp.addProperty('App::PropertyLength', 's_as', '6 - Slave gear data', 'Standard Pitch Circle Addendum', 1)
        fp.addProperty('App::PropertyLength', 's_ap', '6 - Slave gear data', 'Pitch Circle Addendum', 1)
        fp.addProperty('App::PropertyLength', 's_bs', '6 - Slave gear data', 'Standard Pitch Circle Dedendum', 1)
        fp.addProperty('App::PropertyLength', 's_bp', '6 - Slave gear data', 'Pitch Circle Dedendum', 1)
        fp.addProperty('App::PropertyAngle', 's_angle', '6 - Slave gear data', 'Gear orientation', 1)
        fp.addProperty('App::PropertyBool', 's_FirstCond', '6 - Slave gear data', 'First Condition', 1)
        fp.addProperty('App::PropertyBool', 's_SecondCond', '6 - Slave gear data', 'Second Condition', 1)
        fp.addProperty('App::PropertyBool', 's_ThirdCond', '6 - Slave gear data', 'Third Condition', 1)
        fp.addProperty('Part::PropertyPartShape', 'W_p', '6 - Slave gear data', 'Pinion Wire', 1)

    def execute(self, fp):
        inputData = inputDataClass(fp.m.Value, fp.phi_s.Value, fp.deltaCs.Value, fp.c, fp.rk, fp.Bn.Value, fp.iL, fp.m_N, fp.s_N, fp.deltatp.Value, fp.n,
                                   - fp.m_offset.Value, fp.s_offset.Value)
        cD = commonData()
        gear = gearData()
        pinion = gearData()

        mainCalculations(inputData, cD, gear, pinion, True)

        # if not gear.FirstCond:
        #     App.Console.PrintWarning("WARNING: Undercutting en 1 \n")
        # if not pinion.FirstCond:
        #     App.Console.PrintWarning("WARNING: Undercutting en 2 \n")

        # if not gear.SecondCond and gear.FirstCond:
        #     App.Console.PrintWarning("WARNING: Interference en 1(Second Condition). Reducir rf, Incrementar deltaC o Cambiar valores \n")
        # if not pinion.SecondCond and pinion.FirstCond:
        #     App.Console.PrintWarning("WARNING: Interference en 2(Second Condition). Reducir rf, Incrementar deltaC o Cambiar valores \n")

        # if not gear.ThirdCond:
        #     App.Console.PrintWarning("WARNING: Third Condition. yc1_p = {}. Reducir rf o Cambiar valores \n".format(gear.yc_a))
        # if not pinion.ThirdCond:
        #     App.Console.PrintWarning("WARNING: Third Condition. yc2_p = {}. Reducir rf o Cambiar valores \n".format(pinion.yc_a))

        # if not cD.fourthCond:
        #     App.Console.PrintWarning("WARNING: Fourth Condition. mc = {} < 1.4 \n".format(cD.mc))

        getProfile(gear, pinion, cD, True)
        getProfile(pinion, gear, cD)

        loadProperties(fp, cD, gear, pinion)
        fp.Cs.Value = abs(gear.Rs - pinion.Rs)
        fp.C.Value = abs(gear.Rp - pinion.Rp)
        fp.s_angle.Value = pinion.beta0 * 180 / pi - 180 + 180 / fp.s_N

        W_g = getWire(gear)

        fp.height.Value = fp.height.Value + 0.0005
        Solid_g = getInternalShape(fp, W_g)

        height = fp.height.Value - 0.0005
        cylinder = makeCylinder(gear.RTc + fp.thickness.Value, height)
        Solid_g = cylinder.cut(Solid_g)
        fp.Shape = Solid_g

        W_p = getWire(pinion)
        fp.W_p = W_p


class ViewProviderMasterGear():
    def __init__(self, obj):
        obj.Proxy = self

    def attach(self, vobj):
        self.vobj = vobj

    def getIcon(self):
        return ":/icons/master_gear.svg"

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


class MasterGear():

    def __init__(self, fp, body, widget):
        self.Type = 'masterGear'
        fp.Proxy = self

        body.addObject(fp)

        if widget.indexComboBox == 0:
            gearType = "Spur"
        if widget.indexComboBox == 1:
            gearType = "Helical"
        if widget.indexComboBox == 2:
            gearType = "DobleHelical"

        fp.addProperty('App::PropertyLength', 'height', '1 - Common input data', 'Height').height = widget.heightEdit.text()
        fp.addProperty('App::PropertyFloat', 'helicalPortion', '1 - Common input data', 'Helical portion').helicalPortion = float(widget.helicalAngleEdit.text())
        fp.addProperty('App::PropertyEnumeration', 'gearType', '1 - Common input data', 'Type of Gear').gearType = ["Spur", "Helical", "DobleHelical"]
        fp.gearType = gearType
        fp.addProperty('App::PropertyLength', 'm', '1 - Common input data', 'Module').m = widget.mEdit.text()
        fp.addProperty('App::PropertyAngle', 'phi_s', '1 - Common input data', 'Standard pressure angle').phi_s = widget.phi_sEdit.text()
        fp.addProperty('App::PropertyDistance', 'deltaCs', '1 - Common input data', 'Center distance offset').deltaCs = widget.deltaCEdit.text()
        fp.addProperty('App::PropertyDistance', 'deltatp', '1 - Common input data', 'Delta Thickness').deltatp = widget.deltaTpEdit.text()
        fp.addProperty('App::PropertyFloat', 'c', '1 - Common input data', 'Clearance constant').c = float(widget.cEdit.text())
        fp.addProperty('App::PropertyFloat', 'rk', '1 - Common input data', 'Cutter Tip Corner Radius Constant').rk = float(widget.rfEdit.text())
        fp.addProperty('App::PropertyLength', 'Bn', '1 - Common input data', 'Backlash along the common normal').Bn = widget.BnEdit.text()
        fp.addProperty('App::PropertyFloat', 'iL', '1 - Common input data', 'Limit of second Interference').iL = float(widget.interfEdit.text())
        fp.addProperty('App::PropertyInteger', 'n', '1 - Common input data', 'Number of Point on curves').n = int(widget.numPointsEdit.text())
        fp.addProperty('App::PropertyAngle', 'phi_p', '4 - Common data', 'Pressure angle', 1)
        fp.addProperty('App::PropertyAngle', 'inv_phi_s', '4 - Common data', 'Involute function of phi_s', 1)
        fp.addProperty('App::PropertyAngle', 'inv_phi_p', '4 - Common data', 'Involute function of phi', 1)
        fp.addProperty('App::PropertyLength', 'Cs', '4 - Common data', 'Standard center distance', 1)
        fp.addProperty('App::PropertyLength', 'C', '4 - Common data', 'Center distance', 1)
        fp.addProperty('App::PropertyLength', 'ps', '4 - Common data', 'Standard Circular pitch', 1)
        fp.addProperty('App::PropertyLength', 'pp', '4 - Common data', 'Circular pitch', 1)
        fp.addProperty('App::PropertyLength', 'pb', '4 - Common data', 'Base Circular pitch', 1)
        fp.addProperty('App::PropertyLength', 'pd', '4 - Common data', 'Diametral pitch', 1)
        fp.addProperty('App::PropertyLength', 'rcT', '4 - Common data', 'Cutter Tip Corner Radius', 1)
        fp.addProperty('App::PropertyLength', 'B', '4 - Common data', 'Circular Backlash', 1)
        fp.addProperty('App::PropertyFloat', 'mc', '4 - Common data', 'Contact Ratio', 1)
        fp.addProperty('App::PropertyBool', 'FourthCond', '4 - Common data', 'Fourth Condition', 1)
        fp.addProperty('App::PropertyInteger', 'm_N', '2 - Master gear input data', 'Number of Teeth').m_N = int(widget.N_m_Edit.text())
        fp.addProperty('App::PropertyDistance', 'm_offset', '2 - Master gear input data', '3D printer offset').m_offset = widget.offset_m_Edit.text()
        fp.addProperty('App::PropertyLength', 'm_Rs', '5 - Master gear data', 'Standard Pitch Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_Rp', '5 - Master gear data', 'Pitch Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_Rb', '5 - Master gear data', 'Base Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_RT', '5 - Master gear data', 'Tip Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_Rroot', '5 - Master gear data', 'Root Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_RL', '5 - Master gear data', 'Limit Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_Rf', '5 - Master gear data', 'Fillet Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_Ru', '5 - Master gear data', 'Undercut Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_ts', '5 - Master gear data', 'Tooth thickness at the standard pitch circle', 1)
        fp.addProperty('App::PropertyLength', 'm_tp', '5 - Master gear data', 'Tooth thickness at the pitch circle', 1)
        fp.addProperty('App::PropertyLength', 'm_tb', '5 - Master gear data', 'Tooth thickness at the base circle', 1)
        fp.addProperty('App::PropertyLength', 'm_tT', '5 - Master gear data', 'Tooth thickness at the tip circle', 1)
        fp.addProperty('App::PropertyDistance', 'm_e', '5 - Master gear data', 'Profile Shift', 1)
        fp.addProperty('App::PropertyLength', 'm_as', '5 - Master gear data', 'Standard Pitch Circle Addendum', 1)
        fp.addProperty('App::PropertyLength', 'm_ap', '5 - Master gear data', 'Pitch Circle Addendum', 1)
        fp.addProperty('App::PropertyLength', 'm_bs', '5 - Master gear data', 'Standard Pitch Circle Dedendum', 1)
        fp.addProperty('App::PropertyLength', 'm_bp', '5 - Master gear data', 'Pitch Circle Dedendum', 1)
        fp.addProperty('App::PropertyBool', 'm_FirstCond', '5 - Master gear data', 'First Condition', 1)
        fp.addProperty('App::PropertyBool', 'm_SecondCond', '5 - Master gear data', 'Second Condition', 1)
        fp.addProperty('App::PropertyBool', 'm_ThirdCond', '5 - Master gear data', 'Third Condition', 1)
        fp.addProperty('App::PropertyInteger', 's_N', '3 - Slave gear input data', 'Number of Teeth').s_N = int(widget.N_s_Edit.text())
        fp.addProperty('App::PropertyDistance', 's_offset', '3 - Slave gear input data', '3D printer offset').s_offset = widget.offset_s_Edit.text()
        fp.addProperty('App::PropertyLength', 's_Rs', '6 - Slave gear data', 'Standard Pitch Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_Rp', '6 - Slave gear data', 'Pitch Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_Rb', '6 - Slave gear data', 'Base Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_RT', '6 - Slave gear data', 'Tip Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_Rroot', '6 - Slave gear data', 'Root Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_RL', '6 - Slave gear data', 'Limit Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_Rf', '6 - Slave gear data', 'Fillet Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_Ru', '6 - Slave gear data', 'Undercut Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_ts', '6 - Slave gear data', 'Tooth thickness at the standard pitch circle', 1)
        fp.addProperty('App::PropertyLength', 's_tp', '6 - Slave gear data', 'Tooth thickness at the pitch circle', 1)
        fp.addProperty('App::PropertyLength', 's_tb', '6 - Slave gear data', 'Tooth thickness at the base circle', 1)
        fp.addProperty('App::PropertyLength', 's_tT', '6 - Slave gear data', 'Tooth thickness at the tip circle', 1)
        fp.addProperty('App::PropertyDistance', 's_e', '6 - Slave gear data', 'Profile Shift', 1)
        fp.addProperty('App::PropertyLength', 's_as', '6 - Slave gear data', 'Standard Pitch Circle Addendum', 1)
        fp.addProperty('App::PropertyLength', 's_ap', '6 - Slave gear data', 'Pitch Circle Addendum', 1)
        fp.addProperty('App::PropertyLength', 's_bs', '6 - Slave gear data', 'Standard Pitch Circle Dedendum', 1)
        fp.addProperty('App::PropertyLength', 's_bp', '6 - Slave gear data', 'Pitch Circle Dedendum', 1)
        fp.addProperty('App::PropertyAngle', 's_angle', '6 - Slave gear data', 'Gear orientation', 1)
        fp.addProperty('App::PropertyBool', 's_FirstCond', '6 - Slave gear data', 'First Condition', 1)
        fp.addProperty('App::PropertyBool', 's_SecondCond', '6 - Slave gear data', 'Second Condition', 1)
        fp.addProperty('App::PropertyBool', 's_ThirdCond', '6 - Slave gear data', 'Third Condition', 1)
        fp.addProperty('Part::PropertyPartShape', 'W_p', '6 - Slave gear data', 'Pinion Wire', 1)

    def execute(self, fp):
        inputData = inputDataClass(fp.m.Value, fp.phi_s.Value, fp.deltaCs.Value, fp.c, fp.rk, fp.Bn.Value, fp.iL, fp.m_N, fp.s_N, fp.deltatp.Value, fp.n,
                                   fp.m_offset.Value, fp.s_offset.Value)
        cD = commonData()
        gear = gearData()
        pinion = gearData()

        mainCalculations(inputData, cD, gear, pinion)

        # if not gear.FirstCond:
        #     App.Console.PrintWarning("WARNING: Undercutting en 1 \n")
        # if not pinion.FirstCond:
        #     App.Console.PrintWarning("WARNING: Undercutting en 2 \n")

        # if not gear.SecondCond and gear.FirstCond:
        #     App.Console.PrintWarning("WARNING: Interference en 1(Second Condition). Reducir rf, Incrementar deltaC o Cambiar valores \n")
        # if not pinion.SecondCond and pinion.FirstCond:
        #     App.Console.PrintWarning("WARNING: Interference en 2(Second Condition). Reducir rf, Incrementar deltaC o Cambiar valores \n")

        # if not gear.ThirdCond:
        #     App.Console.PrintWarning("WARNING: Third Condition. yc1_p = {}. Reducir rf o Cambiar valores \n".format(gear.yc_a))
        # if not pinion.ThirdCond:
        #     App.Console.PrintWarning("WARNING: Third Condition. yc2_p = {}. Reducir rf o Cambiar valores \n".format(pinion.yc_a))

        # if not cD.fourthCond:
        #     App.Console.PrintWarning("WARNING: Fourth Condition. mc = {} < 1.4 \n".format(cD.mc))

        getProfile(gear, pinion, cD)
        getProfile(pinion, gear, cD)

        loadProperties(fp, cD, gear, pinion)

        W_g = getWire(gear)
        Solid_g = getMasterShape(fp, W_g)
        fp.Shape = Solid_g

        W_p = getWire(pinion)
        fp.W_p = W_p


class ViewProviderSlaveGear():
    def __init__(self, obj):
        obj.Proxy = self

    def attach(self, vobj):
        self.vobj = vobj

    def getIcon(self):
        return ":/icons/slave_gear.svg"

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


class SlaveGear():

    def __init__(self, fp, body, fp_master, positionAngle):
        self.Type = 'slaveGear'
        fp.Proxy = self

        body.addObject(fp)

        fp.addProperty('App::PropertyLinkGlobal', 'fp_master', 'Slave gear data', 'Master Feature Python').fp_master = fp_master
        fp.addProperty('App::PropertyLinkGlobal', 'body_master', 'Slave gear data', 'Master Feature Python', 4).body_master = fp_master._Body
        fp.addProperty('App::PropertyAngle', 'positionAngle', 'Slave gear data', 'Position Angle').positionAngle = positionAngle
        fp.addProperty('App::PropertyBool', 'attachToMaster', 'Slave gear data', 'Attach to master').attachToMaster = True
        fp.addProperty('App::PropertyPlacement', 'last_Placement', 'Slave gear data', 'Last Placement', 4).last_Placement = fp.body_master.Placement.copy()

    def execute(self, fp):
        fp_master = fp.fp_master

        epsi = 0.000001
        if (fp.last_Placement.Base.distanceToPoint(fp.body_master.Placement.Base) < epsi and
                fp.last_Placement.Rotation.isSame(fp.body_master.Placement.Rotation, epsi)):

            Solid_p = getSlaveShape(fp_master)
            fp.Shape = Solid_p

        fp.last_Placement = fp.body_master.Placement.copy()

        if fp.attachToMaster:
            updatePosition(fp)


class ViewProviderSlaveMasterGear():
    def __init__(self, obj):
        obj.Proxy = self

    def attach(self, vobj):
        self.vobj = vobj

    def getIcon(self):
        return ":/icons/slave-master_gear.svg"

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


class SlaveMasterGear():

    def __init__(self, fp, body, fp_master, positionAngle, widget):
        self.Type = 'slaveMasterGear'
        fp.Proxy = self

        body.addObject(fp)

        fp.addProperty('App::PropertyDistance', 'hseparator', '2 - Master gear input data', 'Height separator').hseparator = widget.hseparatorEdit.text()
        fp.addProperty('App::PropertyAngle', 'tita', '2 - Master gear input data', 'Gear orientation').tita = widget.titaEdit.text()
        fp.addProperty('App::PropertyLinkGlobal', 'fp_master', 'Slave gear data', 'Master Feature Python').fp_master = fp_master
        fp.addProperty('App::PropertyLinkGlobal', 'body_master', 'Slave gear data', 'Master Feature Python', 4).body_master = fp_master._Body
        fp.addProperty('App::PropertyAngle', 'positionAngle', 'Slave gear data', 'Position Angle').positionAngle = positionAngle
        fp.addProperty('App::PropertyBool', 'attachToMaster', 'Slave gear data', 'Attach to master').attachToMaster = True
        fp.addProperty('App::PropertyPlacement', 'last_Placement', 'Slave gear data', 'Last Placement', 4).last_Placement = fp.body_master.Placement
        if widget.indexComboBox == 0:
            gearType = "Spur"
        if widget.indexComboBox == 1:
            gearType = "Helical"
        if widget.indexComboBox == 2:
            gearType = "DobleHelical"
        fp.addProperty('App::PropertyLength', 'height', '1 - Common input data', 'Height').height = widget.heightEdit.text()
        fp.addProperty('App::PropertyFloat', 'helicalPortion', '1 - Common input data', 'Helical portion').helicalPortion = float(widget.helicalAngleEdit.text())
        fp.addProperty('App::PropertyEnumeration', 'gearType', '1 - Common input data', 'Type of Gear').gearType = ["Spur", "Helical", "DobleHelical"]
        fp.gearType = gearType
        fp.addProperty('App::PropertyLength', 'm', '1 - Common input data', 'Module').m = widget.mEdit.text()
        fp.addProperty('App::PropertyAngle', 'phi_s', '1 - Common input data', 'Standard pressure angle').phi_s = widget.phi_sEdit.text()
        fp.addProperty('App::PropertyDistance', 'deltaCs', '1 - Common input data', 'Center distance offset').deltaCs = widget.deltaCEdit.text()
        fp.addProperty('App::PropertyDistance', 'deltatp', '1 - Common input data', 'Delta Thickness').deltatp = widget.deltaTpEdit.text()
        fp.addProperty('App::PropertyFloat', 'c', '1 - Common input data', 'Clearance constant').c = float(widget.cEdit.text())
        fp.addProperty('App::PropertyFloat', 'rk', '1 - Common input data', 'Cutter Tip Corner Radius Constant').rk = float(widget.rfEdit.text())
        fp.addProperty('App::PropertyLength', 'Bn', '1 - Common input data', 'Backlash along the common normal').Bn = widget.BnEdit.text()
        fp.addProperty('App::PropertyFloat', 'iL', '1 - Common input data', 'Limit of second Interference').iL = float(widget.interfEdit.text())
        fp.addProperty('App::PropertyInteger', 'n', '1 - Common input data', 'Number of Point on curves').n = int(widget.numPointsEdit.text())
        fp.addProperty('App::PropertyAngle', 'phi_p', '4 - Common data', 'Pressure angle', 1)
        fp.addProperty('App::PropertyAngle', 'inv_phi_s', '4 - Common data', 'Involute function of phi_s', 1)
        fp.addProperty('App::PropertyAngle', 'inv_phi_p', '4 - Common data', 'Involute function of phi', 1)
        fp.addProperty('App::PropertyLength', 'Cs', '4 - Common data', 'Standard center distance', 1)
        fp.addProperty('App::PropertyLength', 'C', '4 - Common data', 'Center distance', 1)
        fp.addProperty('App::PropertyLength', 'ps', '4 - Common data', 'Standard Circular pitch', 1)
        fp.addProperty('App::PropertyLength', 'pp', '4 - Common data', 'Circular pitch', 1)
        fp.addProperty('App::PropertyLength', 'pb', '4 - Common data', 'Base Circular pitch', 1)
        fp.addProperty('App::PropertyLength', 'pd', '4 - Common data', 'Diametral pitch', 1)
        fp.addProperty('App::PropertyLength', 'rcT', '4 - Common data', 'Cutter Tip Corner Radius', 1)
        fp.addProperty('App::PropertyLength', 'B', '4 - Common data', 'Circular Backlash', 1)
        fp.addProperty('App::PropertyFloat', 'mc', '4 - Common data', 'Contact Ratio', 1)
        fp.addProperty('App::PropertyBool', 'FourthCond', '4 - Common data', 'Fourth Condition', 1)
        fp.addProperty('App::PropertyInteger', 'm_N', '2 - Master gear input data', 'Number of Teeth').m_N = int(widget.N_m_Edit.text())
        fp.addProperty('App::PropertyDistance', 'm_offset', '2 - Master gear input data', '3D printer offset').m_offset = widget.offset_m_Edit.text()
        fp.addProperty('App::PropertyLength', 'm_Rs', '5 - Master gear data', 'Standard Pitch Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_Rp', '5 - Master gear data', 'Pitch Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_Rb', '5 - Master gear data', 'Base Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_RT', '5 - Master gear data', 'Tip Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_Rroot', '5 - Master gear data', 'Root Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_RL', '5 - Master gear data', 'Limit Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_Rf', '5 - Master gear data', 'Fillet Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_Ru', '5 - Master gear data', 'Undercut Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'm_ts', '5 - Master gear data', 'Tooth thickness at the standard pitch circle', 1)
        fp.addProperty('App::PropertyLength', 'm_tp', '5 - Master gear data', 'Tooth thickness at the pitch circle', 1)
        fp.addProperty('App::PropertyLength', 'm_tb', '5 - Master gear data', 'Tooth thickness at the base circle', 1)
        fp.addProperty('App::PropertyLength', 'm_tT', '5 - Master gear data', 'Tooth thickness at the tip circle', 1)
        fp.addProperty('App::PropertyDistance', 'm_e', '5 - Master gear data', 'Profile Shift', 1)
        fp.addProperty('App::PropertyLength', 'm_as', '5 - Master gear data', 'Standard Pitch Circle Addendum', 1)
        fp.addProperty('App::PropertyLength', 'm_ap', '5 - Master gear data', 'Pitch Circle Addendum', 1)
        fp.addProperty('App::PropertyLength', 'm_bs', '5 - Master gear data', 'Standard Pitch Circle Dedendum', 1)
        fp.addProperty('App::PropertyLength', 'm_bp', '5 - Master gear data', 'Pitch Circle Dedendum', 1)
        fp.addProperty('App::PropertyBool', 'm_FirstCond', '5 - Master gear data', 'First Condition', 1)
        fp.addProperty('App::PropertyBool', 'm_SecondCond', '5 - Master gear data', 'Second Condition', 1)
        fp.addProperty('App::PropertyBool', 'm_ThirdCond', '5 - Master gear data', 'Third Condition', 1)
        fp.addProperty('App::PropertyInteger', 's_N', '3 - Slave gear input data', 'Number of Teeth').s_N = int(widget.N_s_Edit.text())
        fp.addProperty('App::PropertyDistance', 's_offset', '3 - Slave gear input data', '3D printer offset').s_offset = widget.offset_s_Edit.text()
        fp.addProperty('App::PropertyLength', 's_Rs', '6 - Slave gear data', 'Standard Pitch Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_Rp', '6 - Slave gear data', 'Pitch Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_Rb', '6 - Slave gear data', 'Base Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_RT', '6 - Slave gear data', 'Tip Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_Rroot', '6 - Slave gear data', 'Root Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_RL', '6 - Slave gear data', 'Limit Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_Rf', '6 - Slave gear data', 'Fillet Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_Ru', '6 - Slave gear data', 'Undercut Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 's_ts', '6 - Slave gear data', 'Tooth thickness at the standard pitch circle', 1)
        fp.addProperty('App::PropertyLength', 's_tp', '6 - Slave gear data', 'Tooth thickness at the pitch circle', 1)
        fp.addProperty('App::PropertyLength', 's_tb', '6 - Slave gear data', 'Tooth thickness at the base circle', 1)
        fp.addProperty('App::PropertyLength', 's_tT', '6 - Slave gear data', 'Tooth thickness at the tip circle', 1)
        fp.addProperty('App::PropertyDistance', 's_e', '6 - Slave gear data', 'Profile Shift', 1)
        fp.addProperty('App::PropertyLength', 's_as', '6 - Slave gear data', 'Standard Pitch Circle Addendum', 1)
        fp.addProperty('App::PropertyLength', 's_ap', '6 - Slave gear data', 'Pitch Circle Addendum', 1)
        fp.addProperty('App::PropertyLength', 's_bs', '6 - Slave gear data', 'Standard Pitch Circle Dedendum', 1)
        fp.addProperty('App::PropertyLength', 's_bp', '6 - Slave gear data', 'Pitch Circle Dedendum', 1)
        fp.addProperty('App::PropertyAngle', 's_angle', '6 - Slave gear data', 'Gear orientation', 1)
        fp.addProperty('App::PropertyBool', 's_FirstCond', '6 - Slave gear data', 'First Condition', 1)
        fp.addProperty('App::PropertyBool', 's_SecondCond', '6 - Slave gear data', 'Second Condition', 1)
        fp.addProperty('App::PropertyBool', 's_ThirdCond', '6 - Slave gear data', 'Third Condition', 1)
        fp.addProperty('Part::PropertyPartShape', 'W_p', '6 - Slave gear data', 'Pinion Wire', 1)

    def execute(self, fp):
        epsi = 0.000001
        if (fp.last_Placement.Base.distanceToPoint(fp.body_master.Placement.Base) < epsi and
                fp.last_Placement.Rotation.isSame(fp.body_master.Placement.Rotation, epsi)):
            inputData = inputDataClass(fp.m.Value, fp.phi_s.Value, fp.deltaCs.Value, fp.c, fp.rk, fp.Bn.Value, fp.iL, fp.m_N, fp.s_N, fp.deltatp.Value, fp.n,
                                       fp.m_offset.Value, fp.s_offset.Value)
            cD = commonData()
            gear = gearData()
            pinion = gearData()

            mainCalculations(inputData, cD, gear, pinion)

            # if not gear.FirstCond:
            #     App.Console.PrintWarning("WARNING: Undercutting en 1 \n")
            # if not pinion.FirstCond:
            #     App.Console.PrintWarning("WARNING: Undercutting en 2 \n")

            # if not gear.SecondCond and gear.FirstCond:
            #     App.Console.PrintWarning("WARNING: Interference en 1(Second Condition). Reducir rf, Incrementar deltaC o Cambiar valores \n")
            # if not pinion.SecondCond and pinion.FirstCond:
            #     App.Console.PrintWarning("WARNING: Interference en 2(Second Condition). Reducir rf, Incrementar deltaC o Cambiar valores \n")

            # if not gear.ThirdCond:
            #     App.Console.PrintWarning("WARNING: Third Condition. yc1_p = {}. Reducir rf o Cambiar valores \n".format(gear.yc_a))
            # if not pinion.ThirdCond:
            #     App.Console.PrintWarning("WARNING: Third Condition. yc2_p = {}. Reducir rf o Cambiar valores \n".format(pinion.yc_a))

            # if not cD.fourthCond:
            #     App.Console.PrintWarning("WARNING: Fourth Condition. mc = {} < 1.4 \n".format(cD.mc))

            getProfile(gear, pinion, cD)
            getProfile(pinion, gear, cD)

            loadProperties(fp, cD, gear, pinion)

            W_g = getWire(gear)

            fp_master = fp.fp_master
            hseparator = fp.hseparator.Value
            tita = fp.tita.Value

            slave_height = fp_master.height.Value
            if hseparator < 0.0:
                z = - fp.height.Value
            else:
                z = slave_height

            Solid_g = getMasterShape(fp, W_g, z + hseparator, tita)

            Solid_p = getSlaveShape(fp_master)

            W_p = fp_master.W_p.copy()

            if hseparator < 0.0:
                z = hseparator
            else:
                z = slave_height
            height = abs(hseparator)

            if fp_master.s_N >= fp.m_N:
                if fp.gearType == "Helical" and hseparator < 0:
                    angle2 = fp.helicalPortion * (360 / fp_master.m_N)
                else:
                    angle2 = 0
                Solid_separator = commonextrusion(W_g, height, App.Vector(0, 0, z), tita + angle2)
            else:
                if fp_master.gearType == "Helical" and hseparator > 0:
                    angle = - fp_master.helicalPortion * (360 / fp_master.s_N)
                else:
                    angle = 0
                Solid_separator = commonextrusion(W_p, height, App.Vector(0, 0, z), tita + angle)

            if hseparator < 0.0:
                z = 0
            else:
                z = slave_height
            faces = Solid_p.Faces + Solid_separator.Faces + Solid_g.Faces
            faces = [f for f in faces if not (abs(f.CenterOfMass.z - z) < 0.001 or abs(f.CenterOfMass.z - (z + hseparator)) < 0.001)]

            if fp_master.s_N != fp.m_N:
                if fp_master.gearType == "Helical" and hseparator > 0:
                    angle = - fp_master.helicalPortion * (360 / fp_master.s_N)
                else:
                    angle = 0
                if fp.gearType == "Helical" and hseparator < 0:
                    angle2 = fp.helicalPortion * (360 / fp_master.m_N)
                else:
                    angle2 = 0
                if fp_master.s_N > fp.m_N:
                    W_g.Placement = App.Placement(App.Vector(0, 0, z), App.Rotation(App.Vector(0, 0, 1), tita + angle2))
                    W_p.Placement = App.Placement(App.Vector(0, 0, z), App.Rotation(App.Vector(0, 0, 1), angle))
                    W_p.reverse()
                    middleFace = Face([W_p, W_g])
                else:
                    W_p.Placement = App.Placement(App.Vector(0, 0, z + hseparator), App.Rotation(App.Vector(0, 0, 1), angle))
                    W_g.Placement = App.Placement(App.Vector(0, 0, z + hseparator), App.Rotation(App.Vector(0, 0, 1), tita + angle2))
                    W_g.reverse()
                    middleFace = Face([W_g, W_p])
                faces.append(middleFace)

            Solid_pg = makeSolid(makeShell(faces))

            fp.Shape = Solid_pg

            W_p = getWire(pinion)
            fp.W_p = W_p

        fp.last_Placement = fp.body_master.Placement.copy()

        if fp.attachToMaster:
            updatePosition(fp)
