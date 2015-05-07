SUID Scan
=========

SUID Scan is a lightweight script to help you check for files with execute-as bits set (i.e. the SUID and SGID bits). In general, it is intended for use in distributed environments as a supplement to your routine OS X systems' maintenance cycle.

## Contents

* [Download](#download) - get the .dmg
* [System Requirements](#system-requirements) - what you need
* [Contact](#contact) - how to reach us
* [Uninstall](#uninstall) - how to remove SUID Scan
* [What Is It](#what-is-it)
  * [What Is Rootpipe](#what-is-rootpipe) - the vulnerability we're attempting to address
  * [Disclaimer](#disclaimer) - we make no guarantees
  * [Recommendation](#recommendation) - how we advise you use this
* [How To Use It](#how-to-use-it)
  * [Usage Options](#usage-options) - command-line options
  * [Automated (via launchd)](#automated-via-launchd) - automagic
    * [Periodic Scan](#periodic-scan)
    * [Logout Scan](#logout-scan)
* [How It Works](#how-it-works) - behind-the-scenes
  * [Installation](#installation) - details on the installation procedure
    * [Periodic Scan](#periodic-scan)
    * [Logout Scan](#logout-scan)
* [Footnotes](#footnotes) - miscellaneous odds and ends
  * [SUID/SGID Permissions](#1)
  * [Hash Function](#2)

## Download

[Download the latest installer here!](../../releases/)

## System Requirements

The SUID Scan script has been tested to work on Mac OS X 10.9 and 10.10, and uses Python version 2.7.

## Contact

If you have any comments, questions, or other input, either [file an issue](../../issues) or [send an email to us](mailto:mlib-its-mac-github@lists.utah.edu). Thanks!

## Uninstall

To remove SUID Scan from your system, download the .dmg and run the "Uninstall SUID Scan" package to uninstall it. (Note that it will say "Installation Successful" but don't bleive it - it will only remove files.)

## What Is It?

We developed SUID Scan as a frontline, lightweight defense mechanism against the [rootpipe security vulnerability](https://truesecdev.wordpress.com/2015/04/09/hidden-backdoor-api-to-root-privileges-in-apple-os-x/) published in April, 2015.

### What Is Rootpipe?

[CVE-2015-1130](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2015-1130), or "rootpipe" as it is commonly called, is a weakness in the private Admin Framework of Mac OS X ***versions 10.7.0 through 10.10.2***. In particular, a specific unsecured XPC service allows the unauthorized creation of files owned by root with the setuid (SUID) bit set<sup>[[1]](#1)</sup>. Binaries with the setuid bit set behave as if the owner of the file has launched them, regardless of who the actual launching user is. Normally the SUID bit is used when a process must be run as a specific user, and sometimes that user is root. Rootpipe can easily be used for malicious purposes, to create binaries with root-level (complete access) privileges.

SUID Scan searches for files with this bit set. It allows administrators to create a list of known SUID applications.

### Disclaimer

We acknowledge up-front that our approach (detailed in this document) is not intended to be a comprehensive solution, and it may not suit the needs of your particular environment. There are plenty of holes available to someone with enough know-how to really abuse the rootpipe exploit. However, we hope that this initial implementation can be used as an early-warning detection system until a more thorough approach is made available.

### Recommendation

Our best recommendation is that you update your computer(s) to OS X 10.10.3, which is not vulnerable to this exploit. However, we are sympathetic to the fact that this may be difficult and so we provide SUID Scan to you.

## How To Use It

1. Start with a machine in a known state. In many cases this means starting with a machine that has just been imaged. For us, it means using a machine that has just completed its Radmind post-maintenance cycle.
2. `suid_scan.py --output /secure/path/to/a/file` will produce a file with a list of all files owned by root and that have the SUID or SGID bit set.
3. Periodically run the scan again, and compare against the previously-created file: `suid_scan.py --input /secure/path/to/a/file`

We recommend setting up (3) to occur periodically via LaunchDaemon, and to set it to automatically email the result.

### Usage Options

| Option              | Purpose                                                                                                 |
|---------------------|---------------------------------------------------------------------------------------------------------|
| `--help`            | Prints help information and quits.                                                                      |
| `--version`         | Prints program version information and quits.                                                           |
| `--output out_file` | Specifies the destination for a list of found bad files with their hashes and modification timestamps.  |
| `--input in_file`   | Where to read in a list to compare against the current scan.                                            |
| `--mailto address`  | Send information to 'address' via email. 'address' can be given as a comma-separated list of addresses. |
| `--hash function`   | Override the default hashing function. Give 'function' as '/path/to/function with parameters'.          |

### Automated (via launchd)

Included in this repository are three plists to be used with `launchd`: one for a recurring, periodic scan of the file system, and two for a per-logout scan. These `launchd` items are included in the installer. See [Installation](#installation) for more specific information.

#### Periodic Scan

The file `edu.utah.scl.suid_scan.periodic.plist` should be moved into `/Library/LaunchDaemons/` and configured appropriately for your desired settings. This will cause SUID Scan to run on an interval (by default, every 30 minutes).

#### Logout Scan

To run a script on logout, move `edu.utah.scl.suid_scan.login.plist` and `edu.utah.scl.suid_scan.logout.plist` to `/Library/LaunchAgents/`, and the simple shell script `suid_scan.logout_wrapper.sh` to `/usr/local/bin/`.

The way this system works is when a user logs in, the `.login` plist checks for the existence of a trigger file (by default it's `/private/tmp/edu.utah.scl.suid_scan.runatlogout`). If the file does not exist, it is created.

When a user logs out, the `.logout` plist is executed. It checks for the trigger file, removes it, and then runs a scan.

All SUID scan settings for this automated process should be configured in the `suid_scan.logout_wrapper.sh` script. By default it will produce a base scan, and then comparison scans after that.

## How It Works

When you run `suid_scan.py`, it starts by generating a list of all currently-mounted volumes. Then it executes a `find` process on each of these volumes to search for files that:

 * are files (not directories or links or any of that stuff)
 * are owned by root
 * have 2000 (SGID) or 4000 (SUID) permissions set

This list is then sorted (for easier `diff`ing), and each file is checked for a modification timestamp and a hash. These three items (path, modification time, hash) are outputted in one line separated by tabs, with one line for each file found.

## Installation

To install SUID Scan, grab the latest `.dmg` from [the releases page](../../releases/). Open it up, and inside you will find a package to perform installation.

When installing the script, you will be given the option of also installing some `launchd` items. These are provided to help you run SUID Scan on an automated schedule, and they are given in two forms: periodic and logout.

Note that any time you modify a LaunchDaemon or LaunchAgent, you must first unload it with `sudo launchctl unload {path to plist}`, then do your modifications, and then load it back with `sudo launchctl load {path to plist}`. For some of these you may get a warning that the daemon/agent "cannot be loaded in this session", but that's okay.

### Periodic Scan

The periodic scan occurs on a given time interval. It is controlled by a property list file installed to `/Library/LaunchDaemons/edu.utah.scl.suid_scan.periodic.plist`. If you modify this plist, you can change the configuration options for how the SUID Scan is run (input comparison file, output file location, etc.) as well as how often the scan runs. The default is to run every 1800 seconds (30 minutes).

### Logout Scan

If you want to scan after users logout, use the Logout LaunchAgent. It installs a few files to be able to manage the automated logout procedure:

1. `/Library/LaunchAgents/edu.utah.scl.suid_scan.logout.plist`
2. `/Library/LaunchAgents/edu.utah.scl.suid_scan.login.plist`
3. `/usr/local/bin/suid_scan.logout_wrapper.sh`

If you want to configure how the scan is run, you can set all of the execution options in the `/usr/local/bin/suid_scan.logout_wrapper.sh` script. Some options are preconfigured so that the first time the script runs, it will produce a base scan, and every scan after that compares its results to that base scan. This comparison is what will be outputted.

## Footnotes

### <a name="1"></a>1. SUID/SGID Permissions

You are likely familiar with octal permissions (if not, see the [`chmod` manual entry](https://developer.apple.com/library/mac/documentation/Darwin/Reference/ManPages/man1/chmod.1.html)). Usually you only see the Unix octal permissions written with three digits, such as "777" or "644", etc.

In fact there are more permission bits that can be set than just the nine (owner rwx, group rwx, and world rwx). Two of these extra bits are the SUID and the SGID bits (set-user-ID-on-execution and set-group-ID-on-execution, respectively). When these bits are set on a file, they modify how the file is executed by changing the effective user ID (SUID) or the effective group ID (SGID) of the executing user, resulting in a potential change of permissions.

Let's assume we have a file `my_file` in a directory, and it is executable:

```
$ ls -l my_file
-rwxr-xr-x  1 alice  wheel  0 Apr 17 14:42 my_file
```

SUID permissions can be set by using the `chmod` command like so:

```
$ chmod u+s my_file
```

and the permissions are revealed when listing the contents of a directory with the long format:

```
$ ls -l my_file
-rwsr-xr-x  1 alice  wheel  0 Apr 17 14:42 my_file
```

(The octal permissions for this file are "4755".)

What this means is that if `bob` were to execute `my_file`, the program would run *as though `alice` were running it.* In general this is not used very often by regular users. Where the SUID bit matters is if `root` owns the file, because then anybody executing the file will have super-user permissions. Some executables always have the SUID bit set, such as `sudo`, `ping`, and `top` (to name a few).

What the rootpipe vulnerability does is allow the creation of files owned by root and with the SUID bit set. This is a huge security vulnerability since this means anybody can run anything with full super-user permissions.

(Note that I do not go in-depth with SGID because it is less used, but it is effectively the same as SUID except with group permissions instead of owner permissions.)

### <a name="2"></a>2. Hash function

A hash is like a digital fingerprint for a file. Hashes are often used by websites that offer downloads so you can tell whether the file has become corrupted during transfer; they post a hash with the file link, and then you can check the hash of the downloaded file to compare. Hash functions that generate hashes are designed to reduce the likelihood of hash collision (i.e. when two different files have the same hash), but this cannot be guaranteed and is a risk.

The default hash function used by SUID Scan is the SHA1 hash provided by `/usr/bin/openssl sha1`. You may provide your own hash-generating command as an argument on the command line at invocation of the `suid_scan.py` script. Any argument are concatenated into one command for a hash-generator, which must take a file path as its final argument.

For example, we use the hash provided by Radmind's fsdiff tool. For our invocation, we would do:

```
$ suid_scan.py /usr/local/bin/fsdiff -1c sha1
```

The script will take this input and use it in a Python subprocess call as `/usr/local/bin/fsdiff -1c sha1 /path/to/file`. The first part of the argument you give must be a full path to a command that will be executed to generate a hash.

## Update History

This is a short summary of the project's history.

| Date       | Version | Update Description                                                                                 |
|------------|:-------:|----------------------------------------------------------------------------------------------------|
| 2015-04-30 | 1.2     | Updated Periodic LaunchDaemon and added Logout LaunchAgents to help with automation.               |
| 2015-04-21 | 1.2     | Updated documentation and added a Periodic LaunchDaemon for automatation.                          |
| 2015-04-21 | 1.2     | Fixed an issue where cross-checking files didn't actually work.                                    |
| 2015-04-17 | 1.1     | Updated to disregard Time Machine volumes and allowed crossreferencing against pre-existing scans. |
| 2015-04-16 | 1.0     | First commit contained a somewhat usable script to search the file system.                         |
| 2015-04-09 | -       | Emil Kvarnhammar published [Hidden backdoor API to root privileges in Apple OS X](https://truesecdev.wordpress.com/2015/04/09/hidden-backdoor-api-to-root-privileges-in-apple-os-x/), prompting us to develop a method of monitoring file permissions. |
