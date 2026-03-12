"""
Enhanced Movement Helper Module for MAYA
Provides utility functions for robot movement commands with improved error handling
"""

import requests
import logging
import time

# Configure logging
logger = logging.getLogger("MovementHelper")

class MovementHelper:
    def __init__(self, api_url="http://localhost:5001/command"):
        """Initialize the movement helper with API endpoint"""
        self.api_url = api_url
        self.last_command_time = 0
        self.command_cooldown = 0.5  # Minimum time between commands
        logger.info(f"Movement Helper initialized with API endpoint: {api_url}")
        
    def send_command(self, command):
        """
        Send movement command to robot API with rate limiting and error handling
        
        Args:
            command (str): Single letter command (F, B, L, R, S)
            
        Returns:
            bool: True if command was sent successfully, False otherwise
        """
        # Valid command check
        if command not in ['F', 'B', 'L', 'R', 'S']:
            logger.error(f"Invalid command: {command}")
            return False
        
        # Rate limiting to prevent command flooding
        current_time = time.time()
        if current_time - self.last_command_time < self.command_cooldown:
            logger.warning("Command rate limited")
            return False
            
        try:
            # Prepare payload
            payload = {
                "type": "instant",
                "command": command
            }
            
            # Send request to Flask API with timeout
            logger.info(f"Sending command: {command}")
            response = requests.post(
                self.api_url, 
                json=payload, 
                timeout=3  # 3 second timeout
            )
            
            # Update last command time
            self.last_command_time = current_time
            
            # Check response
            if response.status_code == 200:
                logger.info(f"Command sent successfully: {response.json()}")
                return True
            else:
                logger.error(f"Command failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("Robot API timeout - command may not have been executed")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to robot API - is the main controller running?")
            return False
        except Exception as e:
            logger.error(f"Error sending command: {str(e)}")
            return False
    
    def test_connection(self):
        """Test the connection to the robot API"""
        try:
            response = requests.get("http://localhost:5001/", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def move_forward(self):
        """Send forward command"""
        return self.send_command('F')
        
    def move_backward(self):
        """Send backward command"""
        return self.send_command('B')
        
    def turn_left(self):
        """Send left turn command"""
        return self.send_command('L')
        
    def turn_right(self):
        """Send right turn command"""
        return self.send_command('R')
        
    def stop(self):
        """Send stop command"""
        return self.send_command('S')
    
    def get_connection_status(self):
        """Get the current connection status"""
        return "Connected" if self.test_connection() else "Disconnected"