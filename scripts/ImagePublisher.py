#!/usr/bin/python
import os
import rospy
from openhab_msgs.msg import ImageCommand
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import numpy as np
import base64
import io
import cv2
from imageio import imread
import matplotlib.pyplot as plt

class ImagePublisher(object):
    """Node example class."""

    def __init__(self, item_name):
        self.item_name = item_name
        self.pub = rospy.Publisher("/bytes/" + self.item_name, ImageCommand, queue_size=10)
        self.rate = rospy.Rate(10) # 10hz

        # Initialize message variables.
        self.enable = False
        self.message = None
        self.bridge = CvBridge()
        self.image = None

        if self.enable:
            self.start()
        else:
            self.stop()

    def start(self):
        """Turn on publisher."""
        self.enable = True
        self.pub = rospy.Publisher("/bytes/" + self.item_name, ImageCommand, queue_size=10)

        while not rospy.is_shutdown():
            self.message = ImageCommand()

            filename = "/home/ubuntu/testImageBytes"
            with open(filename, 'r') as file:
                data = file.read()

            data = eval(data)

            # reconstruct image as an numpy array
            img = imread(io.BytesIO(data))
            height, width, channels = img.shape

            rospy.loginfo("Got image with height %s, width %s and channels %s" % (height, width, channels))

            # finally convert RGB image to BGR for opencv
            cv2_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            try:
                self.image = self.bridge.cv2_to_imgmsg(cv2_img, 'bgr8')
            except CvBridgeError as e:
                print(e)

            self.message.command = self.image
            self.message.header.stamp = rospy.Time.now()
            self.message.header.frame_id = "/base_link"
            self.message.item = self.item_name

            message = "Publishing %s at %s" % (self.message.item, rospy.get_time())
            rospy.loginfo(message)

            self.pub.publish(self.message)
            self.rate.sleep()

    def stop(self):
        """Turn off publisher."""
        self.enable = False
        self.pub.unregister()

# Main function.
if __name__ == "__main__":
    # Initialize the node and name it.
    rospy.init_node("ImagePublisherNode", anonymous=True)
    # Go to class functions that do all the heavy lifting.

    imagePublisher = ImagePublisher("testImage")

    try:
        imagePublisher.start()
    except rospy.ROSInterruptException:
        pass
    # Allow ROS to go to all callbacks.
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()
