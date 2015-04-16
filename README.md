SUID Scan
=========

SUID Scan is a simple script to help you check for files with execute-as bits set (i.e. the SUID and SGID bits). In general it is intended for use in distributed environments where you may not be able to upgrade your computers to the most recent version of OS X immediately.

## Origins

SUID Scan came around when our group heard about the [rootpipe security vulnerability](https://truesecdev.wordpress.com/2015/04/09/hidden-backdoor-api-to-root-privileges-in-apple-os-x/). In our environment, upgrading immediately to Yosemite (10.10.3) is not feasible, so we needed a way to at least detect whether somebody had modified our systems.

We acknowledge up front that the method detailed within is not 100% secure. There are plenty of holes available to somebody with enough know-how to really abuse the rootpipe exploit. However, we hope that this at least offers some sort of mediocre detection system.

## How to use it

1. Start with a machine in a known state. This may mean starting with a just-imaged machine. In our case, it's a machine that has just finished its Radmind post-maintenance cycle.
2. Run the script, and redirect the output to a file. The script generates a tab-separated list of absolute file paths, modification times, and hashes for those files. (Items that are not files, such as directories, will simply have blank modification times/hashes set.)
3. Periodically during regular use of the computer, run the script again and compare. We have not arrived at definitive number for this. You may want to run frequently during use (e.g. every 5 minutes), or maybe only when users logout. We're leaning towards the latter because we don't want the `find` process to negatively impact our users' experience.
