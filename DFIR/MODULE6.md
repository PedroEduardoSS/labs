# Incident Response Methodology (PICERL)

## Phase 1 & 2: Preparation and Identification

1. Preparation
    - Creating the Team: Establishing the Computer Security Incident Response Team (CSIRT). Knowing exactly who to call (external forensics, legal counsel, PR firm).
    - Infrastructure Setup: Deploying Endpoint Detection and Response (EDR) agents, configuring central logging (SIEM), and ensuring network segmentation.
    - Playbooks: Writing step-by-step guides for handling specific incidents (e.g., "Ransomware Playbook", "Phishing Playbook").
    - Tabletop Exercises: Conducting simulated cyber attack drills with executives and technical teams to practice the response.

2. Identification
    - Events vs. Incidents: An Event is anything that happens on a network (a user logging in, a firewall blocking a packet). An Incident is a violation of security policy (a user logging in from Russia using stolen credentials).
    - Indicators of Compromise (IoCs): Analysts use IoCs to identify bad activity. These are technical artifacts like malicious IPs, domains, or file hashes.
    - Alert Triage: SOC analysts review alerts from the SIEM. If an alert is deemed a true positive, the Incident Response process officially begins.
    - Scoping: Answering the crucial question: "How bad is it?" Did the attacker compromise one laptop, or the entire Active Directory domain controller database? You cannot contain an incident if you do not know the full scope.

## Phase 3: Containment

### The Containment Dilemma

- Immediate Containment (Pulling the Plug):
    - Action: As soon as a compromised machine is found, it is instantly disconnected from the network.
    - Pros: Stops the attacker dead in their tracks. Prevents data exfiltration and ransomware encryption.
    - Cons: Alerts the attacker that you know they are there. If you haven't fully scoped the incident, the attacker will immediately activate their dormant "Plan B" backdoors on other systems and bury themselves deeper. Furthermore, you lose Volatile Evidence (RAM) if the machine is powered off.
- Delayed Containment (Monitoring):
    - Action: The defenders leave the compromised system online and silently watch the attacker.
    - Pros: Allows defenders to fully understand the attacker's toolkit, discover all their backdoors, and fully scope the incident. Gives time to capture RAM and network packets.
    - Cons: Highly risky. The attacker might suddenly decide to steal sensitive data or deploy ransomware while you are watching them.

### Containment Actions

- Network Segmentation: Moving infected hosts to an isolated Quarantine VLAN where they cannot talk to the internet or the rest of the corporate network.
- Firewall Blocks: Blocking the known Command and Control (C2) IP addresses and domains at the perimeter firewall.
- Account Disablement: Forcing password resets on compromised user accounts and disabling compromised service accounts.
- Endpoint Isolation: Using EDR tools to logically cut the machine's network access, allowing it to only communicate with the IR team's forensic servers.

## Phase 4 & 5: Eradication and Recovery

### Phase 4: Eradication

- You cannot just delete the single malware file you found and call it a day. If you missed a persistent backdoor in the registry, the attacker will be back in 5 minutes.
- Complete Removal: You must delete malware, remove malicious scheduled tasks, delete attacker-created user accounts, and fix the vulnerability that allowed them in the first place (e.g., patching the exploited firewall, or implementing MFA).
- Nuking from Orbit: Because advanced malware is so good at hiding, standard IR practice is often to skip manual deletion. Instead, the infected machine's hard drive is completely wiped, and the OS is reinstalled from a known-good, pristine image. "When in doubt, wipe it out."

### Phase 5: Recovery

- Restoring from Backup: If a machine was wiped (or encrypted by ransomware), the data must be restored from secure, offline backups.
- Reconnecting: Slowly and carefully moving the repaired systems out of the Quarantine VLAN and back into the production network.
- Enhanced Monitoring: The days following recovery are critical. The IR team will place the recovered systems under extreme scrutiny, looking for any signs that the eradication failed and the attacker has returned.
- Business Continuity: Restoring normal business operations, which might involve bringing email servers back online or reopening customer portals.

## Phase 6: Lessons Learned

### The Post-Incident Report

- The Timeline: A blow-by-blow, minute-by-minute account of exactly what the attacker did, and exactly how the defense team responded.
- Root Cause Analysis: Precisely how the attacker gained initial access (The "Patient Zero" vector). E.g., "Employee Bob Smith clicked a link in a phishing email on Tuesday."
- The Impact: Exactly what data was stolen, how much money was lost, and the total downtime of the business. (This is usually required for cyber insurance claims and legal/regulatory compliance).

### The Post-Mortem Meeting

- What went right? (e.g., the EDR tool successfully blocked the ransomware from spreading past the initial host).
- What went wrong? (e.g., it took the SOC 14 hours to notice the alert; the backups for the HR database were corrupted and failed to restore).

### Continuous Improvement

- If the attacker used a stolen password, the business implements mandatory Multi-Factor Authentication (MFA).
- If the IR team didn't know how to contain the threat quickly, the business rewrite the playbooks and funds more tabletop training exercises.
- The output of "Lessons Learned" feeds directly back into Phase 1, "Preparation", creating a continuous loop of strengthening security.