# ***************************************************************************
# *   Copyright (c) 2021 Sebastian Ernesto García <sebasg@outlook.com>      *
# *                                                                         *
# *   widget.py                                                            *
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

from PySide2.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QGroupBox, QPushButton, QComboBox, QCheckBox
from PySide2.QtCore import Qt


class GearWidget(QWidget):
    def __init__(self, type, attach_master_gear=None, load_parameters=None):
        QWidget.__init__(self)
        self.attach_master_gear = attach_master_gear
        self.load_parameters = load_parameters
        self.type = type
        self.initUI()

    def initUI(self):
        if self.type == "Master" or self.type == "SlaveMaster" or self.type == "Internal" or self.type == "SVG":
            self.gearLayout = QGridLayout()
            self.gearLayout.addWidget(QLabel("Module:"), 0, 0, 1, 1, Qt.AlignRight)
            self.mEdit = QLineEdit("1.0")
            self.gearLayout.addWidget(self.mEdit, 0, 1, 1, 1, Qt.AlignLeft)
            self.gearLayout.addWidget(QLabel("Standard pressure angle:"), 0, 2, 1, 1, Qt.AlignRight)
            self.phi_sEdit = QLineEdit("20.0")
            self.gearLayout.addWidget(self.phi_sEdit, 0, 3, 1, 1, Qt.AlignLeft)
            self.gearLayout.addWidget(QLabel("Number of master gear teeth:"), 1, 0, 1, 1, Qt.AlignRight)
            self.N_m_Edit = QLineEdit("24")
            self.gearLayout.addWidget(self.N_m_Edit, 1, 1, 1, 1, Qt.AlignLeft)
            self.gearLayout.addWidget(QLabel("Number of slave gear teeth:"), 1, 2, 1, 1, Qt.AlignRight)
            self.N_s_Edit = QLineEdit("16")
            self.gearLayout.addWidget(self.N_s_Edit, 1, 3, 1, 1, Qt.AlignLeft)
            self.gearLayout.addWidget(QLabel("Clearance constant (Clearance / module):"), 2, 0, 1, 1, Qt.AlignRight)
            self.cEdit = QLineEdit("0.25")
            self.gearLayout.addWidget(self.cEdit, 2, 1, 1, 1, Qt.AlignLeft)
            self.gearLayout.addWidget(QLabel("Circular section of Cutter (Radius / Module):"), 2, 2, 1, 1, Qt.AlignRight)
            self.rfEdit = QLineEdit("0.1")
            self.gearLayout.addWidget(self.rfEdit, 2, 3, 1, 1, Qt.AlignLeft)
            self.gearLayout.addWidget(QLabel("Delta Distance Center:"), 3, 0, 1, 1, Qt.AlignRight)
            self.deltaCEdit = QLineEdit("0.0")
            self.gearLayout.addWidget(self.deltaCEdit, 3, 1, 1, 1, Qt.AlignLeft)
            self.gearLayout.addWidget(QLabel("Delta Tooth Thickness at Rp:"), 3, 2, 1, 1, Qt.AlignRight)
            self.deltaTpEdit = QLineEdit("0.0")
            self.gearLayout.addWidget(self.deltaTpEdit, 3, 3, 1, 1, Qt.AlignLeft)
            self.gearLayout.addWidget(QLabel("Backlash Along the Common Normal:"), 4, 0, 1, 1, Qt.AlignRight)
            self.BnEdit = QLineEdit("0.0")
            self.gearLayout.addWidget(self.BnEdit, 4, 1, 1, 1, Qt.AlignLeft)
            self.gearLayout.addWidget(QLabel("Value for second condition (interference):"), 4, 2, 1, 1, Qt.AlignRight)
            self.interfEdit = QLineEdit("0.025")
            self.gearLayout.addWidget(self.interfEdit, 4, 3, 1, 1, Qt.AlignLeft)
            self.gearLayout.addWidget(QLabel("Number of points for involute and fillet curves:"), 5, 0, 1, 1, Qt.AlignRight)
            self.numPointsEdit = QLineEdit("20")
            self.gearLayout.addWidget(self.numPointsEdit, 5, 1, 1, 1, Qt.AlignLeft)
            if self.type != "SVG":
                self.gearLayout.addWidget(QLabel("Gear height:"), 5, 2, 1, 1, Qt.AlignRight)
                self.heightEdit = QLineEdit("4.0")
                self.gearLayout.addWidget(self.heightEdit, 5, 3, 1, 1, Qt.AlignLeft)
                self.gearLayout.addWidget(QLabel("Gear type:"), 6, 0, 1, 1, Qt.AlignRight)
                self.comboBox = QComboBox(self)
                self.comboBox.addItem("Spur")
                self.comboBox.addItem("Helical")
                self.comboBox.addItem("DobleHelical")
                self.indexComboBox = 0
                self.comboBox.currentIndexChanged.connect(self.onChanged)
                self.gearLayout.addWidget(self.comboBox, 6, 1, 1, 1, Qt.AlignLeft)
                self.gearLayout.addWidget(QLabel("Helical portion:"), 6, 2, 1, 1, Qt.AlignRight)
                self.helicalAngleEdit = QLineEdit("0.5")
                self.helicalAngleEdit.setEnabled(False)
                self.gearLayout.addWidget(self.helicalAngleEdit, 6, 3, 1, 1, Qt.AlignLeft)
                next_number = 7
            else:
                next_number = 6
            self.gearLayout.addWidget(QLabel("3d printing offset for master gear:"), next_number, 0, 1, 1, Qt.AlignRight)
            self.offset_m_Edit = QLineEdit("0.0")
            self.gearLayout.addWidget(self.offset_m_Edit, next_number, 1, 1, 1, Qt.AlignLeft)
            self.gearLayout.addWidget(QLabel("3d printing offset for slave gear:"), next_number, 2, 1, 1, Qt.AlignRight)
            self.offset_s_Edit = QLineEdit("0.0")
            self.gearLayout.addWidget(self.offset_s_Edit, next_number, 3, 1, 1, Qt.AlignLeft)
            if self.type != "SVG":
                self.gearLayout.addWidget(QLabel("List with angular locations of slave gears:"), 8, 0, 1, 1, Qt.AlignRight)
                self.list_angular_s_Edit = QLineEdit("")
                self.gearLayout.addWidget(self.list_angular_s_Edit, 8, 1, 1, 3)
            else:
                self.gearLayout.addWidget(QLabel("Internal gear:"), 7, 0, 1, 1, Qt.AlignRight)
                self.checkBox = QCheckBox()
                self.checkBox.stateChanged.connect(self.onStatusChanged)
                self.gearLayout.addWidget(self.checkBox, 7, 1, 1, 3)
                self.gearLayout.addWidget(QLabel("Thickness:"), 7, 2, 1, 1, Qt.AlignRight)
                self.thicknessEdit = QLineEdit("2.0")
                self.gearLayout.addWidget(self.thicknessEdit, 7, 3, 1, 1, Qt.AlignLeft)
                self.print_warnings = QLabel("")
                self.gearLayout.addWidget(self.print_warnings, 8, 0, 1, 4, Qt.AlignCenter)

            if self.type == "Internal":
                self.gearLayout.addWidget(QLabel("Thickness:"), 9, 1, 1, 1, Qt.AlignRight)
                self.thicknessEdit = QLineEdit("2.0")
                self.thicknessEdit.setEnabled(False)
                self.gearLayout.addWidget(self.thicknessEdit, 9, 2, 1, 1, Qt.AlignLeft)
                self.print_warnings = QLabel("")
                self.gearLayout.addWidget(self.print_warnings, 10, 0, 1, 4, Qt.AlignCenter)

            self.groupBox = QGroupBox()
            self.groupBox.setLayout(self.gearLayout)

        if self.type == "Slave" or self.type == "SlaveMaster" or self.type == "SVG":
            self.slaveLayout = QGridLayout()
            self.print_warnings = QLabel("")
            self.slaveLayout.addWidget(self.print_warnings, 0, 0, 1, 4, Qt.AlignCenter)
            self.master_gear_Button = QPushButton("")
            self.master_gear_Button.clicked.connect(self.attach_master_gear)
            self.slaveLayout.addWidget(self.master_gear_Button, 1, 0, 1, 1)
            self.master_gear_Edit = QLineEdit("")
            self.slaveLayout.addWidget(self.master_gear_Edit, 1, 1, 1, 3)
            if self.type != "SVG":
                self.slaveLayout.addWidget(QLabel("List with angular locations of slave gears:"), 2, 0, 1, 1)
                self.list_angular_s_Edit2 = QLineEdit("")
                self.slaveLayout.addWidget(self.list_angular_s_Edit2, 2, 1, 1, 3)
            else:
                self.load_Parameters_Button = QPushButton("Load Parameters")
                self.load_Parameters_Button.clicked.connect(self.load_parameters)
                self.slaveLayout.addWidget(self.load_Parameters_Button, 2, 0, 1, 4)

            self.groupBox2 = QGroupBox()
            self.groupBox2.setLayout(self.slaveLayout)

        if self.type == "SlaveMaster":
            self.positionLayout = QGridLayout()
            self.positionLayout.addWidget(QLabel("Gear separator height:"), 0, 1, 1, 1, Qt.AlignRight)
            self.hseparatorEdit = QLineEdit("2.0")
            self.positionLayout.addWidget(self.hseparatorEdit, 0, 2, 1, 1)
            self.positionLayout.addWidget(QLabel("Orientation:"), 0, 3, 1, 1, Qt.AlignRight)
            self.titaEdit = QLineEdit("0.0")
            self.positionLayout.addWidget(self.titaEdit, 0, 4, 1, 1)

            self.groupBox3 = QGroupBox()
            self.groupBox3.setLayout(self.positionLayout)

        self.mainLayout = QGridLayout()
        if self.type == "Master" or self.type == "Internal":
            self.mainLayout.addWidget(self.groupBox, 0, 0)
        elif self.type == "Slave":
            self.mainLayout.addWidget(self.groupBox2, 0, 0)
        elif self.type == "SlaveMaster":
            self.mainLayout.addWidget(self.groupBox2, 0, 0)
            self.mainLayout.addWidget(self.groupBox, 1, 0)
            self.mainLayout.addWidget(self.groupBox3, 2, 0)
        elif self.type == "SVG":
            self.mainLayout.addWidget(self.groupBox2, 0, 0)
            self.mainLayout.addWidget(self.groupBox, 1, 0)

        self.setLayout(self.mainLayout)

    def onChanged(self, index):
        self.indexComboBox = index
        if index == 0:
            self.helicalAngleEdit.setEnabled(False)
        else:
            self.helicalAngleEdit.setEnabled(True)

    def onStatusChanged(self, state):
        if state == 0:
            self.thicknessEdit.setEnabled(False)
        else:
            self.thicknessEdit.setEnabled(True)
