# ***************************************************************************
# *   Copyright (c) 2021 Sebastian Ernesto García <sebasg@outlook.com>      *
# *                                                                         *
# *   gears.py                                                            *
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

from dataclasses import dataclass
from numpy import NaN, pi, sqrt, sin, cos, tan, arcsin, arccos, arctan, linspace, array, size, dot
from numpy.core.shape_base import hstack, vstack
from numpy.linalg import norm


class getProfile():

    def __init__(self, gear, pinion, cD, internal=False):

        i_ps, i_norm = self.__involute(gear, cD, internal)
        f_ps, f_norm = self.__fillet(gear, pinion, cD)

        middle_p = (i_ps[:, -1] + f_ps[:, 0]) / 2
        i_ps[:, -1] = middle_p
        f_ps[:, 0] = middle_p

        if internal:
            RTg = gear.RTc
        else:
            RTg = gear.RT

        Rroot = gear.Rroot

        if(abs(gear.offset) > 0.00001):
            i_ps = i_ps - gear.offset * i_norm
            f_ps = f_ps - gear.offset * f_norm
            RTg = RTg - gear.offset
            Rroot = Rroot - gear.offset

            inter_p, i_index, f_index = self.__intersection(i_ps, f_ps)

            if(i_index == -1):
                middle_p = (i_ps[:, -1] + f_ps[:, 0]) / 2
                i_ps[:, -1] = middle_p
                f_ps[:, 0] = middle_p

            else:
                i_ps = hstack((i_ps[:, :i_index], inter_p))
                f_ps = hstack((inter_p, f_ps[:, f_index:]))
            
            inter_p, index = self.__tipIntersection(i_ps, RTg)
            i_ps = hstack((inter_p, i_ps[:, index:]))

        M = array([[1, 0], [0, -1]])
        i_ps_rev = dot(M, i_ps[:, ::-1])
        f_ps_rev = dot(M, f_ps[:, ::-1])
        tip_ps = hstack((i_ps_rev[:, [-1]], vstack([RTg, 0]), i_ps[:, [0]]))

        tita0 = gear.tita_Rroot
        titaf = 2 * pi / gear.N - tita0
        tita = linspace(tita0, titaf, 3)
        x = Rroot * cos(tita)
        y = Rroot * sin(tita)
        root_ps = vstack([x, y])

        tooth_profile = [f_ps_rev, i_ps_rev, tip_ps, i_ps, f_ps, root_ps]
        gear.tooth_profile = tooth_profile

        angle = 2 * pi / gear.N
        M = array([[cos(angle), -sin(angle)], [sin(angle), cos(angle)]])
        profile = tooth_profile
        aux_profile = tooth_profile
        for i in range(gear.N - 1):
            aux_profile = list(map(lambda x: dot(M, x), aux_profile))
            profile.extend(aux_profile)

        gear.profile = profile

    def __tipIntersection(self, i_ps, RTg):
        for i in range(size(i_ps, 1)):
            if norm(i_ps[:, i + 1]) < RTg:
                index = i
                break

        xA, yA = i_ps[:, index]
        xB, yB = i_ps[:, index + 1]
        m = (yB - yA) / (xB - xA)
        mxA = m * xA
        a = (1 + m**2)
        b = 2 * m * (yA - mxA)
        c = yA**2 + mxA**2 - 2 * yA * mxA - RTg**2
        x = (-b + sqrt(b**2 - 4 * a * c)) / (2 * a)
        y = yA + m * (x - xA)
        inter_p = vstack([x, y])
        index = index + 1
        return inter_p, index

    def __intersection(self, i_ps, f_ps):
        for i in range(size(i_ps, 1) - 1):
            for j in range(size(f_ps, 1) - 1):
                i_pA = i_ps[:, i]
                i_pB = i_ps[:, i + 1]
                f_pA = f_ps[:, j]
                f_pB = f_ps[:, j + 1]

                Di = i_pB - i_pA
                Df = f_pB - f_pA
                DA = i_pA - f_pA

                M = array([DA[0], -DA[1]]) / (Df[0] * Di[1] - Di[0] * Df[1])

                ki = dot(M, vstack([Df[1], Df[0]]))
                kf = dot(M, vstack([Di[1], Di[0]]))

                if 0 < ki < 1 and 0 < kf < 1:
                    inter_p = i_ps[:, [i]] + ki * (i_ps[:, [i + 1]] - i_ps[:, [i]])
                    i_index = i
                    f_index = j + 1
                    return inter_p, i_index, f_index

        return -1, -1, -1

    def __involute(self, gear, cD, internal):
        if internal:
            RTg = gear.RTc
        else:
            RTg = gear.RT
        Rc_r = gear.Rc_r
        Rbg = gear.Rb
        tbg = gear.tb
        n = cD.n
        R = linspace(RTg, Rc_r, n)
        phi_R = arccos(Rbg / R)
        inv_phi_R = sqrt(R**2 - Rbg**2) / Rbg - phi_R
        tita_R = tbg / (2 * Rbg) - inv_phi_R

        diff_tita_R = -sqrt(R**2 - Rbg**2) / (R * Rbg)

        x = array(R * cos(tita_R))
        y = array(R * sin(tita_R))

        dx = cos(tita_R) - R * sin(tita_R) * diff_tita_R
        dy = sin(tita_R) + R * cos(tita_R) * diff_tita_R
        xn = array(-dy / sqrt(dx**2 + dy**2))
        yn = array(dx / sqrt(dx**2 + dy**2))

        points = vstack([x, y])
        normal = vstack([xn, yn])

        gear.tita_RT = tita_R[0]

        return points, normal

    def __fillet(self, gear, pinion, cD):
        N = gear.N
        Rsg = gear.Rs
        Rpg = gear.Rp
        Rc_l = gear.Rc_l
        FirstCond = gear.FirstCond
        Rc_a = pinion.Rc_a
        tita_c_a = pinion.tita_c_a
        Rpc = pinion.Rp
        Rsc = pinion.Rs
        Rbc = pinion.Rb
        phi_p = cD.phi_p
        ps = cD.ps
        rcT = cD.rcT
        n = cD.n

        if not FirstCond:
            alpha = 0
            epsilon = 0.001 * pi / N
            while True:
                xi_a = Rpc - Rc_a * cos(alpha)
                eta_a = -Rc_a * sin(alpha)
                s_a = - sqrt(xi_a**2 + eta_a**2)
                s = s_a - rcT
                xi = (s / s_a) * xi_a
                eta = (s / s_a) * eta_a
                R = sqrt((Rpg + xi)**2 + eta**2)
                if R > Rc_l:
                    alpha0 = alpha - epsilon
                    break
                alpha = alpha + epsilon
        else:
            alpha0 = arccos(Rbc / Rc_a) - phi_p

        alphaf = 0.0
        alpha = linspace(alpha0, alphaf, n)
        xi_a = Rpc - Rc_a * cos(alpha)
        eta_a = -Rc_a * sin(alpha)
        s_a = - sqrt(xi_a**2 + eta_a**2)
        s = s_a - rcT
        xi = (s / s_a) * xi_a
        eta = (s / s_a) * eta_a

        betac = alpha - tita_c_a
        betag = - (Rsc * betac + (ps / 2)) / Rsg

        R = sqrt((Rpg + xi)**2 + eta**2)
        tita_R = arctan(eta / (Rpg + xi)) - betag

        diff_xi_a = Rc_a * sin(alpha)
        diff_eta_a = -Rc_a * cos(alpha)

        diff_s_a = - (xi_a * diff_xi_a + eta_a * diff_eta_a) / sqrt(xi_a**2 + eta_a**2)
        diff_s = diff_s_a

        diff_xi = ((diff_s * s_a - s * diff_s_a) / (s_a**2)) * xi_a + (s / s_a) * diff_xi_a
        diff_eta = ((diff_s * s_a - s * diff_s_a) / (s_a**2)) * eta_a + (s / s_a) * diff_eta_a

        diff_betag = - Rsc / Rsg

        diff_R = ((Rpg + xi) * diff_xi + eta * diff_eta) / sqrt((Rpg + xi)**2 + eta**2)
        diff_tita_R = (diff_eta * (Rpg + xi) - eta * diff_xi) / ((Rpg + xi)**2 + eta**2) - diff_betag

        x = array(R * cos(tita_R))
        y = array(R * sin(tita_R))

        dx = diff_R * cos(tita_R) - R * sin(tita_R) * diff_tita_R
        dy = diff_R * sin(tita_R) + R * cos(tita_R) * diff_tita_R
        xn = array(-dy / sqrt(dx**2 + dy**2))
        yn = array(dx / sqrt(dx**2 + dy**2))

        points = vstack([x, y])
        normal = vstack([xn, yn])

        gear.tita_Rroot = tita_R[-1]

        return points, normal


class mainCalculations():
    def __init__(self, inputData, cD, gear, pinion, internal=False):

        self.__get_load_commonData1(cD, inputData)

        self.__get_load_gearData1(gear, cD, inputData.Ng, inputData.m_offset, inputData.deltatp)
        self.__get_load_gearData1(pinion, cD, inputData.Np, inputData.s_offset, -gear.deltatp)

        self.__get_load_commonData2(cD, gear, pinion)

        self.__get_load_gearData2(gear, pinion, cD)
        self.__get_load_gearData2(pinion, gear, cD)

        gear.beta0 = 0.0
        pinion.beta0 = pi - ((gear.tp + pinion.tp) / 2 + gear.Rp * gear.beta0) / pinion.Rp

        self.__get_load_gearData3(gear, pinion, cD)
        self.__get_load_gearData3(pinion, gear, cD)

        self.__get_load_gearData4(gear, pinion, cD)
        self.__get_load_gearData4(pinion, gear, cD, internal)

        self.__get_load_gearData5(gear, pinion, cD)
        self.__get_load_gearData5(pinion, gear, cD)

        self.__get_load_gearData6(gear, pinion, cD)
        self.__get_load_gearData6(pinion, gear, cD)

        self.__get_load_commonData3(cD, gear, pinion)

    def __get_load_commonData1(self, cD, inputData):
        cD.m = inputData.m
        cD.phi_s = inputData.phi_s * pi / 180
        cD.deltaCs = inputData.deltaCs
        cD.c = inputData.c
        cD.rk = inputData.rk
        cD.Bn = inputData.Bn
        cD.iL = inputData.iL
        cD.n = inputData.n
        cD.ps = pi * cD.m
        cD.pb = cD.ps * cos(cD.phi_s)
        cD.pd = 1 / cD.m
        cD.rcT = cD.rk * cD.m

    def __get_load_gearData1(self, gear, cD, N, offset, deltatp):
        gear.N = N
        gear.offset = offset
        gear.deltatp = deltatp
        gear.Rs = gear.N * cD.m / 2
        gear.Rb = gear.Rs * cos(cD.phi_s)

    def __get_load_commonData2(self, cD, gear, pinion):
        cD.C = (gear.N + pinion.N) * cD.m / 2 + cD.deltaCs
        cD.Cs = gear.Rs + pinion.Rs
        RbplusRb = gear.Rb + pinion.Rb
        cD.phi_p = arccos((RbplusRb) / cD.C)
        cD.inv_phi_p = sqrt((cD.C / RbplusRb)**2 - 1) - cD.phi_p
        cD.inv_phi_s = sqrt((cD.Cs / RbplusRb)**2 - 1) - cD.phi_s
        cD.pp = 2 * pi * cD.C / (gear.N + pinion.N)
        cD.B = cD.Bn / cos(cD.phi_p)

    def __get_load_gearData2(self, gear, pinion, cD):
        gear.Rp = gear.N * cD.C / (gear.N + pinion.N)
        gear.tp = (cD.pp - cD.B) / 2 + gear.deltatp
        gear.tb = gear.Rb * (gear.tp / gear.Rp + 2 * cD.inv_phi_p)
        gear.ts = gear.Rs * (gear.tb / gear.Rb - 2 * cD.inv_phi_s)
        gear.e = (gear.ts - cD.ps / 2) / (2 * tan(cD.phi_s))

    def __get_load_gearData3(self, gear, pinion, cD):
        gear.ap = cD.m - (gear.Rp - pinion.Rp - gear.Rs + pinion.Rs - gear.e + pinion.e) / 2
        gear.RT = gear.Rp + gear.ap

    def __get_load_gearData4(self, gear, pinion, cD, internal=False):
        gear.tpc = cD.pp - pinion.tp
        gear.tbc = gear.Rb * (gear.tpc / gear.Rp + 2 * cD.inv_phi_p)
        gear.tsc = gear.Rs * (gear.tbc / gear.Rb - 2 * cD.inv_phi_s)

        if internal:
            gear.RTc = gear.RT
        else:
            gear.RTc = gear.RT + cD.c * cD.m
        gear.apc = gear.RTc - gear.Rp

        gear.Rc_a = gear.RTc - cD.rcT

        gear.Rhc = sqrt(gear.Rb**2 + (sqrt(gear.Rc_a**2 - gear.Rb**2) + cD.rcT)**2)

        pinion.Rroot = cD.C - gear.RTc

        gear.phi_hc = arccos(gear.Rb / gear.Rhc)
        gear.inv_phi_hc = sqrt(gear.Rhc**2 - gear.Rb**2) / gear.Rb - gear.phi_hc

        gear.tita_hc = gear.tsc / (2 * gear.Rs) + cD.inv_phi_s - gear.inv_phi_hc
        gear.gamma_hc = gear.phi_hc - gear.tita_hc

        gear.xc_a = gear.Rhc * cos(gear.tita_hc) - cD.rcT * sin(gear.gamma_hc)
        gear.yc_a = gear.Rhc * sin(gear.tita_hc) - cD.rcT * cos(gear.gamma_hc)

        gear.tita_c_a = arctan(gear.yc_a / gear.xc_a)
        if gear.yc_a > 0:
            gear.ThirdCond = True
        else:
            gear.ThirdCond = False

    def __get_load_gearData5(self, gear, pinion, cD):
        if (cD.C**2 - gear.Rb**2 - 2 * gear.Rb * pinion.Rb - pinion.RT**2) > 0:
            gear.FirstCond = True
        else:
            gear.FirstCond = False
        RbplusRb = gear.Rb + pinion.Rb
        gear.RL = sqrt(gear.Rb**2 + (sqrt(cD.C**2 - (RbplusRb)**2) - sqrt(pinion.RT**2 - pinion.Rb**2))**2)
        gear.Rf = sqrt(gear.Rb**2 + (sqrt(cD.C**2 - (RbplusRb)**2) - sqrt(pinion.Rhc**2 - pinion.Rb**2))**2)
        if gear.Rf < gear.RL - cD.iL * cD.m:
            gear.SecondCond = True
        else:
            gear.SecondCond = False

    def __get_load_gearData6(self, gear, pinion, cD):
        if not gear.FirstCond:
            R = gear.Rb
            while True:
                phi_R = arccos(gear.Rb / R)
                inv_phi_R = sqrt(R**2 - gear.Rb**2) / gear.Rb - phi_R
                tita_R = gear.tb / (2 * gear.Rb) - inv_phi_R

                betac = arccos((cD.C**2 + pinion.Rhc**2 - R**2) / (2 * cD.C * pinion.Rhc)) - pinion.tita_hc
                betag = - (pinion.Rs * betac + cD.ps / 2) / gear.Rs
                tita_R_d = - arcsin((pinion.Rhc / R) * sin(betac + pinion.tita_hc)) - betag

                if tita_R_d > tita_R:
                    gear.Ru = R
                    break
                R = R + 0.001 * cD.m
            gear.Rc_r = gear.Ru
            gear.Rc_l = gear.Ru - 0.001 * cD.m
        else:
            gear.Ru = NaN
            gear.Rc_r = gear.Rf
            gear.Rc_l = gear.Rf

    def __get_load_commonData3(self, cD, gear, pinion):
        if not gear.FirstCond:
            cD.mc = (sqrt(gear.RT**2 - gear.Rb**2) - sqrt(gear.Ru**2 - gear.Rb**2)) / cD.pb
        if not pinion.FirstCond:
            mc2 = (sqrt(pinion.RT**2 - pinion.Rb**2) - sqrt(pinion.Ru**2 - pinion.Rb**2)) / cD.pb
            if not gear.FirstCond:
                if mc2 < cD.mc:
                    cD.mc = mc2
            else:
                cD.mc = mc2
        if gear.FirstCond and pinion.FirstCond:
            RbplusRb = gear.Rb + pinion.Rb
            cD.mc = (sqrt(gear.RT**2 - gear.Rb**2) + sqrt(pinion.RT**2 - pinion.Rb**2) - sqrt(cD.C**2 - (RbplusRb)**2)) / cD.pb

        if cD.mc > 1.4:
            cD.fourthCond = True
        else:
            cD.fourthCond = False


@dataclass
class inputDataClass:
    m: float
    phi_s: float
    deltaCs: float
    c: float
    rk: float
    Bn: float
    iL: float
    Ng: int
    Np: int
    deltatp: float
    n: int
    m_offset: float
    s_offset: float


@dataclass
class commonData:
    # Module (mm)
    m: float = 0.0
    # Pressure angle (rad)
    phi_p: float = 0.0
    # Standard pressure angle (rad)
    phi_s: float = 0.0
    # Involute function of phi_p (rad)
    inv_phi_p: float = 0.0
    # Involute function of phi_s (rad)
    inv_phi_s: float = 0.0
    # Center Distance (mm)
    C: float = 0.0
    # Center Standard Distance (mm)
    Cs: float = 0.0
    # Center Distance offset (mm)
    deltaCs: float = 0.0
    # Circular pitch (mm)
    pp: float = 0.0
    # Standard Circular pitch (mm)
    ps: float = 0.0
    # Base Circular pitch (mm)
    pb: float = 0.0
    # Diametral pitch (1/mm)
    pd: float = 0.0
    # Clearance (mm)
    c: float = 0.0
    # Cutter Tip Corner Radius Constant
    rk: float = 0.0
    # Cutter Tip Corner Radius (mm)
    rcT: float = 0.0
    # Circular Backlash (mm)
    B: float = 0.0
    # Backlash along the common normal (mm)
    Bn: float = 0.0
    # Limit of second Interference
    iL: float = 0.0
    # Contact Ratio
    mc: float = 0.0
    # Number of Point on curves
    n: int = 0
    FourthCond: bool = False


@dataclass
class gearData:
    # Number of Teeth
    N: int = 0
    # 3D printer offset (mm)
    offset: float = 0
    # Pitch Circle Radius (mm)
    Rp: float = 0.0
    # Standard Pitch Circle Radius (mm)
    Rs: float = 0.0
    # Base Circle Radius (mm)
    Rb: float = 0.0
    # Tip Circle Radius (mm)
    RT: float = 0.0
    # Root Circle Radius (mm)
    Rroot: float = 0.0
    # Limit Circle Radius (mm)
    RL: float = 0.0
    # Fillet Circle Radius (mm)
    Rf: float = 0.0
    # Undercut Circle Radius (mm)
    Ru: float = 0.0
    # If FirsCond is true Rc_r=Rf, else Rc_r=Ru + delta
    Rc_r: float = 0.0
    # If FirsCond is true Rc_l=Rf, else Rc_l=Ru - delta
    Rc_l: float = 0.0
    # Tip Circle Radius for cutter(mm)
    RTc: float = 0.0
    # Tooth thickness at the pitch circle
    tp: float = 0.0
    # Tooth thickness at the standard pitch circle
    ts: float = 0.0
    # Tooth thickness at the base circle
    tb: float = 0.0
    # Tooth thickness at the tip circle
    tT: float = 0.0
    # Tooth thickness at the pitch circle for cutter
    tpc: float = 0.0
    # Tooth thickness at the standard pitch circle for cutter
    tsc: float = 0.0
    # Tooth thickness at the base circle for cutter
    tbc: float = 0.0
    # Tooth thickness at the tip circle for cutter
    tTc: float = 0.0
    # Profile Shift
    e: float = 0.0
    # Delta Thickness
    deltatp: float = 0.0
    # Pitch Circle Addendum
    ap: float = 0.0
    # Standard Pitch Circle Addendum
    as_: float = 0.0
    # Pitch Circle Addendum for cutter
    apc: float = 0.0
    # Pitch Circle Dedendum
    bp: float = 0.0
    # Standard Pitch Circle Dedendum
    bs: float = 0.0
    # Initial Angle position
    beta0: float = 0.0
    # Angular Pitch
    deltaTitap: float = 0.0
    # Radius in hc (mm)
    Rhc: float = 0.0
    # Presure angle in hc (rad)
    phi_hc: float = 0.0
    # Involute function in hc (rad)
    inv_phi_hc: float = 0.0
    # Tita in hc (rad)
    tita_hc: float = 0.0
    # gamma in hc (rad)
    gamma_hc: float = 0.0
    # Coordenada polar tita del putno Ac'
    Rc_a: float = 0.0
    tita_c_a: float = 0.0
    # Coordenadas Cartesianas del Punto Ac'
    xc_a: float = 0.0
    yc_a: float = 0.0
    # Angle where tip curve finish
    tita_RT: float = 0.0
    # Angle where root curve start
    tita_Rroot: float = 0.0

    FirstCond: bool = False
    SecondCond: bool = False
    ThirdCond: bool = False
