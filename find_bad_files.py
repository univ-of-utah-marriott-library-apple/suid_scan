#!/usr/bin/env python

import os
import shlex
import stat
import subprocess
import sys

# Gotta have access to the special places.
if os.geteuid() != 0:
    print("Must be root to run this script!")
    sys.exit(1)

# Sets the default hash function.
HASHER = '/usr/bin/openssl sha1'


def main():
    # Get the inventory of everything on the filesystem and then sort it
    # alphabetically.
    filesystem_inventory = inventory_filesystem()
    filesystem_inventory = sorted(filesystem_inventory, key=lambda entry: entry[0].lower())
    
    # Print the findings. Tabs are used for separation because they're parsable.
    print("Total dangerous items found: {}").format(len(filesystem_inventory))
    for entry in filesystem_inventory:
        print("{path}\t{mtime}\t{hash}").format(
            path  = os.path.abspath(entry[0]),
            mtime = entry[1] if entry[1] else "",
            hash  = entry[2] if entry[2] else ""
        )


def inventory_filesystem():
    """
    Composes an inventory of all attaches filesystems and finds files with the
    SUID or GUID bits set.
    
    :return: a list of tuples containing (file, modification time, hash)
    """
    results = []
    
    ####
    # Get a list of mounted disks.
    mount_info = subprocess.check_output(['/bin/df', '-Pl']).split('\n')
    mount_info = [x for x in mount_info if x][1:]
    mounted_disks = []
    for disk in mount_info:
        disk = "/{}".format(disk.split(' /')[1])
        mounted_disks.append(disk)

    ####
    # Find all the offending files on each disk.
    bad_files_on_disks = {}
    for disk in mounted_disks:
        bad_files_on_disks[disk] = find_bad_files_on_disk(disk)

    ####
    # Iterate over the files found.
    for files in bad_files_on_disks.values():
        for file in files:
            # Ensure we have an absolute path.
            file = os.path.abspath(file)
            # Check file exists.
            if os.path.isfile(file):
                try:
                    mtime = int(os.path.getmtime(file))
                except:
                    mtime = ""
                try:
                    file_hash = get_hash(file)
                except:
                    file_hash = ""
                results.append((file, mtime, file_hash))
    
    return results


def get_hash(file):
    """
    Uses the given hash function to generate a hash of the given file.

    :return: the hash of the file
    """
    if not os.path.isfile(file):
        # It's not a file, which means... it doesn't have a hash. So don't hash
        # it. I thought about checking for specific errors but I don't want to
        # interrupt output.
        return None
    path = os.path.abspath(file)

    # Split the hash function into command form, then add the path.
    hasher = shlex.split(HASHER)
    hasher.append(path)
    if not os.path.isfile(hasher[0]):
        # The given hash function doesn't work.
        raise ValueError("Invalid hash function given: {}").format(haseher[0])

    try:
        # Get the hash of the file.
        info = subprocess.check_output(hasher).split('\n')[0]
        # I assume that the hash will be the last thing outputted on the line.
        file_hash = info.split()[-1]
        return file_hash
    except subprocess.CalledProcessError:
        # Something went wrong.
        return None


def find_bad_files_on_disk(disk=None):
    if not disk:
        disk = '/'
    tm_vol = get_tm_volume()
    if tm_vol:
        if disk == tm_vol:
            return []
    # print("Checking disk '{}'").format(disk)
    find_command = [
        '/usr/bin/find',
        disk,
        '-xdev',
        '-uid', '0',
        '-type', 'f',
        '-perm', '+6000',
    ]
    output = subprocess.check_output(find_command).split('\n')
    output = [x for x in output if x]

    return output


def get_tm_volume():
    """
    Finds the currently-set Time Machine volume, if there is one.

    :return: TM volume mountpoint, or else None if there isn't one
    """
    try:
        tm_dir = subprocess.check_output(['/usr/bin/tmutil', 'machinedirectory'], stderr=subprocess.STDOUT).split('\n')[0]
    except subprocess.CalledProcessError:
        tm_dir = None
    if not tm_dir:
        return None
    
    # Get the filesystem the Time Machine volume is mounted on.
    # (e.g. /dev/disk1s1)
    df = ['/bin/df', '-P', '-k', str(tm_dir)]
    df_info = subprocess.check_output(df).split('\n')
    df_info = [x for x in df_info if x]
    if len(df_info) != 2:
        # Unable to find responsible Time Machine filesystem.
        return None
    info = df_info[1].split()
    index = 0
    for index in range(len(info)):
        try:
            int(info[index])
            break
        except ValueError:
            pass
    fs_id = ' '.join(info[:index])
    
    # Take the filesystem identifier and get the volume name.
    fs_info = subprocess.check_output(['/sbin/mount']).split('\n')
    result = [x for x in fs_info if fs_id == x.split(' on')[0]]
    if len(result) != 1:
        # Something went wrong, but we don't want to halt execution.
        return None

    result = result[0].split('on ')[1]
    return result.split(' (')[0]


if __name__ == '__main__':
    if len(sys.argv) > 1:
        HASHER = ' '.join(sys.argv[1:])
    if not os.path.isfile(shlex.split(HASHER)[0]):
        sys.stderr.write("ERROR: Invalid hash function given: {}\n".format(shlex.split(HASHER)[0]))
        sys.stderr.write("    Please specify the full path to the hash function.\n")
        sys.stderr.flush()
        sys.exit(1)
    main()
