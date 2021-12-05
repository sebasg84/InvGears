
# ***************************************************************************
# *   Copyright (c) 2021 Sebastian Ernesto García <sebasg@outlook.com>      *
# *                                                                         *
# *   functions.py                                                          *
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
from Part import makeHelix, makeSolid, makeShell, Wire, Face, Arc, BSplineCurve, makeSphere, Point, makeLoft
from numpy import pi, sin, cos, arctan, array, sqrt


def commonextrusion(wire, height, vPos=App.Vector(0, 0, 0), orientation=0):
    wire.Placement = App.Placement(vPos, App.Rotation(App.Vector(0, 0, 1), orientation))
    face = Face(wire)
    solid = face.extrude(App.Vector(0.0, 0.0, height))
    return solid


def helicalextrusion(wire, height, angle, vPos=App.Vector(0, 0, 0), orientation=0):
    direction = bool(angle < 0)
    first_spine = makeHelix(height * (2 * pi / abs(angle)), height, height, 0, direction)
    first_spine.Placement = App.Placement(vPos, App.Rotation(App.Vector(0, 0, 1), 0))
    wire.Placement = App.Placement(vPos, App.Rotation(App.Vector(0, 0, 1), orientation))
    first_solid = first_spine.makePipeShell([wire], True, True)
    return first_solid


def doublehelicalextrusion(wire, height, angle, vPos=App.Vector(0, 0, 0), orientation=0):
    direction = bool(angle < 0)
    first_spine = makeHelix((height / 2) * (2 * pi / abs(angle)), height / 2, height, 0, direction)
    first_spine.Placement = App.Placement(vPos, App.Rotation(App.Vector(0, 0, 1), 0))
    wire.Placement = App.Placement(vPos, App.Rotation(App.Vector(0, 0, 1), orientation))
    first_solid = first_spine.makePipeShell([wire], True, True)
    second_solid = first_solid.mirror(App.Vector(0, 0, vPos.z + height / 2), App.Vector(0, 0, 1))
    faces = first_solid.Faces + second_solid.Faces
    faces = [f for f in faces if not (abs(f.CenterOfMass.z - (vPos.z + height / 2)) < 0.001)]
    solid = makeSolid(makeShell(faces))
    return solid


def getMasterShape(fp, W, z=0.0, tita=0.0):
    thickness = fp.thickness.Value
    if fp.gearType == "Spur":
        Solid = commonextrusion(W, thickness, App.Vector(0, 0, z), tita)
    if fp.gearType == "Helical":
        helicalAngle = fp.helicalPortion * (2 * pi / fp.N_m)
        Solid = helicalextrusion(W, thickness, helicalAngle, App.Vector(0, 0, z), tita)
    if fp.gearType == "Double Helical":
        helicalAngle = fp.helicalPortion * (2 * pi / fp.N_m)
        Solid = doublehelicalextrusion(W, thickness, helicalAngle, App.Vector(0, 0, z), tita)
    return Solid


def getSlaveShape(fp_master):
    thickness = fp_master.thickness.Value
    W = fp_master.W_s.copy()
    if fp_master.gearType == "Spur":
        Solid = commonextrusion(W, thickness)
    if fp_master.gearType == "Helical":
        helicalAngle = -fp_master.helicalPortion * (2 * pi / fp_master.N_s)
        Solid = helicalextrusion(W, thickness, helicalAngle)
    if fp_master.gearType == "Double Helical":
        helicalAngle = -fp_master.helicalPortion * (2 * pi / fp_master.N_s)
        Solid = doublehelicalextrusion(W, thickness, helicalAngle)
    return Solid


def getInternalShape(fp, W, z=0.0, tita=0.0):
    thickness = fp.thickness.Value
    if fp.gearType == "Spur":
        Solid = commonextrusion(W, thickness, App.Vector(0, 0, z), tita)
    if fp.gearType == "Helical":
        helicalAngle = - fp.helicalPortion * (2 * pi / fp.N_m)
        Solid = helicalextrusion(W, thickness, helicalAngle, App.Vector(0, 0, z), tita)
    if fp.gearType == "Double Helical":
        helicalAngle = - fp.helicalPortion * (2 * pi / fp.N_m)
        Solid = doublehelicalextrusion(W, thickness, helicalAngle, App.Vector(0, 0, z), tita)
    return Solid


def getBevelShape(fp, W, slave=False):
    if slave is True:
        W = fp.W_s.copy()
    s1 = makeSphere(fp.lambda_.Value, App.Vector(0, 0, 0))
    s2 = makeSphere(fp.lambda_.Value + fp.thickness.Value, App.Vector(0, 0, 0))
    s3=s2.cut(s1)

    origin_vertex = Point(App.Vector(0,0,0)).toShape()

    loft = makeLoft([W, origin_vertex], True)

    solid = s3.common(loft)
    return solid


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


def getBevelWire(gear):
    S = []
    index = 1
    for profile in gear.profile_onPlane:
        if index % 3 == 0:
            arc = Arc(*list(map(lambda x, y, z: App.Vector(x, y, z), profile[0, :], profile[1, :], profile[2, :])))
            S.append(arc.toShape())
        else:
            curve = BSplineCurve()
            curve.interpolate(list(map(lambda x, y, z: App.Vector(x, y, z), profile[0, :], profile[1, :], profile[2, :])))
            S.append(curve.toShape())
        index = index + 1
    W = Wire(S)
    return W


def updatePosition(fp):
    fp_master = fp.fp_master
    body = fp._Body
    beta = fp.beta.Value
    angle_s = fp_master.angle_s.Value
    body_master_angle = fp_master._Body.Placement.Rotation.Angle * 180 / pi

    if fp_master.Proxy.Type == "masterGear" or fp_master.Proxy.Type == "masterBevelGear":
        angle = angle_s + (beta - body_master_angle) * (fp_master.N_m / fp_master.N_s)
    elif fp_master.Proxy.Type == "slaveMasterGear":
        tita = fp_master.tita.Value
        angle = angle_s + (beta - tita - body_master_angle) * (fp_master.N_m / fp_master.N_s)
    elif fp_master.Proxy.Type == "internalGear":
        angle = angle_s + (-beta + body_master_angle) * (fp_master.N_m / fp_master.N_s)
    
    body.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(0, 0, 1), angle))


def getPartFromFPMaster(fp):
    for part in fp._Body.InList:
        if part.Type == "Part_Master" or part.Type == "Part_Slave_Master" or part.Type == "Part_Internal":
            return part


def getPartFromFPSlave(fp):
    for part in fp._Body.InList:
        if part.Type == "Part_Slave" or part.Type == "Part_Slave_Master":
            return part

def getPartFromFPBevelSlave(fp):
    for part in fp._Body.InList:
        if part.Type == "Part_Slave_Bevel":
            return part