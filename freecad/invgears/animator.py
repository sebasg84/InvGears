# -*- coding: utf-8 -*-
__version__ = "0.2021.10.29"
#Animator
import FreeCAD, FreeCADGui, Part
import time
from pivy import coin
from PySide import QtCore, QtGui

class Animator:
    def __init__(self, obj):
        animv = "Animator.v"+__version__
        obj.addProperty("App::PropertyBool","ShowProgress",animv,"Whether to show progress in Description/Label2 column during animation").ShowProgress = True
        obj.addProperty("App::PropertyBool","StartAnimating",animv,"[Trigger] Start animating (or double click Animator in tree)").StartAnimating = False
        obj.addProperty("App::PropertyBool","StopAnimating",animv,"[Trigger] Stop animating (or double click Animator in tree)").StopAnimating = False
        obj.addProperty("App::PropertyBool","Refresh",animv,"[Trigger] Refreshes Variables property lists, sets self back to False\nUse this if objects/properties have changed").Refresh = False
        obj.addProperty("App::PropertyInteger","Frames",animv,"Number of frames / iterations per loop").Frames = 100
        obj.addProperty("App::PropertyFloat","Sleep",animv,"Optional sleep time (in seconds) per frame / iteration").Sleep = 0
        obj.addProperty("App::PropertyFloatConstraint","InitialDelay",animv,"Initial delay (in seconds) before animation starts").InitialDelay = (0,-.045,60,.1)
        obj.addProperty("App::PropertyIntegerConstraint","VariableCount",animv,"Number of variables to use").VariableCount = (3,0,100,1)
        obj.addProperty("App::PropertyStringList","BlacklistedObjects","SettingsAdvanced","Object types not to include in Properties").BlacklistedObjects =\
["App::Origin","App::Line","App::Plane"]
        obj.addProperty("App::PropertyStringList","Supported","SettingsAdvanced","Supported property types")
        obj.Supported = ["App::PropertyInteger","App::PropertyIntegerConstraint","App::PropertyFloat","App::PropertyFloatConstraint",
"App::PropertyLength","App::PropertyAngle","App::PropertyArea","App::PropertyDistance","App::PropertyPercent","App::PropertyQuantity",
"App::PropertyQuantityConstraint","App::PropertySpeed","App::PropertyVolume","App::PropertyPlacement","App::PropertyVector",
"App::PropertyMatrix","Sketcher::PropertyConstraintList"]
        self.properties = []
        self.fpName = obj.Name
        self.isAnimating = False
        self.expressionDict = {} #to hold objects' initial ExpressionEngine before animation
        obj.Proxy = self

    def getSubProperties(self,prop,typeId,obj):
        if not "Placement" in typeId and not "Vector" in typeId and not "Matrix" in typeId and not "ConstraintList" in typeId and not "Spreadsheet::Sheet" in typeId and not "Rotation" in typeId:
            return [prop]
        elif "Rotation" in typeId:
            return [prop+".Angle",prop+".Axis.x",prop+".Axis.y",prop+".Axis.z"]
        elif "Placement" in typeId:
            return [prop+".Rotation.Angle",prop+".Rotation.Axis.x",prop+".Rotation.Axis.y",prop+".Rotation.Axis.z",prop+".Base.x",prop+".Base.y",prop+".Base.z"]
        elif "Vector" in typeId:
            return [prop+".x",prop+".y",prop+".z"]
        elif "Matrix" in typeId:
            return [prop+".A11",prop+".A12",prop+".A13",prop+".A14",prop+".A21",prop+".A22",prop+".A23",prop+".A24",prop+".A31",prop+".A32",prop+".A33",prop+".A34",
                    prop+".A41",prop+".A42",prop+".A43",prop+".A44"]
        elif "ConstraintList" in typeId:
            conlist = getattr(obj,prop)
            names = [prop + "." + con.Name for con in conlist if con.Name]
            return names
        elif "Spreadsheet::Sheet" in typeId:
            FreeCAD.Console.PrintMessage("Spreadsheet aliases\n")
            ignore = ["columnWidths","rowHeights"]
            aliases = [prop + "." + pl for pl in obj.PropertiesList if pl not in ignore]
            FreeCAD.Console.PrintMessage(str(aliases)+"\n")
            return aliases

    def onChanged(self, fp, prop):
        if prop == "Refresh" and fp.Refresh:
            fp.Refresh = False
            self.setupVariables(fp) #calls refresh()
        elif prop == "VariableCount":
            self.setupVariables(fp)
        elif prop == "StartAnimating" and fp.StartAnimating:
            fp.StartAnimating = False
            t = QtCore.QTimer()
            t.singleShot(50+fp.InitialDelay*1000, self.startAnimating) #avoid warning message about selection changing while committing data
        elif "Variable" in prop and not bool("Count" in prop or "Nth" in prop or "Start" in prop or "Step" in prop):
            self.checkAndWarnAliases(fp,prop)

    def startAnimating(self):
        self.isAnimating = True
        fp = FreeCAD.ActiveDocument.getObject(self.fpName)
        variables = {} #tuple ii:(prop,start,step)
        animated = 0
        for ii in range(1,fp.VariableCount+1):
            variables[ii] = (getattr(fp,"Variable"+format(ii,'03')),getattr(fp,"Variable"+format(ii,'03')+"Start"),\
                             getattr(fp,"Variable"+format(ii,'03')+"Step"),getattr(fp,"Variable"+format(ii,'03')+"Nth"))
            if getattr(fp,"Variable"+format(ii,'03')) != "Select Property":
                animated += 1
        if animated == 0:
            FreeCAD.Console.PrintError("No properties to animate.  Select some properties and try again.\n")
            return
        else:
            for k,v in variables.items(): #save obj.ExpressionEngine for each obj in self.expressionsDict
                prop = v[0]
                objname = prop.split(".")[0]
                obj = FreeCAD.ActiveDocument.getObject(objname)
                self.saveExpressions(fp,obj)
        counter = 1
        oldLabel2 = fp.Label2
        while (counter <= fp.Frames and not fp.StopAnimating):
            for jj in range(1,fp.VariableCount+1):
                if variables[jj][0] != "Select Property":
                    nth = counter % variables[jj][3] #remainder of dividing counter by Nth property
                    if nth == 0:
                        self.setProperty(fp,variables[jj][0],variables[jj][1] + variables[jj][2] * counter)
            if fp.ShowProgress:
                fp.Label2 = str(counter)+"/"+str(fp.Frames)
            FreeCADGui.updateGui()
            time.sleep(fp.Sleep)
            counter += 1
        fp.StopAnimating = False
        self.isAnimating = False
        self.restoreExpressions(fp)
        fp.Label2 = oldLabel2
        FreeCAD.ActiveDocument.recompute()

    def setupVariables(self,fp):
        self.refresh(fp)
        ii = fp.VariableCount+1
        while hasattr(fp,"Variable"+format(ii,'03')):
            fp.removeProperty("Variable"+format(ii,'03'))
            fp.removeProperty("Variable"+format(ii,'03')+"Start")
            fp.removeProperty("Variable"+format(ii,'03')+"Step")
            fp.removeProperty("Variable"+format(ii,'03')+"Nth")
            ii += 1
        for ii in range(1,fp.VariableCount+1):
            baseName = "Variable"+format(ii,'03')
            if not hasattr(fp,baseName):
                fp.addProperty("App::PropertyEnumeration",baseName,"AnimatorVariables","Object.Property to use for this variable")
                setattr(fp,baseName,self.properties)
            else:
                saved = getattr(fp,baseName)
                setattr(fp,baseName,self.properties)
                if saved in self.properties:
                    setattr(fp,baseName,saved)
            if not hasattr(fp,baseName+"Start"):
                fp.addProperty("App::PropertyFloat",baseName+"Start","AnimatorVariables","Starting value for this variable")
                setattr(fp,baseName+"Start",0)
            if not hasattr(fp,baseName+"Step"):
                fp.addProperty("App::PropertyFloat",baseName+"Step","AnimatorVariables","Step -- amount by which this variable is incremented (or decremented if negative) each frame.")
                setattr(fp,baseName+"Step",1)
            if not hasattr(fp,baseName+"Nth"):
               fp.addProperty("App::PropertyIntegerConstraint",baseName+"Nth","AnimatorVariables","If other than 1, only increment/decrement every nth frame.")
               setattr(fp,baseName+"Nth",(1,1,10000,1))

    def isSupportedType(self,fp,typeId):
        '''returns False if not supported, else True'''
        if typeId not in fp.Supported:
            return False
        else:
            return True

    def getProperties(self,fp,obj):
        '''get the supported properties of obj'''
        if obj.TypeId != "Spreadsheet::Sheet":
            props = [prop for prop in obj.PropertiesList if self.isSupportedType(fp,obj.getTypeIdOfProperty(prop)) and obj.getEditorMode(prop) == []]
        else:
            props = [prop for prop in obj.PropertiesList if self.isSupportedType(fp,obj.getTypeIdOfProperty(prop))]
        return props

    def saveExpressions(self,fp,obj):
        '''saves expression engine property of obj the first time setProperty() is called for obj'''
        if not obj in self.expressionDict.keys() and hasattr(obj,"ExpressionEngine"):
            self.expressionDict[obj.Name] = obj.ExpressionEngine

    def restoreExpressions(self,fp):
        for k,v in self.expressionDict.items():
            obj = FreeCAD.ActiveDocument.getObject(k)
            for expr in v:
                obj.setExpression(expr[0],expr[1])
        self.expressionDict = {}

    def checkAndWarnAliases(self,fp,prop):
        '''if user has selected an alias, then warn'''
        objname = getattr(fp,prop).split(".")[0]
        obj = FreeCAD.ActiveDocument.getObject(objname)
        if hasattr(obj,"TypeId") and obj.TypeId == "Spreadsheet::Sheet":
            FreeCAD.Console.PrintWarning("Warning: Spreadsheet aliases containing expressions will not be restored after animation is complete.\n")

    def setProperty(self,fp,prop,val):
        '''prop is in form "objectname.property.subproperty.subproperty" ,e.g. "Box.Placement.Base.x"'''
        objname = prop.split(".")[0]
        obj = FreeCAD.ActiveDocument.getObject(objname)
        if obj.TypeId != "Spreadsheet::Sheet":
            obj.setExpression(prop[len(objname)+1:],str(val))
            FreeCAD.ActiveDocument.recompute()
            obj.setExpression(prop[len(objname)+1:],None)
        else:
            obj.set(prop[len(objname)+1:],str(val))
            FreeCAD.ActiveDocument.recompute()

    def refresh(self,fp):
        '''setup Properties enumeration to contain each property of the objects supported objectname.propertyname format'''
        doc = FreeCAD.ActiveDocument
        objects = [obj for obj in doc.Objects if obj != fp and not obj.TypeId in fp.BlacklistedObjects]
        self.properties = []
        for obj in objects:
            if obj.TypeId == 'App::Part':
                props = self.getProperties(fp,obj)
                if props:
                    for prop in props:
                        # subprops = self.getSubProperties(prop,obj.getTypeIdOfProperty(prop),obj)
                        # for sub in subprops:
                        #     self.properties.extend([obj.Name+"."+sub])
                        if prop == "masterRotation" or prop == "slaveAngularPosition":
                            self.properties.extend([obj.Name+"."+prop])
        self.properties.sort()
        self.properties = ["Select Property"] + self.properties



class AnimatorVP:
    def __init__(self, obj):
        '''Set this object to the proxy object of the actual view provider'''
        obj.Proxy = self

    def doubleClicked(self,vobj):
        if vobj.Object.Proxy.isAnimating:
            vobj.Object.StopAnimating = True
        else:
            vobj.Object.StartAnimating = True

    def attach(self,vobj):
        self.Object = vobj.Object
        self.standard = coin.SoGroup()
        vobj.addDisplayMode(self.standard,"Standard")

    def onDelete(self, vobj, subelements):
        return True

    def updateData(self, fp, prop):
        '''If a property of the handled feature has changed we have the chance to handle this here'''
        if prop == "StartAnimating" or prop == "StopAnimating":
            fp.ViewObject.signalChangeIcon()

    def getDisplayModes(self,obj):
        '''Return a list of display modes.'''
        modes=["Standard"]
        return modes

    def claimChildren(self):
        return[]

    def getDefaultDisplayMode(self):
        '''Return the name of the default display mode. It must be defined in getDisplayModes.'''
        return "Standard"

    def setDisplayMode(self,mode):
        '''Map the display mode defined in attach with those defined in getDisplayModes.\
                Since they have the same names nothing needs to be done. This method is optional'''
        return mode

    def onChanged(self, vp, prop):
        '''Here we can do something when a single property got changed'''
        #FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")
        pass

    def getIcon(self):
        '''Return the icon in XPM format which will appear in the tree view. This method is\
                optional and if not defined a default icon is shown.'''
        iconAnimating = """
/* XPM */
static char *_635391677201[] = {
/* columns rows colors chars-per-pixel */
"64 64 4 1 ",
"  c black",
". c #FFFF7F7F2727",
"X c #FFFFF2F20000",
"o c None",
/* pixels */
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX    ooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX    ooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX    ooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX    ooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX    ooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX    ooo",
"ooo   XXXooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"ooo   XXXooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"ooo   XXXooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"ooo   XXXooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX    ooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX    ooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX    ooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX    ooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX    ooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX    ooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX    ooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo     ................................................     ooo",
"ooo     ................................................     ooo",
"ooo     ................................................     ooo",
"ooo     ................................................     ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo     ................................................     ooo",
"ooo     ................................................     ooo",
"ooo     ................................................     ooo",
"ooo     ................................................     ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo     ................................................     ooo",
"ooo     ................................................     ooo",
"ooo     ................................................     ooo",
"ooo     ................................................     ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo"
};"""
        iconNormal = """
/* XPM */
static char *_635391677201[] = {
/* columns rows colors chars-per-pixel */
"64 64 4 1 ",
"  c black",
". c #FFFF7F7F2727",
"X c #FFFFF2F20000",
"o c None",
/* pixels */
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"ooooooooooooooooooooooooooooooooooooooooooXXX   XXX   XXX    ooo",
"ooooooooooooooooooooooooooooooooooooooooooXXX   XXX   XXX    ooo",
"ooooooooooooooooooooooooooooooooooooooooooXXX   XXX   XXX    ooo",
"ooooooooooooooooooooooooooooooooooooooooooXXX   XXX   XXX    ooo",
"ooooooooooooooooooooooooXXX   XXX   XXX   XXX   XXX   XXX    ooo",
"ooooooooooooooooooooooooXXX   XXX   XXX   XXXooooooooooooooooooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXXooooooooooooooooooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXXooooooooooooooooooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXXooooooooooooooooooo",
"ooo   XXX   XXX   XXX   oooooooooooooooooooooooooooooooooooooooo",
"ooo   XXX   XXX   XXX   oooooooooooooooooooooooooooooooooooooooo",
"ooo   XXXooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"ooo   XXXooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"ooo   XXXooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"ooo   XXXooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"ooo   XXXooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX    ooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX    ooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX    ooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX    ooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX    ooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX    ooo",
"ooo   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX   XXX    ooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo     ................................................     ooo",
"ooo     ................................................     ooo",
"ooo     ................................................     ooo",
"ooo     ................................................     ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo     ................................................     ooo",
"ooo     ................................................     ooo",
"ooo     ................................................     ooo",
"ooo     ................................................     ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo     ................................................     ooo",
"ooo     ................................................     ooo",
"ooo     ................................................     ooo",
"ooo     ................................................     ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"ooo                                                          ooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",
"oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo"
};"""
        if self.Object.Proxy.isAnimating:
            return iconAnimating
        else:
            return iconNormal

    def __getstate__(self):
        '''When saving the document this object gets stored using Python's json module.\
                Since we have some un-serializable parts here -- the Coin stuff -- we must define this method\
                to return a tuple of all serializable objects or None.'''
        return None

    def __setstate__(self,state):
        '''When restoring the serialized object from document we have the chance to set some internals here.\
                Since no data were serialized nothing needs to be done here.'''
        return None
#######################################
