from mininet.topo import Topo
from mininet.node import Node

class LinuxRouter(Node):
    # "A Node with IP forwarding enabled."

    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        # Enable forwarding on the router
        self.cmd('sysctl net.ipv4.ip_forward=1')
    
    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class MyTopo(Topo):
    def build(self):
        DG_KOAS = '192.168.138.1/26'
        DG_INTERSHIP = '192.168.138.65/27'
        DG_SPESIALIS = '192.168.138.97/28'
        DG_RESIDEN = '192.168.138.113/29'
        DG_ROUTER_ASRAMA = '192.168.138.121/30'
        DG_ROUTER_RS = '192.168.138.122/30'

        #add router
        # r01 = Asrama
        # r02 = RS

        router_1 = self.addNode('r01', cls=LinuxRouter, ip=DG_ROUTER_ASRAMA)
        router_2 = self.addNode('r02', cls=LinuxRouter, ip=DG_ROUTER_RS)
        
        #add switch
        # s1 = KOAS
        # s2 = Internship
        # s3 = Spesialis
        # s4 = Residen
        
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        #add link
        self.addLink(router_1, router_2, intfName1='r01-eth0', intfName2='r02-eth0',params1={'ip': DG_ROUTER_ASRAMA},params2={'ip': DG_ROUTER_RS})

        self.addLink(s1,router_1, intfName2='r01-eth1', params2={'ip': DG_KOAS})
        self.addLink(s2,router_1, intfName2='r01-eth2', params2={'ip': DG_INTERSHIP})
        self.addLink(s3,router_2, intfName2='r02-eth1', params2={'ip': DG_SPESIALIS})
        self.addLink(s4,router_2, intfName2='r02-eth2', params2={'ip': DG_RESIDEN})

        
        #add host (subnet koas)
        for i in range(61):
            host_name = 'K' + str(i+1)
            ip_addr = '192.168.138.' + str(i+2) + '/26'
            self.addHost(host_name, ip=ip_addr, defaultRoute='via ' + DG_KOAS[:-3])
            self.addLink(host_name, s1)


        #add host (subnet internship)
        for i in range(29):
            host_name = 'I' + str(i+1)
            ip_addr = '192.168.138.' + str(i+66) + '/27'
            self.addHost(host_name, ip=ip_addr, defaultRoute='via ' + DG_INTERSHIP[:-3])
            self.addLink(host_name, s2)

        #add host (subnet spesialis)
        for i in range(13):
            host_name = 'S' + str(i+1)
            ip_addr = '192.168.138.' + str(i+98) + '/28'
            self.addHost(host_name, ip=ip_addr, defaultRoute='via ' + DG_SPESIALIS[:-3])
            self.addLink(host_name, s3)

        #add host (subnet residen)
        for i in range(5):
            host_name = 'R' + str(i+1)
            ip_addr = '192.168.138.' + str(i+114) + '/29'   
            self.addHost(host_name, ip=ip_addr, defaultRoute='via ' + DG_RESIDEN[:-3])
            self.addLink(host_name, s4)

topos = {'mytopo': (lambda: MyTopo())}





