# Dynamic Text Object for Blender

**Version**: 1.10.7  
**Author**: Rolf Jethon, ChatGPT  
**Blender Version**: 4.2+  
**Category**: Add > Dynamic Text

## Description
This Blender add-on creates special text objects whose content can dynamically display values controlled by drivers or properties.  
Text can contain markers in the form `{marker}`, which will be replaced at runtime with formatted values.
Example:
``` 
Speed: {speed} Height: {height}   
```
will display:

Speed: 34.50 Height: 12.00

## Features
* Use {marker} syntax in the text body - multiple markers are supported
* Assign and edit marker values in the object data properties panel
* Supports driver-controlled values (e.g. linked to another object's location or rotation)
* Updates driver generated values immediately
* Custom format strings (e.g. "%.1f" or "%.3f")
* Escaped markers: Use \{ or \} to display literal curly braces
* Updates automatically when switching between Edit and Object mode
* Fully replaces Blender's native text object for dynamic scenarios
* Fully supports Blender's text formatting possibilities like text boxes, fonts, extrude, beveling etc.
* Escaped braces (`\{` or `\}`) allow literal curly brace characters

## Usage
1. Go to "Add >  Dynamic Text" to create a dynamic text object.
2. In Edit Mode, type text with markers (e.g. Speed: {speed}).
3. Switch to Object Mode - the text will update to display values.
4. In the Object Data Properties panel, edit the value or format.
5. To drive values via Blender drivers, add a driver to the marker's value field.

## Known Limitations
- Markers must be alphanumeric (no spaces or special characters).
- If the same marker name is used twice, only the first is used for editing.
- Does not work consistently togehter with the blender undo stack.

## License
GPL-3.0-or-later# Blender_dynamic_text
Blender addon - add a dynamic text object

## Links
Blender demo of the addon https://www.youtube.com/watch?v=nDNOk_NRz9Q
