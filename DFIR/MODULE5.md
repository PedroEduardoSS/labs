# Network Forensics (PCAP Analysis)

## Introduction to Packet Captures

Network Forensics is the capture, recording, and analysis of network events in order to discover the source of security attacks. The foundational artifact of network forensics is the Packet Capture (PCAP) file.

### Why Network Forensics?

Malware can hide on a hard drive using rootkits. Attackers can delete Event Logs. But it is incredibly difficult for an attacker to hide their network traffic from a properly configured network sensor.

- "Packets don't lie." If data left the building, there is a record of it.

### The PCAP Format

A `.pcap` (or the newer `.pcapng`) file contains a complete, byte-for-byte copy of every network packet that passed a specific point on the network during the capture window.

This is fundamentally different from NetFlow logs.

- NetFlow: Like a phone bill. It tells you who talked to whom, when, and for how long (e.g., IP A talked to IP B on port 443 for 5 minutes). It does not contain the conversation.
- PCAP: Like a recorded phone call. It contains the metadata and the actual data payloads (the contents of the downloaded file, the HTTP GET arrays, the DNS queries).

### Capturing Traffic

To capture traffic, sensors (often running software like tcpdump or Zeek) are placed at strategic chokepoints in the network:

- Ingress/Egress points: The main firewall connecting the corporate network to the Internet.
- Core Switches: Monitoring internal Lateral Movement (e.g., User VLAN talking to the Server VLAN).
- Endpoint: Capturing traffic directly on a specific laptop using tools like Wireshark.
- Promiscuous Mode: Normally, a network card only reads packets addressed specifically to its own MAC address. To capture all traffic on a network segment, the network interface card (NIC) must be put into "Promiscuous Mode," telling it to read everything it sees.

## Wireshark Fundamentals

Wireshark is the world's foremost network protocol analyzer. It allows you to open PCAP files and view the captured network traffic at a microscopic level.

### The Three-Pane View

When you open a PCAP in Wireshark, the interface is split into three main panels:

- Packet List (Top): Shows a chronological list of every captured packet, with basic summary info (Source IP, Destination IP, Protocol, Length).
- Packet Details (Middle): Shows the selected packet broken down layer by layer, matching the OSI model (e.g., Ethernet frame -> IPv4 header -> TCP header -> HTTP payload).
- Packet Bytes (Bottom): Shows the raw hexadecimal and ASCII representation of exactly what the raw packet looks like in binary.

### Display Filters

PCAP files can contain millions of packets. To find evil, you must master Display Filters. They allow you to hide the noise and focus only on relevant traffic.

- Filter by IP:
    - `ip.addr == 192.168.1.50` (Shows packets where this IP is either the source OR destination)
    - `ip.src == 10.0.0.5` (Shows packets originating from this IP)
- Filter by Protocol:
    - `http` (Shows only unencrypted web traffic)
    - `dns` (Shows only DNS queries and responses)
- Filter by Port:
    - `tcp.port == 443` (Shows typical HTTPS traffic)
    - `udp.port == 53` (Shows typical DNS traffic)
- Combining Filters (Boolean Logic):
    - `ip.src == 192.168.1.100 && tcp.port == 80` (Finds HTTP traffic leaving a specific host)
    - `http.request.method == "POST"` (Finds data being uploaded/sent to a web server)

### "Follow TCP Stream"

This is arguably Wireshark's most powerful feature for analysts.

A single file download might span 500 individual packets. Trying to read the file chunk by chunk in the "Packet Bytes" pane is impossible.

By right-clicking a packet and selecting Follow -> TCP Stream, Wireshark automatically reassembles all 500 packets in the correct order, strips away the networking headers, and displays the pure application data (the actual conversation) in a clean, readable text window.


## Analyzing Protocols: DNS and HTTP

### DNS (Domain Name System)

Before malware can connect to `evil.com`, it must ask DNS for the IP address of that domain.

- Port: UDP 53.
- Forensic Value: DNS occurs before the connection. Because DNS is usually unencrypted, you can see every domain a computer tries to visit.
- Key Indicator: Look for DGA (Domain Generation Algorithms). If you see a machine making DNS queries for qbxvzmpklj.com, zxywqabcn.net, etc., it is highly likely infected with malware trying to find its Command and Control server.

### HTTP (Hypertext Transfer Protocol)

HTTP is the foundation of the web, but it's also perfect for malware because it is almost never blocked by firewalls.

When analyzing HTTP, look closely at these fields:

- User-Agent: This tells the server what browser the client is using (e.g., Mozilla/5.0 (Windows NT 10.0...)).
    - Red Flag: Malware often uses default, hardcoded User-Agents missing typical browser strings, like simply curl/7.68.0, python-requests/2.25.1, or even unique strings like Go-http-client/1.1.
- URI (Uniform Resource Identifier): The actual path of the file requested (e.g., /images/logo.png).
    - Red Flag: Extremely long URIs with random characters might indicate data exfiltration encoded in the URL itself.
- HTTP Status Codes:
    - 200 OK: The server successfully received and answered the request (The malware successfully downloaded its payload).
    - 404 Not Found: The target file isn't there (The C2 server infrastructure might have been taken down).

### Extracting Files from PCAPs

If an employee downloads a suspicious executable over HTTP (unencrypted), that entire executable is stored inside the PCAP file. You can extract it.

- In Wireshark:
    - Go to File -> Export Objects -> HTTP.
    - Wireshark will present a list of every file transferred over HTTP during the capture.
    - Select the file and click "Save As" to dump the actual file to your hard drive for malware analysis.


## Tshark & Command Line Analysis

### What is Tshark?

Tshark is the command-line version of Wireshark. It uses the exact same parsing engine and the exact same display filters, but it runs entirely in the terminal.

Because it doesn't have to render a GUI, it is incredibly fast and uses vastly less RAM. It is also easily scriptable in Bash.

### Basic Syntax

- Read a PCAP: `tshark -r capture.pcap`
- Apply a Filter: `tshark -r capture.pcap -Y "http.request.method == GET"` (Notice the capital -Y for display filters).

### The Power of Fields (-T fields)

The true power of Tshark is its ability to extract only specific pieces of data from a packet, turning a messy PCAP into a clean CSV file that can be fed into Excel, Splunk, or ElasticSearch.

Use -T fields to tell Tshark you only want specific data. Use -e <field_name> to specify exactly what you want.

Example 1: Extract all DNS queries `tshark -r capture.pcap -Y "dns.flags.response == 0" -T fields -e dns.qry.name` This tells Tshark: Read the file, filter for DNS requests (not responses), and print out only the domain name that was queried.

Example 2: Create an HTTP forensic timeline `tshark -r capture.pcap -Y http.request -T fields -e frame.time -e ip.src -e http.request.uri -e http.user_agent` This creates a clean log file showing the Time, the Source IP, the requested URL, and the User-Agent for every HTTP request in the entire capture.

### Combining with Bash

Because Tshark outputs text, you can pipe it into standard Linux tools like grep, sort, and uniq. If you want to see the top 5 most frequently visited domains: `tshark -r capture.pcap -Y dns -T fields -e dns.qry.name | sort | uniq -c | sort -nr | head -n 5`