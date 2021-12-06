## FreeCAD InvGears Workbench v0.1.2

## Overview

The InvGears workbench allows the creation of gear systems. The gear generation algorithm is based on [[1]](#1), which generates the involute and fillet curves. 

Now with spherical involute gear!!!

Starting from the equations in the book [[1]](#1), I obtained all the equations of the involute and fillet curves for the spherical gears.

Given a set of parameters corresponding to a pair of gears, the algorithm finds the geometry of both gears.

It is also possible to create a body with two gears, allowing the creation of cascading gears.
In addition, it is possible to create internal gears.

The offsets of the gears on the plane are calculated analytically, since the derivatives of the geometric equations were obtained to achieve this goal.

On the other hand, it is possible to create gears in an SVG file independently. If you want to create gears in SVG from those already created, this last tool allows you to load the parameters of these gears and then create the SVG file.

InvGears makes use of PartDesign to create bodies in which the gears are located. This allows the gears to be modified using PartDesign. It also uses parts that allow you to easily link other parts with the gears.

Two control parameters are added to the master part that allows to animate the gears easily, making use for example of animator macro (https://github.com/mwganson/animator). This macro was added within the workbench, but to only show the gears control variables.


![](freecad/invgears/Resources/media/sphericalGears.gif)


## Installation

### GNU/Linux
<details>
  <summary>Expand for details</summary>

#### Installing for all users

Copy InvGears folder into `/usr/share/freecad/Mod/`

#### Installing for a single user

Copy InvGears folder into `/home/username/.FreeCAD/Mod/`  where username is your user name
</details>

### Windows
<details>
  <summary>Expand for details</summary>

#### Installing for all users

Copy InvGears/ folder into `C:\Program Files\FreeCAD\Mod\`

#### Installing for a single user

Copy InvGears folder into `C:\Users\username\Appdata\Roaming\FreeCAD\Mod\` where username is your user name
</details>

### macOS
<details>
  <summary>Expand for details</summary>

#### Installing for all users

Copy InvGears folder into `/Applications/FreeCAD/Mod/`

#### Installing for a single user

Copy InvGears folder into `/Users/username/Library/Preferences/FreeCAD/Mod/` where username is your user name
</details>

## Getting Started

[Tutorial #1](freecad/invgears/Resources/tutorial/tutorial1.md)

[Tutorial #2](freecad/invgears/Resources/tutorial/tutorial2.md)

## Release notes

- 2021.12.04 (0.1.2)
    Spherical involute gear were added

    The use of Part is incorporated for a better workflow, which allows to obtain links with other parts and animations easily

    Task panels were improved

- 2021.10.31 (0.1.1)

    Animator was added inside the workbench as a last button

    Animator information is found at: https://github.com/mwganson/animator

## References

<a id="1">[1]</a> Colbourne, John R. The geometry of involute gears. Springer Science & Business Media, 2012.

## Acknowledgments

I want to thank the Telegram group ["FreeCAD en español"](https://t.me/FreeCAD_Es), and give a special thanks to Maxi, Juan Manuel, and Pepe for their suggestions and corrections

---------------------------------------------------------

## FreeCAD Entorno de trabajo InvGears

## Visión general

El entorno de trabajo InvGears permite la creación de sistemas de engranajes. El algoritmo de generación de engranajes se basa en [[1]](#1), el cual genera las curvas involutas y de fileteo.

Ahora con engranajes esféricos involutivos!!!

The InvGears workbench allows the creation of gear systems. The gear generation algorithm is based on [[1]](#1). In which the involute and fillet curves are generated.

Now with spherical involute gear!!!

Arrancando de las ecuaciones del libro [[1]](#1), obtuve todas las ecuaciones de las curvas involutas y de fileteo de los engranajes esféricos.

Dado un conjunto de parámetros correspondientes a un par de engranajes, el algoritmo encuentra la geometría de ambos engranajes.

También es posible crear un cuerpo con dos engranajes, lo que permite la creación de engranajes en cascada. Además, es posible crear engranajes internos.

Los offset de los engranajes sobre el plano se calculan analíticamente, ya que se obtuvieron las derivadas de las ecuaciones geométricas para lograr este objetivo.

Por otro lado, es posible crear engranajes en un archivo SVG de forma independiente. Si desea crear engranajes en SVG a partir de los ya creados, esta última herramienta le permite cargar los parámetros de estos engranajes y luego crear el archivo SVG.

InvGears hace uso de PartDesign para crear cuerpos en los que se ubican los engranajes. Esto permite modificar los engranajes utilizando PartDesign.

![](freecad/invgears/Resources/media/sphericalGears.gif)


## Instalación

### GNU/Linux
<details>
  <summary>Expandir para detalles</summary>

#### Instalación para todos los usuarios

Copie la carpeta InvGears en `/usr/share/freecad/Mod/`

#### Instalación para un solo usuario

Copie la carpeta InvGears en `/home/username/.FreeCAD/Mod/` donde username es su nombre de usuario
</details>

### Windows
<details>
  <summary>Expandir para detalles</summary>
  
#### Instalación para todos los usuarios

Copie la carpeta InvGears en `C:\Archivos de programa\FreeCAD\Mod\`

#### Instalación para un solo usuario

Copie la carpeta InvGears en `C:\Users\username\Appdata\Roaming\FreeCAD\Mod\` donde username es su nombre de usuario
</details>

### macOS
<details>
  <summary>Expandir para detalles</summary>
  
#### Instalación para todos los usuarios

Copie la carpeta InvGears en `/Aplicaciones/FreeCAD/Mod/`

#### Instalación para un solo usuario

Copie la carpeta InvGears en `/Users/username/Library/Preferences/FreeCAD/Mod/` donde username es su nombre de usuario
</details>

## Empezando

* [Tutorial #1](freecad/invgears/Resources/tutorial/tutorial1.md)
* [Tutorial #2](freecad/invgears/Resources/tutorial/tutorial2.md)

## Notas de lanzamiento

- 2021.12.04 (0.1.2)
    Se añadieron engranajes esféricos involutivos

    Se incorpora el uso de Part para un mejor flujo de trabajo, que permite obtener enlaces con otras partes y animaciones facilmente.

    Los paneles de tareas fueron mejorados

- 2021.10.31 (0.1.1)

    La macro Animator se agregó dentro del entorno de trabajo como último botón

    La información de Animator se encuentra en: https://github.com/mwganson/animator

## Referencias

<a id="1">[1]</a> Colbourne, John R. The geometry of involute gears. Springer Science & Business Media, 2012.


## Agradecimientos

Quiero agradecer al grupo de Telegram ["FreeCAD en español"](https://t.me/FreeCAD_Es), y dar un especial agradecimientoa  Maxi, Juan Manuel y Pepe por sus sugerencias y correcciones.
