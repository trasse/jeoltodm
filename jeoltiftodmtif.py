#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Created on Wed Feb  1 09:15:43 2017
ver: 0.1

Script for converting JEOL TIFF files in current directory with data embedded
in xml in the tiff tags into a tiff with the correct meta data to have scale
included in digital Micrograph...

Warning: May invalidate Institution/JEOL legal agreements.

N.B.
    1. can not find where unit for length per pixel is in the JEOL xml data -
    currently assuming LengthPerPixel is always in nanometers? If not, can
    change this in Digital Micrograph properties using Ctrl+D
    2. Diffraction length calibration will require updating for some camera
    lengths and after calibration of microscope - can't find where this is
    stored in the XML content...


TODO: convert to dm3

@author: dr richard f webster
"""

import os
import tifffile as tif
import untangle
import tkinter as tk
import tkinter.filedialog

# Camera Length look up dictionary
def diffperpix(x):
    return {
        60   : 1,
        80   : 1,
        100  : 0.0754716981,
        120  : 1,
        150  : 0.0583090379,
        200  : 1,
        250  : 0.05832227429446,
        300  : 0.033803513370276,
        400  : 0.044270673277212,
        500  : 0.017923967937704,
        600  : 0.012224825868968,
        800  : 0.014601665494512,
        1000 : 0.008620147191317,
        1200 : 1,
        }[x]


# Function to get xml and add as gatan type (DM readable) of TIFF tags
def adddm3tags(filename):
    image = tif.imread(filename)
    print(filename)
    # Opens File and gets tag information
    with tif.TiffFile(filename) as tiff:
        for page in tiff:
            for tag in page.tags.values():
                #t = tag.name, tag.value
                if tag.name == "image_description":
                    # Get the JEOL xml data (its in byte format)
                    raw_xml=tag.value


            #image = page.asarray()

    # debug: print(raw_xml)

    # saves xml data into textfile and decodes it from bytes to a UTF8 string
    # actual file is needed for untangle
    xml_filename = "{}.xml".format(filename)
    xml_file = open(xml_filename, "w", encoding="utf-8")
    xml_file.write(raw_xml.decode("utf-8"))
    xml_file.close()

    try:    # only do files with valid xml i.e. the JEOL files
            # could add extra step to ake sure that the xml is the right xml, i.e. TemReporter2 as the first
        xml = untangle.parse(xml_filename)
    except:
        print("Not a JEOL TIFF")
        return


    lengthperpix = float(xml.TemReporter2.MeasurementReporter.a_MeasureLengthPerPixelReporter.a_LengthPerPixel.cdata)
    mode = str(xml.TemReporter2.MeasurementReporter.a_MeasurementUnitType.cdata)

    #Camera length
    CL = int(xml.TemReporter2.MeasurementReporter.a_SelectorValue.cdata)

    print("Length Per Pixel: \t {}".format(lengthperpix))

        # for nm images doesn't work for STEM images?
    if mode == "UnitType_Scanning" or mode == "UnitType_Length":
        sunitname = "nm"
        lunitname = "nanometer"
    # for diffraction patterns
    elif mode == "UnitType_Diffraction":
        sunitname = "1/nm"
        lunitname = "1/nanometer"
        print(CL)
        lengthperpix = diffperpix(CL)
        print("Length Per Pixel: \t {}".format(lengthperpix))

    else: print("Wrong Mode investigate {}".format(filename))


    tags = [( 65003, 's', 3, sunitname, False ),
            ( 65004, 's', 3, sunitname, False ),
            ( 65009, 'd', 1, lengthperpix, False ),
            ( 65010, 'd', 1, lengthperpix, False ),
            ( 65012, 's', 10, lunitname, False ),
            ( 65013, 's', 10, lunitname, False )]


    with tif.TiffWriter("{}_{}.tif".format(filename[:-4], "dm"),
                        imagej=True) as tiff:
        tiff.save(image, resolution=(float(1/lengthperpix), float(1/lengthperpix)),
                 extratags=tags, metadata={"unit":sunitname})
    # Delete xml file just created
    os.remove(xml_filename)


if __name__ == "__main__":
    root = tk.Tk()
    root.title('JEOLtiff to DMtiff')


    # Open Sesame
    dirname = tkinter.filedialog.askdirectory(parent=root,initialdir="\\",title="Choose a Directory...")
    os.chdir(dirname)

    if len(dirname ) > 0:
        print("You chose {}".format(dirname))

    print(os.getcwd())
    print(os.listdir(os.getcwd()))
    os.mkdir("dm")

    for file in os.listdir(os.getcwd()):
        if os.path.isdir(file): continue
        else:
            print(file)
            filen = os.path.splitext(file)
            if filen[-1] == (".tif" or ".tiff"): # only do TIFF files
                adddm3tags("{}/{}".format(dirname,file))


    root.destroy()

"""
Reference:
 Other important info from xml for possible use in the future?

 Image size x:         xml.TemReporter2.ImageDataInformation.a_ImageSize.b_width.cdata
 Image size y:         xml.TemReporter2.ImageDataInformation.a_ImageSize.b_height.cdata

 Accel. Voltage:       xml.TemReporter2.MeasurementReporter.a_AccVoltage.cdata
 Wavelength:           xml.TemReporter2.MeasurementReporter.MeasureDiffractionPerPixelReporter.a_WaveLength.cdata

 Length Per Pixel:     xml.TemReporter2.MeasurementReporter.a_MeasureLengthPerPixelReporter.a_LengthPerPixel.cdata

 unit?                 always nm or nm-1
                       xml.TemReporter2.MeasurementReporter.a_CameraIsInverse.cdata

 Magnification:        xml.TemReporter2.MeasurementReporter.a_SelectorValue.cdata
 Camera Length:        xml.TemReporter2.MeasurementReporter.a_SelectorValueScanningDiffraction.cdata

 Defocus:              xml.TemReporter2.ObservationReporter.a_EOSReporter.b_DefocusString.cdata
 Defocus unit:         xml.TemReporter2.ObservationReporter.a_EOSReporter.b_DefocusUnitString.cdata


B, s, H, I, 2I, b, h, i, 2i, f, d, Q, or q
"""
