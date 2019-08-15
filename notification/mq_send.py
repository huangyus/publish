import pika


class RabbitMQ(object):
    def __init__(self, **kwargs):
        self.host = kwargs.get('host', None)
        self.port = kwargs.get('port', None)
        self.user = kwargs.get('user', None)
        self.passwd = kwargs.get('passwd', None)
        self.cluster = kwargs.get('cluster', None)
        if self.cluster:
            self.connection = pika.BlockingConnection()
        else:
            credentials = pika.PlainCredentials(self.user, self.passwd)
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host, port=self.port, virtual_host='/', credentials=credentials))

    def send_message(self, message):
        channel = self.connection.channel()
        channel.queue_declare(queue='Servers', durable=True)
        channel.basic_publish(exchange='', routing_key='Servers', body=message, properties=pika.BasicProperties(delivery_mode=2))
        self.connection.close()
