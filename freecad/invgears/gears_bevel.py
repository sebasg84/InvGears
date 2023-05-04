# ***************************************************************************
# *   Copyright (c) 2021 Sebastian Ernesto García <sebasg@outlook.com>      *
# *                                                                         *
# *   gears_bevel.py                                                        *
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
from numpy import NaN, pi, sqrt, sin, cos, tan, arcsin, arccos, arctan, linspace, array, size, dot, ones, copysign
from numpy.core.shape_base import hstack, vstack
from numpy.linalg import norm


def brent(func, gear1, gear2, cD, a, b, xtol=1e-8, rtol=1.e-12, maxIter=100):
    fa = func(gear1, gear2, cD, a)
    fb = func(gear1, gear2, cD, b)
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
        fb = func(gear1, gear2, cD, b)
    return b


class getProfile_b():

    def __init__(self, gear1, gear2, cD):

        i_ps, i_m_ps = self.__involute_bevel(gear1, cD)
        f_ps, f_m_ps = self.__fillet(gear1, gear2, cD)

        i_ps, f_ps = self.__fusionpoint(i_ps, f_ps)
        f_m_ps, i_m_ps = self.__fusionpoint(f_m_ps, i_m_ps)

        tip_ps = self.__tip(gear1)

        base_ps = self.__root(gear1)

        tooth_profile = [f_m_ps, i_m_ps, tip_ps, i_ps, f_ps, base_ps]
        gear1.tooth_profile = tooth_profile

        angle = 2 * pi / gear1.N
        M = array([[cos(angle), -sin(angle), 0], [sin(angle), cos(angle), 0], [0, 0, 1]])
        profile = tooth_profile
        aux_profile = tooth_profile
        for i in range(gear1.N - 1):
            aux_profile = list(map(lambda x: dot(M, x), aux_profile))
            profile.extend(aux_profile)

        zp = cD.lambda_ + cD.thickness
        gear1.profile = profile
        gear1.profile_onPlane = list(map(lambda x: vstack([(zp / x[2, :]) * x[0, :], (zp / x[2, :]) * x[1, :], zp * ones((1 , x.shape[1]))]), gear1.profile))

        M = (cD.lambda_ + cD.thickness) / cD.lambda_ * array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        gear1.profile2 = list(map(lambda x: dot(M, x), gear1.profile))

    def __involute_bevel(self, gear1, cD):
        gamma = linspace(gear1.gamma_T, gear1.gamma_c, cD.n)

        phi = arccos(cos(gear1.phi_p) * tan(gear1.gamma_p) / tan(gamma))
        psi = (arctan(tan(phi) * sin(gear1.gamma_b)) / sin(gear1.gamma_b)) - phi

        tita = gear1.tp / (2 * gear1.Rp) + gear1.psi_p - psi

        x = array(cD.lambda_ * sin(gamma) * cos(tita))
        y = array(cD.lambda_ * sin(gamma) * sin(tita))
        z = array(cD.lambda_ * cos(gamma))

        points = vstack([x, y, z])
        mirror_points = vstack([x, -y, z])
        mirror_points = mirror_points[:, ::-1]

        gear1.tita_T = tita[0]
        gear1.z_T = z[0]

        return points, mirror_points

    def __fillet(self, gear1, gear2, cD):
        if not gear1.FirstCond:
            alpha0 = brent(self.__gammaComparation, gear1, gear2, cD, 0, pi / 2)
        else:
            alpha0 = gear2.phi_Tc - gear2.phi_p

        alphaf = 0.0
        alpha = linspace(alpha0, alphaf, cD.n)
       
        betac = alpha - gear2.tita_Tc
        betag = - (gear2.Rp * betac + (cD.pp / 2)) / gear1.Rp
        gamma = arccos(cos(gear2.gamma_Tc) * cos(cD.Sigma) + sin(gear2.gamma_Tc) * sin(cD.Sigma) * cos(alpha))
        tita  = -arctan((sin(gear2.gamma_Tc) * sin(cD.Sigma) * sin(alpha)) / (cos(gear2.gamma_Tc) - cos(cD.Sigma) * cos(gamma))) - betag

        x = array(cD.lambda_ * sin(gamma) * cos(tita))
        y = array(cD.lambda_ * sin(gamma) * sin(tita))
        z = array(cD.lambda_ * cos(gamma))

        points = vstack([x, y, z])
        mirror_points = vstack([x, -y, z])
        mirror_points = mirror_points[:, ::-1]

        gear1.tita_root = tita[-1]
        gear1.z_root = z[-1]

        return points, mirror_points

    def __tip(self, gear1):
        tita = linspace(-gear1.tita_T, gear1.tita_T, 3)
        x = gear1.RT * cos(tita)
        y = gear1.RT * sin(tita)
        z = gear1.z_T * ones((1, 3))
        points = vstack([x, y, z])

        return points

    def __root(self, gear1):
        tita0 = gear1.tita_root
        titaf = 2 * pi / gear1.N - tita0
        tita = linspace(tita0, titaf, 3)
        x = gear1.Rroot * cos(tita)
        y = gear1.Rroot * sin(tita)
        z = gear1.z_root * ones((1, 3))
        points = vstack([x, y, z])

        return points

    def __gammaComparation(self, gear1, gear2, cD, alpha):
        gamma = arccos(cos(gear2.gamma_Tc) * cos(cD.Sigma) + sin(gear2.gamma_Tc) * sin(cD.Sigma) * cos(alpha))
        return gamma - gear1.gamma_c
    
    def __fusionpoint(self, points1, points2):
        fusion_p = (points1[:, -1] + points2[:, 0]) / 2
        points1[:, -1] = fusion_p
        points2[:, 0] = fusion_p
        return points1, points2


class mainCalculations_b():
    def __init__(self, inputData, cD, gear1, gear2):

        self.__get_load_commonData1(cD, inputData)

        self.__get_load_gearData1(gear1, cD, inputData.N_m, inputData.deltatp)
        self.__get_load_gearData1(gear2, cD, inputData.N_s, -gear1.deltatp)

        self.__get_load_commonData2(cD, gear1, gear2)

        self.__get_load_gearData2(gear1, gear2, cD)
        self.__get_load_gearData2(gear2, gear1, cD)

        gear1.beta0 = 0.0
        gear2.beta0 = pi - ((gear1.tp + gear2.tp) / 2 + gear1.Rp * gear1.beta0) / gear2.Rp

        self.__get_load_gearData3(gear1, cD)
        self.__get_load_gearData3(gear2, cD)

        self.__get_load_gearData4(gear1, gear2, cD)
        self.__get_load_gearData4(gear2, gear1, cD)

        self.__get_load_gearData5(gear1, gear2, cD)
        self.__get_load_gearData5(gear2, gear1, cD)

        self.__get_load_gearData6(gear1, gear2, cD)
        self.__get_load_gearData6(gear2, gear1, cD)

    def __get_load_commonData1(self, cD, inputData):
        cD.m = inputData.m
        cD.rho = inputData.rho * pi / 180
        cD.Bl = inputData.Bl
        cD.thickness = inputData.thickness
        cD.Sigma = inputData.Sigma * pi / 180
        cD.c = inputData.c
        cD.n = inputData.n
        cD.iL = inputData.iL
        cD.addendum = inputData.addendum
        cD.pp = pi * cD.m
        cD.pb = cD.pp / sqrt(1 + tan(cD.rho)**2)
        cD.pd = 1 / cD.m

    def __get_load_gearData1(self, gear1, cD, N, deltatp):
        gear1.N = N
        gear1.deltatp = deltatp
        gear1.Rp = gear1.N * cD.m / 2
        gear1.Rb = gear1.Rp / sqrt(1 + tan(cD.rho)**2)

    def __get_load_commonData2(self, cD, gear1, gear2):
        cD.lambda_ = cD.m * sqrt(gear1.N**2 + gear2.N**2 + 2 * gear1.N * gear2.N * cos(cD.Sigma)) / (2 * sin(cD.Sigma)) #diameter from center where gear starts or ends
        cD.delta_c = (cD.c-(cD.addendum-1)) * cD.m / cD.lambda_
        cD.delta_addendum = (cD.addendum-1) * cD.m / cD.lambda_
        cD.B = cD.Bl * sqrt(1 + tan(cD.rho)**2)

    def __get_load_gearData2(self, gear1, gear2, cD):
        gear1.gamma_p = arctan(sin(cD.Sigma) / ((gear2.N / gear1.N) + cos(cD.Sigma)))
        gear1.phi_p = arctan(tan(cD.rho) / cos(gear1.gamma_p))
        gear1.gamma_b = arctan(cos(gear1.phi_p) * tan(gear1.gamma_p))
        gear1.psi_p = (arctan(tan(gear1.phi_p) * sin(gear1.gamma_b)) / sin(gear1.gamma_b)) - gear1.phi_p

        gear1.tp = (cD.pp - cD.B) / 2 + gear1.deltatp
        gear1.tb = gear1.Rb * (gear1.tp / gear1.Rp + 2 * gear1.psi_p)

    def __get_load_gearData3(self, gear1, cD):
        gear1.delta_a = cD.m / cD.lambda_  + cD.delta_addendum
        gear1.delta_d = gear1.delta_a + cD.delta_c 
        gear1.gamma_T = gear1.gamma_p + gear1.delta_a 
        gear1.gamma_root = gear1.gamma_p - gear1.delta_d

        gear1.RT = cD.lambda_ * sin(gear1.gamma_T)
        gear1.Rroot = cD.lambda_ * sin(gear1.gamma_root)

    def __get_load_gearData4(self, gear1, gear2, cD):
        gear1.tpc = cD.pp - gear2.tp
        gear1.tbc = gear1.Rb * (gear1.tpc / gear1.Rp + 2 * gear1.psi_p)

        gear1.gamma_Tc = gear1.gamma_T + cD.delta_c
        gear1.RTc = cD.lambda_ * sin(gear1.gamma_Tc)

        gear2.gamma_root2 = cD.Sigma - gear1.gamma_Tc
        gear2.Rroot2 = cD.lambda_ * sin(gear2.gamma_root2)

        gear1.delta_ac = gear1.gamma_Tc - gear1.gamma_p

        gear1.phi_Tc = arccos(cos(gear1.phi_p) * tan(gear1.gamma_p) / tan(gear1.gamma_Tc))
        gear1.psi_Tc = (arctan(tan(gear1.phi_Tc) * sin(gear1.gamma_b)) / sin(gear1.gamma_b)) - gear1.phi_Tc

        gear1.tita_Tc = gear1.tpc / (2 * gear1.Rp) + gear1.psi_p - gear1.psi_Tc
        if gear1.tita_Tc > 0:
            gear1.ThirdCond = True
        else:
            gear1.ThirdCond = False

    def __get_load_gearData5(self, gear1, gear2, cD):
        a = arctan(sin(gear1.gamma_b) * tan(gear1.phi_p)) + arctan(sin(gear2.gamma_b) * tan(gear2.phi_p)) - arccos(cos(gear2.gamma_T) / cos(gear2.gamma_b))
        if a > 0:
            gear1.FirstCond = True
        else:
            gear1.FirstCond = False

        gear1.gamma_L = arccos(cos(a) * cos(gear1.gamma_b))
        gear1.RL = cD.lambda_ * sin(gear1.gamma_L)

        a = arctan(sin(gear1.gamma_b) * tan(gear1.phi_p)) + arctan(sin(gear2.gamma_b) * tan(gear2.phi_p)) - arccos(cos(gear2.gamma_Tc) / cos(gear2.gamma_b))
        gear1.gamma_f = arccos(cos(a) * cos(gear1.gamma_b))
        gear1.Rf = cD.lambda_ * sin(gear1.gamma_f)

        if gear1.gamma_f * cD.lambda_ < gear1.gamma_L * cD.lambda_ - cD.iL * cD.m:
            gear1.SecondCond = True
        else:
            gear1.SecondCond = False

    def __get_load_gearData6(self, gear1, gear2, cD):
        if not gear1.FirstCond:
            gear1.gamma_u = brent(self.__titaComparation, gear1, gear2, cD, gear1.gamma_b, gear1.gamma_p, 1e-8)
            gear1.Ru = cD.lambda_ * sin(gear1.gamma_u)
            gear1.gamma_c = gear1.gamma_u
            gear1.Rc = gear1.Ru
        else:
            gear1.gamma_u = NaN
            gear1.Ru = NaN
            gear1.gamma_c = gear1.gamma_f
            gear1.Rc = gear1.Rf

    def __titaComparation(self, gear1, gear2, cD, gamma):
        phi = arccos(cos(gear1.phi_p) * tan(gear1.gamma_p) / tan(gamma))
        psi = (arctan(tan(phi) * sin(gear1.gamma_b)) / sin(gear1.gamma_b)) - phi
        tita = gear1.tp / (2 * gear1.Rp) + gear1.psi_p - psi

        betac = arccos((cos(gamma) - cos(gear2.gamma_Tc) * cos(cD.Sigma)) / (sin(gear2.gamma_Tc) * sin(cD.Sigma))) - gear2.tita_Tc
        betag = - (gear2.Rp * betac + cD.pp / 2) / gear1.Rp
        tita_a = -arcsin(sin(gear2.tita_Tc + betac) * sin(gear2.gamma_Tc) / sin(gamma)) - betag

        return tita_a - tita


@dataclass
class inputDataClass_b:
    m: float
    rho: float
    N_m: int
    N_s: int
    Bl: float
    thickness : float
    Sigma: float
    c: float
    deltatp: float
    n: int
    iL: float
    addendum : float = 1

@dataclass
class commonData_b:
    # Module (mm)
    m: float = 0.0
    # Pressure angle (rad)
    phi_p: float = 0.0
    # Involute function of phi_p (rad)
    psi_p: float = 0.0
    # Circular pitch (mm)
    pp: float = 0.0
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
    lambda_: float = 0.0
    thickness: float = 0.0


@dataclass
class gearData_b:
    # Number of Teeth
    N: int = 0
    # 3D printer offset (mm)
    offset: float = 0
    # Pitch Circle Radius (mm)
    Rp: float = 0.0
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
    # Tooth thickness at the base circle for cutter
    tbc: float = 0.0
    # Tooth thickness at the tip circle for cutter
    tTc: float = 0.0
    # Delta Thickness
    deltatp: float = 0.0
    # Pitch Circle Addendum
    ap: float = 0.0
    # Pitch Circle Addendum for cutter
    apc: float = 0.0
    # Pitch Circle Dedendum
    bp: float = 0.0
    # Initial Angle position
    beta0: float = 0.0
    # Angular Pitch
    deltaTitap: float = 0.0
    # Radius in hc (mm)
    RTc: float = 0.0
    # Presure angle in hc (rad)
    phi_Tc: float = 0.0
    # Involute function in hc (rad)
    psi_Tc: float = 0.0
    # Tita in hc (rad)
    tita_Tc: float = 0.0
    # gamma in hc (rad)
    gamma_Tc: float = 0.0
    # Angle where tip curve finish
    tita_T: float = 0.0
    # Angle where root curve start
    tita_root: float = 0.0

    FirstCond: bool = False
    SecondCond: bool = False
    ThirdCond: bool = False
