import random
from Target import Target
from Host import Host
from Subnet import Subnet
from Honeypot import Honeypot
from Honeyrouter import Honeyrouter
from Route import Route
from NetworkPrinter import NetworkPrinter
import math

class GenerateVirtualView(object):

    def __init__(self,maxSubn,maxHosts):
        self.viewtext=""
        self.shortnamesHost=1
        self.shortnamesHP=1
        self.shortnamesHR=1
        self.subnetList={}
        self.honeyrouterList=[]
        self.routeList=[]
        self.target=None
        self.maxSubnet=maxSubn
        self.maxHost=maxHosts
        self.targetsubnet=-1
        self.lowerSubnet=-1
        self.upperSubnet=-1
        self.up=False



    def generatgeView(self,rHosts,subnetSpace,targetPort,NCDSPort,HoneyPort,numSubnets,minHP,maxHP,Strategy):

        self.targetsubnet = numSubnets
        self.lowerSubnet = numSubnets/2
        self.upperSubnet = 0
        #generate specified number of subnets
        for s in range(1,numSubnets):
            self.getAvaiSubnet(numSubnets)

        hosts=[]
        #assign hosts to subnets, and deceive their data
        for k in rHosts.keys():
            if k!=NCDSPort and k!=HoneyPort:
                #create new host object
                realip=rHosts[k].split("/")[0]
                realmac=rHosts[k].split("/")[1]
                if k==targetPort:
                    self.target=Host(self.getShortnameHost(),realip,realmac,k)
                    #get subnet address for target
                    self.target=self.setAvailableSubnetAddress(subnetSpace,numSubnets,self.target,targetPort)
                    #print(str(self.target.deceptiveIP))
                else:
                    host=Host(self.getShortnameHost(),realip,realmac,k)
                    #get subnet address for host
                    host=self.setAvailableSubnetAddress(subnetSpace,numSubnets,host,targetPort)
                    #print(str(host.deceptiveIP))

        #assign honeypots to subnets
        realHoneyIP=rHosts[HoneyPort].split("/")[0]
        realHoneyMac=rHosts[HoneyPort].split("/")[1]
        for subKey in self.subnetList.keys():
            numHoneypots=random.randint(minHP,maxHP)
            for hp in range(1,numHoneypots):
                subnet=self.subnetList[subKey]
                hpAddr=self.getAvaiHoneypotforSubnet(subnet)
                honeyAddr=str(subnetSpace[:-2]) + "." + str(subnet.number) + "." + str(hpAddr)
                honeypot=Honeypot(self.getShortnameHoneypot(),realHoneyIP,realHoneyMac,honeyAddr,self.randMac(),HoneyPort)
                self.subnetList[subnet.number].honeypots.append(honeypot)
                #print("Honeypot " + honeyAddr)

        #create honeyrouters
        routerMac=self.randMac()
        targetSubnet = int(self.target.deceptiveIP.split(".")[2])

        subnet=self.subnetList[targetSubnet]
        subnetAddr=str(subnetSpace[:-2]) + "." + str(subnet.number) + ".1"
        hr=Honeyrouter(self.getShortnameHoneyrouter(),subnetAddr,routerMac,NCDSPort)
        subnet.honeyrouter.append(hr)
        gateway=hr.shortName
        self.subnetList[subnet.number]=subnet
        self.honeyrouterList.append(hr)

        for subKey in self.subnetList.keys():
            subnet=self.subnetList[subKey]
            if subnet.number != targetSubnet:
                subnetAddr=str(subnetSpace[:-2]) + "." + str(subnet.number) + ".1"
                hr=Honeyrouter(self.getShortnameHoneyrouter(),subnetAddr,routerMac,NCDSPort)
                subnet.honeyrouter.append(hr)
                self.subnetList[subKey]=subnet
                self.honeyrouterList.append(hr)



        #generate routes
        numhops=1
        for subKey in self.subnetList.keys():
            subnet=self.subnetList[subKey]
            targetSubnet = int(self.target.deceptiveIP.split(".")[2])

            if subnet.number != targetSubnet:
                numhops+=1
                #numhops=random.randint(2,networkDiameter)
                hostIdx=0
                for host in subnet.hosts:
                    r=Route(self.target,host)
                    hostSubnet = int(host.deceptiveIP.split(".")[2])
                    #hops = int(math.fabs(hostSubnet-targetSubnet))

                    #max sub dist min hop dist
                    if Strategy=="minhop_maxsub":
                        hops = numSubnets - hostSubnet

                    if Strategy=="maxhop_maxsub":
                    #max sub dist max hop dist
                        hops = hostSubnet

                    for hop in range(0,hops):
                        r.addHop(self.honeyrouterList[hop])
                    self.routeList.append(r)
                    host.distance=hops
                    #subnet.hosts.insert(hostIdx,host)
                    #hostIdx+=1
                for honeypot in subnet.honeypots:
                    r=Route(self.target,honeypot)
                    for hop in range(0,numhops-1):
                        r.addHop(self.honeyrouterList[hop])
                    self.routeList.append(r)
            else:
                for host in subnet.hosts:
                    r=Route(self.target,host)
                    self.routeList.append(r)
                for honeypot in subnet.honeypots:
                    r=Route(self.target,honeypot)
                    self.routeList.append(r)

        #set gateway


        printer = NetworkPrinter()
        realhosts = printer.printView(self.target,self.subnetList,self.routeList,targetPort,gateway)
        #for printhost in realhosts:
            #print("realhosts.append(\"" + printhost + "\")")
        return (realhosts, self.targetsubnet)



    def randMac(self):
        s1=hex(random.randint(0,255))[2:].zfill(2)
        s2=hex(random.randint(0,255))[2:].zfill(2)
        s3=hex(random.randint(0,255))[2:].zfill(2)
        s4=hex(random.randint(0,255))[2:].zfill(2)
        s5=hex(random.randint(0,255))[2:].zfill(2)
        s6=hex(random.randint(0,255))[2:].zfill(2)
        mac = str(s1) + ":" + str(s2) + ":" + str(s3) + ":" + str(s4) + ":" + str(s5) + ":" + str(s6)
        return mac

    def getShortnameHost(self):
        sn="h"+str(self.shortnamesHost)
        self.shortnamesHost+=1
        return sn

    def getShortnameHoneypot(self):
        sn="hp"+str(self.shortnamesHP)
        self.shortnamesHP+=1
        return sn

    def getShortnameHoneyrouter(self):
        sn="hr"+str(self.shortnamesHR)
        self.shortnamesHR+=1
        return sn

    def setAvailableSubnetAddress(self,subnetSpace,numSubnets,host,targetport):
        if host.portNum != targetport: #normal host
            subnet=self.getAvaiSubnet(numSubnets)
            #subnet=self.subnetList[1] #use same subnet for all hosts
            hostNum = self.getAvaiHostforSubnet(subnet)
            addr=subnetSpace[:-1] + str(subnet.number) + "." + str(hostNum)
            host.setDecIPAddr(addr)
            self.subnetList[subnet.number].hosts.append(host)
        elif host.portNum == 5: #honeypot
            subnet=self.getAvaiSubnet(numSubnets)
            hostNum = self.getAvaiHostforSubnet(subnet)
            addr=subnetSpace[:-1] + str(subnet.number) + "." + str(hostNum)
            host.setDecIPAddr(addr)
            self.subnetList[subnet.number].hosts.append(host)
        else:
            subnet=Subnet(self.targetsubnet)
            self.subnetList[self.targetsubnet]=subnet
            hostNum = self.getAvaiHostforSubnet(subnet)
            addr=subnetSpace[:-1] + str(subnet.number) + "." + str(hostNum)
            host.setDecIPAddr(addr)
        return host

    #generate subnets with linear distance to target
    def getAvaiSubnet(self,numSubnets):
        ns = len(self.subnetList.keys())
        if ns<numSubnets:
            self.upperSubnet+=1
            subnet=self.upperSubnet
            self.up=False
            sub=Subnet(subnet)
            self.subnetList[subnet]=sub
        else:
            subnetId=-1
            minHosts=99
            for k in self.subnetList.keys():
                subnetHosts=self.subnetList[k].hosts
                if len(subnetHosts)<minHosts:
                    minHosts=len(subnetHosts)
                    subnetId=k
            sub=self.subnetList[subnetId]
        return sub



    def getAvaiHostforSubnet(self,subnet):
        host=random.randint(2,self.maxHost)
        while(True):
            if host in subnet.hostNums:
                host=random.randint(2,self.maxHost)
            else:
                break
        #subnet.hosts.append(host)
        subnet.hostNums.append(host)
        self.subnetList[subnet.number]=subnet
        return host

    def getAvaiHoneypotforSubnet(self,subnet):
        honeypot=random.randint(2,self.maxHost)
        while(True):
            if honeypot in subnet.hostNums:
                honeypot=random.randint(2,self.maxHost)
            else:
                break
        #subnet.honeypots.append(honeypot)
        subnet.hostNums.append(honeypot)
        self.subnetList[subnet.number]=subnet
        return honeypot