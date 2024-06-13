from rabbitmq_functions import *
import pipeline

REFRESH_DELAY = 2

def main():
    rabbit = RabbitMQHandler()

    while True:
        try:
            print("Waiting for messages...")
            
            last_req = None

            while last_req is None:
                last_req = rabbit.get_last_request(QUEUE_INPUT)
                sleep(REFRESH_DELAY)

            print("Message received: ", last_req)

            # Do something with the message
            response = pipeline.educhat(last_req['user_id'], last_req['message'])

            # Send the response
            rabbit.send_result(response, QUEUE_OUTPUT)
            print("Message sent: ", response)

        except Exception as e:
            print("RabbitMQ Error: ", str(e))
            rabbit.close()

if __name__ == "__main__":
    main()
