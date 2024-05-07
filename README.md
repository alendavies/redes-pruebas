# redes-tp1
## Packet Structure
Type and Size are headers, common to all packet types with variable size.
They are first because we use them to know how many bytes to read, and how to parse the data.

METADATA PACKET (Sent & Ack once):
Type:1
Size: Size(Type) + Size(Size) + Size(ActionType) + Size(TotalFileSize) + Size(Resource)
ActionType: 1="Upload"/0="Download"
TotalFileSize: N (If ActionType = Download, ignore)
Resource: "path"


METADA ACK PACKET:
Type: 2
Size: Size(Type) + Size(Size) + Size(ActionType) + Size(TotalFileSize) + Size(Resource)
ActionType: 1="Upload"/0="Download"
TotalFileSize: N
Resource: "path"
    
DATA PACKET: 3
Type:3
Size: Size(Type) + Size(Size) + Size(Offset) + Size(Data)
Offset: 
Data: 

DATA ACK PACKET: 
Type:4
Offset: 

DATA NACK PACKET: 
Type:5
Offset: 

## How to run MiniNet
#### 1. Install MiniNet
Open a terminal and run the following commands:
```bash
git clone https://github.com/mininet/mininet
```
```bash
cd mininet
git tag  # list available versions
git checkout -b mininet-2.3.0 2.3.0 
cd ..
```
```bash
mininet/util/install.sh -a
```
After the installation has completed, test the basic Mininet functionality:
```bash
sudo mn --switch ovsbr --test pingall
```
#### 2. Install mininet Python package
```bash
pip3 install mininet
```
#### 3. Run the topology provided
Open a terminal and run the following command:
```bash
sudo mn --custom <PATH>/src/SimpleTopology.py --topo ourtopo --mac --switch ovsk --link tc
```
`<PATH>` is the path to the directory where the SimpleTopology.py file is located.
#### 4. Get the IP addresses and ports of the hosts
```bash
dump
```
We can see the following output for the hosts:
```bash
<Host hx: hx-eth<PORT>:<IP> pid=<PID>>
```
Where `hx` is the host name, `<PORT>` is the port number, `<IP>` is the IP address, and `<PID>` is the process ID.

With the IP addresses and ports, you can run the server and client scripts. 
#### 5. Open a new terminal window for each host
```bash
xterm h1 h2 h3 h4
```
This will open a new terminal window for each host.
#### 6. Run the server script
In each host's terminal, navigate to the directory where the scripts are located and run 
the appropriate script. For example, on h1 (which can be the server), you might run:
```bash
python3 start-server.py [ -h ] [ -v | -q ] -H ADDR -p PORT -s DIRPATH [ -sw | -sr ]
```
* -h, --help: show this help message and exit
* -v, --verbose: increase output verbosity
* -q, --quiet: decrease output verbosity
* -H, --host: service address
* -p, --port: service port
* -s, --storage: storage dir path
* -sw, --stwa: use stop-and-wait protocol
* -sr, --sere: use selective repeat protocol
#### 7. Run the client scripts
And on h2, h3, and h4 (which can be the clients), you might run:
```bash
python3 download.py [ -h ] [ -v | -q ] -H ADDR -p PORT -d FILEPATH -n FILENAME [ -sw | -sr ]
```
* -h, --help: show this help message and exit
* -v, --verbose: increase output verbosity
* -q, --quiet: decrease output verbosity
* -H, --host: server IP address
* -p, --port: server port
* -d, --dst: destination file path
* -n, --name: file name
* -sw, --stwa: stop and wait protocol
* -sr, --sere: selective repeat protocol

Or:
```bash
python3 upload.py [ -h ] [ -v | -q ] -H ADDR -p PORT -s FILEPATH -n FILENAME [ -sw | -sr ]
```
* -h, --help: show this help message and exit
* -v, --verbose: increase output verbosity
* -q, --quiet: decrease output verbosity
* -H, --host: server IP address
* -p, --port: server port
* -s, --src: source file path
* -n, --name: file name
* -sw, --stwa: stop and wait protocol
* -sr, --sere: selective repeat protocol

Make sure that your server script is listening on the correct IP address and port, and 
that your client scripts are sending to the correct IP address and port.