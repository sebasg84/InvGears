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
from Part import Face, makeShell, makeSolid, makeCylinder
from freecad.invgears.gears import inputDataClass, commonData, gearData, mainCalculations, getProfile
from freecad.invgears.gears_bevel import inputDataClass_b, commonData_b, gearData_b, mainCalculations_b, getProfile_b
from freecad.invgears.functions import getWire, getBevelWire, getMasterShape, getSlaveShape, getInternalShape, getBevelShape, commonextrusion, updatePosition
from freecad.invgears.properties import loadProperties, addMasterProperties, addSlaveProperties, addAdditionalProperties
from freecad.invgears.expressions import slavePartExpressions, slaveBevelPartExpressions
from freecad.invgears.functions import getPartFromFPSlave, getPartFromFPBevelSlave

from numpy import pi


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

    def __init__(self, fp, form):
        self.Type = 'masterGear'
        fp.Proxy = self

        addMasterProperties(fp, form[0], form[1])

    def execute(self, fp):
        inputData = inputDataClass(fp.m.Value, fp.phi_s.Value, fp.N_m, fp.N_s, fp.Bl.Value, fp.c, fp.deltaCs.Value, fp.deltatp.Value, fp.offset_m.Value, fp.offset_s.Value, fp.n, fp.iL,fp.addendum_master)
        cD = commonData()
        master = gearData()
        slave = gearData()

        mainCalculations(inputData, cD, master, slave)

        getProfile(master, slave, cD)
        
        inputData = inputDataClass(fp.m.Value, fp.phi_s.Value, fp.N_m, fp.N_s, fp.Bl.Value, fp.c_slave, fp.deltaCs.Value, fp.deltatp.Value, fp.offset_m.Value, fp.offset_s.Value, fp.n, fp.iL,fp.addendum_slave)
        mainCalculations(inputData, cD, master, slave)

        getProfile(slave, master, cD)

        loadProperties(fp, cD, master, slave)

        W_m = getWire(master)
        Solid_m = getMasterShape(fp, W_m)
        fp.Shape = Solid_m

        W_s = getWire(slave)
        fp.W_s = W_s
        print("done")


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

    def __init__(self, fp, fp_master, angle):
        self.Type = 'slaveGear'
        fp.Proxy = self

        addSlaveProperties(fp, fp_master, angle)

        part_slave = getPartFromFPSlave(fp)
        part_slave.addProperty('App::PropertyFloat', 'relation', 'Gear relation', 'Gear relation')
        part_slave.addProperty('App::PropertyFloat', 'global_relation', 'Gear relation', 'Gear relation from first master gear')
        slavePartExpressions(fp, fp_master)

        self.betaChanged = False
    
    def onChanged(self, fp, prop):
        if prop == "beta":
            self.betaChanged = True
        else:
            self.betaChanged = False

    def execute(self, fp):
        if self.betaChanged is False:
            fp_master = fp.fp_master
            Solid_s = getSlaveShape(fp_master)
            fp.Shape = Solid_s

        updatePosition(fp)
        self.betaChanged = False


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

    def __init__(self, fp, fp_master, form, angle):
        self.Type = 'slaveMasterGear'
        fp.Proxy = self

        addSlaveProperties(fp, fp_master, angle)

        part_slave = getPartFromFPSlave(fp)
        part_slave.addProperty('App::PropertyFloat', 'relation', 'Gear relation', 'Gear relation')
        part_slave.addProperty('App::PropertyFloat', 'global_relation', 'Gear relation', 'Gear relation from first master gear')

        fp.addProperty('App::PropertyDistance', 'hseparator', '1 - Separator Parameters', 'Separator thickness').hseparator = form[1].doubleSpinBox.text()
        fp.addProperty('App::PropertyAngle', 'tita', '1 - Separator Parameters', 'Orientation offset').tita = form[1].doubleSpinBox_2.text()

        addMasterProperties(fp, form[2], form[3])

        slavePartExpressions(fp, fp_master)

        self.betaChanged = False

    def onChanged(self, fp, prop):
        if prop == "beta":
            self.betaChanged = True
        else:
            self.betaChanged = False

    def execute(self, fp):
        if self.betaChanged is False:
            inputData = inputDataClass(fp.m.Value, fp.phi_s.Value, fp.N_m, fp.N_s, fp.Bl.Value, fp.c, fp.deltaCs.Value, fp.deltatp.Value, fp.offset_m.Value, fp.offset_s.Value, fp.n, fp.iL,fp.addendum_master)
            cD = commonData()
            master = gearData()
            slave = gearData()

            mainCalculations(inputData, cD, master, slave)

            getProfile(master, slave, cD)
            getProfile(slave, master, cD)

            loadProperties(fp, cD, master, slave)

            W_m = getWire(master)           

            fp_master = fp.fp_master
            hseparator = fp.hseparator.Value
            tita = fp.tita.Value

            slave_thickness = fp_master.thickness.Value
            if hseparator < 0.0:
                z = - fp.thickness.Value
            else:
                z = slave_thickness

            Solid_m = getMasterShape(fp, W_m, z + hseparator, tita)

            Solid_s = getSlaveShape(fp_master)

            W_s = fp_master.W_s.copy()

            if hseparator < 0.0:
                z = hseparator
            else:
                z = slave_thickness
            thickness = abs(hseparator)

            if fp_master.N_s >= fp.N_m:
                if fp.gearType == "Helical" and hseparator < 0:
                    angle2 = fp.helicalPortion * (360 / fp_master.N_m)
                else:
                    angle2 = 0
                Solid_separator = commonextrusion(W_m, thickness, App.Vector(0, 0, z), tita + angle2)
            else:
                if fp_master.gearType == "Helical" and hseparator > 0:
                    angle = - fp_master.helicalPortion * (360 / fp_master.N_s)
                else:
                    angle = 0
                Solid_separator = commonextrusion(W_s, thickness, App.Vector(0, 0, z), angle)

            if hseparator < 0.0:
                z = 0
            else:
                z = slave_thickness
            faces = Solid_s.Faces + Solid_separator.Faces + Solid_m.Faces
            faces = [f for f in faces if not (abs(f.CenterOfMass.z - z) < 0.001 or abs(f.CenterOfMass.z - (z + hseparator)) < 0.001)]

            if fp_master.N_s != fp.N_m:
                if fp_master.gearType == "Helical" and hseparator > 0:
                    angle = - fp_master.helicalPortion * (360 / fp_master.N_s)
                else:
                    angle = 0
                if fp.gearType == "Helical" and hseparator < 0:
                    angle2 = fp.helicalPortion * (360 / fp_master.N_m)
                else:
                    angle2 = 0
                if fp_master.N_s > fp.N_m:
                    W_m.Placement = App.Placement(App.Vector(0, 0, z), App.Rotation(App.Vector(0, 0, 1), tita + angle2))
                    W_s.Placement = App.Placement(App.Vector(0, 0, z), App.Rotation(App.Vector(0, 0, 1), angle))
                    W_s.reverse()
                    middleFace = Face([W_s, W_m])
                else:
                    W_s.Placement = App.Placement(App.Vector(0, 0, z + hseparator), App.Rotation(App.Vector(0, 0, 1), angle))
                    W_m.Placement = App.Placement(App.Vector(0, 0, z + hseparator), App.Rotation(App.Vector(0, 0, 1), tita + angle2))
                    W_m.reverse()
                    middleFace = Face([W_m, W_s])
                faces.append(middleFace)

            Solid_sm = makeSolid(makeShell(faces))

            fp.Shape = Solid_sm

            W_s = getWire(slave)
            fp.W_s = W_s

        updatePosition(fp)
        self.betaChanged = False


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

    def __init__(self, fp, form):
        self.Type = 'internalGear'
        fp.Proxy = self

        addMasterProperties(fp, form[0], form[1])
            
        fp.addProperty('App::PropertyLength', 'extThickness', '1 - Gears Parameters', 'External thickness').extThickness = form[0].doubleSpinBox_7.text()

    def execute(self, fp):
        inputData = inputDataClass(fp.m.Value, fp.phi_s.Value, fp.N_m, fp.N_s, fp.Bl.Value, fp.c, fp.deltaCs.Value, fp.deltatp.Value, fp.offset_m.Value, fp.offset_s.Value, fp.n, fp.iL,fp.addendum_master)
        cD = commonData()
        master = gearData()
        slave = gearData()

        mainCalculations(inputData, cD, master, slave, True)

        getProfile(master, slave, cD, True)
        inputData = inputDataClass(fp.m.Value, fp.phi_s.Value, fp.N_m, fp.N_s, fp.Bl.Value, fp.c_slave, fp.deltaCs.Value, fp.deltatp.Value, fp.offset_m.Value, fp.offset_s.Value, fp.n, fp.iL,fp.addendum_slave)
        mainCalculations(inputData, cD, master, slave, True)

        getProfile(slave, master, cD)

        loadProperties(fp, cD, master, slave)
      
        fp.Cs.Value = abs(master.Rs - slave.Rs)
        fp.Center_d.Value = abs(master.Rp - slave.Rp)
        fp.angle_s.Value = slave.beta0 * 180 / pi - 180 + 180 / fp.N_s

        W_m = getWire(master)

        fp.thickness.Value = fp.thickness.Value + 0.005
        Solid_m = getInternalShape(fp, W_m)

        thickness = fp.thickness.Value - 0.005
        cylinder = makeCylinder(master.RTc + fp.extThickness.Value, thickness)
        Solid_m = cylinder.cut(Solid_m)
        fp.Shape = Solid_m

        W_s = getWire(slave)
        fp.W_s = W_s


class ViewProviderMasterBevelGear():
    def __init__(self, obj):
        obj.Proxy = self

    def attach(self, vobj):
        self.vobj = vobj

    def getIcon(self):
        return ":/icons/master_bevel_gear.svg"

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


class MasterBevelGear():

    def __init__(self, fp, form):
        self.Type = 'masterBevelGear'
        fp.Proxy = self

        addMasterProperties(fp, form[0], form[1], True)

    def execute(self, fp):
        inputData = inputDataClass_b(fp.m.Value, fp.rho.Value, fp.N_m, fp.N_s, fp.Bl.Value, fp.thickness.Value, fp.Sigma.Value, fp.c, fp.deltatp.Value, fp.n, fp.iL,fp.addendum_master)
        cD = commonData_b()
        master = gearData_b()
        slave = gearData_b()

        mainCalculations_b(inputData, cD, master, slave)

        getProfile_b(master, slave, cD)

        inputData = inputDataClass_b(fp.m.Value, fp.rho.Value, fp.N_m, fp.N_s, fp.Bl.Value, fp.thickness.Value, fp.Sigma.Value, fp.c_slave, fp.deltatp.Value, fp.n, fp.iL,fp.addendum_slave)
        mainCalculations_b(inputData, cD, master, slave)
        getProfile_b(slave, master, cD)

        loadProperties(fp, cD, master, slave, True)

        W_m = getBevelWire(master)

        Solid_m = getBevelShape(fp, W_m)
        fp.Shape = Solid_m

        W_s = getBevelWire(slave)
        fp.W_s = W_s


class ViewProviderSlaveBevelGear():
    def __init__(self, obj):
        obj.Proxy = self

    def attach(self, vobj):
        self.vobj = vobj

    def getIcon(self):
        return ":/icons/master_bevel_gear.svg"

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


class SlaveBevelGear():

    def __init__(self, fp, fp_master, angle):
        self.Type = 'slaveBevelGear'
        fp.Proxy = self

        addSlaveProperties(fp, fp_master, angle)

        part_slave = getPartFromFPBevelSlave(fp)
        part_slave.addProperty('App::PropertyFloat', 'relation', 'Gear relation', 'Gear relation')

        addAdditionalProperties(fp)
        slaveBevelPartExpressions(fp, fp_master)

        self.betaChanged = False

    def onChanged(self, fp, prop):
        if prop == "beta":
            self.betaChanged = True
        else:
            self.betaChanged = False

    def execute(self, fp):
        if self.betaChanged is False:
            fp_master = fp.fp_master

            Solid_s = getBevelShape(fp_master, None, True)
            fp.Shape = Solid_s

        updatePosition(fp)
        self.betaChanged = False
