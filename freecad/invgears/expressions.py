# ***************************************************************************
# *   Copyright (c) 2021 Sebastian Ernesto García <sebasg@outlook.com>      *
# *                                                                         *
# *   expressions.py                                                        *
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
from freecad.invgears.functions import getPartFromFPMaster, getPartFromFPSlave, getPartFromFPBevelSlave


def slavePartExpressions(fp, fp_master):
    part_master = getPartFromFPMaster(fp_master)
    part_slave = getPartFromFPSlave(fp)

    x = f"{part_master.Name}.Placement.Base.x"
    y = f"{part_master.Name}.Placement.Base.y"
    z = f"{part_master.Name}.Placement.Base.z"
    C = f"{fp_master.Name}.C"

    N_m = f"{fp_master.Name}.N_m"
    N_s = f"{fp_master.Name}.N_s"

    relation = f"({N_m} / {N_s})"
    global_relation = relation

    if fp_master.Proxy.Type == "masterGear" or fp_master.Proxy.Type == "internalGear":
        masterRotation = f"{part_master.Name}.masterRotation"
        slaveAngularPosition = f"{part_master.Name}.slaveAngularPosition"
    elif fp_master.Proxy.Type == "slaveMasterGear":
        masterRotation = f"{part_master.Name}.Placement.Rotation.Angle"
        master_beta = f"{fp_master.Name}.beta"
        part_Previusmaster = getPartFromFPMaster(fp_master.fp_master)
        slaveAngularPositions = f"{part_Previusmaster.Name}.slaveAngularPosition"
        last_fp_master = fp_master
        while True:
            last_fp_master = last_fp_master.fp_master
            N_m = f"{last_fp_master.Name}.N_m"
            N_s = f"{last_fp_master.Name}.N_s"
            global_relation = f"{global_relation} * ({N_m} / {N_s})"

            if last_fp_master.Proxy.Type == "slaveMasterGear":
                master_beta = f"{master_beta} + {last_fp_master.Name}.beta"

                part_Previusmaster = getPartFromFPMaster(last_fp_master.fp_master)

                slaveAngularPositions = f"{slaveAngularPositions} + {part_Previusmaster.Name}.slaveAngularPosition"
            else:
                break
        slaveAngularPosition = f"({part_master.Name}.slaveAngularPosition + {slaveAngularPositions} + {master_beta})"

    beta = f"{fp.Name}.beta"
    xp = f"{x} + {C} * cos({beta} + {slaveAngularPosition})"
    yp = f"{y} + {C} * sin({beta} + {slaveAngularPosition})"
    if fp_master.Proxy.Type == "slaveMasterGear":
        hseparator = f"{fp_master.Name}.hseparator"
        if fp_master.hseparator.Value < 0.0:
            thickness = f"{fp_master.Name}.thickness"
            zp = f"{z} + {hseparator} - {thickness}"
        else:
            thickness = f"{fp_master.fp_master.Name}.thickness"
            zp = f"{z} + {hseparator} + {thickness}"
    else:
        zp = f"{z}"

    if fp_master.Proxy.Type == "masterGear" or fp_master.Proxy.Type == "slaveMasterGear":
        angle = f"{beta} + {slaveAngularPosition} + ({slaveAngularPosition} - {masterRotation}) * {relation}"
    elif fp_master.Proxy.Type == "internalGear":
        angle = f"{beta} + {slaveAngularPosition} + (-{slaveAngularPosition} + {masterRotation}) * {relation}"

    part_slave.setExpression("Placement", f"create(<<placement>>; create(<<vector>>; {xp}; {yp}; {zp}); create(<<rotation>>; create(<<vector>>; 0; 0; 1); {angle}))")
    part_slave.setExpression("relation", relation)
    part_slave.setExpression("global_relation", global_relation)


def slaveBevelPartExpressions(fp, fp_master):
    part_slave = getPartFromFPBevelSlave(fp)
    Sigma = f"{fp_master.Name}.Sigma"
    beta = f"{fp.Name}.beta"
    for part in fp_master._Body.InList:
        if part.Type == "Part_Master_Bevel":
            part_master = part
    masterRotation = f"{part_master.Name}.masterRotation"
    slaveAngularPosition = f"{part_master.Name}.slaveAngularPosition"
    N_m = f"{fp_master.Name}.N_m"
    N_s = f"{fp_master.Name}.N_s"

    relation = f"({N_m} / {N_s})"
    part_slave.setExpression("relation", relation)

    gamma = f"({beta} + {slaveAngularPosition})"
    theta = f"(({slaveAngularPosition} - {masterRotation}) * {relation})"
    part_slave.setExpression("rotationAxis", f"{theta}")
    lambda_ = f"{fp_master.Name}.lambda_"
    xPos = f"{lambda_} * cos({gamma}) * sin({Sigma})"
    yPos = f"{lambda_} * sin({gamma}) * sin({Sigma})"
    part_slave.setExpression("rotationAxis", f"{theta}")
    part_slave.setExpression("xPos", f"{xPos}")
    part_slave.setExpression("yPos", f"{yPos}")
    part_slave.setExpression("q1z", f"sin({theta} / 2)")
    part_slave.setExpression("q1w", f"cos({theta} / 2)")
    part_slave.setExpression("q2y", f"sin({Sigma} / 2)")
    part_slave.setExpression("q2w", f"cos({Sigma} / 2)")
    part_slave.setExpression("q3z", f"sin({gamma} / 2)")
    part_slave.setExpression("q3w", f"cos({gamma} / 2)")
    q1z = f"{part_slave.Name}.q1z"
    q1w = f"{part_slave.Name}.q1w"
    q2y = f"{part_slave.Name}.q2y"
    q2w = f"{part_slave.Name}.q2w"
    q3z = f"{part_slave.Name}.q3z"
    q3w = f"{part_slave.Name}.q3w"
    part_slave.setExpression("qrx", f"{q1z} * {q2y} * {q3w} - {q1w} * {q2y} * {q3z}")
    part_slave.setExpression("qry", f"{q1z} * {q2y} * {q3z} + {q1w} * {q2y} * {q3w}")
    part_slave.setExpression("qrz", f"{q1w} * {q2w} * {q3z} + {q1z} * {q2w} * {q3w}")
    part_slave.setExpression("qrw", f"{q1w} * {q2w} * {q3w} - {q1z} * {q2w} * {q3z}")
    qrx = f"{part_slave.Name}.qrx"
    qry = f"{part_slave.Name}.qry"
    qrz = f"{part_slave.Name}.qrz"
    qrw = f"{part_slave.Name}.qrw"

    part_slave.setExpression("Placement", f"create(<<placement>>; create(<<vector>>; 0; 0; 0); create(<<rotation>>; create(<<vector>>; {qrx} / sqrt(1- {qrz}^2); {qry} / sqrt(1- {qrz}^2); {qrz} / sqrt(1- {qrz}^2)); 2*atan(sqrt({qrz}^2+{qry}^2+{qrx}^2)/{qrw})))")
