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
from numpy import NaN, pi, sqrt, sin, cos, tan, arcsin, arccos, arctan, linspace, array, size, dot, copysign
from numpy.core.shape_base import hstack, vstack
from numpy.linalg import norm


def brent(func, gear1, pinion, cD, a, b, xtol=1e-8, rtol=1.e-12, maxIter=100):
    fa = func(gear1, pinion, cD, a)
    fb = func(gear1, pinion, cD, b)
    if (fa > 0 and fb > 0) or (fa < 0 and fb < 0):
       return -1
    c = b
    fc = fb
    for i in range(maxIter):
        if ( fb > 0 and fc > 0) or (fb < 0 and fc < 0):
            c = a
            fc = fa
            d = b - a
            e = d
        if abs(fc) < abs(fb):
            a = b
            b = c
            c = a
            fa = fb
            fb = fc
            fc = fa
        tol1 = 2 * rtol * abs(b) + 0.5 * xtol
        xm = 0.5 * (c-b)
        if abs(xm) <= tol1 or fb == 0:
            return b
        if abs(e) >= tol1 and abs(fa) > abs(fb):
            s = fb / fa
            if a == c:
                p = 2 * xm * s
                q = 1 - s
            else:
                q = fa / fc
                r = fb / fc
                p = s * (2 * xm * q * (q - r) - (b - a) * (r - 1))
                q = (q - 1) * (r - 1) * (s - 1)
            if p > 0:
                q = -q
            p = abs(p)
            if 2 * p < min(3 * xm * q - abs(tol1 * q), abs(e * q)):
                e = d
                d = p / q
            else:
                d = xm
                e = d
        else:
            d = xm
            e = d
        a = b
        fa = fb
        if abs(d) > tol1:
            b = b + d
        else:
            b = b + copysign(tol1, xm)
        fb = func(gear1, pinion, cD, b)
    return b


class getProfile():

    def __init__(self, gear1, gear2, cD, internal=False):

        i_ps, i_norm = self.__involute(gear1, cD, internal)
        f_ps, f_norm = self.__fillet(gear1, gear2, cD)

        i_ps, f_ps = self.__fusionpoint(i_ps, f_ps)

        if internal:
            RT1 = gear1.RTc
        else:
            RT1 = gear1.RT

        Rroot1 = gear1.Rroot

        if(abs(gear1.offset) > 0.00001):
            i_ps = i_ps - gear1.offset * i_norm
            f_ps = f_ps - gear1.offset * f_norm
            RT1 = RT1 - gear1.offset
            Rroot1 = Rroot1 - gear1.offset

            inter_p, i_index, f_index = self.__intersection(i_ps, f_ps)

            if(i_index == -1):
                i_ps, f_ps = self.__fusionpoint(i_ps, f_ps)
            else:
                i_ps = hstack((i_ps[:, :i_index], inter_p))
                f_ps = hstack((inter_p, f_ps[:, f_index:]))
            
            inter_p, index = self.__tipIntersection(i_ps, RT1)
            i_ps = hstack((inter_p, i_ps[:, index:]))

        M = array([[1, 0], [0, -1]])
        i_ps_rev = dot(M, i_ps[:, ::-1])
        f_ps_rev = dot(M, f_ps[:, ::-1])
        tip_ps = hstack((i_ps_rev[:, [-1]], vstack([RT1, 0]), i_ps[:, [0]]))

        tita0 = gear1.tita_Rroot
        titaf = 2 * pi / gear1.N - tita0
        tita = linspace(tita0, titaf, 3)
        x = Rroot1 * cos(tita)
        y = Rroot1 * sin(tita)
        root_ps = vstack([x, y])

        tooth_profile = [f_ps_rev, i_ps_rev, tip_ps, i_ps, f_ps, root_ps]
        gear1.tooth_profile = tooth_profile

        angle = 2 * pi / gear1.N
        M = array([[cos(angle), -sin(angle)], [sin(angle), cos(angle)]])
        profile = tooth_profile
        aux_profile = tooth_profile
        for i in range(gear1.N - 1):
            aux_profile = list(map(lambda x: dot(M, x), aux_profile))
            profile.extend(aux_profile)

        gear1.profile = profile

    def __tipIntersection(self, i_ps, RT1):
        for i in range(size(i_ps, 1)):
            if norm(i_ps[:, i + 1]) < RT1:
                index = i
                break

        xA, yA = i_ps[:, index]
        xB, yB = i_ps[:, index + 1]
        m = (yB - yA) / (xB - xA)
        mxA = m * xA
        a = (1 + m**2)
        b = 2 * m * (yA - mxA)
        c = yA**2 + mxA**2 - 2 * yA * mxA - RT1**2
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

    def __involute(self, gear1, cD, internal):
        if internal:
            RT1 = gear1.RTc
        else:
            RT1 = gear1.RT
        R = linspace(RT1, gear1.Rc, cD.n)
        phi_R = arccos(gear1.Rb / R)
        psi_R = sqrt(R**2 - gear1.Rb**2) / gear1.Rb - phi_R
        tita_R = gear1.tb / (2 * gear1.Rb) - psi_R

        diff_tita_R = -sqrt(R**2 - gear1.Rb**2) / (R * gear1.Rb)

        x = array(R * cos(tita_R))
        y = array(R * sin(tita_R))

        dx = cos(tita_R) - R * sin(tita_R) * diff_tita_R
        dy = sin(tita_R) + R * cos(tita_R) * diff_tita_R
        xn = array(-dy / sqrt(dx**2 + dy**2))
        yn = array(dx / sqrt(dx**2 + dy**2))

        points = vstack([x, y])
        normal = vstack([xn, yn])

        gear1.tita_RT = tita_R[0]

        return points, normal

    def __fillet(self, gear1, gear2, cD):
        if not gear1.FirstCond:
            alpha0 = brent(self.__RComparation, gear1, gear2, None, 0, pi / 2)
        else:
            alpha0 = arccos(gear2.Rb / gear2.RTc) - cD.phi_p

        alphaf = 0.0
        alpha = linspace(alpha0, alphaf, cD.n)
        xi = gear2.Rp - gear2.RTc * cos(alpha)
        eta = -gear2.RTc * sin(alpha)

        betac = alpha - gear2.tita_Tc
        betag = - (gear2.Rs * betac + (cD.ps / 2)) / gear1.Rs

        R = sqrt((gear1.Rp + xi)**2 + eta**2)
        tita_R = arctan(eta / (gear1.Rp + xi)) - betag

        diff_xi = gear2.RTc * sin(alpha)
        diff_eta = -gear2.RTc * cos(alpha)

        diff_betag = - gear2.Rs / gear1.Rs

        diff_R = ((gear1.Rp + xi) * diff_xi + eta * diff_eta) / sqrt((gear1.Rp + xi)**2 + eta**2)
        diff_tita_R = (diff_eta * (gear1.Rp + xi) - eta * diff_xi) / ((gear1.Rp + xi)**2 + eta**2) - diff_betag

        x = array(R * cos(tita_R))
        y = array(R * sin(tita_R))

        dx = diff_R * cos(tita_R) - R * sin(tita_R) * diff_tita_R
        dy = diff_R * sin(tita_R) + R * cos(tita_R) * diff_tita_R
        xn = array(-dy / sqrt(dx**2 + dy**2))
        yn = array(dx / sqrt(dx**2 + dy**2))

        points = vstack([x, y])
        normal = vstack([xn, yn])

        gear1.tita_Rroot = tita_R[-1]

        return points, normal

    def __RComparation(self, gear1, gear2, cD, alpha):
        xi = gear2.Rp - gear2.RTc * cos(alpha)
        eta = -gear2.RTc * sin(alpha)
        R = sqrt((gear1.Rp + xi)**2 + eta**2)
        return R - gear1.Rc

    def __fusionpoint(self, i_ps, f_ps):
        fusion_p = (i_ps[:, -1] + f_ps[:, 0]) / 2
        i_ps[:, -1] = fusion_p
        f_ps[:, 0] = fusion_p
        return i_ps, f_ps


class mainCalculations():
    def __init__(self, inputData, cD, gear1, gear2, internal=False):

        self.__get_load_commonData1(cD, inputData)

        if internal:
            self.__get_load_gearData1(gear1, cD, inputData.N_m, -inputData.offset_m, -inputData.deltatp)
        else:
            self.__get_load_gearData1(gear1, cD, inputData.N_m, inputData.offset_m, inputData.deltatp)

        self.__get_load_gearData1(gear2, cD, inputData.N_s, inputData.offset_s, -inputData.deltatp)

        self.__get_load_commonData2(cD, gear1, gear2)

        self.__get_load_gearData2(gear1, gear2, cD, internal)
        self.__get_load_gearData2(gear2, gear1, cD)

        gear1.beta0 = 0.0
        gear2.beta0 = pi - ((gear1.tp + gear2.tp) / 2 + gear1.Rp * gear1.beta0) / gear2.Rp

        self.__get_load_gearData3(gear1, gear2, cD)
        self.__get_load_gearData3(gear2, gear1, cD)

        self.__get_load_gearData4(gear1, gear2, cD)
        self.__get_load_gearData4(gear2, gear1, cD, internal)

        self.__get_load_gearData5(gear1, gear2, cD)
        self.__get_load_gearData5(gear2, gear1, cD)

        self.__get_load_gearData6(gear1, gear2, cD)
        self.__get_load_gearData6(gear2, gear1, cD)

        self.__get_load_commonData3(cD, gear1, gear2)

    def __get_load_commonData1(self, cD, inputData):
        cD.m = inputData.m
        cD.phi_s = inputData.phi_s * pi / 180
        cD.Bl = inputData.Bl
        cD.c = inputData.c
        cD.deltaCs = inputData.deltaCs
        cD.n = inputData.n
        cD.iL = inputData.iL
        cD.addendum = inputData.addendum
        cD.ps = pi * cD.m
        cD.pb = cD.ps * cos(cD.phi_s)
        cD.pd = 1 / cD.m

    def __get_load_gearData1(self, gear1, cD, N, offset, deltatp):
        gear1.N = N
        gear1.offset = offset
        gear1.deltatp = deltatp
        gear1.Rs = gear1.N * cD.m / 2
        gear1.Rb = gear1.Rs * cos(cD.phi_s)

    def __get_load_commonData2(self, cD, gear1, gear2):
        cD.Center_d = (gear1.N + gear2.N) * cD.m / 2 + cD.deltaCs
        cD.Cs = gear1.Rs + gear2.Rs
        RbplusRb = gear1.Rb + gear2.Rb
        cD.phi_p = arccos((RbplusRb) / cD.Center_d)
        cD.psi_p = sqrt((cD.Center_d / RbplusRb)**2 - 1) - cD.phi_p
        cD.psi_s = sqrt((cD.Cs / RbplusRb)**2 - 1) - cD.phi_s
        cD.pp = 2 * pi * cD.Center_d / (gear1.N + gear2.N)
        cD.B = cD.Bl / cos(cD.phi_p)

    def __get_load_gearData2(self, gear1, gear2, cD, internal=False):
        gear1.Rp = gear1.N * cD.Center_d / (gear1.N + gear2.N)
        if internal is True:
            gear1.tp = (cD.pp + cD.B) / 2 + gear1.deltatp
        else:
            gear1.tp = (cD.pp - cD.B) / 2 + gear1.deltatp
        gear1.tb = gear1.Rb * (gear1.tp / gear1.Rp + 2 * cD.psi_p)
        gear1.ts = gear1.Rs * (gear1.tb / gear1.Rb - 2 * cD.psi_s)
        gear1.e = (gear1.ts - cD.ps / 2) / (2 * tan(cD.phi_s))

    def __get_load_gearData3(self, gear1, gear2, cD):
        gear1.ap = (cD.m - (gear1.Rp - gear2.Rp - gear1.Rs + gear2.Rs - gear1.e + gear2.e) / 2) * cD.addendum
        gear1.ap = cD.m * cD.addendum
        gear1.RT = gear1.Rp + gear1.ap

    def __get_load_gearData4(self, gear1, gear2, cD, internal=False):
        gear1.tpc = cD.pp - gear2.tp
        gear1.tbc = gear1.Rb * (gear1.tpc / gear1.Rp + 2 * cD.psi_p)
        gear1.tsc = gear1.Rs * (gear1.tbc / gear1.Rb - 2 * cD.psi_s)

        if internal:
            gear1.RTc = gear1.RT

        else:
            gear1.RTc = gear1.Rp + (1+cD.c) * cD.m

        gear1.apc = gear1.RTc - gear1.Rp

        gear2.Rroot = cD.Center_d - gear1.RTc

        gear1.phi_Tc = arccos(gear1.Rb / gear1.RTc)
        gear1.psi_Tc = sqrt(gear1.RTc**2 - gear1.Rb**2) / gear1.Rb - gear1.phi_Tc

        gear1.tita_Tc = gear1.tsc / (2 * gear1.Rs) + cD.psi_s - gear1.psi_Tc

        if gear1.tita_Tc > 0:
            gear1.ThirdCond = True
        else:
            gear1.ThirdCond = False

    def __get_load_gearData5(self, gear1, gear2, cD):
        if (cD.Center_d**2 - gear1.Rb**2 - 2 * gear1.Rb * gear2.Rb - gear2.RT**2) > 0:
            gear1.FirstCond = True
        else:
            gear1.FirstCond = False
        RbplusRb = gear1.Rb + gear2.Rb
        gear1.RL = sqrt(gear1.Rb**2 + (sqrt(cD.Center_d**2 - (RbplusRb)**2) - sqrt(gear2.RT**2 - gear2.Rb**2))**2)
        gear1.Rf = sqrt(gear1.Rb**2 + (sqrt(cD.Center_d**2 - (RbplusRb)**2) - sqrt(gear2.RTc**2 - gear2.Rb**2))**2)
        if gear1.Rf < gear1.RL - cD.iL * cD.m:
            gear1.SecondCond = True
        else:
            gear1.SecondCond = False

    def __get_load_gearData6(self, gear1, gear2, cD):
        if not gear1.FirstCond:
            gear1.Ru = brent(self.__titaComparation, gear1, gear2, cD, gear1.Rb, gear1.Rp)
            gear1.Rc = gear1.Ru
        else:
            gear1.Ru = NaN
            gear1.Rc = gear1.Rf

    def __get_load_commonData3(self, cD, gear1, gear2):
        if not gear1.FirstCond:
            cD.mc = (sqrt(gear1.RT**2 - gear1.Rb**2) - sqrt(gear1.Ru**2 - gear1.Rb**2)) / cD.pb
        if not gear2.FirstCond:
            mc2 = (sqrt(gear2.RT**2 - gear2.Rb**2) - sqrt(gear2.Ru**2 - gear2.Rb**2)) / cD.pb
            if not gear1.FirstCond:
                if mc2 < cD.mc:
                    cD.mc = mc2
            else:
                cD.mc = mc2
        if gear1.FirstCond and gear2.FirstCond:
            RbplusRb = gear1.Rb + gear2.Rb
            cD.mc = (sqrt(gear1.RT**2 - gear1.Rb**2) + sqrt(gear2.RT**2 - gear2.Rb**2) - sqrt(cD.Center_d**2 - (RbplusRb)**2)) / cD.pb

        if cD.mc > 1.4:
            cD.fourthCond = True
        else:
            cD.fourthCond = False

    def __titaComparation(self, gear1, gear2, cD, R):
        phi_R = arccos(gear1.Rb / R)
        psi_R = sqrt(R**2 - gear1.Rb**2) / gear1.Rb - phi_R
        tita_R = gear1.tb / (2 * gear1.Rb) - psi_R

        betac = arccos((cD.Center_d**2 + gear2.RTc**2 - R**2) / (2 * cD.Center_d * gear2.RTc)) - gear2.tita_Tc
        betag = - (gear2.Rs * betac + cD.ps / 2) / gear1.Rs
        tita_R_a = - arcsin((gear2.RTc / R) * sin(betac + gear2.tita_Tc)) - betag

        return tita_R_a - tita_R


@dataclass
class inputDataClass:
    m: float
    phi_s: float
    N_m: int
    N_s: int
    Bl: float
    c: float
    deltaCs: float
    deltatp: float
    offset_m: float
    offset_s: float
    n: int
    iL: float
    addendum : float = 1

@dataclass
class commonData:
    # Module (mm)
    m: float = 0.0
    # Pressure angle (rad)
    phi_p: float = 0.0
    # Standard pressure angle (rad)
    phi_s: float = 0.0
    # Involute function of phi_p (rad)
    psi_p: float = 0.0
    # Involute function of phi_s (rad)
    psi_s: float = 0.0
    # Center Distance (mm)
    Center_d: float = 0.0
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
    # Circular Backlash (mm)
    B: float = 0.0
    # Backlash along the common normal (mm)
    Bl: float = 0.0
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
    # If FirsCond is true Rc=Rf, else Rc=Ru
    Rc: float = 0.0
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
    # Radius in Tc (mm)
    RTc: float = 0.0
    # Presure angle in Tc (rad)
    phi_Tc: float = 0.0
    # Involute function in Tc (rad)
    psi_Tc: float = 0.0
    # Tita in Tc (rad)
    tita_Tc: float = 0.0
    # Angle where tip curve finish
    tita_RT: float = 0.0
    # Angle where root curve start
    tita_Rroot: float = 0.0

    FirstCond: bool = False
    SecondCond: bool = False
    ThirdCond: bool = False
