from mininet.topo import Topo
from mininet.node import Node


class Router(Node):
    def config(self, **kwargs):
        super(Router, self).config(**kwargs)
        self.cmd("sysctl net.ipv4.ip_forward=1")

    def terminate(self):
        self.cmd("sysctl net.ipv4.ip_forward=0")
        super(Router, self).terminate()


class TwoRouterFourSubnetTopo(Topo):
    "Topology consisting 2 routers and 4 subnets. each router has 2 subnets"

    def build(self):
        switches_router_rs = 2
        switches_router_asrama = 2
        subnet_koas_host = 61
        subnet_internship_host = 29
        subnet_spesialis_host = 13
        subnet_residen_host = 5

        DG_KOAS = "192.168.GANTI.1/26"
        DG_INTERNSHIP = "192.168.GANTI.65/27"
        DG_SPESIALIS = "192.168.GANTI.97/28"
        DG_RESIDEN = "192.168.GANTI.113/29"
        DG_ROUTER_ASRAMA = "192.168.138.121/30"
        DG_ROUTER_RS = "192.168.138.122/30"

        # instatiating Routers
        router_asrama = self.addNode("Router Asrama", cls=Router, ip=DG_KOAS, defaultRoute=f'via {DG_ROUTER_RS[:-3]}')
        router_rs = self.addNode("Router Rumah Sakit", cls=Router, ip=DG_SPESIALIS, defaultRoute=f"via {DG_ROUTER_ASRAMA[:-3]}")

        # Instatiating Switches
        s_koas = self.addSwitch("s1")
        s_internship = self.addSwitch("s2")
        s_spesialis = self.addSwitch("s3")
        s_residen = self.addSwitch("s4")

        self.addLink(s_koas, router_asrama, intfName1="s1-eth1", intfName2="asrama-eth1", params2={"ip": DG_KOAS})
        self.addLink(
            s_internship, router_asrama, intfName1="s2-eth1", intfName2="asrama-eth2", params2={"ip": DG_INTERNSHIP}
        )
        self.addLink(s_spesialis, router_rs, intfName1="s3-eth1", intfName2="rs-eth1", params2={"ip": DG_SPESIALIS})
        self.addLink(s_residen, router_rs, intfName1="s4-eth1", intfName2="rs-eth2", params2={"ip": DG_RESIDEN})

        # Connecting Router Asrama to Router RS
        self.addLink(
            router_asrama,
            router_rs,
            intfName1="asrama-eth3",
            intfName2="rs-eth3",
            params1={"ip": DG_ROUTER_ASRAMA},
            params2={"ip": DG_ROUTER_RS},
        )

        span = subnet_koas_host + 3 + 1
        span += subnet_internship_host + 3 + 1
        span += subnet_spesialis_host + 3 + 1
        span += subnet_residen_host + 3 + 1

        for i in range(1, span + 1):
            if i <= 62 and i >= 2:
                host = f"K{i - 1}"

                last_byte = i
                IP = f"192.168.{GANTI + (last_byte // 256)}.{last_byte % 256 }/26"
                self.addHost(host, ip=IP, defaultRoute=f"via {DG_KOAS[:-3]}")
                self.addLink(host, s_koas)

            elif i >= 66 and i <= 94:
                host = f"I{i - 65}"

                last_byte = i
                IP = f"192.168.{GANTI + (last_byte // 256)}.{last_byte % 256 }/27"
                self.addHost(host, ip=IP, defaultRoute=f"via {DG_INTERNSHIP[:-3]}")
                self.addLink(host, s_internship)

            elif i >= 98 and i <= 110:
                host = f"S{i - 97}"

                last_byte = i
                IP = f"192.168.{GANTI + (last_byte // 256)}.{last_byte % 256 }/28"
                self.addHost(host, ip=IP, defaultRoute=f"via {DG_SPESIALIS[:-3]}")
                self.addLink(host, s_spesialis)

            elif i >= 114 and i <= 118:
                host = f"R{i - 113}"

                last_byte = i
                IP = f"192.168.{GANTI + (last_byte // 256)}.{last_byte % 256 }/29"
                self.addHost(host, ip=IP, defaultRoute=f"via {DG_RESIDEN[:-3]}")
                self.addLink(host, s_residen)
            else:
                continue


topos = {"TwoRouterFourSubnetTopo": (lambda: TwoRouterFourSubnetTopo())}
