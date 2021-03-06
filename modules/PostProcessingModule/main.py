# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import os
import random
import time
import sys
from azure.iot.device import IoTHubModuleClient
from azure.iot.device import IoTHubMessageDispositionResult, IoTHubError

# pylint: disable=E0611

# messageTimeout - the maximum time in milliseconds until a message times out.
# The timeout period starts at IoTHubModuleClient.send_event_async.
# By default, messages do not expire.
MESSAGE_TIMEOUT = 10000

# Set the CONNECTION_STRING from Azure Portal
IOTHUB_CONNECTION_STRING = os.getenv('IOTHUB_CONNECTION_STRING')
print("IOTHUB_CONNECTION_STRING", IOTHUB_CONNECTION_STRING)
if not IOTHUB_CONNECTION_STRING:
    raise Exception("You have to set ENV variable for iothub connection string. See main.py of inference module.")

def send_confirmation_callback(message, result, user_context):
    """
    Callback received when the message that we're forwarding is processed.
    """
    print ( "Confirmation[%d] received for message with result = %s" % (user_context, result) )


def receive_message_callback(message, hub_manager):
    """
    receive_message_callback is invoked when an incoming message arrives on the specified 
    input queue (in the case of this sample, "postprocessinginput").
    """
    hub_manager.forward_event_to_output("postprocessingoutput", message, 0)
    return IoTHubMessageDispositionResult.ACCEPTED


class HubManager(object):

    def __init__(self):
        self.client = IoTHubDeviceClient.create_from_connection_string(IOTHUB_CONNECTION_STRING)

        # set the time until a message times out
        self.client.set_option("messageTimeout", MESSAGE_TIMEOUT)

        self.connect()

    async def connect(self):
        await self.client.connect()

        # sets the callback when a message arrives on "postprocessinginput" queue.  Messages sent to 
        # other inputs or to the default will be silently discarded.
        self.client.set_message_callback("postprocessinginput", receive_message_callback, self)

    # Forwards the message received onto the next stage in the process.
    def forward_event_to_output(self, outputQueueName, event, send_context):
        self.client.send_event_async(
            outputQueueName, event, send_confirmation_callback, send_context)

def main():
    print("Module for post processing. Currently just runs a callback function to send to iothub, but feel free to add your own processing.")
    try:
        hub_manager = HubManager()
        while True:
            time.sleep(1)

    except IoTHubError as iothub_error:
        print ( "Unexpected error %s from IoTHub" % iothub_error )
        return
    except KeyboardInterrupt:
        print ( "IoTHubModuleClient sample stopped" )

if __name__ == '__main__':
    main()
