import obd
import tkinter as tk
import sys
from utils import MovingAverage
import math

moving_average_window_rpm = 5
moving_average_window_speed = 10

# What rpm is divided by before being displayed
rpm_display_factor = 10
rpm_low_threshold = 500
rpm_high_threshold = 3500

# Time between display refreshes (ms)
refresh_time = 1000//60

class connectionOBD:
    def __init__(self):
        self.connection=obd.OBD()
        if not self.connection.is_connected():
            raise ConnectionError("Connection to car was unsuccessful")
    
    def getEngineRPM(self):
        """
        Returns engine RPM
        """
        result = self.connection.query(obd.commands.RPM)
        try:
            return result.value.magnitude
        except AttributeError:
            return -1
    
    def getSpeed(self):
        """
        Returns speed in KMH
        """
        # TODO: Add Speed
        return 0

class connectionDummy:
    def __init__(self):
        self.rpm = 0
        self.speed = 100
        self.t = 0
    
    def getEngineRPM(self):
        """
        Returns engine RPM
        """
        self.t += 0.02
        self.rpm=2000+1700*math.cos(self.t)
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
        
        # Create Item Offsets
        self.si_offset_x = self.screen_width // 4
        self.si_offset_y = self.screen_height // 2
        
        # Initialize Values
        self.connection = connection
        self.moving_average_rpm = MovingAverage(moving_average_window_rpm)
        self.moving_average_speed = MovingAverage(moving_average_window_speed)
        
        # Draw HUD
        self.drawHUD()
        
        # Dynamic item list to remove on each refresh
        self.temporary_items = []
        
        # Update Values
        self.update_values()
        
    def drawHUD(self):
        # Draw RPM Indicator
        si_offset_x = self.si_offset_x
        si_offset_y = self.si_offset_y
        
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
                si_offset_x + 28, 
                si_offset_y - 250, 
                width=2, fill="Lime"
            )
        
        # Lower Bound
        self.canvas.create_line(
                si_offset_x - 50, 
                si_offset_y + 250, 
                si_offset_x + 28, 
                si_offset_y + 250, 
                width=2, fill="Lime"
            )
        
        # Main Indicator
        points = [
            si_offset_x-80, si_offset_y+30,
            si_offset_x-10, si_offset_y+30,
            si_offset_x-10, si_offset_y+6,
            si_offset_x, si_offset_y,
            si_offset_x-10, si_offset_y-6,
            si_offset_x-10, si_offset_y-30,
            si_offset_x-80, si_offset_y-30,
        ]
        self.rpm_pointer = self.canvas.create_polygon(points, outline = "Lime", fill = "Black", width = 2)
        
        # Draw RPM
        self.rpmItem = self.canvas.create_text(si_offset_x-16, si_offset_y+3, text="E", fill="Lime", font=("Helvetica", 27), anchor=tk.E, justify=tk.RIGHT)
        
    def update_rpm_indicators(self):
        si_offset_x = self.si_offset_x
        si_offset_y = self.si_offset_y
        
        rpm = round(self.moving_average_rpm.get_mean())
        
        # Clear temporary items
        for line in self.temporary_items:
            self.canvas.delete(line)
        
        self.temporary_items=[]
        
        for i in range(10):
            # if value is lower than 0 do not draw the lines
            number = (rpm//250-5+(10-i))*250//rpm_display_factor
            if number < 0:
                continue
            
            # Print markers
            posY = si_offset_y - 250 + i * 50 + (rpm//5) % 50
            line = self.canvas.create_line(
                si_offset_x, 
                posY,
                si_offset_x + 20, 
                posY, 
                width=2, fill="Lime"
            )
            self.temporary_items.append(line)
            
            # Print labels
            # display only every second label
            if number%(100//rpm_display_factor) != 0:
                continue
            label = self.canvas.create_text(
                si_offset_x-25, 
                posY, 
                text=str(number), 
                fill="Lime", 
                font=("Helvetica", 18),
                anchor=tk.CENTER, justify=tk.CENTER
            )
            
            self.temporary_items.append(label)
            
        # Print low rpm threshold
        lower_bound = rpm-1250        
        low_threshold_range = rpm_low_threshold-lower_bound
        low_threshold_start_y = si_offset_y + 250 - low_threshold_range//5
        if low_threshold_range>0:
            n_boxes = low_threshold_range//25//5
            for i in range(n_boxes):
                box_fill = "Lime" if i%2==0 else "Black"
                box = self.canvas.create_rectangle(
                    si_offset_x+20, 
                    low_threshold_start_y+i*25, #
                    si_offset_x+28, 
                    low_threshold_start_y+(i+1)*25, #
                    fill=box_fill,width=2,outline="Lime"
                )
                self.temporary_items.append(box)
            # Add last box with custom size
            box_fill = "Lime" if n_boxes%2==0 else "Black"
            box = self.canvas.create_rectangle(
                    si_offset_x+20, 
                    low_threshold_start_y+n_boxes*25,
                    si_offset_x+28, 
                    si_offset_y+250,
                    fill=box_fill,width=2,outline="Lime"
                )
            self.temporary_items.append(box)
        
        # Print high rpm threshold
        high_bound = rpm+1250        
        high_threshold_range = high_bound-rpm_high_threshold
        high_threshold_start_y = si_offset_y - 250 + high_threshold_range//5
        if high_threshold_range>0:
            n_boxes = high_threshold_range//25//5
            # Add First box with custom size
            box_fill = "Lime" if n_boxes%2==0 else "Black"
            box = self.canvas.create_rectangle(
                    si_offset_x+20, 
                    si_offset_y-250,
                    si_offset_x+28, 
                    high_threshold_start_y-n_boxes*25,
                    fill=box_fill,width=2,outline="Lime"
                )
            self.temporary_items.append(box)
            for i in range(n_boxes):
                box_fill = "Lime" if i%2==0 else "Black"
                box = self.canvas.create_rectangle(
                    si_offset_x+20, 
                    high_threshold_start_y-(i+1)*25, #
                    si_offset_x+28, 
                    high_threshold_start_y-i*25, #
                    fill=box_fill,width=1,outline="Lime"
                )
                self.temporary_items.append(box)
                
        # Print warning bar
        if high_threshold_range>-250:
            box = self.canvas.create_rectangle(
                    si_offset_x+20, 
                    high_threshold_start_y+50,
                    si_offset_x+24, 
                    high_threshold_start_y if high_threshold_start_y>si_offset_y-250 else si_offset_y-250,
                    fill="Black",width=2,outline="Lime"
                )
            self.temporary_items.append(box)
        
    def update_values(self):
        """
        Get current values from connection (Dummy or OBD)
        """
        self.moving_average_rpm.add_value(self.connection.getEngineRPM())
        self.moving_average_speed.add_value(self.connection.getSpeed())
        
        averaged_rpm_string = str(round(self.moving_average_rpm.get_mean())//rpm_display_factor)
        averaged_speed_string = str(round(self.moving_average_speed.get_mean()))
        
        self.update_rpm_indicators()
        self.canvas.tkraise(self.rpm_pointer)
        
        self.canvas.itemconfig(self.rpmItem, text=averaged_rpm_string)
        self.canvas.tkraise(self.rpmItem)
        
        self.root.after(refresh_time, self.update_values)
        
    def end_app(self, event):
        self.root.destroy()
        exit()

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