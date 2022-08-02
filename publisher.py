#!/usr/bin/python3

import sys
import my_sock as msock
import argparse 
import time 

#------- 
# Global settings
#-------

_pub_id = None
_pub_port = None
_host = "localhost"
_broker_port = None
_pub_file    = None

_pub_cmds = []                                  # commands in the file
_sock = None                                    # socket to broker

#------- 
# Command line arguments parsing
#-------

def parse_args ():
    """
    Sets and parses the arguments in the command line
    storing them in the respective global variables.
    """
    
    global  _pub_id, _pub_port, _host, _broker_port, _pub_file

    parser  = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, metavar='ID', nargs=1, required=True,
                              dest='pub_id', 
                              help='Id of this publisher')

    parser.add_argument('-r', type=int, metavar='XXXX', nargs=1, required=True,
                              dest='pub_port', 
                              help='Port of the publisher')

    parser.add_argument('-H', type=str, metavar='broker_IP', nargs=1, required=True,
                              dest='broker_ip', 
                              help='IP address of the broker')

    parser.add_argument('-p', type=int, metavar='XXXX', nargs=1, required=True,
                              dest='broker_port', 
                              help='Port of the broker')
    
    parser.add_argument('-f', type=argparse.FileType('r'), metavar='file', nargs=1, 
                              dest='pub_file', 
                              help='Pub commands to execute')
    
    d = parser.parse_args()
   
    _pub_id = d.pub_id[0]
    _pub_port = d.pub_port[0]
    _broker_port = d.broker_port[0]
    _pub_file    = d.pub_file[0].name if d.pub_file is not None else None

#-------

def get_file_cmds():
    
    """
    Reads a passed file containing the publisher's commands and stores the
    commands in global variable "_pub_cmds":
        [(sleep, cmd, tpc, msg), ..]
    """
    global _pub_cmds
    
    print("Publisher> Passed file is %s" % _pub_file)
    
    if _pub_file is None:
        return
    
    with open(_pub_file, 'r') as f:
        cmds = [l.strip('\n') for l in f.readlines()]
    print("Publisher> Read commands from file:\n %s" % cmds)
    
    _pub_cmds = [parse_command(s) for s in cmds]
    print("Publisher> Stored file-commands:\n %s" % _pub_cmds)

#------

def parse_command (cmd):
    """
    Parses a command either read from a file or input from the keyboard.
    The command should be:
        sleep     --> int
        what      --> str 
        topic     --> str
        msg_words --> str
            OR
        'quit'
    It also validates the above expected structure.
    
    Returns:
        - None                      invalid command
        - (slp, what, tpc, msg)     valid   command, not 'quit'
        - (0, 'quit', '',  '')      valid   command, if  'quit'
    """
    words  = cmd.split(' ')
    nwords = len(words)
    
    if nwords == 1:
        if words[0] != 'quit':
            print('Publisher> Invalid command, expected (single) <quit>')
            return None
        
        return 0, 'quit', '',  ''
    
    if nwords < 4:
        print('Publisher> Invalid command, expected at least 4 words')
        return None
    
    if not words[0].isnumeric():
        print('Publisher> Invalid command, first word (sleep time) should be int')
        return None
    
    return int(words[0]), words[1], words[2], ' '.join(words[3:])

#------
# Running the publisher
#-------

def exec_file_cmds():
    """
    Executes the commands found in the passed file, if any.
    The commands in the file are stored in the global var "_pub_cmds":
        [(sleep, cmd, tpc, msg), ..]
    """
    print("Publisher> Ready to exec %d commands" % len(_pub_cmds))
    i = 0
    for cmd in _pub_cmds:
        
        i = i + 1
        print("Publisher> Executing command #%d" % i)
        
        if cmd is None:
            print("\t\tSkipping invalid command")
            continue
        
        exec_cmd(cmd)
        
#------

def exec_cmd (cmd):
    """
    Executes a command from file or keyboard:
        sleep, what, tpc, msg
    """
    slp, what, tpc, msg = cmd
    
    print("\t\tSleeping for %d secs" % slp)
    time.sleep(slp)
    
    print("\t\tWriting to topic %s, msg=<%s>" % (tpc, msg))
    smsg = ' '.join((_pub_id, what, tpc, msg))
    n = msock.write2socket(_sock, smsg)
    if n == -1:
        print("Publisher> Cannot write to socket .. Quiting")   
        sys.exit(-2)
    
    smsg = msock.read_from_socket(_sock)      # _ack
    print("Publisher> Received from broker <%s>" % smsg)    
    if smsg != msock._ack:
        print("Publisher> Invalid ack")
        sys.exit(-2)
        
    print("Publisher> Published msg for topic %s: %s" % (tpc, msg))

#------

def exec_keyboard_commands ():
    """
    Executes the commands entered from keyboard:
        sleep, cmd, tpc, msg
            OR
        quit
    """
    while 1:
        cmd = input('Enter: sleeptime, what, topic, msg OR quit to quit> ')
        res = parse_command(cmd)
        
        if res is None:
            print('Invalid command, try again\n')
            continue
        
        if res[1] == 'quit':
            break
        
        exec_cmd(res)
        
#------

if __name__ == "__main__":
    
    parse_args()
    get_file_cmds()
    
    _sock = msock.connect2socket(_host, _broker_port)
    if _sock is None:
        print("Publisher> Cannot connect to broker .. Quiting")
        sys.exit(-1)
    
    exec_file_cmds()
    exec_keyboard_commands()
    
    msock.term_socket(_sock)
    
    print("\nPublisher> Bye")