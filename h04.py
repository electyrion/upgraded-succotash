from mininet.topo import Topo
from mininet.node import Node

class LinuxRouter(Node):
    # "A Node with IP forwarding enabled."
    def config(self, **params):
        super (LinuxRouter, self).config(**params)
        # Enable forwarding on the router
        self. cmd ('sysctl net.ipv4. ip_forward-1')

    def terminate( self ):
        self.cmd ('sysctl net.ipv4.ip_forward=0')
        super (LinuxRouter, self).terminate()

class MyTopo (Topo) :
    def build (self):
        #number of router = 1
        num_switch = 4
        number_host_per_switch = [61, 29, 13, 5]

        DG_KOAS = '192.168.138.1/26'
        DG_INTERSHIP = '192.168.138.65/27' 
        DG_SPESIALIS = '192.168.138.97/28'
        DG_RESIDEN = '192.168.138.113/29'
        DG_ROUTER_ASRAMA = '192.168.138.121/30'
        DG_ROUTER_RS = '192.168.138.122/30'
        
        # initiate router
        router_asrama = self.addNode("Router Asrama", cls=LinuxRouter, ip=DG_KOAS, defaultRoute=f'via {DG_ROUTER_RS[:-3]}')
        router_rs = self.addNode("Router Rumah Sakit", cls=LinuxRouter, ip=DG_SPESIALIS, defaultRoute=f"via {DG_ROUTER_ASRAMA[:-3]}")

        #add 2 switch
        s1 = self.addswitch('S1')
        s2 = self.addswitch('S2')
        s3 = self.addswitch('S3')
        s4 = self.addswitch('S4')

        #add link for each switch
        self.addLink(s1,router_asrama, intfName2='r1-eth1', params2={'ip': DG_KOAS})
        self.addLink(s2,router_asrama, intfName2='r1-eth2', params2={'ip': DG_INTERSHIP})
        self.addLink(s3,router_rs, intfName2='r2-eth1', params2={'ip': DG_SPESIALIS})
        self.addLink(s4,router_rs, intfName2='r2-eth2', params2={'ip': DG_RESIDEN})

        # connect router asrama to router rumah sakit
        self.addLink(router_asrama,
                     router_rs,
                     intfName1='r1-eth0',
                     intfName2='r2-eth0',
                     params1={'ip': DG_ROUTER_ASRAMA},
                     params2={'ip': DG_ROUTER_RS})


        #add host (subnet koas)
        for i in range(61):
            host_name = 'K' + str(i+1)
            ip_addr = '192.168.250.' + str(i+2) + '/26'
            self.addHost(host_name, ip=ip_addr, defaultRoute='via ' + DG_KOAS[:-3])
            self.addLink(host_name, s1)

        #add host (subnet internship)
        for i in range(29):
            host_name = 'I' + str(i+1)
            ip_addr = '192.168.250.' + str(i+66) + '/27'
            self.addHost(host_name, ip=ip_addr, defaultRoute='via ' + DG_INTERSHIP[:-3])
            self.addLink(host_name, s2)

        #add host (subnet spesialis)
        for i in range(13):
            host_name = 'S' + str(i+1)
            ip_addr = '192.168.250.' + str(i+98) + '/28'
            self.addHost(host_name, ip=ip_addr, defaultRoute='via ' + DG_SPESIALIS[:-3])
            self.addLink(host_name, s3)

        #add host (subnet residen)
        for i in range(5):
            host_name = 'R' + str(i+1)
            ip_addr = '192.168.250.' + str(i+114) + '/29'   
            self.addHost(host_name, ip=ip_addr, defaultRoute='via ' + DG_RESIDEN[:-3])
            self.addLink(host_name, s4)

topos = {'mytopo': (lambda: MyTopo())}