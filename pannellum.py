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


class PannellumGenerator(Generator):
    """Generate XMLs on the output dir, for articles containing pano_ids"""
    
    def __init__(self, *args, **kwargs):
        """doc"""
        super(PannellumGenerator, self).__init__(*args, **kwargs)
        self.tile_folder = self.settings['TILE_FOLDER']
        self.json_folder = self.settings['JSON_FOLDER']
        self.fullsize_panoramas  = os.path.join(CONTENT_FOLDER, self.settings['FULLSIZE_PANORAMAS'])
        if not os.path.isdir(self.fullsize_panoramas):
            logger.warn("%s does not exist" % self.fullsize_panoramas)
        self.debug = self.settings['PANNELLUM_DEBUG']


    def _create_json(self, obj, json_path, tile_path, base_path):
        
        if hasattr(obj,'pano_ids'):
            output_json = os.path.join(json_path, obj.slug + ".js")
            logger.info(output_json)            
            pano_ids = [pano_id.strip() for pano_id in obj.pano_ids.split(',')]
            panoramas = []
            for pano_id in pano_ids:
                panorama = os.path.join(self.fullsize_panoramas, pano_id + '.jpg')
                if os.path.isfile(panorama):
                    panoramas.append(panorama)
                else:
                    logger.error("%s does not exist" % panorama)
            
            if len(panoramas) > 0:
                tour = Tour(author="Peter Reimer", debug=self.debug, tile_folder=tile_path, basePath=base_path, panoramas=panoramas)
                for scene in tour.scenes:
                    scene.tile(force=False)

                # writing viewer configuration file
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
        base_path = '../' + self.tile_folder
        self._get_or_create_path(json_path)
        self._get_or_create_path(tile_path)
        logger.warn(tile_path)

        for article in self.context['articles']:
            self._create_json(article, json_path, tile_path, base_path)

def get_generators(generators):
    return PannellumGenerator


def register():
    signals.get_generators.connect(get_generators)
