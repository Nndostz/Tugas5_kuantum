#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI


class LinuxRouter(Node):
    """Node yang berfungsi sebagai Linux router"""
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        # Enable IP forwarding
        self.cmd('sysctl -w net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class NetworkTopo(Topo):
    """Topologi dengan 3 router dan 3 host"""
    def build(self, **_opts):
        # Tambahkan router
        r1 = self.addNode('R1', cls=LinuxRouter, ip='10.0.0.1/24')
        r2 = self.addNode('R2', cls=LinuxRouter, ip='10.0.1.2/24')
        r3 = self.addNode('R3', cls=LinuxRouter, ip='10.0.3.2/24')

        # Tambahkan host
        h1 = self.addHost('h1', ip='10.0.0.2/24', defaultRoute='via 10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.2.2/24', defaultRoute='via 10.0.2.1')
        h3 = self.addHost('h3', ip='10.0.4.2/24', defaultRoute='via 10.0.4.1')

        # Koneksi h1 ke R1
        self.addLink(h1, r1,
                     intfName2='eth0',
                     params2={'ip': '10.0.0.1/24'})

        # Koneksi R1 ke R2
        self.addLink(r1, r2,
                     intfName1='eth1', intfName2='eth0',
                     params1={'ip': '10.0.1.1/24'},
                     params2={'ip': '10.0.1.2/24'})

        # Koneksi R2 ke R3
        self.addLink(r2, r3,
                     intfName1='eth2', intfName2='eth0',
                     params1={'ip': '10.0.3.1/24'},
                     params2={'ip': '10.0.3.2/24'})

        # Koneksi h2 ke R2
        self.addLink(h2, r2,
                     intfName2='eth1',
                     params2={'ip': '10.0.2.1/24'})

        # Koneksi h3 ke R3
        self.addLink(h3, r3,
                     intfName2='eth1',
                     params2={'ip': '10.0.4.1/24'})


def run():
    """Menjalankan topologi"""
    topo = NetworkTopo()
    net = Mininet(topo=topo, waitConnected=True)

    info('\n*** Mengatur routing static\n')

    # Routing untuk R1
    net['R1'].cmd('ip route add 10.0.2.0/24 via 10.0.1.2')
    net['R1'].cmd('ip route add 10.0.3.0/24 via 10.0.1.2')
    net['R1'].cmd('ip route add 10.0.4.0/24 via 10.0.1.2')

    # Routing untuk R2
    net['R2'].cmd('ip route add 10.0.0.0/24 via 10.0.1.1')
    net['R2'].cmd('ip route add 10.0.4.0/24 via 10.0.3.2')

    # Routing untuk R3
    net['R3'].cmd('ip route add 10.0.0.0/24 via 10.0.3.1')
    net['R3'].cmd('ip route add 10.0.1.0/24 via 10.0.3.1')
    net['R3'].cmd('ip route add 10.0.2.0/24 via 10.0.3.1')

    net.start()

    info('\n*** Uji konektivitas otomatis\n')
    info(net['h1'].cmd('ping -c 2 10.0.2.2'))
    info(net['h1'].cmd('ping -c 2 10.0.4.2'))

    info('\n*** Masuk ke CLI Mininet (untuk tes manual)\n')
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
