#!/usr/bin/python3

import sys
import time 
import my_sock as msock
import argparse
import threading

#------- 
# Global settings
#-------

_sub_id   = None
_sub_port = None
_host     = "localhost"
_broker_port = None
_sub_file    = None

_sub_cmds = []                              # commands in the file
_sock = None                                # socket to broker

_num_smsgs = 0                              # for ensuring that messages to broker
_num_acks  = 0                              # are sent after acks of previous messages


#------- 
# Command line parsing
#-------

def parse_args ():
    global  _sub_id, _sub_port, _host, _broker_port, _sub_file
    
    parser  = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, metavar='ID', nargs=1, required=True,
                              dest='sub_id', 
                              help='Id of this subscriber')

    parser.add_argument('-r', type=int, metavar='XXXX', nargs=1, required=True,
                              dest='sub_port', 
                              help='Port of the subscriber')

    parser.add_argument('-H', type=str, metavar='broker_IP', nargs=1, required=True,
                              dest='broker_ip', 
                              help='IP address of the broker')

    parser.add_argument('-p', type=int, metavar='XXXX', nargs=1, required=True,
                              dest='broker_port', 
                              help='Port of the broker')
    
    parser.add_argument('-f', type=argparse.FileType('r'), metavar='file', nargs=1, 
                              dest='sub_file', 
                              help='Sub commands to execute')
    
    d = parser.parse_args()

    _sub_id      = d.sub_id[0]
    _sub_port    = d.sub_port[0]
    _host        = d.broker_ip[0]
    _broker_port = d.broker_port[0]
    _sub_file    = d.sub_file[0].name

#------

def get_file_cmds():
    
    """
    Reads a passed file containing the subscriber's commands and stores the
    commands in global variable "_sub_cmds":
        [(sleep, cmd, tpc), ..]
    """
    global _sub_cmds
    
    print("Subscriber> Passed file is %s" % _sub_file)

    if _sub_file is None:
        return

    with open(_sub_file, 'r') as f:
        cmds = [l.strip('\n') for l in f.readlines()]
    print("Subscriber> Read commands from file:\n %s" % cmds)
        
    _sub_cmds = [parse_command(s) for s in cmds]
    print("Subscriber> Stored file-commands:\n %s" % _sub_cmds)

#------

def parse_command (cmd):
    """
    Parses a command either read from a file or input from the keyboard.
    The command should be:
        sleep     --> int
        what      --> str 
        topic     --> str
            OR
        'quit'
    It also validates the above expected structure.
    
    Returns:
        - None                      invalid command
        - (slp, what, tpc)          valid   command, not 'quit'
        - (0, 'quit', '')           valid   command, if  'quit'
    """
    words  = cmd.split(' ')
    nwords = len(words)
    
    if nwords == 1:
        if words[0] != 'quit':
            print('Subscriber> Invalid command, expected (single) <quit>')
            return None
        
        return 0, 'quit', ''
    
    if nwords < 3:
        print('Subscriber> Invalid command, expected at least 3 words')
        return None
    
    if not words[0].isnumeric():
        print('Subscriber> Invalid command, first word (sleep time) should be int')
        return None
    
    return int(words[0]), words[1], ' '.join(words[2:])

#------- 
# Thread for reading from broker the published messages in the topics of interest
#-------

def readthread ():
    """
    Reads from established socket to the broker the messages from the publishers
    published for a topic where the subscriber has expressed interest.
    """
    global _num_acks 
    
    while True:
        smsg = msock.read_from_socket(_sock)      # tpc msg OR _ack
        if smsg is None:
            print("Subscriber> Disconnected from broker, cannot read from broker")
            break
        print("Subscriber> Received from broker <%s>" % smsg)    

        words = smsg.split(' ')
        if len(words) == 1:                     # _ack
            _num_acks += 1
            continue                            
        tpc, msg = words[0], ' '.join(words[1:])
        print("Subscriber> Received msg for topic %s: %s" % (tpc, msg))

#------
# Running the subscriber
#-------

def exec_file_cmds():
    """
    Executes the commands found in the passed file, if any.
    The commands in the file are stored in the global var "_sub_cmds":
        [(sleep, cmd, tpc), ..]
    """
    print("Subscriber> Ready to exec %d commands" % len(_sub_cmds))
    i = 0
    for cmd in _sub_cmds:
        
        i = i + 1
        print("Subscriber> Executing command #%d" % i)
        
        if cmd is None:
            print("\t\tSkipping invalid command")
            continue
        
        exec_cmd(cmd)
        
#------

def exec_cmd (cmd):
    """
    Executes a command from file or keyboard:
        sleep, what, tpc
    """
    global _num_smsgs
    slp, what, tpc = cmd
    
    while _num_acks < _num_smsgs:
        print("\t\tWaiting to receive ack of previous msgs sent to broker")
        time.sleep(1)
        
    print("\t\tSleeping for %d secs" % slp)
    time.sleep(slp)
    
    print("\t\tSubscribing to topic %s" % tpc)
    smsg = ' '.join((_sub_id, what, tpc))
    n = msock.write2socket(_sock, smsg)
    if n == -1:
        print("Subscriber> Cannot write to socket .. Quiting")   
        sys.exit(-2)
    
    _num_smsgs += 1
        
#------

def exec_keyboard_commands ():
    """
    Executes the commands entered from keyboard:
        sleep, cmd, tpc
            OR
        quit
    """
    while 1:
        cmd = input('Enter: sleeptime, what, topic OR quit to quit> ')
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
        print("Subscriber> Cannot connect to broker .. Quiting")
        sys.exit(-1)
    
    r_sub = threading.Thread(target=readthread)
    r_sub.start()
     
    exec_file_cmds()   
    exec_keyboard_commands()
    
    msock.term_socket(_sock)                    # readthread stops
    
    print("\nSubscriber> Bye")