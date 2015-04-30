#!/bin/bash

# This short script toggles the "runatlogout" state for the two LaunchAgents
# that should be installed:
#   edu.utah.scl.suid_scan.login
#   edu.utah.scl.suid_scan.logout
# These allow for an on-logout scan of the filesystem for SUID/SGID files.
#
# For more information, see the GitHub repository at:
#   https://github.com/univ-of-utah-marriott-library-apple/suid_scan

# If you change the trigger file, update it in the plists too.
TRIGGERFILE="/private/tmp/edu.utah.scl.suid_scan.runatlogout"
BASESCAN="/var/log/suid_scan.base_scan.txt"
NEWSCAN="/var/log/suid_scan.new_scan.txt"

if [ -f "${TRIGGERFILE}" ]; then
    rm -f "${TRIGGERFILE}"
    # Enter whatever customization options you want here.
    # If the base run has been complete, do a comparison scan. Otherwise,
    # generate the base scan.
    if [ -f "${BASESCAN}" ]; then
        # Run a comparison scan.
        /usr/local/bin/python /usr/local/bin/suid_scan.py \
            --input "${BASESCAN}" \
            --output "${NEWSCAN}"
    else
        # Run a base scan.
        /usr/local/bin/python /usr/local/bin/suid_scan.py \
            --output "${BASESCAN}"
    fi
else
    touch "${TRIGGERFILE}"
fi
