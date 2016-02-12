
from pox.core import core
import pox.openflow.nicira as nx
from pox.lib.util import str_to_bool
from pox.SDNController_ncds.FlowCreator import FlowCreator
from pox.SDNController_ncds.ViewReader import ViewReader
from pox.openflow.of_json import *
import os

log = core.getLogger()

class Controller(object):

  def __init__ (self,connection,transparent):
    log.info("Init...")
    self.connection = connection
    self.transparent = transparent
    connection.addListeners(self)

    self.flowcreator = FlowCreator()

    self.createFlowRules()

  def _handle_PacketIn (self, event):
    packet = event.parsed
    log.info("Packet from " + str(packet.src) + " to " + str(packet.dst))

  def createFlowRules(self):
    viewreader = ViewReader()
    #viewfile = str(raw_input("Enter the path to your view file (e.g. /home/mininet/nv.nv):"))
    with open("/home/mininet/config.conf") as file:
        lines = file.readlines()
    print("Loaded path from config file " + lines[0])
    viewfile = lines[0].replace("\n", "")
    nv = viewreader.readNetworkView(viewfile)
    rules = self.flowcreator.generateRules(nv)
    for r in rules:
      self.connection.send(r)
      #print(str(r))

class ncds_controller(object):
  def __init__ (self,transparent):
    core.openflow.addListeners(self)
    self.transparent = transparent

  def _handle_ConnectionUp (self, event):
    log.debug("Connection %s" % (event.connection,))
    Controller(event.connection, self.transparent)
  
def launch (transparent=False):
  core.registerNew(ncds_controller, str_to_bool(transparent))
  log.info("NCDS SDN Controller running...")
