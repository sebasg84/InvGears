
# ***************************************************************************
# *   Copyright (c) 2021 Sebastian Ernesto García <sebasg@outlook.com>      *
# *                                                                         *
# *   functions.py                                                            *
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
from Part import makeHelix, makeSolid, makeShell, Face
from numpy import pi


def loadProperties(fp, cD, gear, pinion):
    fp.phi_p.Value = cD.phi_p * 180 / pi
    fp.inv_phi_s.Value = cD.inv_phi_s * 180 / pi
    fp.inv_phi_p.Value = cD.inv_phi_p * 180 / pi
    fp.Cs.Value = cD.Cs
    fp.C.Value = cD.C
    fp.ps.Value = cD.ps
    fp.pp.Value = cD.pp
    fp.pb.Value = cD.pb
    fp.pd.Value = cD.pd
    fp.rcT.Value = cD.rcT
    fp.B.Value = cD.B
    fp.mc = cD.mc
    fp.FourthCond = cD.FourthCond

    fp.m_Rs.Value = gear.Rs
    fp.m_Rp.Value = gear.Rp
    fp.m_Rb.Value = gear.Rb
    fp.m_RT.Value = gear.RT
    fp.m_Rroot.Value = gear.Rroot
    fp.m_RL.Value = gear.RL
    fp.m_Rf.Value = gear.Rf
    fp.m_Ru.Value = gear.Ru
    fp.m_ts.Value = gear.ts
    fp.m_tp.Value = gear.tp
    fp.m_tb.Value = gear.tb
    fp.m_tT.Value = gear.tT
    fp.m_e.Value = gear.e
    fp.m_as.Value = gear.as_
    fp.m_ap.Value = gear.ap
    fp.m_bs.Value = gear.bs
    fp.m_bp.Value = gear.bp
    fp.m_FirstCond = gear.FirstCond
    fp.m_SecondCond = gear.SecondCond
    fp.m_ThirdCond = gear.ThirdCond

    fp.s_Rs.Value = pinion.Rs
    fp.s_Rp.Value = pinion.Rp
    fp.s_Rb.Value = pinion.Rb
    fp.s_RT.Value = pinion.RT
    fp.s_Rroot.Value = pinion.Rroot
    fp.s_RL.Value = pinion.RL
    fp.s_Rf.Value = pinion.Rf
    fp.s_Ru.Value = pinion.Ru
    fp.s_ts.Value = pinion.ts
    fp.s_tp.Value = pinion.tp
    fp.s_tb.Value = pinion.tb
    fp.s_tT.Value = pinion.tT
    fp.s_e.Value = pinion.e
    fp.s_as.Value = pinion.as_
    fp.s_ap.Value = pinion.ap
    fp.s_bs.Value = pinion.bs
    fp.s_bp.Value = pinion.bp
    fp.s_angle.Value = pinion.beta0 * 180 / pi
    fp.s_FirstCond = pinion.FirstCond
    fp.s_SecondCond = pinion.SecondCond
    fp.s_ThirdCond = pinion.ThirdCond


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


def doblehelicalextrusion(wire, height, angle, vPos=App.Vector(0, 0, 0), orientation=0):
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
