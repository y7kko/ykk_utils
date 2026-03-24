# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 09:58:43 2022

Module to control the scanner during sequential impulse response measurements

@author: ericb
"""

# general imports
import os
import time

# Arduino imports
from telemetrix import telemetrix


#pathh = 'D:/dropbox/Dropbox/2022/meas_29_06/'
# cwd = os.path.dirname(__file__) # Pega a pasta de trabalho atual
# os.chdir(cwd)
#import SSRfunctions as SSR

class RobotClass():
    def __init__(self,
            x_pwm_pin = 2, x_digital_pin = 24,
            y_pwm_pin = 3, y_digital_pin = 26,
            z_pwm_pin = 5, z_digital_pin = 28,
            dht_pin = 40, pausing_time_array = [8, 8, 8],
            ):
        """

        Parameters
        ----------
        x_pwm_pin : int
            pin number of PWM on x-axis
        x_digital_pin : int
            pin number of digital signal on x-axis
        y_pwm_pin : int
            pin number of PWM on y-axis
        y_digital_pin : int
            pin number of digital signal on y-axis
        z_pwm_pin : int
            pin number of PWM on z-axis
        z_digital_pin : int
            pin number of digital signal on z-axis
        dht_pin : int
            pin number of dht reading
        pausing_time_array : numpy 1dArray
            1x3 array with the x, y, z pausing times to stablize movement
        """
        
        self.micro_steps = 1600
        
        # arduino main parameters
        self.arduino_params = {'step_pins': [[x_pwm_pin, x_digital_pin],  # x axis
                                [y_pwm_pin, y_digital_pin],  # y axis
                                [z_pwm_pin, z_digital_pin]], # z axis
                               'dht_pin': dht_pin}
        
        self.pausing_time_array = pausing_time_array
        self.exit_flag = 0
        self.u_t = []
        # Felipe e João added
        self.initError = 0
        
    
    def set_arduino_parameters(self,):
        """ set arduino parameters
        
        """        
        self.exit_flag = 0
        self.u_t = []
        # humidity in air - current and list filled at each meas
        self.humidity_list = []
        self.humidity_current = None
        # temperature - current and list filled at each meas
        self.temperature_current = None
        self.temperature_list = []        
        # ARDUINO BOARD COMMUNICATION
        self.board = telemetrix.Telemetrix()
        
    def set_motors(self, ):
        """ Set the ARDUINO board and motors
        
        """
        print('Pre-setting the motors and arduino controller.')
        
        
        try:
            self.board = telemetrix.Telemetrix(com_port=os.environ['SCANNER_MEAS_COMPORT'])
        except: # Primeira conexão com arduino
            self.board = telemetrix.Telemetrix()
            os.environ['SCANNER_MEAS_COMPORT'] = self.board.serial_port.portstr

        
        # Motors:
        self.motor_x = self.board.set_pin_mode_stepper(interface=1, 
            pin1 = self.arduino_params['step_pins'][0][0], 
            pin2 = self.arduino_params['step_pins'][0][1], 
            enable = False)
        self.motor_y = self.board.set_pin_mode_stepper(interface=1, 
            pin1 = self.arduino_params['step_pins'][1][0], 
            pin2 = self.arduino_params['step_pins'][1][1], enable=False)
        self.motor_z = self.board.set_pin_mode_stepper(interface=1, 
            pin1 = self.arduino_params['step_pins'][2][0], 
            pin2 = self.arduino_params['step_pins'][2][1], enable=False)
        
        # Temperature and humidity
        # self.set_dht_sensor()
        # Motor dictionaries
        self.motor_dict = {'x' : self.motor_x, 'y' : self.motor_y,
                           'z' : self.motor_z}
        self.motor_pause_dict = {'x' : self.pausing_time_array[0], 
             'y' : self.pausing_time_array[1], 
             'z' : self.pausing_time_array[2]}
        
        # print("We are moving y motor to make sure everything is working.")
        # self.move_motor(self, motor_to_move = 'y', dist = -0.001)
        # self.move_motor(self, motor_to_move = 'y', dist = 0.001)
        
        # Alteração Felipe e João
        print("Setting up motors... Moving y-axis +1mm and -1mm")
        self.move_motor(motor_to_move = 'y', dist = -0.001)
        self.move_motor(motor_to_move = 'y', dist = 0.001)
        print("Setup complete! y-axis moved correctly")

    def set_dht_sensor(self,):
        """ Set sensor to measure humifdity and temperature
        """
        self.board.set_pin_mode_dht(pin = self.arduino_params['dht_pin'], 
            callback = self.the_callback_dht, dht_type=11)

    def the_callback_dht(self, data):
        """Callback function to measure the current humidity and temperature
        
        It keeps being called every some seconds. We need a better way to
        call it on demand.
        """
        # print(data[1])
        if data[1]:
            print(f'DHT Error Report: Pin: {data[2]}, CHECK CONNECTION!')
        else:
            self.humidity_current = data[4]
            self.temperature_current = data[5]
    
    def the_callback_dht2(self, data):
        """Callback function to measure the current humidity and temperature
        
        It keeps being called every some seconds. We need a better way to
        call it on demand. Original function.
        """
        #global u_t
        if self.u_t != []:
            self.u_t = []
        else:
            pass
        if data[1]:
            print(f'dht error report: pin: {data[2]}, check connection!')
        else:
            self.u_t.append(data[4])
            self.u_t.append(data[5])

    def stepper_run_base(self, motor, steps_to_send):
        """ Base method to move a motor
        
        Parameters
        ----------
        motor : int
            The motor to be moved
        steps_to_send : int
            The number of steps to move the motor
        """ 
        self.board.stepper_set_current_position(0, 0)
        self.board.stepper_set_max_speed(motor, 400)
        self.board.stepper_set_acceleration(motor, 50)
        self.board.stepper_move(motor, steps_to_send)
        self.board.stepper_run(motor, completion_callback = self.completion_callback)
        self.pause(pausing_time = 0.2)
        self.board.stepper_is_running(motor, callback = self.running_callback)
        self.pause(pausing_time = 0.2)
        while self.exit_flag == 0:
            self.pause(pausing_time = 0.2)
         
    def stepper_run(self, motor, dist = 0.01,bypass_correction=False):
        """ Move the motor
        
        If the distance is larger than 16 [cm], then the movement is executed
        in two steps to avoid bad behaviour
        
        Parameters
        ----------
        motor : int
            The motor to be moved
        dist : float
            Distance in [m] to move the motor
        """
        pre_steps_to_send = dist * self.micro_steps / 0.008
        if bypass_correction:
            steps_to_send = int(pre_steps_to_send)
            print(f'Mandando esses steps {steps_to_send}')
            self.exit_flag = 0
            self.stepper_run_base(motor, steps_to_send)
            return


        if abs(dist) <= 0.16:
            steps_to_send = int(pre_steps_to_send)
            print(f'Mandando esses steps {steps_to_send}')
            self.exit_flag = 0
            self.stepper_run_base(motor, steps_to_send)
        elif abs(dist) > 0.16 and abs(dist) < 0.32:
            steps_to_send = int(pre_steps_to_send/2)
            print(f'Mandando esses steps {steps_to_send} em 2x')
            self.exit_flag = 0
            self.stepper_run_base(motor, steps_to_send)            
            self.exit_flag = 0
            self.stepper_run_base(motor, steps_to_send)
        elif abs(dist) >= 0.32 and abs(dist) < 0.64:
            steps_to_send = int(pre_steps_to_send/4)
            print(f'Mandando esses steps {steps_to_send} em 4x')
            self.exit_flag = 0
            self.stepper_run_base(motor, steps_to_send)            
            self.exit_flag = 0
            self.stepper_run_base(motor, steps_to_send)
            self.exit_flag = 0
            self.stepper_run_base(motor, steps_to_send)
            self.exit_flag = 0
            self.stepper_run_base(motor, steps_to_send)
        else:
            steps_to_send = int(pre_steps_to_send/6)
            print(f'Mandando esses steps {steps_to_send} em 6x')
            for run in range(6):
                self.exit_flag = 0
                self.stepper_run_base(motor, steps_to_send)            



    
    def running_callback(self, data):
        """Callback function to inform if the motor is moving or not
        """
        if data[1]:
            print('The motor is running.')
        else:
            print('The motor IS NOT running.')            
    
    def completion_callback(self, data):
        """Callback function to inform that the movement is complete
        
        Informs that the movement of a certain motor is complete and changes
        the value of the exit_flag variable in the class
        """
        # global exit_flag
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[2]))
        print(f'Motor {data[1]} absolute motion completed at: {date}.')
        self.exit_flag += 1
        
    def pause(self, pausing_time = 0.2):
        """ Pause for a few seconds
        
        Used to stabilize the measurement system.
        
        Parameters
        ----------
        time : float
            time to pause
        """
        time.sleep(pausing_time)
    
    def move_motor(self, motor_to_move = 'x', dist = 0.01,bypass_correction=False):
        """ Move motor x, y or z
        
        Parameters
        ----------
        motor : float
            can be either 'x', 'y' or 'z' - specifying the motor to be moved
        dist : float
            distance along x-axis in [m]
        micro_steps : int
            number of micro steps
        """
        self.stepper_run(self.motor_dict[motor_to_move], dist = -dist,bypass_correction=bypass_correction)
        self.pause(pausing_time = self.motor_pause_dict[motor_to_move])
        
    def move_motor_xyz(self, distance_vector):
        """ Move three motors sequentially
        
        Parameters
        ----------
        distance_vector : numpy 1dArray
            vector containing the x, y, z distances to displace each motor        
        """
        keys = list(self.motor_dict.keys())
        for axis in range(3):
            if distance_vector[axis] != 0:
                self.move_motor(motor_to_move = keys[axis],
                                dist = distance_vector[axis])
                
    def shutdown_motors(self,):
        if not self.board.shutdown_flag:
            try:
                self.board.shutdown()
            except:
                Warning('RobotClass: Shutdown() Failed')
        else:
            Warning('RobotClass: Motors are already off')

            