# Windows Forensics

## The Windows Registry

The Windows Registry is the central hierarchical database used to store information necessary to configure the system for one or more users, applications, and hardware devices. For forensics analysts, it is an absolute goldmine.

Whenever a user executes a program, plugs in a USB drive, or changes a setting, a trace is left in the Registry.

### Structure of the Registry

The registry is divided into five main logical root keys (Hives):

- HKEY_LOCAL_MACHINE (HKLM): Settings applied to the entire machine, regardless of who is logged in.
- HKEY_CURRENT_USER (HKCU): Settings unique to the currently logged-in user.
- HKEY_USERS (HKU): Contains all the loaded user profiles. (HKCU is actually just a pointer into a specific subkey inside HKU).
- HKEY_CLASSES_ROOT (HKCR): File extension associations (e.g., telling Windows that .txt opens with Notepad).
- HKEY_CURRENT_CONFIG (HKCC): Information about the hardware profile currently being used.

### Where are the files?

- `C:\Windows\System32\config\SYSTEM` (Maps to HKLM\SYSTEM)
- `C:\Windows\System32\config\SOFTWARE` (Maps to HKLM\SOFTWARE)
- `C:\Windows\System32\config\SECURITY` (Maps to HKLM\SECURITY)
- `C:\Windows\System32\config\SAM` (Security Account Manager - Holds local password hashes)
- `C:\Users\<username>\NTUSER.DAT` (Maps to the specific user's HKCU)

### Key Forensic Artifacts in the Registry

1. Persistence (Auto-Start Extensibility Points)

Attackers want their malware to survive a reboot. The easiest way to do this is to add a registry key telling Windows to run the malware every time it starts.

- Run Keys: `HKLM\Software\Microsoft\Windows\CurrentVersion\Run` and `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
- Forensic Value: Always check these keys. If you see `C:\Users\Public\svchost.exe` launching from a Run key, the machine is compromised.

2. USB Device History (USBStor)

- Location: `HKLM\SYSTEM\CurrentControlSet\Enum\USBSTOR`
- Forensic Value: Records the Vendor, Product ID, and unique Serial Number of every USB mass storage device that has ever been plugged into the machine.

3. UserAssist

- Location: `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist`
- Forensic Value: Tracks which GUI applications the user executed, how many times they ran them, and the last time they were executed. The names of the programs are lightly obfuscated using ROT-13 encryption, which your forensic tools will decrypt automatically.


## Windows Event Logs

Windows Event Logs (.evtx files) are the primary source of chronological historical data on a Windows system. They track logins, service starts, application crashes, and security policy changes.

They are stored in `C:\Windows\System32\winevt\Logs\`

### The Big Three

- System: Events logged by Windows system components (e.g., a driver failing to load, or the system booting up).
- Application: Events logged by installed software (e.g., Microsoft Word crashing, or an antivirus detecting a file).
- Security: Events related to authentication, privilege use, and object access. By default, only Administrators can view this log.

### Crucial Security Event IDs (EIDs)

1. Logon & Authentication

- EID 4624: Successful Logon.
    - Forensic Value: Shows who logged in, when, and from where (Source IP). The "Logon Type" field is critical. Type 2 means Interactive (Physical keyboard). Type 3 means Network (e.g., accessing a shared folder). Type 10 means Remote Interactive (RDP).
- EID 4625: Failed Logon.
    - Forensic Value: A high volume of 4625s in a short time frame indicates a Brute Force or Password Spraying attack.
- EID 4672: Special Privileges Assigned to New Logon.
    - Forensic Value: This means the user logged in as an Administrator (or used "Run as Administrator").

2. Account Management

- EID 4720: A user account was created.
    - Forensic Value: Attackers often create backup "backdoor" accounts (like SysAdmin1) just in case their malware is discovered and removed.
- EID 4722 / 4724: Account enabled / Password reset.
- EID 4732: A member was added to a security-enabled local group.
    - Forensic Value: Look closely if the target group is "Administrators". This is a sign of local privilege escalation.

3. Process Execution
- EID 4688: A new process has been created.
    - Forensic Value: Tells you exactly what time a program ran. If command-line auditing is turned on, it will even log the exact arguments (e.g., powershell.exe -NoProfile -EncodedCommand JABX...), which is incredibly useful for catching malicious scripts.

4. Clearing Logs
- EID 1102: The audit log was cleared.
    - Forensic Value: The massive red flag. Attackers often run the command wevtutil cl Security to erase their tracks. If you see EID 1102, assume an attacker was present, had Administrator rights, and intentionally deleted evidence.

## Evidence of Execution

1. Prefetch (*.pf files)

Windows uses Prefetch to speed up the boot process and application launch times. When an application runs for the first time, Windows analyzes what files and DLLs it needs and creates a `.pf` file in `C:\Windows\Prefetch\`.

The next time the application runs, Windows reads the `.pf` file and pre-loads the necessary components into memory, making the application launch faster.

- Forensic Value:
    - Proof of execution: If nc.exe-0D12ABCD.pf exists, Netcat was absolutely executed on this machine.
    - Execution count: The file stores exactly how many times the application has been run.
    - Timestamps: It stores the timestamp of the last execution, as well as up to 7 previous execution timestamps (in Windows 8+).
    - Target path: It shows exactly where the executable was located when it ran (e.g., was it run from C:\Temp or from a USB drive?).

2. Shimcache (Application Compatibility Cache)

Whenever an application runs, Windows checks if it needs any special compatibility settings (shims) to run properly (e.g., "Does this program think it's running on Windows XP?").

Windows caches these checks in the Registry at `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache`.

- Forensic Value:
    - The Shimcache tracks the file path, the file size, and the Last Modified time of the executable.
    - It is fantastic for tracking executables that were run from a USB drive and subsequently deleted. Even if the USB is removed, the trace remains in the Shimcache.
    - Note: The Shimcache does not definitively prove execution (a file can enter the cache just by being browsed in Explorer), but it proves the file existed on the system at a specific path.

3. Amcache

A newer artifact (Windows 8+) located at `C:\Windows\AppCompat\Programs\Amcache.hve`. It is technically its own registry hive file.

- Forensic Value:
    - Similar to Shimcache but records much more detail, notably the SHA-1 hash of the executable.
    - This is incredibly powerful. Even if an attacker renames their malware from `mimikatz.exe` to `svchost.exe`, the Amcache will record its true SHA-1 hash, allowing analysts to instantly identify the malicious binary.

## File System Artifacts

### Master File Table (MFT)

NTFS uses a database called the Master File Table (MFT) to track every single file and folder on the volume. The file itself is called `$MFT`.

- MACB Timestamps: The MFT records four critical timestamps for every file:
    - Modified: When the file contents were last changed.
    - Accessed: When the file was last opened/read.
    - Created: When the file was first created on this volume.
    - MFT Modified (B for birthed/metadata): When the file's metadata (permissions, name) was last changed.
- Time Stomping: Advanced attackers use anti-forensic tools to alter MAC timestamps to make malicious files blend in (e.g., changing malware creation date to 2018). However, it is very difficult to successfully forge the 'MFT Modified' timestamp, meaning forensic tools can often detect time stomping.

### Windows Shortcut Files (.lnk)

When a user opens a file, Windows often automatically creates a shortcut (`.lnk`) file pointing to it (e.g., in the "Recent Items" folder).

- Forensic Value: LNK files are gold. They contain metadata about the target file and the system it was on. Even if the target file was on a USB drive that is now gone, the LNK file left behind tells us:
    - The original path of the file.
    - The MAC timestamps of the target file.
    - The Volume Serial Number of the USB drive it was on.
    - The MAC address of the machine where the file was originally created.

### The Recycle Bin

When a user "deletes" a file, Windows doesn't actually erase the 1s and 0s. Firstly, it just moves the file to a hidden system folder called `$Recycle.Bin`.

Inside the Recycle Bin, Windows splits the deleted file into two pieces:
- $R file: The actual contents of the deleted file, renamed with a random string ($R123456.docx).
- $I file: A metadata file containing the original name of the file, its original path before it was deleted, and the exact timestamp it was deleted.

If you find a suspicious file in the Recycle Bin, parsing its corresponding `$I` file tells you exactly where it came from and when the suspect tried to get rid of it.