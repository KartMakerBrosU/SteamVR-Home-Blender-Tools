
# SteamVR Home - Blender

Set of tools to aid with model creation for SteamVR home environments.

## Installation
Download the .zip file, then go to `Edit > Preferences > Addons > Install`, and select the .zip file.

## Location
`3D Viewport > Object Mode > SVR`

## Support
Create Issues request.

## Features
* Modelling:
    * Set dev VMAT such as nodraw, reflectivity_50, etc.
    * Open previously developed VMAT files (must select mod first)

* Attatchments
    * Exports empties as attatchment file (.attatch)

## Notes
 * This tool is intended to be used when exporting the model as an **FBX**. 
    * `FBX Export > Include > Custom Properties` must be enabled.
    * `FBX Export > Transform > Scale` must be set to `3.28084` for Blender's inch to match SVR Hammer's inch unit.
      * At some point blender changed its writing scale, if the previous scale is too big, try `0.393701`.  

 * You must set the scene units to **Imperial.**

* While setting the VMAT creates a `FBX_vmatPath` custom property in the selected material, editing this property by hand *will not* result in the dev texture dropdown being updated (yet).

## TODO
* Update dev tex enum to let user know if the `FBX_vmatPath` custom property doesnt match the dev tex enum.

* Add more developer/internal VMAT's (reflectivity_40, clip space, blocklight, etc.)
