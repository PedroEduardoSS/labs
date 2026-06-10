# Evidence Acquisition & Handling

## First Responder Operations

1. Secure the Scene

- Isolate the hardware: Ensure no unauthorized personnel can walk up to the server rack or the suspect's laptop.
- Document physical connections: Take photographs of the computer, showing exactly what cables are plugged into what ports before you touch anything. If someone later claims a rogue USB was plugged in, you have photographic proof it wasn't.

2. Triage the System State

- Is it powered off? Do NOT turn it on. Booting a computer modifies thousands of files, altering timestamps and potentially triggering malware designed to destroy data upon boot.
- Is it powered on? Do NOT turn it off normally. Do NOT "pull the plug" right away. Leave it as is while you decide on your acquisition strategy (RAM first, then disk).
- Is there a screen saver or lock screen? Photograph what is visible. Do not attempt to guess the password, as modern systems (like BitLocker or Apple's secure enclave) will permanently wipe the encryption keys after too many failed attempts.

3. Network Isolation

- The modern way: Use the switch, router, or EDR tool to logically isolate the machine. This allows you, the forensic analyst, to still remotely query the machine and pull RAM over the network, while preventing the machine from reaching the internet or the rest of the corporate network.
- Warning: If dealing with a mobile device, immediately put it in airplane mode or place it in a Faraday bag to prevent a remote wipe command from being received.

4. The "Live Response" Toolkit

If you must interact with the live machine (e.g., to capture RAM), you cannot use the tools already installed on the machine (like the built-in Task Manager or ps command). Why? Because a rootkit might have replaced the built-in ps command to hide its own processes.

Instead, first responders bring a "Live Response Toolkit" on a clean, trusted USB drive containing statically compiled, trusted forensic binaries.


## Disk Acquisition & Write Blockers

Disk acquisition is the process of creating an exact, bit-for-bit replica of a storage medium (Hard Drive, SSD, USB, SD Card). We never analyze the original evidence directly; we analyze the replica to preserve the original.

### Logical vs. Physical Acquisition

1. Logical Acquisition

A logical acquisition relies on the Operating System to read the files and copy them. It copies only the files the OS can see.

- Pros: Fast. Good for targeted collections (e.g., "Just copy the user's Documents folder").
- Cons: It misses deleted files, hidden partitions, and slack space.

2. Physical (Bit-Stream) Acquisition

A physical image reads the raw 1s and 0s directly from the physical disk hardware, ignoring the OS entirely.

- Pros: Captures absolutely everything, including deleted files, unallocated space, and hidden partitions. This is the gold standard for full investigations.
- Cons: Very slow. A 2TB drive requires a 2TB image file, even if the drive is 90% empty.

### Write Blockers

If you plug a suspect's Windows hard drive into your forensic laptop just to "take a look", your Windows OS will aggressively mount the drive. In the background, it will update recycle bin files, change access timestamps, and create thumbnail caches. The evidence is now legally compromised.

To prevent this, we use Write Blockers. A write blocker is a device that intercepts all commands headed to the suspect drive. It allows READ commands to pass through but drops and blocks any WRITE commands.

- Hardware Write Blockers: Physical devices (like Tableau or WiebeTech) that you physically plug the suspect drive into. They are considered the most reliable method.
- Software Write Blockers: Software utilities or registry keys (like Linux mounting a drive as read-only). Less foolproof than hardware, but necessary for laptops where the SSD is soldered to the motherboard and cannot be physically removed.

### Forensic Image Formats

- Raw (DD): The simplest format. Just a massive file containing the exact 1s and 0s of the disk. No compression, no built-in metadata.
- EnCase (E01): The industry standard. Combines the raw bitstream with compression, built-in hashing, and metadata (investigator name, case number) all wrapped into a single secure file.
- AFF4: Advanced Forensic Format version 4. A newer, open-source format designed for high speed and massive datasets.


## Memory (RAM) Acquisition

### Why RAM is the Holy Grail

A full memory dump contains a snapshot of the exact state of the system at that moment in time. It holds:

- Running Processes: Not just what the OS thinks is running, but what is actually executing in memory, including hidden rootkits.
- Active Network Connections: You can see which processes are actively talking to external IP addresses (Command & Control beacons).
- Decrypted Data: Even if the hard drive is encrypted with BitLocker, the system must hold the decryption key in RAM to function. Ram dumps routinely yield cleartext passwords, decryption keys, and private SSL keys.
- Clipboard Contents: What the user just copied and pasted.
- Command History: History of terminal commands recently run.

### Acquisition Tools

Because RAM is actively being used by the operating system, you cannot use a simple copy command to grab it. You need a specialized kernel driver to access the raw memory space.

Common free tools include:

- DumpIt (Windows): A fast, simple executable. You run it from a USB drive, and it drops a .raw memory file onto your USB.
- WinPmem (Windows/Linux/Mac): Part of the Rekall project. Powerful, scriptable, and supports the generic .raw format as well as the more advanced AFF4 format.
- LiME (Linux): Linux Memory Extractor. A Loadable Kernel Module (LKM) that creates a full memory capture of Linux devices.

### Hibernation Files and Pagefiles

Even if a machine is powered off, you might still recover RAM data:

- hiberfil.sys (Hibernation File): When a Windows laptop is put to sleep/hibernation, the OS dumps the entire contents of RAM into this file on the hard drive to save power. Extracting this file provides a perfect, frozen memory dump from the exact moment the laptop went to sleep.
- pagefile.sys / swapfile.sys: When RAM gets full, the OS temporarily moves idle data from RAM onto the hard drive to free up space. Analyzing these files can reveal historical artifacts that were once in memory.

## Network Evidence Acquisition

### Full Packet Capture (PCAP)

The ultimate form of network evidence is a Full Packet Capture. This records every single bit of data traversing the wire—the headers, the routing information, and the actual payload (the contents of the emails, the files being downloaded, the web pages viewed).

- Tools: Wireshark, tcpdump.
- The Problem: Storing full PCAPs is incredibly expensive. A busy corporate firewall might process 10 Terabytes of data per day. Retaining full PCAPs for 30 days requires massive, specialized storage clusters (like Arkime/Moloch). Because of this, most organizations do not save full PCAPs.

### NetFlow (Network Telemetry)

NetFlow is metadata about network traffic. It records:

- Source IP & Destination IP
- Source Port & Destination Port
- Protocol (TCP/UDP)
- Total Bytes Transferred
- Start time & End time

NetFlow does not record the payload. It cannot tell you what was inside the HTTP request, only that an HTTP request occurred and transferred 40MB of data.

- Pros: Requires 99% less storage than full PCAPs. You can store months of NetFlow data easily.
- Usage in DFIR: If an analyst sees a NetFlow record indicating 50 Gigabytes of data was sent from the internal Database Server to an unknown IP in Russia at 3:00 AM, they don't need the PCAP to know data exfiltration just occurred.

### Log files

When PCAP and NetFlow are unavailable, analysts rely heavily on network appliance logs:

- Firewall Logs: Shows allowed and blocked connections.
- Proxy Logs / Web Gateways: Shows the exact URLs internal users visited, the user-agent strings, and HTTP status codes. This is critical for catching users clicking phishing links.
- DNS Logs: Attackers frequently use DNS to locate internal assets or even to exfiltrate data (DNS Tunneling). Analyzing DNS queries is a staple of network forensics.

### Collecting Evidence on the Wire

How do we actually capture the traffic without interrupting the network?

- Port Mirroring (SPAN Port): You configure the corporate network switch to take a copy of every packet passing through it and send that copy to a dedicated monitor port, where your forensic capture tool is plugged in.
- Network Taps: A physical hardware device inserted directly inline with the network cable. It acts like a splitter, passively duplicating the optical or electrical signal to a capture device. Taps are completely invisible to the network and are more reliable than SPAN ports under heavy load.
