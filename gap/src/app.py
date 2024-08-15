import sys
import os

from client import Client
from .gap import GapPlugin
from .xml import XmlPlugin
from .utils import parse_xml_to_gbpluginmethods

ID = 3


def run(data: str):
    #convert from xml to methods
    methods = parse_xml_to_gbpluginmethods(data)
    #run plugin
    plugin = GapPlugin()
    structure_interact = plugin.apply(dependency_outputs= None, methods= methods)
    #convert back to xml
    dep_outputs = dict()
    dep_outputs["OverlapPlugin"] = structure_interact
    plugin2 = XmlPlugin()
    res_in_xml = plugin2.apply(dependency_outputs= dep_outputs, methods= methods)
    return res_in_xml
   

def do_it():
    client = Client(ID, run)
    client.run_client()

if __name__ == "__main__":
    do_it()
