A small script for converting JEOL TIFF files (from JEOL "Analysis Center") from a chosen directory with data embedded in xml format  in the tiff tags into a tiff with the correct meta data to have scale included in Gatan Digital Micrograph and ImageJ...

Warning: May invalidate Institution/JEOL legal agreements.

<b>N.B.</b>
 - 1. can not find where unit for length per pixel is in the JEOL xml data -
    currently assuming LengthPerPixel is always in nanometers? If not, can
    change this in Digital Micrograph properties using Ctrl+D
 - 2. Diffraction length calibration will require updating for some camera
    lengths and after calibration of microscope - can't find where this is
    stored in the XML content...

Requirements (install using your favourite python package manager):
 - "untangle" for parsing xml files (e.g. pip install untangle)
 - "tifffile" for editing tiff tags (e.g. pip install tifffile)
 - "tkinter" for file dialogue (e.g. pip install tkinter)
