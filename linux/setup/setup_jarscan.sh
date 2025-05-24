#!/bin/bash
cmd_name="jarscan"
script_fn="scan_jars.py"

# Re-run the script as root if we're not
if [ "$EUID" != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

echo "Setting up $cmd_name"
if ! command -v /usr/bin/python3 2>&1 >/dev/null
then
    echo "/usr/bin/python3 does not exist! Please install it before continuing..."
    exit 1
fi

mkdir -p /opt/scripts
cp "../python/$script_fn" "/opt/scripts/$script_fn"

# Create executable as a script, install to local/bin
echo "/usr/bin/python3 /opt/scripts/$script_fn \"\$@\"" > $cmd_name
chmod +x $cmd_name
mv $cmd_name /usr/local/bin

echo "Done! Try the command '$cmd_name' to see the effects!"
