'''
    OnionHA
    ~~~~~~~

        https://github.com/ValentinBELYN/OnionHA

    :copyright: Copyright 2017-2020 Valentin BELYN.
    :license: GNU GPLv3, see the LICENSE for details.

    ~~~~~~~

    This program is free software: you can redistribute it and/or
    modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see
    <https://www.gnu.org/licenses/>.
'''

from os import getpid, geteuid
from pathlib import PosixPath
from re import findall, sub
from subprocess import run, SubprocessError, DEVNULL, STDOUT


_PID = getpid()
_PID_FILE = PosixPath('/var/run/oniond.pid')


def parse_command(string):
    '''
    Splits a string using a shell-like syntax. Returns a `list`.

    '''
    pattern = r'[\'"].*?[\'"]|\S+'

    return [
        sub(r'[\'"]', '', part)
        for part in findall(pattern, string)
    ]


def run_command(command):
    '''
    Executes the command passed in parameters and waits for the end of
    its execution. Returns a `boolean` indicating the success of the
    operation or not.

    '''
    try:
        run(command, stdout=DEVNULL, stderr=STDOUT, check=True)
        return True

    except (OSError, SubprocessError):
        return False


def dump_cluster(cluster):
    '''
    Describes the status of the nodes of a cluster object in a string.

    '''
    dump = 'STATUS'

    for node in cluster.nodes:
        status = int(node.is_alive) + int(node.is_active)
        dump += f' {node.address}:{status}'

    return dump


def read_cluster_dump(dump):
    '''
    Reads the sequence generated by the `dump_cluster` function and
    returns a dictionary containing the status of the nodes.

    '''
    pattern = r'([0-9.]*):([0-2])'

    return {
        address: int(status)
        for address, status in findall(pattern, dump)
    }


def is_root():
    '''
    Indicates whether the current user has root privileges.
    Returns a `boolean`.

    '''
    return geteuid() == 0


def is_running():
    '''
    Indicates whether an instance of Onion HA is already running.
    Returns a `boolean`.

    '''
    return _PID_FILE.is_file()


def get_instance_pid():
    '''
    Retrieves the PID of the running instance. Returns 0 if this
    identifier could not be retrieved.

    '''
    try:
        with open(_PID_FILE, 'r') as file:
            return int(file.readline())

    except (OSError, ValueError):
        return 0


def write_pid_file():
    '''
    Writes a file containing the PID of the current program instance.
    This file is used by the `is_running` and `get_instance_pid`
    functions to determine if an instance is running or to retrieve the
    PID.

    '''
    try:
        with open(_PID_FILE, 'w') as file:
            file.write(str(_PID))

    except OSError:
        pass


def unlink_pid_file():
    '''
    Deletes the PID file created by the `write_pid_file` function. This
    function must be called when the program stops.

    '''
    if is_running():
        _PID_FILE.unlink()
