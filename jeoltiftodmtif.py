'''
'CL'ass for handeling tif files from JEOL Analysis Software

@author: dr richard f webster
'''

import os
import tifffile as tif
import untangle
import numpy

import sys
import PyQt5.QtWidgets as QtW
import PyQt5.QtGui as QtG

class JEOLtif:

    type = 'JEOL Tiff'

    def __init__(self, fname):

        self.filename = fname
        self.isJEOL = False

        self.image = tif.imread(self.filename)
        self.open()

        self.meta = {
            'lengthperpix' : 1.0,
            'units' : 'nm',
            'sunitname' : 'nanometers',
            'lunitname' : 'nanometers',
            'mode' : 'TEM',
            'CL' : '300',
            'size_x' : 512,
            'size_y' : 512,
            'kV' : 200,
            'wave' : 2.059e-12,
            'mag' : 1e6
        }
        self.getmetadata()


    def open(self):
        pass

    def close(self):
        pass


    # Camera Length look up dictionary
    def diffperpix(self, x):
        return {
            1000: 0.00593389253664256,
            800 : 0.00725577076695097,
            600 : 0.00995112809088877,
            500 : 0.0118255519223004,
            400 : 0.0142978211147556,
            300  : 0.0196071150493987,
            250  : 0.023058213328805,
            200 : 0.028400313443593,
            150 : 0.0382279170393504,
            #might not be right...
            60   : 1,
            80   : 1,
            100  : 0.0754716981,
            120  : 1,
            1200 : 1,
            }[x]


    #%%
    #   Function to get xml from JEOL tif and add as gatan type (ImageJ and Digital
    #   Micrograph readable) of TIFF tags
    def getmetadata(self):

        # Opens File and gets tag information
        with tif.TiffFile(self.filename) as tiff:
            for page in tiff:
                for tag in page.tags.values():
                    #t = tag.name, tag.value
                    if tag.name == 'image_description':
                        # Get the JEOL xml data (its in byte format)
                        raw_xml=tag.value


        # saves xml data into textfile and decodes it from bytes to a UTF8 string
        # actual file is needed for untangle
        xml_filename = '{}.xml'.format(self.filename)
        with open(xml_filename, 'w', encoding='utf-8') as xml_file:
            xml_file.write(raw_xml.decode('utf-8'))

        try:    # only do files with valid xml i.e. the JEOL files
                # could add extra step to ake sure that the xml is the right xml, i.e. TemReporter2 as the first
            xml = untangle.parse(xml_filename)
            # Delete xml file just created

            self.isJEOL = True

        except:
            print('Not a JEOL TIFF')
            self.isJEOL = False
            return

        self.meta['mode'] = str(xml.TemReporter2.MeasurementReporter.a_MeasurementUnitType.cdata)
        self.meta['lengthperpix'] = float(xml.TemReporter2.MeasurementReporter.a_MeasureLengthPerPixelReporter.a_LengthPerPixel.cdata)
        self.meta['CL'] = int(xml.TemReporter2.MeasurementReporter.a_SelectorValue.cdata)

            # for nm images doesn't work for STEM images?
        if self.meta['mode'] == 'UnitType_Scanning' or self.meta['mode'] == 'UnitType_Length':
            self.meta['sunitname'] = 'nm'
            self.meta['lunitname'] = 'nanometer'
            self.meta['units'] = 'nm'
        # for diffraction patterns
        elif self.meta['mode'] == 'UnitType_Diffraction':
            self.meta['sunitname'] = '1/nm'
            self.meta['lunitname'] = '1/nanometer'
            self.meta['units'] = '1/nm'
            self.meta['lengthperpix'] = self.diffperpix(self.meta['CL'])

        else: print('Wrong _mode_ investigate {}'.format(self.filename))

        # image size
        self.meta['size_x'] = int(xml.TemReporter2.ImageDataInformation.a_ImageSize.b_width.cdata)
        self.meta['size_y'] = int(xml.TemReporter2.ImageDataInformation.a_ImageSize.b_height.cdata)
        # microscope operation conditions
        self.meta['kV'] = int(xml.TemReporter2.MeasurementReporter.a_AccVoltage.cdata)
        self.meta['mag'] = int(xml.TemReporter2.MeasurementReporter.a_SelectorValue.cdata)
        os.remove(xml_filename)


    def savewithtags(self):
        if self.isJEOL == True:
            # save these tags for Digital micrograph to read scale correctly
            # TODO add other metadata - microscope etc - work out how DM does this.
            tags = [( 65003, 's', 3, self.meta['sunitname'], False ),
                    ( 65004, 's', 3, self.meta['sunitname'], False ),
                    ( 65009, 'd', 1, self.meta['lengthperpix'], False ),
                    ( 65010, 'd', 1, self.meta['lengthperpix'], False ),
                    ( 65012, 's', 10, self.meta['lunitname'], False ),
                    ( 65013, 's', 10, self.meta['lunitname'], False )]

            with tif.TiffWriter('{}_{}.tif'.format(self.filename[:-4], 'dm'),
                                imagej=True) as tiff:
                tiff.save(self.image, resolution=(float(1/self.meta['lengthperpix']), float(1/self.meta['lengthperpix'])),
                         extratags=tags, metadata={'unit':self.meta['sunitname']})





#%%
# Main function of the script
def main():

    app = QtW.QApplication(sys.argv)

    # Open Sesame
    dirname = str(QtW.QFileDialog.getExistingDirectory(None, 'Select Directory'))
    os.chdir(dirname)

    if len(dirname ) > 0:
        print('You chose {}'.format(dirname))

    print(os.getcwd())
    print(os.listdir(os.getcwd()))


    for file in os.listdir(os.getcwd()):
        if os.path.isdir(file): continue
        else:
            print(file)
            filen = os.path.splitext(file)
            if filen[-1] == ('.tif' or '.tiff'): # only do TIFF files
                tiff = JEOLtif('{}/{}'.format(dirname,file))
                tiff.savewithtags()

    app.quit()

#%%
if __name__ == '__main__':
    main()
