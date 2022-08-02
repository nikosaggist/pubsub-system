# pubsub-system

The main purpose for the project was to implement a simple Pub/Sub system, similar to Apache Kafka and RabbitMQ. The
current implementation supports only 1 publisher and 1 subscriber and not multiple
publishers and subscribers. The code is organized in 4 modules, broker.py,
publisher.py, subscriber.py for the broker, the publisher and the subscriber respectively and
the last one is my_sock.py. Of course, there are detailed comments on each module describing the whole procedure.

APublisher/Subscriber system is a form of asynchronous service-to-service communication used in serverless and microservices architectures. In a pub/sub model, any message published to a topic is immediately received by all of the subscribers to the topic. Pub/sub messaging can be used to enable event-driven architectures, or to decouple applications in order to increase performance, reliability and scalability.
