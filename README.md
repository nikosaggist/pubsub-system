# PubSub-system

The main purpose for the project was to implement a simple Pub/Sub system, similar to Apache Kafka and RabbitMQ. The
current implementation supports only 1 publisher and 1 subscriber and not multiple
publishers and subscribers. The code is organized in 4 modules, broker.py,
publisher.py, subscriber.py for the broker, the publisher and the subscriber respectively and
the last one is my_sock.py. Of course, there are detailed comments on each module describing the whole procedure.

A Publisher/Subscriber system is a form of asynchronous service-to-service communication used in serverless and microservices architectures. In a pub/sub model, any message published to a topic is immediately received by all of the subscribers to the topic. Pub/sub messaging can be used to enable event-driven architectures, or to decouple applications in order to increase performance, reliability and scalability.


![Screenshot from 2022-08-02 13-49-46](https://user-images.githubusercontent.com/84461356/182357430-96f672b6-c7a8-435f-a4a4-277dae5b03ba.png)

# User instructions

# Broker

$ python3 broker.py -s s_port -p p_port

For example: $ python3 broker.py -s 9090 -p 9000

positional arguments:

    -s               Indicates the port of this specific broker where subscribers will connect.
    -p               Indicates the port of this specific broker where publishers will connect.
    

# Publisher

$ python3 publisher.py -i ID -r sub_port -h broker_IP -p port [-f command_file]

For example: $ python3 publisher.py -i p1 -r 8200 -H localhost -p 9000 -f publisher1.cmd

positional arguments:

    -i               Indicates the id of this publisher.
    -r               Indicates the port of this specific publisher.
    -h               Indicates the IP address of the broker
    -p               Indicates the port of the broker.

optional arguments:

    -f               Indicates a file name where there are commands that the publisher will execute once started and connected 
    
# Subscriber

$ python3 subscriber.py -i ID -r sub_port -h broker_IP -p port [-f command_file]

For example: $ python3 subscriber.py -i s1 -r 8000 -H localhost -p 9090 -f subscriber1.cmd

positional arguments:

    -i               Indicates the id of this subscriber.
    -r               Indicates the port of this specific subscriber.
    -h               Indicates the IP address of the broker
    -p               Indicates the port of the broker.

optional arguments:

    -f               Indicates a file name where there are commands that the subscriber will execute once started and connected to the broker
