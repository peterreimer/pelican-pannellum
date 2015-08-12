# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import math

# Krefeld
# Art Breitengrad Längengrad
# DG  51.354577629215335  6.537648439407349
# GMS N 51° 21' 16.479''  O 6° 32' 15.534''


class LatLng:

    def __init__(self, latlng):
        self.latlng = latlng
        self.lat, self.lng = latlng

    def _dec_to_sexa(self, pos, precision):
        """convert decimal to sexagesimal coordinates"""

        degree = abs(pos)
        minutes = 60 * (degree % 1)
        seconds = 60 * (minutes % 1)
        
        return "%d°%d'%.*f''" % (degree, minutes, precision, seconds)

    def sexagesimal(self, precision=0):
        if self.lat < 0:
            latRef = "S"
        elif self.lat > 0:
            latRef = "N"
        else:
            latRef = ""
        
        if self.lng < 0:
            lngRef = "W"
        elif self.lng > 0:
            lngRef = "O"
        else:
            lngRef = ""

        return "%s %s %s %s" % (self._dec_to_sexa(self.lat,precision), latRef, self._dec_to_sexa(self.lng, precision), lngRef)

latlng = (51.354577629215335, 6.537648439407349)
l = LatLng(latlng)
print(l.sexagesimal(precision=2))
