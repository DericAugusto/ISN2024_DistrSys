#!/usr/bin/env python
import queue
import threading
from time import sleep
import paho.mqtt.client as mqtt
from request import Request
import random
import json
class Lamport:
    TOPIC = 'LAMPORT'    # id of exchange common to all nodes (used as broadcast)
    MSG_REQUEST = 'REQUEST'    # Lamport request message prefix
    MSG_RELEASE = 'RELEASE'    # Lamport release message prefix
    MSG_PERMISSION = 'PERMISSION' # Lamport granted permission message prefix

    def __init__(self,network_size):
        self.network_size = network_size
        self.requests = queue.PriorityQueue() # thread-safe requests queue, automatically ordered by timestamps
        self.clock = 0 # logical clock used by Lamport Algorithm
        self.received_permissions = 0 # global counter: number of received permissions for the actual request
        self.node_id = '' # identifier of this node in the system
    def start_consumer(self):
        # start connection
        self.node_id="client-"+str(random.randint(1,100))
        print('Starting connection with id:'+self.node_id)
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1,self.node_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.process_received_messages
        self.client.connect("localhost", 1883, 60)
        thread_consumer = threading.Thread(target=self.client.loop_start)
        thread_consumer.daemon = True
        thread_consumer.start()
    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.client.subscribe(Lamport.TOPIC)
    # increment global variable clock
    def increment_clock(self):
        self.clock += 1
        print(f"[CLOCK] incremented clock to {self.clock}")
    # return True if, and only if, all the necessary permissions for the last request have been received
    def node_has_permissions(self):
        return self.received_permissions == (self.network_size-1)
    # put a request in node's request queue
    def requests_put(self,request):
        self.requests.put_nowait(request)
        print(f'[PUT] {request}')
        print(self.requests.queue)
    # get the first request from node's request queue
    def requests_get(self):
        req = self.requests.get()  # equivalent to get(False)
        print(f'[GET] {req}')
        print(self.requests.queue)
        return req
    # send a message where the body is msg_type;
    # if the message is_broadcast, the message is sent in broadcast and routing_key is ignored;
    # else, the message is sent individually and routing_key should be the receiver id;
    def send_msg(self,msg_type):
        payload = json.dumps({"type":msg_type,"clock":self.clock, "sender_id":self.node_id})
        self.client.publish(Lamport.TOPIC, payload=payload)
        print('[SEND] msg: %s, timestamp: %s, routing_key: %s' % (msg_type, self.clock, Lamport.TOPIC))
    # trigger a request according to the steps of Lamport algorithm
    def create_request(self):
        # increment timestamp before creating a request
        self.increment_clock()
        # push request to own queue
        request = Request(self.clock, self.node_id)
        self.requests_put(request)
        # broadcast request msg
        self.send_msg(Lamport.MSG_REQUEST)
    # callback for main channel basic_consume
    # decode and process a received message
    def process_received_messages(self,client,userdata,msg):
        # decode message attributes
        #sender_id, msg_type, msg_timestamp = props.reply_to, body.decode('UTF-8'), props.timestamp
        payload = json.loads(msg.payload)
        print(payload)
        msg_type = payload['type']
        msg_timestamp = payload['clock']
        sender_id = payload['sender_id']
        print("[RECEIVE] msg: %r, timestamp: %s, sender: %r" % (payload, msg_timestamp, sender_id))
        # ignore own broadcast messages
        if sender_id == self.node_id:
            return

        # recalculate clock, according to Lamport Algorithm
        self.clock = max(self.clock, msg_timestamp)
        self.increment_clock()
        # process messages differently according to their types
        if msg_type == Lamport.MSG_REQUEST:
            # put received request in requests queue
            self.requests_put(Request(msg_timestamp, sender_id))
            # send permission to the sender
            self.send_msg(Lamport.MSG_PERMISSION)
        elif msg_type == Lamport.MSG_PERMISSION:
            self.received_permissions += 1
            print('[PERMISSION]', self.received_permissions)
            # after receiving all permissions, stop waiting
            if self.node_has_permissions():
                print('All the permissions were received')
                # if the first request in the queue is from this node, process it
                # else, ignore it and keep waiting for a release
                req = self.requests_get()
                if req.owner_id == self.node_id:
                    self.enter_critical_section(req)
                else:
                    self.requests_put(req)
        elif msg_type == Lamport.MSG_RELEASE:
            # remove first element from queue, since it was released by its owner
            if not self.requests.empty():
                self.requests_get()
            if not self.requests.empty(): # we still have a request
                if self.node_has_permissions():
                    print('All the permissions were received')
                    # if the first request in the queue is from this node, process it
                    # else, ignore it and keep waiting for a release
                    req = self.requests_get()
                    if req.owner_id == self.node_id:
                        self.enter_critical_section(req)
                    else:
                        self.requests_put(req)
        # simulate a critical section usage;
        # it can be replaced by any function that really uses a critical section;
        # this function must only be called after receiving all permissions for a request;
        # the received_permissions global counter is reset to zero;
        # the thread enter in critical section and a release message is broadcast after finishing the usage of CS;
        # then, the following request is processed;
    def enter_critical_section(self,request):
        self.received_permissions = 0

        self.simulate_critical_section_usage(5)

        # warn other nodes that the use of CS is over
        self.send_msg(Lamport.MSG_RELEASE)
    def simulate_critical_section_usage(self,seconds):
        print('ENTER critical section for', seconds, 'seconds')
        for i in range(1, seconds+1):
            sleep(1)
            print('work done: ' + str(int(100*(i/seconds))) + '%')
        print('EXIT critical section')

# infinite looping to read keyboard inputs and process them as requests
def read_keyboard(l):
    print("Type requests to send: \t")
    while 1:
        try:
            user_input = input("")
            request_time = int(user_input)
            # send request and wait for responses
            l.create_request()
        except ValueError:
            print("Your request should be an integer")
            continue


if __name__ == '__main__':
    l = Lamport(2)
    l.start_consumer()
    # create thread to read user inputs
    thread_input = threading.Thread(target=read_keyboard,args=(l,))
    thread_input.start()
