# Pixel Constant Projection Addon

Addon for Blender that helps with fitting object of interest in the pixel constant view of the camera.

Tested on Blender 3.2.1, but could work on other versions.

## Usage
- Locate `Pixel Constant Projection` in the right side panel of the 3D viewport
- Set camera angle, distance from center and pixels per unit
- Update camera, make sure the target object is selected
- Camera view now fits active object's bounding box. The camera resolution is changed based on bouding box size

## Installation
- Clone this repository
- Launch Blender
- Open the User Preferences window by navigating to `Edit` > `Preferences`
- Switch to the Add-ons tab
- Click the Install button at the top right corner
- Locate and select the `.py` file located in this repository
- Click the Install Add-on button
- Enable the addon by checking the checkbox next to its name in the addons list
- Save the preferences to ensure the addon is enabled on Blender startup.

## Contributing
If you would like to contribute, please follow the guidelines outlined in the `CONTRIBUTING.md` file.

## Licence
This project is licensed under the MIT License.
