import math
import tkinter as tk
from tkinter import filedialog, messagebox

def calculate_winding(inner_diameter, length, fiber_thickness, total_length, rpm, filename="winding_program.gcode"):
    """
    Generate G-code for regular/parallel winding pattern.
    
    Parameters:
    - inner_diameter: Diameter of the mandrel/bobbin (mm)
    - length: Length of the winding area (mm)
    - fiber_thickness: Thickness of the fiber (mm)
    - total_length: Total length of fiber to wind (mm)
    - rpm: Rotation speed of the mandrel (RPM) - used for feed rate calculation
    - filename: Output file name
    
    Returns:
    - G-code as a string
    """

    # 1 rotation = 4 mm

    length = length - fiber_thickness
    # Basic calculations
    mandrel_circumference = math.pi * inner_diameter
    
    
    # Calculate feed rate based on RPM for proper synchronization
    feed_rate = rpm * 60  # RPM to degrees per minute
    
    # Number of layers
    calc_layers = int(math.sqrt(total_length/(inner_diameter * math.pi + 2 * inner_diameter)))



    # G-code initialization
    gcode = [
        "G21 ; Set millimeters as units",
        "G90 ; Absolute positioning",
        f"F{feed_rate} ; Set feed rate based on RPM",
        "G0 X0 Y0 ; Initial position",
        "M8 ; Enable fiber feed",
        "G92 E0 ; Reset extrusion distance"
    ]
    
    # Current position tracking
    x_pos = 0
    y_pos = 0
    e_value = 0

    length_to_rotation_coef = 4
    
    # Generate winding pattern for complete layers
    for layer in range(calc_layers):
        if layer % 2 == 0:
            x_pos = fiber_thickness / 2
        else:
            x_pos = length + fiber_thickness / 2

        y_pos = layer * length / fiber_thickness * length_to_rotation_coef

        
            
        # Add movement command with synchronized rotation
        gcode.append(f"G1 X{x_pos:.2f} Y{y_pos:.2f} E{e_value:.2f}")

        if e_value * 1000 > total_length:
            break

        e_value += (inner_diameter + 2 * fiber_thickness * (layer - 1)) * math.pi * length / fiber_thickness / 1000
        
    
    # Finish G-code
    gcode.extend([
        "M9 ; Disable fiber feed",
        # "G0 X0 ; Return to zero position",
        "M30 ; End of program"
    ])
    
    gcode_output = "\n".join(gcode)
    
    # Write to file
    with open(filename, "w") as file:
        file.write(gcode_output)
        
    return gcode_output

def generate_gcode():
    try:
        inner_diameter = float(entry_inner_diameter.get())
        length = float(entry_length.get())
        # angle = float(entry_angle.get())
        fiber_thickness = float(entry_fiber_thickness.get())
        total_length = float(entry_total_length.get()) * 1000000  # Переводимо в мм
        rpm = int(entry_rpm.get())
        
        filename = filedialog.asksaveasfilename(defaultextension=".gcode", filetypes=[("G-code Files", "*.gcode"), ("All Files", "*.*")])
        if not filename:
            return
        
        gcode = calculate_winding(inner_diameter, length, fiber_thickness, total_length, rpm, filename)
        messagebox.showinfo("Готово", f"G-code збережено у {filename}")
    except ValueError:
        messagebox.showerror("Помилка", "Будь ласка, введіть коректні числові значення")

# Створення графічного інтерфейсу
root = tk.Tk()
root.title("Калькулятор намотки")

tk.Label(root, text="Внутрішній діаметр (мм):").grid(row=0, column=0)
tk.Label(root, text="Довжина шпулі (мм):").grid(row=1, column=0)
# tk.Label(root, text="Кут намотки (градуси):").grid(row=2, column=0)
tk.Label(root, text="Товщина волокна (мм):").grid(row=3, column=0)
tk.Label(root, text="Довжина волокна (км):").grid(row=4, column=0)
tk.Label(root, text="Швидкість (об/хв):").grid(row=5, column=0)

entry_inner_diameter = tk.Entry(root)
entry_length = tk.Entry(root)
# entry_angle = tk.Entry(root)
entry_fiber_thickness = tk.Entry(root)
entry_total_length = tk.Entry(root)
entry_rpm = tk.Entry(root)

entry_inner_diameter.insert(0, "40")
entry_length.insert(0, "100")
entry_fiber_thickness.insert(0, "0.25")
entry_total_length.insert(0, "10")
entry_rpm.insert(0, "1500")

entry_inner_diameter.grid(row=0, column=1)
entry_length.grid(row=1, column=1)
# entry_angle.grid(row=2, column=1)
entry_fiber_thickness.grid(row=3, column=1)
entry_total_length.grid(row=4, column=1)
entry_rpm.grid(row=5, column=1)

tk.Button(root, text="Згенерувати G-code", command=generate_gcode).grid(row=6, columnspan=2)

root.mainloop()