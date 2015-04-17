SUID Scan
=========

SUID Scan is a lightweight script to help you check for files with execute-as bits set (i.e. the SUID and SGID bits). In general, it is intended for use in distributed environments as a supplement to your routine OS X systems' maintenance cycle.

## What Is It?

We developed SUID Scan as a frontline, lightweight defense mechanism against the [rootpipe security vulnerability](https://truesecdev.wordpress.com/2015/04/09/hidden-backdoor-api-to-root-privileges-in-apple-os-x/) published in April, 2015.

### What Is Rootpipe?

[CVE-2015-1130](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2015-1130), or "rootpipe" as it is commonly called, is a weakness in the private Admin Framework of Mac OS X ***versions 10.7.0 through 10.10.2***. In particular, a specific unsecured XPC service allows the unauthorized creation of files owned by root with the setuid (SUID) bit set<sup>[[1]](#1)</sup>. Binaries with the setuid bit set behave as if the owner of the file has launched them, regardless of who the actual launching user is. Normally the SUID bit is used when a process must be run as a specific user, and sometimes that user is root. Rootpipe can easily be used for malicious purposes, to create binaries with root-level (complete access) privileges.

SUID Scan searches for files with this bit set. It allows administrators to create a list of known SUID applications.

### Disclaimer

We acknowledge up-front that our approach (detailed in this document) is not intended to be a comprehensive solution, and it may not suit the needs of your particular environment. There are plenty of holes available to someone with enough know-how to really abuse the rootpipe exploit. However, we hope that this initial implementation can be used as an early-warning detection system until a more thorough approach is made available.

### Recommendation

Our best recommendation is that you update your computer(s) to OS X 10.10.3, which is not vulnerable to this exploit. However, we are sympathetic to the fact that this may be difficult and so we provide SUID Scan to you.

## How to use it

1. Start with a machine in a known state. This may mean starting with a just-imaged machine. In our case, it's a machine that has just finished its Radmind post-maintenance cycle.
2. Run the script, and redirect the output to a file. The script generates a tab-separated list of absolute file paths, modification times, and hashes<sup>[[2]](#2)</sup> for those files which have either the SUID or SGID bit set (or both). (Items that are not files, such as directories, will simply have blank modification times/hashes set.)
3. Periodically during regular use of the computer, run the script again and compare the results (e.g. with `diff`) to find differences between the known-good SUID applications and new additions. We have not arrived at a definitive number for how often this should be done. You may want to run frequently during use (e.g. every 5 minutes), or maybe only when users logout. We're leaning towards the latter because we don't want the `find` process to negatively impact our users' experience.

## How it works

When you run `suid_scan.py`, it starts by generating a list of all currently-mounted volumes. Then it executes a `find` process on each of these volumes to search for files that:

 * are files (not directories or links or any of that stuff)
 * are owned by root
 * have 2000 (SGID) or 4000 (SUID) permissions set

This list is then sorted (for easier `diff`ing), and each file is checked for a modification timestamp and a hash. These three items (path, modification time, hash) are outputted in one line separated by tabs, with one line for each file found.

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
