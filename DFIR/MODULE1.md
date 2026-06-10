# Introduction to DFIR

## The Incident Response Lifecycle (PICERL)

The industry standard for this process is defined by NIST (National Institute of Standards and Technology) and SANS. We'll be focusing on the widely adopted 6-step SANS PICERL methodology.

1. Preparation
    - Policy & Plan Creation: Having an official Incident Response Plan (IRP).
    - Asset Management: Knowing what servers, endpoints, and data you are defending.
    - Tooling: Deploying EDR (Endpoint Detection & Response), SIEM, and ensuring logs are actually being collected and retained.
    - Team Readiness: Conducting tabletop exercises (IR drills) and ensuring the SOC team has the right access privileges.

2. Identification
    - Monitoring Alerts: Reviewing SIEM alerts, IDS/IPS triggers, and EDR warnings.
    - Triaging: Filtering out false positives. If a user tries to log in over VPN 5 times and fails because they forgot their password, it's an event. If they succeed on the 100th try from an IP in a high-risk country, it's an incident.
    - Declaring an Incident: Officially escalating the event to a security incident so the IR plan can be enacted.

3. Containment
    - Short-term Containment: Immediate actions to stop the spread. E.g., isolating an infected laptop from the network, disabling a compromised VPN account, or pulling a server offline.
    - Long-term Containment: Temporary fixes to allow operations to continue while rebuilding the system. E.g., routing traffic through a newly built, clean proxy server.

4. Eradication
    - Removing Malicious Artifacts: Deleting malware, reversing unauthorized registry changes, and removing persistence mechanisms (like cron jobs or scheduled tasks created by the attacker).
    - Patching the Root Cause: If the attacker got in via an unpatched Apache Struts vulnerability, that server must be patched right now, otherwise they will just come back.

5. Recovery
    - Restoring from Backups: Rebuilding servers from clean, offline backups.
    - Credential Resets: Forcing enterprise-wide password resets if Active Directory was compromised.
    - Monitoring Heightened: Leaving increased monitoring on the affected systems for several weeks to ensure the attacker doesn't return.

6. Lessons Learned
    - Writing the Post-Mortem Report: Documenting exactly what happened, chronological timeline, and the root cause.
    - Process Improvement: Asking "What did we do well?" and "What went wrong?". If containment took 4 hours because the SOC didn't have access to the firewall firewall console, the policy must be updated to give them access.


## Introduction to Digital Forensics

Digital Forensics is the application of scientific investigation applied to digital crimes and attacks. It involves the recovery, investigation, examination, and analysis of material found in digital devices.

### The Goal of Forensics

- Truth: Establishing exactly what occurred.
- Attribution: Finding out who did it (Internal threat? Nation state? Ransomware gang?).
- Impact Analysis: Determining exactly what data was accessed, stolen, or destroyed.
- Legal Admissibility: Ensuring the collected evidence holds up in a court of law.

### Major Branches of Digital Forensics

1. Computer/Disk Forensics

The classic discipline. This involves taking a physical or logical "image" (a bit-by-bit exact copy) of a hard drive or SSD.

- What we look for: Deleted files, browser history, illegal media, timeline of accessed documents, registry modifications.
- Tools: Autopsy, EnCase, FTK (Forensic Toolkit).

2. Memory (RAM) Forensics

Hard drives are slow and persistent. Modern, sophisticated malware often runs entirely in Random Access Memory (RAM) to avoid leaving traces on the hard drive.

- What we look for: Decrypted passwords, active network connections, injected malicious code, running processes.
- Tools: Volatility, Rekall.

3. Network Forensics

Analyzing network traffic to reconstruct events. It's often said that "packets don't lie." Even if an attacker deletes the logs on a compromised server, the network traffic capturing their activity might still exist.

- What we look for: Data exfiltration (large uploads), Command and Control (C2) beacons, unencrypted credentials.
- Tools: Wireshark, Zeek, Suricata, Arkime.

4. Mobile Forensics

Smartphones are essentially highly personal computers. They are often critical in criminal investigations or corporate espionage cases.

- What we look for: SMS/WhatsApp messages, GPS locations, application usage, call logs.
- Tools: Cellebrite, Magnet AXIOM.

### The Friction: Speed vs. Preservation

There is an inherent conflict between IT/Business Operations and Digital Forensics.
A mature Incident Response plan balances these two conflicting needs, outlining exactly when a full forensic investigation is required vs. when rapid recovery is prioritized.


## Chain of Custody & Evidence Handling

### What is the Chain of Custody?

The Chain of Custody is a chronological, written record detailing the seizure, custody, control, transfer, analysis, and disposition of physical or digital evidence.

It answers four critical questions at any given point in time:

- Who collected the evidence?
- How and where was it collected?
- Who had possession of it subsequently?
- How was it stored and protected in the meantime?

If the chain is broken (unaccounted time or an undocumented transfer), the evidence may be deemed inadmissible in legal proceedings.

### Hashing for Integrity

A cryptographic hash (like MD5, SHA-1, or SHA-256) is a one-way mathematical algorithm that assigns a unique, fixed-size string of characters to a piece of data. It acts as a digital fingerprint.

The Hashing Workflow:
- Acquisition: You arrive on scene and create a forensic image (image.dd) of the suspect's laptop.
- Initial Hash: Immediately, you run a SHA-256 hash on image.dd. The result is: 5e884...a13.
- Documentation: You write that hash value down on your official Chain of Custody form.
- Verification: A year later in court, the defense demands proof that the image wasn't tampered with. You run the SHA-256 hash again on your copy. It outputs 5e884...a13. The fingerprints match.

If even a single byte in that 500GB image was changed, the resulting hash would be completely different.

### Write Blockers

When acquiring evidence from a physical hard drive, you must avoid altering it. Simply booting up a Windows hard drive makes hundreds of registry changes and alters file access times instantly.

To prevent this, forensics analysts use hardware or software Write Blockers. A hardware write blocker sits between the suspect's hard drive and your forensic workstation. It allows your computer to read the data from the drive to make a copy, but physically intercepts and blocks any write commands, preserving the original evidence perfectly pristine.

## Core Forensics Principles

### 1. Locard's Exchange Principle

When an attacker breaches a server, they always leave a trace, and they always alter the environment.

- What they leave: IP addresses in Apache logs, malicious binaries dropped in /tmp, newly created user accounts, or modified registry keys.
- What they take: Exfiltrated database files, stolen SSH keys.

The trace is always there. The job of the forensic analyst is simply to know where to look for it before it gets overwritten.

### 2. The Order of Volatility (RFC 3227)

Evidence must be collected based on its Volatility — how easily and quickly it can be lost or destroyed. You must gather the most volatile evidence first, moving down to the least volatile evidence.

The Standard Order of Volatility:
(From Most Volatile / First Collected → to Least Volatile / Last Collected)

- Registers and Cache: Data inside the CPU. (Extremely hard to capture, often ignored in standard IR).
- Routing Tables, ARP Cache, Process Table, Kernel Statistics: This lives in RAM mapping active network/process states. It changes every millisecond.
- System Memory (RAM): The contents of the running memory. If power is lost, this is gone forever.
- Temporary File Systems: E.g., The /tmp directory in Linux, which is often cleared upon a reboot.
- Disk (Hard Drive / SSD): Persistent storage. Files, databases, and logs. This will survive a reboot.
- Remote Logging and Monitoring Data that is relevant to the system in question: E.g., Logs forwarded to a SIEM.
- Physical Configuration and Network Topology: The physical layout of cables and routers.
- Archival Media: Backups stored on tapes or in cold cloud storage.