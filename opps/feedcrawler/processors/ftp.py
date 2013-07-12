#coding: utf-8

from .base import BaseProcessor


class EFEXMLProcessor(BaseProcessor):
    def process(self):
        print self.__dict__
