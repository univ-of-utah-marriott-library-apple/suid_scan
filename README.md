SUID Scan
=========

SUID Scan is a lightweight script to help you check for files with execute-as bits set (i.e. the SUID and SGID bits). In general, it is intended for use in distributed environments as a supplement to your routine OS X systems' maintenance cycle.

## What Is It?

We developed SUID scan as a frontline, lightweight defense mechanism against the [rootpipe security vulnerability](https://truesecdev.wordpress.com/2015/04/09/hidden-backdoor-api-to-root-privileges-in-apple-os-x/) published in April, 2015.

### What Is Rootpipe?

[CVE-2015-1130](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2015-1130), or "rootpipe" as it is commonly called, is a weakness in the private Admin Framework. Specifically, a specific unsecured XPC service allows the unauthorized creation of files owned by root with the setuid (SUID) bit set. Binaries with the setuid bit set behave as if the owner of the file has launched them, regardless of who the actual launching user is. Normally the SUID bit is used when a process must be run as a specific user, and sometimes that user is root. Rootpipe can easily be used for malicious purposes, to create binaries with root-level (complete access) privileges.

SUID Scan searches for files with this bit set. It allows administrators to create a list of known SUID applications.

### Disclaimer

We acknowledge up-front that our approach (detailed in this document) is not intended to be a comprehensive solution, and it may not suit the needs of your particular environment. There are plenty of holes available to someone with enough know-how to really abuse the rootpipe exploit. However, we hope that this initial implementation can be used as an early-warning detection system until a more thorough approach is made available.

## How to use it

1. Start with a machine in a known state. This may mean starting with a just-imaged machine. In our case, it's a machine that has just finished its Radmind post-maintenance cycle.
2. Run the script, and redirect the output to a file. The script generates a tab-separated list of absolute file paths, modification times, and hashes for those files which have either the SUID or SGID bit set (or both). (Items that are not files, such as directories, will simply have blank modification times/hashes set.)
3. Periodically during regular use of the computer, run the script again and compare the results (e.g. with `diff`) to find differences between the known-good SUID applications and new additions. We have not arrived at a definitive number for how often this should be done. You may want to run frequently during use (e.g. every 5 minutes), or maybe only when users logout. We're leaning towards the latter because we don't want the `find` process to negatively impact our users' experience.

## How it works

When you run `suid_scan.py`, it starts by generating a list of all currently-mounted volumes. Then it executes a `find` process on each of these volumes to search for files that:

 * are files (not directories or links or any of that stuff)
 * are owned by root
 * have 2000 (SGID) or 4000 (SUID) permissions set

This list is then sorted (for easier `diff`ing), and each file is checked for a modification timestamp and a hash. These three items (path, modification time, hash) are outputted in one line separated by tabs, with one line for each file found.

## Hash function

The default hash function is the SHA1 hash provided by `/usr/bin/openssl sha1`. You may provide your own hash-generating command as an argument on the command line at invocation of the `suid_scan.py` script. Any argument are concatenated into one command for a hash-generator, which must take a file path as its final argument.

For example, we use the hash provided by Radmind's fsdiff tool. For our invocation, we would do:

```
$ suid_scan.py /usr/local/bin/fsdiff -1c sha1
```

The script will take this input and use it in a Python subprocess call as `/usr/local/bin/fsdiff -1c sha1 /path/to/file`. The first part of the argument you give must be a full path to a command that will be executed to generate a hash.
