# -*- coding: utf-8 -*-
'''
Pannellum Generator
'''

from __future__ import unicode_literals, print_function

import json
import subprocess
import os
import logging
import math
import PIL.Image
from distutils.spawn import find_executable

from pelican import signals
from pelican.generators import Generator

from fourpi.pannellum.tour import Tour
from fourpi.pannellum.exif import Exif
from fourpi.pannellum.utils import _get_or_create_path
from gettext import lngettext

logger = logging.getLogger(__name__)

CONTENT_FOLDER = 'content'

# setting up some defaults
TILE_FOLDER = 'tiles'
SIZES_FOLDER = 'sizes'

class PannellumGenerator(Generator):
    """Generate XMLs on the output dir, for articles containing pano_ids"""
    
    def __init__(self, *args, **kwargs):
        """doc"""
        super(PannellumGenerator, self).__init__(*args, **kwargs)
        
        if 'TILE_FOLDER' not in self.settings: 
            self.tile_folder = TILE_FOLDER
        else:
            self.tile_folder = self.settings['TILE_FOLDER']
        
        if 'SIZES_FOLDER' not in self.settings: 
            self.sizes_folder = SIZES_FOLDER
        else:
            self.sizes_folder = self.settings['SIZES_FOLDER']

        self.json_folder = self.settings['JSON_FOLDER']
        self.sizes  = {
            'banner' : (1024, 256),
            'preview' : (600, 200),
            'icon': (150, 50)
            }
        self.fullsize_panoramas  = os.path.join(CONTENT_FOLDER, self.settings['FULLSIZE_PANORAMAS'])
        if not os.path.isdir(self.fullsize_panoramas):
            logger.warn("%s does not exist" % self.fullsize_panoramas)
        self.debug = self.settings['PANNELLUM_DEBUG']
        self.panoramas = [os.path.join(self.fullsize_panoramas, pano) for pano in os.listdir(self.fullsize_panoramas) if os.path.isfile(os.path.join(self.fullsize_panoramas, pano)) ]
        e = Exif(self.panoramas)
        self.exifdata = e.get_exifdata()

    def js_helper(self):
        file_path = os.path.join(self.output_path, "helper.js")
        #output_js = os.path.join(tile_path, obj.scene, "tour.json")
        f = open(file_path, 'w')
        f.write("var site_url='%s';" % self.settings['SITEURL'])
        f.close
        
    def _create_tiles(self, obj, json_path, tile_path, base_path):
        
        panorama = os.path.join(self.fullsize_panoramas, obj.scene + '.jpg')
        panoramas = [os.path.join(self.fullsize_panoramas, pano + '.jpg') for pano in obj.scenes ]
        exifdata = {scene_id: self.exifdata[scene_id] for scene_id in obj.scenes } 
        
        if not os.path.isfile(panorama):
            logger.error("%s does not exist" % panorama)
        else:    
            tour = Tour(debug=self.debug, tile_folder=tile_path, firstScene=obj.scene, basePath=base_path, exifdata=exifdata, panoramas=panoramas)
            for scene in tour.scenes:
                scene.tile(force=False)
                sizes_path = os.path.join(CONTENT_FOLDER, self.sizes_folder, obj.scene)
                self._get_or_create_path(sizes_path)
            for name, size in self.sizes.iteritems():
                self._get_scales(obj.scene, panorama, name, size[0], size[1], sizes_folder=sizes_path)
            # writing viewer configuration file
            
            output_json = os.path.join(tile_path, obj.scene, "tour.json")
            f = open(output_json, 'w')
            f.write(tour.get_json())
            f.close
            logger.warn('[ok] writing %s' % output_json)

    def _map_locations(self, obj):
        
        output_json = os.path.join(self.output_path, obj.url, "loc.json")
        locations = {}
        for scene in obj.scenes:
            exif = self.exifdata[scene]
            lng = exif['lng']
            lat = exif['lat']
            locations[scene] = {
                'lat':lat,
                'lng':lng,
                'url':obj.url,
                'title':obj.title}
        f = open(output_json, 'w')
        f.write(json.dumps(locations, indent=4, separators=(',', ': ')))
        f.close


    def _get_scales(self, scene, panorama, name, width, height, sizes_folder=None, force=False):
        if sizes_folder:
            sizes_folder = _get_or_create_path(os.path.join(sizes_folder))
        else:
            sizes_folder = _get_or_create_path(os.path.join(self.tile_folder, 'sizes'))

        file_name = '%s-%s.jpg' % (scene, name)
        file_path = os.path.join(sizes_folder, file_name)

        if not os.path.isfile(file_path) or force:
            pano = PIL.Image.open(panorama)
            pano_width, pano_height = pano.size
            left = 0
            scale = pano_width / width
            upper = int(0.5 * (pano_height - height * scale))
            right = pano_width
            lower = upper + height * scale

            cropped = pano.crop([left, upper, right, lower])
            cropped = cropped.resize([width, height], PIL.Image.ANTIALIAS)
            cropped.save(file_path, quality = 80)
        else:
            logger.info('skipping creation of %s' % file_path)

        

    def _get_or_create_path(self, path):
        """create a directory if it does not exist."""

        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except OSError:
                logger.error("Couldn't create the directory" + path)
        return path



    def generate_context(self):
        
        tours = {}
        scenes = []
        for article in self.context['articles']:
            if hasattr(article,'scene'):
                scenes.append(article)
                article.scenes = [article.scene]
                if hasattr(article,'tour'):
                    tour = article.tour
                    if not tour in tours:
                        tours[tour] = []
                    tours[tour].append(article.scene)
        
        for article in scenes:
            if hasattr(article,'tour'):
                article.scenes = tours[article.tour]
                
        self.tours = tours 
                
    
    def generate_output(self, writer=None):
        # we don't use the writer passed as argument here
        # since we write our own files
        json_path = os.path.join(self.output_path, self.json_folder)
        tile_path = os.path.join(CONTENT_FOLDER, self.tile_folder)
        base_path = '../'
        self._get_or_create_path(json_path)
        self._get_or_create_path(tile_path)
        
        self.js_helper()
        for article in self.context['articles']:
            if hasattr(article,'scene'):
                self._create_tiles(article, json_path, tile_path, base_path)
                self._map_locations(article)
                    

def get_generators(generators):
    return PannellumGenerator


def register():
    signals.get_generators.connect(get_generators)
