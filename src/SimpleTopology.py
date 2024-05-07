from mininet.topo import Topo
from mininet.link import TCLink


class OurTopo(Topo):
    def __init__(self, loss_percentage):
        Topo.__init__(self)

        # Add hosts and switches
        leftHost = self.addHost("h1")
        rightHost = self.addHost("h2")
        upHost = self.addHost("h3")
        downHost = self.addHost("h4")
        uniqueSwitch = self.addSwitch("s1")

        # Add links
        self.addLink(
            leftHost,
            uniqueSwitch,
            8080,
            8081,
            cls=TCLink,
            loss=loss_percentage,
        )
        self.addLink(
            rightHost,
            uniqueSwitch,
            8082,
            8083,
            cls=TCLink,
            loss=loss_percentage,
        )
        self.addLink(
            upHost, uniqueSwitch, 8084, 8085, cls=TCLink, loss=loss_percentage
        )
        self.addLink(
            downHost,
            uniqueSwitch,
            8086,
            8087,
            cls=TCLink,
            loss=loss_percentage,
        )


loss_percentage = int(input("Enter loss percentage: "))

topos = {"ourtopo": (lambda: OurTopo(loss_percentage))}
