# ***************************************************************************
# *   Copyright (c) 2021 Sebastian Ernesto García <sebasg@outlook.com>      *
# *                                                                         *
# *   properties.py                                                         *
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

from numpy import pi
from freecad.invgears.functions import getPartFromFPSlave, getPartFromFPBevelSlave


def loadProperties(fp, cD, gear, pinion, bevel=False):
    if bevel is True:
        fp.lambda_.Value = cD.lambda_
    fp.phi_p.Value = cD.phi_p * 180 / pi
    if bevel is False:
        fp.psi_s.Value = cD.psi_s * 180 / pi
    fp.psi_p.Value = cD.psi_p * 180 / pi
    if bevel is False:
        fp.Cs.Value = cD.Cs
        fp.C.Value = cD.C
        fp.ps.Value = cD.ps
    fp.pp.Value = cD.pp
    fp.pb.Value = cD.pb
    fp.pd.Value = cD.pd
    fp.B.Value = cD.B
    fp.mc = cD.mc
    fp.FourthCond = cD.FourthCond

    if bevel is False:
        fp.Rs_m.Value = gear.Rs
    fp.Rp_m.Value = gear.Rp
    fp.Rb_m.Value = gear.Rb
    fp.RT_m.Value = gear.RT
    fp.Rroot_m.Value = gear.Rroot
    fp.RL_m.Value = gear.RL
    fp.Rf_m.Value = gear.Rf
    fp.Ru_m.Value = gear.Ru
    if bevel is False:
        fp.ts_m.Value = gear.ts
    fp.tp_m.Value = gear.tp
    fp.tb_m.Value = gear.tb
    fp.tT_m.Value = gear.tT
    if bevel is False:
        fp.e_m.Value = gear.e
        fp.as_m.Value = gear.as_
    fp.ap_m.Value = gear.ap
    if bevel is False:
        fp.bs_m.Value = gear.bs
    fp.bp_m.Value = gear.bp
    fp.FirstCond_m = gear.FirstCond
    fp.SecondCond_m = gear.SecondCond
    fp.ThirdCond_m = gear.ThirdCond

    if bevel is False:
        fp.Rs_s.Value = pinion.Rs
    fp.Rp_s.Value = pinion.Rp
    fp.Rb_s.Value = pinion.Rb
    fp.RT_s.Value = pinion.RT
    fp.Rroot_s.Value = pinion.Rroot
    fp.RL_s.Value = pinion.RL
    fp.Rf_s.Value = pinion.Rf
    fp.Ru_s.Value = pinion.Ru
    if bevel is False:
        fp.ts_s.Value = pinion.ts
    fp.tp_s.Value = pinion.tp
    fp.tb_s.Value = pinion.tb
    fp.tT_s.Value = pinion.tT
    if bevel is False:
        fp.e_s.Value = pinion.e
        fp.as_s.Value = pinion.as_
    fp.ap_s.Value = pinion.ap
    if bevel is False:
        fp.bs_s.Value = pinion.bs
    fp.bp_s.Value = pinion.bp
    fp.angle_s.Value = pinion.beta0 * 180 / pi
    fp.FirstCond_s = pinion.FirstCond
    fp.SecondCond_s = pinion.SecondCond
    fp.ThirdCond_s = pinion.ThirdCond

def addMasterProperties(fp, widget1, widget2, bevel=False):
        fp.addProperty('App::PropertyLength', 'm', '1 - Gears Parameters', 'Module').m = widget1.doubleSpinBox.text()
        if bevel is False:
            fp.addProperty('App::PropertyAngle', 'phi_s', '1 - Gears Parameters', 'Standard pressure angle').phi_s = widget1.doubleSpinBox_2.text()
        else:
            fp.addProperty('App::PropertyAngle', 'rho', '1 - Gears Parameters', 'Standard pressure angle').rho = widget1.doubleSpinBox_2.text()
        fp.addProperty('App::PropertyInteger', 'N_m', '1 - Gears Parameters', 'Number of master gear teeth').N_m = widget1.spinBox.value()
        fp.addProperty('App::PropertyInteger', 'N_s', '1 - Gears Parameters', 'Number of slave gear teeth').N_s = widget1.spinBox_2.value()
        fp.addProperty('App::PropertyLength', 'Bl', '1 - Gears Parameters', 'Backlash along the line of action').Bl = widget1.doubleSpinBox_3.text()
        if bevel is False:
            fp.addProperty('App::PropertyEnumeration', 'gearType', '1 - Gears Parameters', 'Gear type').gearType = ["Spur", "Helical", "Double Helical"]
            fp.gearType = widget1.comboBox.currentText()
            fp.addProperty('App::PropertyFloat', 'helicalPortion', '1 - Gears Parameters', 'Helical portion').helicalPortion = widget1.doubleSpinBox_4.value()
        fp.addProperty('App::PropertyLength', 'thickness', '1 - Gears Parameters', 'Gear thickness').thickness = widget1.doubleSpinBox_5.text()
        if bevel is True:
            fp.addProperty('App::PropertyAngle', 'Sigma', '1 - Gears Parameters', 'Angle between gear axes').Sigma = widget1.doubleSpinBox_6.text()

        fp.addProperty('App::PropertyFloat', 'c', '2 - Additional Parameters', 'Clearance / module').c = widget2.doubleSpinBox.value()
        if bevel is False:
            fp.addProperty('App::PropertyDistance', 'deltaCs', '2 - Additional Parameters', 'Center distance offset').deltaCs = widget2.doubleSpinBox_2.text()
        fp.addProperty('App::PropertyDistance', 'deltatp', '2 - Additional Parameters', 'Tooth thickness offset').deltatp = widget2.doubleSpinBox_3.text()
        if bevel is False:
            fp.addProperty('App::PropertyDistance', 'offset_m', '2 - Additional Parameters', 'Offset for master gear').offset_m = widget2.doubleSpinBox_4.text()
            fp.addProperty('App::PropertyDistance', 'offset_s', '2 - Additional Parameters', 'Offset for slave gear').offset_s = widget2.doubleSpinBox_5.text()
        fp.addProperty('App::PropertyInteger', 'n', '2 - Additional Parameters', 'Number of points on the curves').n = widget2.spinBox.value()
        fp.addProperty('App::PropertyFloat', 'iL', '2 - Additional Parameters', 'Limit of second Interference').iL = widget2.doubleSpinBox_6.value()
        
        if bevel is True:
            fp.addProperty('App::PropertyLength', 'lambda_', '3 - Common data', 'Spherical radius', 1)
        fp.addProperty('App::PropertyAngle', 'phi_p', '3 - Common data', 'Pressure angle', 1)
        if bevel is False:
            fp.addProperty('App::PropertyAngle', 'psi_s', '3 - Common data', 'Involute function of phi_s', 1)
        fp.addProperty('App::PropertyAngle', 'psi_p', '3 - Common data', 'Involute function of phi', 1)
        if bevel is False:
            fp.addProperty('App::PropertyLength', 'Cs', '3 - Common data', 'Standard center distance', 1)
            fp.addProperty('App::PropertyLength', 'C', '3 - Common data', 'Center distance', 1)
            fp.addProperty('App::PropertyLength', 'ps', '3 - Common data', 'Standard Circular pitch', 1)
        fp.addProperty('App::PropertyLength', 'pp', '3 - Common data', 'Circular pitch', 1)
        fp.addProperty('App::PropertyLength', 'pb', '3 - Common data', 'Base Circular pitch', 1)
        fp.addProperty('App::PropertyLength', 'pd', '3 - Common data', 'Diametral pitch', 1)
        fp.addProperty('App::PropertyLength', 'B', '3 - Common data', 'Circular Backlash', 1)
        fp.addProperty('App::PropertyFloat', 'mc', '3 - Common data', 'Contact Ratio', 1)
        fp.addProperty('App::PropertyBool', 'FourthCond', '3 - Common data', 'Fourth Condition', 1)
        
        if bevel is False:
            fp.addProperty('App::PropertyLength', 'Rs_m', '4 - Master gear data', 'Standard Pitch Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'Rp_m', '4 - Master gear data', 'Pitch Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'Rb_m', '4 - Master gear data', 'Base Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'RT_m', '4 - Master gear data', 'Tip Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'Rroot_m', '4 - Master gear data', 'Root Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'RL_m', '4 - Master gear data', 'Limit Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'Rf_m', '4 - Master gear data', 'Fillet Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'Ru_m', '4 - Master gear data', 'Undercut Circle Radius', 1)
        if bevel is False:
            fp.addProperty('App::PropertyLength', 'ts_m', '4 - Master gear data', 'Tooth thickness at the standard pitch circle', 1)
        fp.addProperty('App::PropertyLength', 'tp_m', '4 - Master gear data', 'Tooth thickness at the pitch circle', 1)
        fp.addProperty('App::PropertyLength', 'tb_m', '4 - Master gear data', 'Tooth thickness at the base circle', 1)
        fp.addProperty('App::PropertyLength', 'tT_m', '4 - Master gear data', 'Tooth thickness at the tip circle', 1)
        if bevel is False:        
            fp.addProperty('App::PropertyDistance', 'e_m', '4 - Master gear data', 'Profile Shift', 1)
            fp.addProperty('App::PropertyLength', 'as_m', '4 - Master gear data', 'Standard Pitch Circle Addendum', 1)
        fp.addProperty('App::PropertyLength', 'ap_m', '4 - Master gear data', 'Pitch Circle Addendum', 1)
        if bevel is False:
            fp.addProperty('App::PropertyLength', 'bs_m', '4 - Master gear data', 'Standard Pitch Circle Dedendum', 1)
        fp.addProperty('App::PropertyLength', 'bp_m', '4 - Master gear data', 'Pitch Circle Dedendum', 1)
        fp.addProperty('App::PropertyBool', 'FirstCond_m', '4 - Master gear data', 'First Condition', 1)
        fp.addProperty('App::PropertyBool', 'SecondCond_m', '4 - Master gear data', 'Second Condition', 1)
        fp.addProperty('App::PropertyBool', 'ThirdCond_m', '4 - Master gear data', 'Third Condition', 1)
        
        if bevel is False:
            fp.addProperty('App::PropertyLength', 'Rs_s', '5 - Slave gear data', 'Standard Pitch Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'Rp_s', '5 - Slave gear data', 'Pitch Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'Rb_s', '5 - Slave gear data', 'Base Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'RT_s', '5 - Slave gear data', 'Tip Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'Rroot_s', '5 - Slave gear data', 'Root Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'RL_s', '5 - Slave gear data', 'Limit Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'Rf_s', '5 - Slave gear data', 'Fillet Circle Radius', 1)
        fp.addProperty('App::PropertyLength', 'Ru_s', '5 - Slave gear data', 'Undercut Circle Radius', 1)
        if bevel is False:
            fp.addProperty('App::PropertyLength', 'ts_s', '5 - Slave gear data', 'Tooth thickness at the standard pitch circle', 1)
        fp.addProperty('App::PropertyLength', 'tp_s', '5 - Slave gear data', 'Tooth thickness at the pitch circle', 1)
        fp.addProperty('App::PropertyLength', 'tb_s', '5 - Slave gear data', 'Tooth thickness at the base circle', 1)
        fp.addProperty('App::PropertyLength', 'tT_s', '5 - Slave gear data', 'Tooth thickness at the tip circle', 1)
        if bevel is False:
            fp.addProperty('App::PropertyDistance', 'e_s', '5 - Slave gear data', 'Profile Shift', 1)
            fp.addProperty('App::PropertyLength', 'as_s', '5 - Slave gear data', 'Standard Pitch Circle Addendum', 1)
        fp.addProperty('App::PropertyLength', 'ap_s', '5 - Slave gear data', 'Pitch Circle Addendum', 1)
        if bevel is False:
            fp.addProperty('App::PropertyLength', 'bs_s', '5 - Slave gear data', 'Standard Pitch Circle Dedendum', 1)
        fp.addProperty('App::PropertyLength', 'bp_s', '5 - Slave gear data', 'Pitch Circle Dedendum', 1)
        fp.addProperty('App::PropertyAngle', 'angle_s', '5 - Slave gear data', 'Gear orientation', 1)
        fp.addProperty('App::PropertyBool', 'FirstCond_s', '5 - Slave gear data', 'First Condition', 1)
        fp.addProperty('App::PropertyBool', 'SecondCond_s', '5 - Slave gear data', 'Second Condition', 1)
        fp.addProperty('App::PropertyBool', 'ThirdCond_s', '5 - Slave gear data', 'Third Condition', 1)
        fp.addProperty('Part::PropertyPartShape', 'W_s', '5 - Slave gear data', 'Pinion Wire', 1)

def addSlaveProperties(fp, fp_master, angle):
    fp.addProperty('App::PropertyLinkGlobal', 'fp_master', 'Slave gear data', 'Master Feature Python').fp_master = fp_master
    fp.addProperty('App::PropertyBool', 'attachToMaster', 'Slave gear data', 'Attach to master').attachToMaster = True

    fp.addProperty('App::PropertyAngle', 'beta', 'Slave gear data', 'Initial Position Angle').beta = angle

def addAdditionalProperties(fp):
    part_slave = getPartFromFPBevelSlave(fp)
    part_slave.addProperty('App::PropertyPrecision', 'q1z', 'Position Calculus', 'z value of q1', 4)
    part_slave.addProperty('App::PropertyPrecision', 'q1w', 'Position Calculus', 'w value of q1', 4)

    part_slave.addProperty('App::PropertyPrecision', 'q2y', 'Position Calculus', 'y value of q2', 4)
    part_slave.addProperty('App::PropertyPrecision', 'q2w', 'Position Calculus', 'w value of q2', 4)

    part_slave.addProperty('App::PropertyPrecision', 'q3z', 'Position Calculus', 'z value of q3', 4)
    part_slave.addProperty('App::PropertyPrecision', 'q3w', 'Position Calculus', 'w value of q3', 4)
    
    part_slave.addProperty('App::PropertyPrecision', 'qrx', 'Position Calculus', 'x value of qr', 4)
    part_slave.addProperty('App::PropertyPrecision', 'qry', 'Position Calculus', 'y value of qr', 4)
    part_slave.addProperty('App::PropertyPrecision', 'qrz', 'Position Calculus', 'z value of qr', 4)
    part_slave.addProperty('App::PropertyPrecision', 'qrw', 'Position Calculus', 'w value of qr', 4)

    part_slave.addProperty('App::PropertyAngle', 'rotationAxis', 'Positions', 'Rotation about axis')
    part_slave.addProperty('App::PropertyDistance', 'xPos', 'Positions', 'x position')
    part_slave.addProperty('App::PropertyDistance', 'yPos', 'Positions', 'x position')    
