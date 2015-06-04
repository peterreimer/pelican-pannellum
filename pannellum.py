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
from distutils.spawn import find_executable

from pelican import signals
from pelican.generators import Generator

from fourpi.pannellum.tour import Tour
from fourpi.pannellum.utils import _get_or_create_path

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


    def _create_json(self, obj, json_path, tile_path, base_path):
        if hasattr(obj,'scene_id'):
            panoramas = []
            panorama = os.path.join(self.fullsize_panoramas, obj.scene_id + '.jpg')
            if os.path.isfile(panorama):
                panoramas.append(panorama)
            else:
                logger.error("%s does not exist" % panorama)
            
            if len(panoramas) > 0:
                tour = Tour(author="Peter Reimer", debug=self.debug, tile_folder=tile_path, basePath=base_path, panoramas=panoramas)
                for scene in tour.scenes:
                    scene.tile(force=False)
                    sizes_path = os.path.join(CONTENT_FOLDER, self.sizes_folder, obj.scene_id)
                    self._get_or_create_path(sizes_path)
                    for name, size in self.sizes.iteritems():
                        scene.sizes(name, size[0], size[1], sizes_folder=sizes_path)
                # writing viewer configuration file
                
                output_json = os.path.join(tile_path, obj.scene_id, "tour.js")
                f = open(output_json, 'w')
                f.write(tour.get_json())
                f.close
                logger.warn('[ok] writing %s' % output_json)
    
    def _get_or_create_path(self, path):
        """create a directory if it does not exist."""

        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except OSError:
                logger.error("Couldn't create the directory" + path)
        return path


    def generate_output(self, writer=None):
        # we don't use the writer passed as argument here
        # since we write our own files
        json_path = os.path.join(self.output_path, self.json_folder)
        tile_path = os.path.join(CONTENT_FOLDER, self.tile_folder)
        base_path = ''
        self._get_or_create_path(json_path)
        self._get_or_create_path(tile_path)

        for article in self.context['articles']:
            self._create_json(article, json_path, tile_path, base_path)

def get_generators(generators):
    return PannellumGenerator


def register():
    signals.get_generators.connect(get_generators)
