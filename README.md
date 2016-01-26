# Simple Image Resizing Server - Python

This is a dead simple image resizing server written using python's Pillow, uwsgi & nginx.  

Image cropping & quality modification are initially done using Pillow, once the modified image is cached, it will be served directly from the file system by nginx to increase the speed.

Any  suggestions/contributions are appreciated.

## Requirements

 - Python 2.7 
 - Pillow 
 - uwsgi

## Configuration

All the configuration should go in `imageserver.ini` in the module directory. Sample Config can be found in `sample_configs` directory.

If *allowed-sizes* & *allowed-qualities* are mentioned, only those sizes will be cropped & all others will be rejected. This  is useful  to prevent attackers from filling your disk-space.


## Usage

    http://example.com/images/<width>x<height:optional>/<quality:optional>/relative/path/to/image.jpg

 **Note**:

 - If quality value is ignored, the `default-quality` will be used. If `default-quality` is not present,  90 will be used as default.
 - If only width is present, height will be calculated automatically to keep the aspect ratio of original image.

## Examples:

 - For original Image:
         http://example.com/images/0/relative/image.jpg
 - To modify only the width & keep the aspect ratio of image
     - http://example.com/images/50x0/90/relative/image.jpg
                                                    *or*
     - http://example.com/images/50/90/relative/image.jpg
 - To modify only the height & keep the aspect ratio of image
        http://example.com/images/0x50/90/relative/image.jpg