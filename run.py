# Copyright 2014 Robological. All Rights Reserved.
#
# Licensed under the GNU General Public License, version 2 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.gnu.org/licenses/gpl-2.0.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import SocketServer
import RPi.GPIO as GPIO
import socket


Pi_Mode = 'Board'
GPIO.setmode(GPIO.BOARD)
app_id_address_list=[]
Robuddy_IpAdress=''
Robuddy_TcpPort=30002 ;

Pi_Non_GPIO_Pin_List = [0, 1, 2, 4, 6, 9, 14, 17, 20, 25]

command1='Pi_GPIO_00_OutputHigh'
command3='Pi_GPIO_MODE_BOARD'

def commandStringSplit(command_string):
    command_list = command_string.split('.')
    return command_list 

def setGpioOutput(pin_number, output_value):
    if (pin_number not in Pi_Non_GPIO_Pin_List) and pin_number<=30:
        GPIO.setup(pin_number, GPIO.OUT)
        GPIO.output(pin_number, output_value)
        
def sendKeyPressEvent():
    return
    

              
def gpioInputCallback(pin_number):
    print "Input from: %d" % pin_number
    print GPIO.input(pin_number)
    if GPIO.input(pin_number)==1:
        msgOut = 'pi.io.in.1.' + str(pin_number)
    else:
        msgOut = 'pi.io.in.0.' + str(pin_number)
    print msgOut
    sendToTcpServer(msgOut)
    
        
def setGpioInput(pin_number, pull_up_down, call_back_func, bounce_time):
    if (pin_number not in Pi_Non_GPIO_Pin_List) and pin_number<=30:
        setting = GPIO.gpio_function(pin_number)
        if setting==GPIO.IN:
            return    
        GPIO.setup(pin_number, GPIO.IN, pull_up_down)
        GPIO.add_event_detect(pin_number, GPIO.BOTH)
        #if pull_up_down==GPIO.PUD_UP: 
        #    GPIO.add_event_detect(pin_number, GPIO.FALLING)
        #elif pull_up_down==GPIO.PUD_DOWN:
        #    GPIO.add_event_detect(pin_number, GPIO.RISING)
        #if call_back_func in vars():
        GPIO.add_event_callback(pin_number, call_back_func, bounce_time)
     
    

        
def piGpioCommandCallback(handler):

    command_string_list = commandStringSplit(handler.data)
    
    if len(command_string_list)<4 or (not 'pi' in command_string_list):
        return
    
    if 'io' in command_string_list:
        pin_number = int(command_string_list[2])
        if 'out' in command_string_list and '1' in command_string_list:
            print pin_number
            setGpioOutput(pin_number, GPIO.HIGH)
            return handler.data
            
        elif 'out' in command_string_list and '0' in command_string_list:
            print pin_number
            setGpioOutput(pin_number, GPIO.LOW)
            return handler.data
            
        #elif 'in' in command_string_list:
            #setGpioInput(pin_number, GPIO.PUD_UP, gpioInputCallback, 10)
            #return handler.data
        #elif 'Input:PullDown' in command_string_list:
            #setGpioInput(pin_number, GPIO.PUD_DOWN, gpioInputCallback, 10)
        elif 'req' in command_string_list:
            setting = GPIO.gpio_function(pin_number)
            if setting==GPIO.IN:
                return (handler.data+'in')
            else:
                return (handler.data+'out')
        elif 'set' in command_string_list and 'In' in command_string_list:
            setGpioInput(pin_number, GPIO.PUD_UP, gpioInputCallback, 10)
            return handler.data	
        elif 'set' in command_string_list and 'Out' in command_string_list:
            GPIO.remove_event_detect(pin_number)
            GPIO.setup(pin_number, GPIO.OUT)
            return handler.data	
      
    return 'error'          
    

    
class MyTCPHandler(SocketServer.BaseRequestHandler):
    
    def handle(self):
        global Robuddy_IpAdress
        # self.request is the TCP socket connected to the client
        
        self.data = self.request.recv(1024).strip()
        print "{} wrote:".format(self.client_address[0])
        print "Rec Message: %s" %self.data
        Robuddy_IpAdress = self.client_address[0]
        print "Robuddy_IpAdress:%s" %Robuddy_IpAdress
        reply=piGpioCommandCallback(self)
        self.request.send(reply)
        print "Send message: %s" %reply



def sendToTcpServer(msgOut):

    if Robuddy_IpAdress=='':
        print "Can't send Input event"
        return
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #sock.settimeout(5.0)
    print Robuddy_IpAdress
    #for address in Robuddy_IpAdress:
    try:
        sock.connect((Robuddy_IpAdress, Robuddy_TcpPort))
        print ("connect to server: %s, port: %d" %(Robuddy_IpAdress, Robuddy_TcpPort))
        
    except socket.error:
        print "socket can't be open correctly"
        #continue
        return
        
    try:
        sock.sendall(msgOut)
        print "msg sent"
    except:
        print "can't send via tcp"
        return
        
    try:
        sock.close()
    except:
        pass


if __name__ == "__main__":

    HOST, PORT = "", 30001

    # Create the server, binding to localhost on port 30001
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you

    # interrupt the program with Ctrl-C
try:
    print "Server Starts Now"
    #GPIO.setup(7, GPIO.IN, GPIO.PUD_UP) 
    #GPIO.add_event_detect(7, GPIO.BOTH)
    #GPIO.add_event_callback(7, gpioInputCallback, 5)
    #setGpioInput(7, GPIO.PUD_UP, gpioInputCallback, 10)
    server.serve_forever()
except KeyboardInterrupt:
    print "Ctrl-C Stopped the Server"
    GPIO.cleanup()
    print "GPIO is cleaned"
    server.shutdown()
