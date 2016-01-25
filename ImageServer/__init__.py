""" Image Resizer

This module provides functionality to resize images using `pillow`
"""

from PIL import Image
import os
import re
from ConfigParser import ConfigParser


common_img_types = {
    # very common
    'ico'  : 'image/vnd.microsoft.icon',
    'jpg'  : 'image/jpeg',
    'jpeg' : 'image/jpeg',
    'gif'  : 'image/gif',
    'png'  : 'image/png',
    'webp' : 'image/webp',
    # not very common
    'ief'  : 'image/ief',
    'jpe'  : 'image/jpeg',
    'pct'  : 'image/pict',
    'pic'  : 'image/pict',
    'pict' : 'image/pict',
    'pgm'  : 'image/x-portable-graymap',
    'pbm'  : 'image/x-portable-bitmap',
    'pgm'  : 'image/x-portable-graymap',
    'pnm'  : 'image/x-portable-anymap',
    'ppm'  : 'image/x-portable-pixmap',
    'ras'  : 'image/x-cmu-raster',
    'rgb'  : 'image/x-rgb',
    'tif'  : 'image/tiff',
    'tiff' : 'image/tiff',
    'xpm'  : 'image/x-xpixmap',
    'xwd'  : 'image/x-xwindowdump' }

class ImageServerException(Exception):
    """Raised when requested size or quality or url is not valid or allowed."""
    pass

class ImageServerConfig(ConfigParser):
    """Parses & sets the configuration values
        
    This class expects a real config file although
    it will be ignored by `ConfigParser` if doesn't exists.

    :param config_file: Path to configuration file
    :return: dictionary containing all the options
    :rtype: dict
    """
    # default config dict
    # no-slashes for dir's
    config =  {
    'images-path' : '',
    'cache-path'  : 'cache',
    'allowed-sizes' : '',
    'allowed-qualities' : '',
    'default-quality': 90
    }


    def as_dict(self, config_file , section_name='imageserver'):
        self.read(config_file)
        if self.has_section(section_name):
            ad = dict(self._sections)
            d = ad[section_name]
            for k,v in self.config.items():
                self.config[k] = d.get(k,v)

                if k == 'allowed-sizes' or k == 'allowed-qualities':
                    self.config[k].split(',')
                

        return self.config

class ImageServer():
    """Main Class for image formatting & resizing
    
    This class resizes & changes the format of the image based
    on the requested URL.
    """

    # default config
    imgType    = None
    image_path = None
    newWidth   = 0
    newHeight  = 0
    quality    = 90

    def __init__(self, config_file='imageserver.ini'):
        if os.path.isfile(config_file):
            self.config = ImageServerConfig().as_dict(config_file)

    def _parse_uri(self , uri):
        """Parses & sets the size & path of the image from REQUEST_URI
        
        This method parses the REQUEST_URI & sets the `newWidth`, `newHeight`,`image_path` & `imgType`.

        :param uri:  REQUEST_URI
        :return: 1
        :rtype: int
        """

        # Parsing 
        pattern = "/(\w+)/(\d*x?\d*)/?(\d{0,2})/?(.+)\.(\w+)"   
        try:
            parts   = re.findall(pattern, uri)[0]
        except IndexError:
            raise ImageServerException('Invalid URL')  
        
        
        size    = parts[1]
        if 'x' in size:
            new_size = [int(s) for s in size.split('x')]
            self.newWidth = new_size[0]
            self.newHeight = new_size[1]
        else:
            try:
                self.newWidth = int(size)
                self.newHeight = 0
            except Exception:
                pass

        try:
            self.quality    = int(parts[2])
        except Exception:
            self.quality    = self.config.get('default-quality' , 90)

        self.image_path = ''.join( (parts[3], '.' ,parts[4]) )

        return 1

    def resize(self , uri):
        """Resizes the given image
        
        This is the main method used to resize the image.

        :param uri:  REQUEST_URI
        :return: Path to resized image

        """
        self._parse_uri(uri)

        orig_imgpath = '/'.join((self.config.get('images-path','') , self.image_path))
        try:
            im = Image.open(orig_imgpath)
        except IOError:
            raise ImageServerException('Image Not Found')
        
        imgtype      = im.format.lower()
        size         = im.size
        width        = im.size[0]
        height       = im.size[1]

        # Size
        size_str = 'x'.join( ( str(self.newWidth) , str(self.newHeight) ) )
        if (self.newWidth == width and self.newHeight == 0) or (self.newWidth == 0 and self.newHeight == height) or (self.newWidth == 0 and self.newHeight == 0) or (self.newWidth == width and self.newHeight == height):
            self.newHeight = height
            self.newWidth  = width

        elif len(self.config.get('allowed-sizes'))>0 and size_str not in self.config.get('allowed-sizes'):
            raise ImageServerException('Invalid Size Value')

        elif self.newWidth != 0 and self.newHeight == 0:
            self.newHeight = int(round( (self.newWidth * height) / (width * 1.0) ))

        elif self.newWidth == 0 and self.newHeight != 0:
            self.newWidth = int(round( (self.newHeight * width) / (height * 1.0) ))


        # Quality
        if len(self.config.get('allowed-qualities'))>0 and str(self.quality) not in self.config.get('allowed-qualities'):
            raise ImageServerException('Invalid Quality value')


        # Create new Image
        new_im = im.resize( (self.newWidth, self.newHeight) , Image.ANTIALIAS)

        # Save
        self.imgType = imgtype
        size_str = 'x'.join( (str(self.newWidth) , str(self.newHeight) ) )
        save_path = '/'.join( (self.config.get('cache-path','') , uri)  )


        if not os.path.exists(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))

        new_im.save(save_path, None, quality=self.quality)

        return save_path

    def get_mime(self):
        """Returns Mime type of the URI

        :return: Content-type
        :rtype: string
        """
        global common_img_types
        return  common_img_types.get(self.imgType, 'text/plain')
    
