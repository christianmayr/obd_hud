import obd
import tkinter as tk
import sys

class connectionOBD:
    def __init__(self):
        self.connection=obd.OBD()
        if not self.connection.is_connected():
            raise ConnectionError("Connection to car was unsuccessful")
    
    def getEngineRPM(self):
        """
        Returns engine RPM
        """
        return self.connection.query(obd.commands.RPM).value
    
    def getSpeed(self):
        """
        Returns speed in KMH
        """
        response = self.connection.query(obd.commands.RPM)
        return response

class connectionDummy:
    def __init__(self):
        self.rpm = 1000
        self.speed = 100
    
    def getEngineRPM(self):
        """
        Returns engine RPM
        """
        self.rpm+=1
        return self.rpm
    
    def getSpeed(self):
        """
        Returns speed in KMH
        """
        self.speed+=1
        return self.speed

class HeadUpDisplayApp:
    def __init__(self, root, connection):
        # Initialize Screen
        self.root = root
        self.root.title("HUD")
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", self.end_app)
        
        # Create canvas
        self.screen_width = 1920
        self.screen_height = 1080
        self.canvas = tk.Canvas(self.root, width=self.screen_width, height=self.screen_height, bg="Black")
        self.canvas.pack()
        
        # Initialize Values
        self.connection = connection
        self.rpm_reading = connection.getEngineRPM()
        self.speed_reading = connection.getSpeed()
        
        # Draw HUD
        self.drawHUD()
        
        # Update Values
        self.update_values()
        
    def drawHUD(self):
        # Draw RPM Indicator
        si_offset_x = self.screen_width // 4
        si_offset_y = self.screen_height // 2
        
        # Main Line
        self.canvas.create_line(
                si_offset_x + 20, 
                si_offset_y - 250, 
                si_offset_x + 20, 
                si_offset_y + 250, 
                width=2, fill="Lime"
            )
        
        # Upper Bound
        self.canvas.create_line(
                si_offset_x - 50, 
                si_offset_y - 250, 
                si_offset_x + 25, 
                si_offset_y - 250, 
                width=2, fill="Lime"
            )
        
        # Lower Bound
        self.canvas.create_line(
                si_offset_x - 50, 
                si_offset_y + 250, 
                si_offset_x + 25, 
                si_offset_y + 250, 
                width=2, fill="Lime"
            )
        
        # Main Indicator
        points = [
            si_offset_x-80, si_offset_y+25,
            si_offset_x-10, si_offset_y+25,
            si_offset_x-10, si_offset_y+10,
            si_offset_x, si_offset_y,
            si_offset_x-10, si_offset_y-10,
            si_offset_x-10, si_offset_y-25,
            si_offset_x-80, si_offset_y-25,
        ]
        self.canvas.create_polygon(points, outline = "Lime", width = 2)
        
        # Draw RPM
        self.rpmItem = self.canvas.create_text(si_offset_x-45, si_offset_y, text="E", fill="Lime", font=("Helvetica", 16, "bold"))
        
        
    def update_values(self):
        """
        Get current values from connection (Dummy or OBD)
        """
        self.rpm_reading = self.connection.getEngineRPM()
        self.speed_reading = self.connection.getSpeed()
        self.canvas.itemconfig(self.rpmItem, text=str(self.rpm_reading))
        self.root.after(20, self.update_values)
        
    def end_app(self, event):
        self.root.destroy()

def main():
    root = tk.Tk()
    
    # Run application in dummy-mode
    if "-d" in sys.argv:
        app = HeadUpDisplayApp(root, connectionDummy())
        root.mainloop()
        
    app = HeadUpDisplayApp(root, connectionOBD())
    root.mainloop()
    
if __name__ == "__main__":
    main()