#!/usr/bin/python3

import threading
import argparse
import my_sock as msock
import sys
import time

#------- 
# Global settings
#-------

_host = "localhost"
_pub_port = None
_sub_port = None

_subs_per_topic = {}
_subs_conn_lock = threading.Lock()

#------- 
# Command line parsing
#-------

def parse_cmd_args ():
    """
    Sets and parses the arguments in the command line
    storing them in the respective global variables.
    """
    global _pub_port, _sub_port

    parser  = argparse.ArgumentParser()
    parser.add_argument('-p', type=int, metavar='XXXX', nargs=1, required=True,
                              dest='pub_port', 
                              help='Port where publishers will connect')
    parser.add_argument('-s', type=int, metavar='YYYY', nargs=1, required=True,
                              dest='sub_port', 
                              help='Port where subscribers will connect')
    
    d = parser.parse_args()

    _pub_port = d.pub_port[0]
    _sub_port = d.sub_port[0]
    print('Broker> got --> pub port %d, sub port %d' % (_pub_port, _sub_port))

#------- 
# Threads for handling publishers and subscribers
#-------

def pubthread():
    """
    Thread for handling publishers.
    Note:
    Currently supports one publisher.
    """
    pub_sock = msock.create_socket_server(_host, _pub_port)
    print("Broker> listening pubs on %s:%d" % (_host, _pub_port))
    
    conn, addr = pub_sock.accept()
    print("Broker> Pub connected: " + addr[0] + ":" + str(addr[1]))

    while True:
        smsg = msock.read_from_socket(conn)      # pub_id, cmd, tpc, msg
        if smsg is None:
            print("Broker> Pub disconnected, cannot read from pub")
            break
        print("Broker> Received from Pub <%s>" % smsg)    

        words = smsg.split(' ')
        pid, cmd, tpc, msg = words[0], words[1], words[2], ' '.join(words[3:])
        print("\t\tpubid: %s" % pid)
        print("\t\ttopic: %s" % tpc)
        print("\t\tmessage: %s" % msg)
        msock.send_ack(conn)
        
        if cmd != "pub":
            print("Broker> Invalid publisher command")
            continue

        with _subs_conn_lock:
            if tpc in _subs_per_topic:
                print("Broker> Sending message to all subscribers for the topic")
                for sid, sconn in _subs_per_topic[tpc]:
                    msock.write2socket(sconn, tpc + ' ' + msg)
                print("Broker> Message sent to all subscribers for the topic")

#------

def subthread():
    """
    Thread for handling subscribers.
    Note:
    Currently supports one subscriber.
    """
    global _subs_per_topic 
    
    sub_sock = msock.create_socket_server(_host, _sub_port)
    print("Broker> listening subs on %s:%d" % (_host, _sub_port))

    conn, addr = sub_sock.accept()
    print("Broker> Sub connected : " + addr[0] + ":" + str(addr[1]))

    while True:
        smsg = msock.read_from_socket(conn)      # subid, cmd, tpc OR _ack
        if smsg is None:
            print("Broker> Sub disconnected, cannot read from sub")
            break
        print("Broker> Received from sub <%s>" % smsg)  

        words = smsg.split(' ')
        if len(words) == 1:                     # _ack
            continue
        sid, cmd, tpc = words
        print("\t\tsubid: %s" % sid)
        print("\t\treceived command: %s" % cmd)
        print("\t\treceived topic: %s" % tpc)
        msock.send_ack(conn)

        if cmd != "sub" and cmd != "unsub":
            print("Broker> Invalid subscriber command")
            continue

        with _subs_conn_lock:                   
            subcs = _subs_per_topic.get(tpc)
            if subcs is None:                   # topic does not exist    
                if cmd == "sub":
                    print("Broker> New subscriber and topic")
                    _subs_per_topic[tpc] = [(sid, conn)]
                else:
                    print("Broker> Invalid unsubscription")
            else:                               # topic exists
                subs = [x[0] for x in subcs]    # already enlisted subscribers
                ndx  = None                     # index of connected subscriber, None if not enlisted
                if sid in subs:
                    ndx = subs.index(sid)
                if cmd == "sub" and ndx is None:
                    print("Broker> New subscriber for existing topic")
                    _subs_per_topic[tpc].append((sid, conn))  
                elif cmd == "sub" and ndx is not None:
                    print("Broker> Subscriber already subscribed") 
                elif cmd == "unsub" and ndx is None:
                    print("Broker> Invalid unsubscription, no previous subscription")
                else:
                    print("Broker> Unsubscription")
                    subcs.pop(ndx)

#------- 
# Running the broker
#-------

if __name__ == "__main__":
    parse_cmd_args()
    try:
        p_pub = threading.Thread(target=pubthread)
        p_pub.start()
        s_sub = threading.Thread(target=subthread)
        s_sub.start()
    except KeyboardInterrupt as msg:
        sys.exit(0)
    
    p_pub.join()
    s_sub.join()
    
    print("Broker> Bye")