import math
import tkinter as tk
from tkinter import filedialog, messagebox

def calculate_winding(inner_diameter, length, edge_diameter, edge_max, fiber_thickness, total_length, rpm, filename="winding_program.gcode"):
    """
    Generate G-code for regular/parallel winding pattern.
    
    Parameters:
    - inner_diameter: Diameter of the mandrel/bobbin (mm)
    - length: Length of the first layer winding area (mm)
    - edge_diameter: Diameter of raunded edge with center in coil edge center (mm)
    - edge_max: Diameter of maximum edge hight (mm)
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
    
    rounded_edge_side_to_center_0 = rounded_edge_side_to_center_distance(inner_diameter=inner_diameter,
                                                                       edge_diametr=edge_diameter,
                                                                       max_diametr=edge_max,
                                                                       fiber_thickness=fiber_thickness,
                                                                       layers=0)
    
    # Generate winding pattern for complete layers
    for layer in range(calc_layers):
        edge_side_to_center_distance_i = rounded_edge_side_to_center_distance(inner_diameter=inner_diameter,
                                                                       edge_diametr=edge_diameter,
                                                                       max_diametr=edge_max,
                                                                       fiber_thickness=fiber_thickness,
                                                                       layers=layer)
        
        length_add_on = length + rounded_edge_side_to_center_0 - edge_side_to_center_distance_i

        if layer % 2 == 0:
            x_pos = fiber_thickness / 2
        else:
            x_pos = length_add_on + fiber_thickness / 2

        y_pos = layer * length_add_on / fiber_thickness * length_to_rotation_coef

        
            
        # Add movement command with synchronized rotation
        gcode.append(f"G1 X{x_pos:.2f} Y{y_pos:.2f} E{e_value:.2f}")

        if e_value * 1000 > total_length:
            break

        e_value += (inner_diameter + 2 * fiber_thickness * (layer - 1)) * math.pi * length_add_on / fiber_thickness / 1000
        
    
    # Finish G-code
    gcode.extend([
        "M30 ; End of program"
    ])
    
    gcode_output = "\n".join(gcode)
    
    # Write to file
    with open(filename, "w") as file:
        file.write(gcode_output)
        
    return gcode_output


def rounded_edge_side_to_center_distance(inner_diameter:float, edge_diametr:float, max_diametr:float, fiber_thickness:float, layers:int) -> float:
    D = inner_diameter + fiber_thickness * layers
    if D > max_diametr:
        raise Exception("Max diameter reached")
    distance = math.sqrt(math.pow(edge_diametr, 2) - math.pow(D, 2))
    return distance


def generate_gcode():
    try:
        inner_diameter = float(entry_inner_diameter.get())
        length = float(entry_length.get())
        edge_diameter = float(entry_edge_diameter.get())
        edge_max = float(entry_edge_max.get())
        fiber_thickness = float(entry_fiber_thickness.get())
        total_length = float(entry_total_length.get()) * 1000000  # Переводимо в мм
        rpm = int(entry_rpm.get())
        
        filename = filedialog.asksaveasfilename(defaultextension=".gcode", filetypes=[("G-code Files", "*.gcode"), ("All Files", "*.*")])
        if not filename:
            return
        
        gcode = calculate_winding(inner_diameter, length, edge_diameter, edge_max, fiber_thickness, total_length, rpm, filename)
        messagebox.showinfo("Готово", f"G-code збережено у {filename}")
    except ValueError:
        messagebox.showerror("Error", "Будь ласка, введіть коректні числові значення")
    except Exception as e:
        messagebox.showerror("Error", e)

# Створення графічного інтерфейсу
root = tk.Tk()
root.title("Калькулятор намотки")

r = 0
tk.Label(root, text="Внутрішній діаметр (мм):").grid(row=0, column=0)
tk.Label(root, text="Довжина шпулі (мм):").grid(row=1, column=0)
tk.Label(root, text="Діаметр зкругленного краю (мм):").grid(row=2, column=0)
tk.Label(root, text="Ефективна висота краю (мм):").grid(row=3, column=0)
tk.Label(root, text="Товщина волокна (мм):").grid(row=4, column=0)
tk.Label(root, text="Довжина волокна (км):").grid(row=5, column=0)
tk.Label(root, text="Швидкість (об/хв):").grid(row=6, column=0)

entry_inner_diameter = tk.Entry(root)
entry_length = tk.Entry(root)
entry_edge_diameter = tk.Entry(root)
entry_edge_max = tk.Entry(root)
entry_fiber_thickness = tk.Entry(root)
entry_total_length = tk.Entry(root)
entry_rpm = tk.Entry(root)

entry_inner_diameter.insert(0, "40")
entry_length.insert(0, "100")
entry_edge_diameter.insert(0, "170")
entry_edge_max.insert(0, "109")
entry_fiber_thickness.insert(0, "0.25")
entry_total_length.insert(0, "10")
entry_rpm.insert(0, "1500")

entry_inner_diameter.grid(row=0, column=1)
entry_length.grid(row=1, column=1)
entry_edge_diameter.grid(row=2, column=1)
entry_edge_max.grid(row=3, column=1)
entry_fiber_thickness.grid(row=4, column=1)
entry_total_length.grid(row=5, column=1)
entry_rpm.grid(row=6, column=1)

tk.Button(root, text="Згенерувати G-code", command=generate_gcode).grid(row=7, columnspan=2)

root.mainloop()