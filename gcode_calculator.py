import math
import tkinter as tk
from tkinter import filedialog, messagebox

def calculate_winding(inner_diameter, length, angle, fiber_thickness, total_length, rpm, filename="winding_program.cnc"):
    inner_radius = inner_diameter / 2
    outer_radius = inner_radius  # Початкове значення, буде змінюватися
    tan_angle = math.tan(math.radians(angle))
    
    # Кількість витків
    turns = total_length / fiber_thickness
    
    # G-code
    gcode = [
        "G21 ; Встановлення мм як одиниць виміру",
        "G90 ; Абсолютне позиціонування",
        "M3 S{} ; Запуск шпулі".format(rpm),
        "F2000 ; Початкова швидкість розкладчика",
        "G0 X0 Y0 ; Початкова позиція",
        "M8 ; Увімкнути подачу волокна",
        "G92 E0 ; Обнулення довжини екструзії"
    ]
    
    y_pos = 0
    e_value = 0
    
    for i in range(int(turns)):
        circumference = 2 * math.pi * outer_radius
        step_y = circumference * tan_angle
        y_pos += step_y
        e_value += fiber_thickness
        
        if i % 2 == 0:
            gcode.append(f"G1 X{length} Y{y_pos:.2f} E{e_value:.2f}")
        else:
            gcode.append(f"G1 X0 Y{y_pos:.2f} E{e_value:.2f}")
        
        outer_radius += fiber_thickness / (2 * math.pi)
        
    gcode.extend([
        "M9 ; Вимкнути подачу волокна",
        "M5 ; Зупинка обертання шпулі",
        "G0 X0 Y0 ; Повернення в нульову точку",
        "M30 ; Кінець програми"
    ])
    
    gcode_output = "\n".join(gcode)
    
    with open(filename, "w") as file:
        file.write(gcode_output)
    
    return gcode_output

def generate_gcode():
    try:
        inner_diameter = float(entry_inner_diameter.get())
        length = float(entry_length.get())
        angle = float(entry_angle.get())
        fiber_thickness = float(entry_fiber_thickness.get())
        total_length = float(entry_total_length.get()) * 1000  # Переводимо в мм
        rpm = int(entry_rpm.get())
        
        filename = filedialog.asksaveasfilename(defaultextension=".cnc", filetypes=[("CNC Files", "*.cnc"), ("All Files", "*.*")])
        if not filename:
            return
        
        gcode = calculate_winding(inner_diameter, length, angle, fiber_thickness, total_length, rpm, filename)
        messagebox.showinfo("Готово", f"G-code збережено у {filename}")
    except ValueError:
        messagebox.showerror("Помилка", "Будь ласка, введіть коректні числові значення")

# Створення графічного інтерфейсу
root = tk.Tk()
root.title("Калькулятор намотки")

tk.Label(root, text="Внутрішній діаметр (мм):").grid(row=0, column=0)
tk.Label(root, text="Довжина шпулі (мм):").grid(row=1, column=0)
tk.Label(root, text="Кут намотки (градуси):").grid(row=2, column=0)
tk.Label(root, text="Товщина волокна (мм):").grid(row=3, column=0)
tk.Label(root, text="Довжина волокна (км):").grid(row=4, column=0)
tk.Label(root, text="Швидкість (об/хв):").grid(row=5, column=0)

entry_inner_diameter = tk.Entry(root)
entry_length = tk.Entry(root)
entry_angle = tk.Entry(root)
entry_fiber_thickness = tk.Entry(root)
entry_total_length = tk.Entry(root)
entry_rpm = tk.Entry(root)

entry_inner_diameter.grid(row=0, column=1)
entry_length.grid(row=1, column=1)
entry_angle.grid(row=2, column=1)
entry_fiber_thickness.grid(row=3, column=1)
entry_total_length.grid(row=4, column=1)
entry_rpm.grid(row=5, column=1)

tk.Button(root, text="Згенерувати G-code", command=generate_gcode).grid(row=6, columnspan=2)

root.mainloop()