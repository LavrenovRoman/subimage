#!/usr/bin/python
# vim: set ts=2 expandtab:
"""
Module: find_by_ar.py
Desc: find image connected components by their aspect ratio
Author: John O'Neil
Email: oneil.john@gmail.com
DATE: Saturday, Sept 21st 2014

  Given an image, find connected components (after basic filtering)
  that match a given aspect ratio.

  Typical usage:
  ./find_by_ar.py poker.jpg --aspect 0.7 --error 0.018 -d -v 
  
"""

import numpy as np
import scipy.ndimage as sp
import scipy.misc as misc
import scipy.signal as signal
import cv2
import math
import sys
import argparse
import os

def find_by_ar(img, ar, error, min_height=50,min_width=50):
  #(t,binary) = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
  (t,binary) = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
  kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
  binary = cv2.erode(binary, kernel)
  ccs = get_connected_components(binary)
  #if args.debug:
  #  cv2.imwrite('binary.png', binary)
  aoi = []
  for cc in ccs:
    (x, y, w, h)=cc_shape(cc)
    if h<=0:return None
    aspect = float(w)/float(h)
    if aspect > ar-error and aspect < ar+error and w>=min_width and h>=min_width:
      aoi.append(cc)

  return aoi

def cc_shape(component):
  x = component[1].start
  y = component[0].start
  w = component[1].stop-x
  h = component[0].stop-y
  return (x, y, w, h)

def get_connected_components(image):
  s = sp.morphology.generate_binary_structure(2,2)
  labels,n = sp.measurements.label(image)#,structure=s)
  objects = sp.measurements.find_objects(labels)
  return objects

def draw_bounding_boxes(img,connected_components,max_size=0,min_size=0,color=(255,0,0),line_size=2):
  for component in connected_components:
    if min_size > 0 and area_bb(component)**0.5<min_size: continue
    if max_size > 0 and area_bb(component)**0.5>max_size: continue
    (ys,xs)=component[:2]
    cv2.rectangle(img,(xs.start,ys.start),(xs.stop,ys.stop),color,line_size)

def save_output(infile, outfile, connected_components):
  img = sp.imread(infile)
  draw_bounding_boxes(img, connected_components)
  misc.imsave(outfile, img) 

def  find_by_ar_from_files(infile, ar, error):
  img = cv2.imread(infile, cv2.CV_LOAD_IMAGE_GRAYSCALE)
  return find_by_ar(img, ar, error)


def main():
  parser = argparse.ArgumentParser(description='Segment raw Manga scan image.')
  parser.add_argument('infile', help='Input primary image in which we will examine.')
  #parser.add_argument('-o','--output', dest='outfile', help='Output image.')
  parser.add_argument('-v','--verbose', help='Verbose operation. Print status messages during processing', action="store_true")
  #parser.add_argument('--display', help='Display output using OPENCV api and block program exit.', action="store_true")
  parser.add_argument('-d','--debug', help='Overlay input image into output.', action="store_true")
  parser.add_argument('--aspect', help='Aspect ratio of components of interest. Width divided by height.',type=float, default=0.5)
  parser.add_argument('--error', help='Error threshold for passable aspect ratio.', type=float, default = 0.1)
  #parser.add_argument('--binary_threshold', help='Binarization threshold value from 0 to 255.',type=float,default=defaults.BINARY_THRESHOLD)
  #parser.add_argument('--additional_filtering', help='Attempt to filter false text positives by histogram processing.', action="store_true")
  args = parser.parse_args()
  infile = args.infile
  outfile = infile + '.locations.png'

  if not os.path.isfile(infile):
    print 'Please provide a regular existing input files. Use -h option for help.'
    sys.exit(-1)

  if args.verbose:
    print 'Processing primary input file ' + infile + '.'
    print 'Generating output ' + outfile

  image_locations = find_by_ar_from_files(infile, args.aspect, args.error)
  if image_locations:
    if args.verbose:
      print str(len(image_locations)) + ' components of appropriate aspect ratio found.'
    save_output(infile, outfile, image_locations)
  elif args.verbose:
    print 'No components of appropriate aspect ratio found in image.'

if __name__ == '__main__':
  main()
