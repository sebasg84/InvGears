# FreeCAD InvGears workbench

Current version 0.1.1

## Overview

The InvGears workbench allows the creation of gear systems. The gear generation algorithm is based on [[1]](#1).

Given a set of parameters corresponding to a pair of gears, the algorithm finds the geometry of both gears.

It is also possible to create a body with two gears, allowing the creation of cascading gears.
In addition, it is possible to create internal gears.

A very important parameter that was added is an offset for 3D printers. The offset of the gears is calculated analytically, since the derivatives of the geometric equations were obtained to achieve this goal.

On the other hand, it is possible to create gears in an SVG file independently. If you want to create gears in SVG from those already created, this last tool allows you to load the parameters of these gears and then create the SVG file.

InvGears makes use of PartDesign to create bodies in which the gears are located. This allows the gears to be modified using PartDesign.

![](freecad/invgears/Resources/media/mainImage.png)

A small example of how to use the workbench is presented in the following video
https://youtu.be/lxtZ2gQRi88

## Installation

### **GNU/Linux**

**Installing for all users**

Copy InvGears folder into /usr/share/freecad/Mod/

**Installing for a single user**

Copy InvGears folder into /home/username/.FreeCAD/Mod/  where username is your user name

### **Windows**

**Installing for all users**

Copy InvGears folder into C:\Program Files\FreeCAD\Mod\

**Installing for a single user**

Copy InvGears folder into C:\Users\username\Appdata\Roaming\FreeCAD\Mod\ where username is your user name

### **macOs**

### Installing for all users

Copy InvGears folder into /Applications/FreeCAD/Mod/

### Installing for a single user

Copy InvGears folder into /Users/username/Library/Preferences/FreeCAD/Mod/ where username is your user name

## Getting Started

[Tutorial #1](Resources/tutorial/tutorial1.md)

## Release notes

- 2021.10.31 (0.1.1)

    Animator was added inside the workbench as a last button

    Animator information is found at: https://github.com/mwganson/animator

## References
<a id="1">[1]</a> 
Colbourne, John R. The geometry of involute gears. Springer Science & Business Media, 2012.

******************************************************************************************************************

# FreeCAD Entorno de trabajo InvGears

## Visión general

El entorno de trabajo InvGears permite la creación de sistemas de engranajes. El algoritmo de generación de engranajes se basa en [[1]](#1).

Dado un conjunto de parámetros correspondientes a un par de engranajes, el algoritmo encuentra la geometría de ambos engranajes.

También es posible crear un cuerpo con dos engranajes, lo que permite la creación de engranajes en cascada. Además, es posible crear engranajes internos.

Un parámetro muy importante que se agregó es un offset para impresoras 3D. El offset de los engranajes se calcula analíticamente, ya que se obtuvieron las derivadas de las ecuaciones geométricas para lograr este objetivo.

Por otro lado, es posible crear engranajes en un archivo SVG de forma independiente. Si desea crear engranajes en SVG a partir de los ya creados, esta última herramienta le permite cargar los parámetros de estos engranajes y luego crear el archivo SVG.

InvGears hace uso de PartDesign para crear cuerpos en los que se ubican los engranajes. Esto permite modificar los engranajes utilizando PartDesign.

![](freecad/invgears/Resources/media/mainImage.png)

Un pequeño ejemplo de cómo usar el banco de trabajo se presenta en el siguiente video https://youtu.be/lxtZ2gQRi88

## Instalación

### **GNU/Linux**

**Instalación para todos los usuarios**

Copie la carpeta InvGears en /usr/share/freecad/Mod/

**Instalación para un solo usuario**

Copie la carpeta InvGears en /home/username/.FreeCAD/Mod/ donde username es su nombre de usuario

### **Windows**

**Instalación para todos los usuarios**

Copie la carpeta InvGears en C:\Archivos de programa\FreeCAD\Mod\

**Instalación para un solo usuario**

Copie la carpeta InvGears en C:\Users\username\Appdata\Roaming\FreeCAD\Mod\ donde username es su nombre de usuario

### **Mac OS**

**Instalación para todos los usuarios**

Copie la carpeta InvGears en /Aplicaciones/FreeCAD/Mod/

**Instalación para un solo usuario**

Copie la carpeta InvGears en /Users/username/Library/Preferences/FreeCAD/Mod/ donde username es su nombre de usuario

## Empezando

[Tutorial #1](Resources/tutorial/tutorial1.md)

## Notas de lanzamiento

- 2021.10.31 (0.1.1)

    La macro Animator se agregó dentro del entorno de trabajo como último botón

    La información de Animator se encuentra en: https://github.com/mwganson/animator

## Referencias
<a id="1">[1]</a> 
Colbourne, John R. The geometry of involute gears. Springer Science & Business Media, 2012.
