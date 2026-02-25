import tkinter as tk
import serial
import time
import ctypes

# --- FIX BLURRY GRAPHICS ON WINDOWS ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1) # Forces HD rendering
except:
    pass

# --- HARDWARE CONFIGURATION ---
ARDUINO_PORT = 'COM3'  # <--- CHANGE THIS TOMORROW IN THE LAB!
BAUD_RATE = 9600

# --- CONNECT TO ARDUINO ---
try:
    arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=2)
    time.sleep(2) # Wait for Arduino to reboot
    hardware_status = f"[ HARDWARE LINKED: {ARDUINO_PORT} ]"
    status_color = "#00FF41" # Green
    is_connected = True
except Exception as e:
    arduino = None
    hardware_status = f"[ OFFLINE: NO HARDWARE ON {ARDUINO_PORT} ]"
    status_color = "#FF0000" # Red
    is_connected = False


def process_data():
    if not is_connected:
        log_box.config(state=tk.NORMAL)
        log_box.insert(tk.END, "[!] ERROR: Cannot encrypt. Hardware disconnected.\n")
        log_box.config(state=tk.DISABLED)
        return

    message = input_box.get(1.0, tk.END).strip()
    if not message:
        return

    # 1. Clear UI
    output_box.config(state=tk.NORMAL)
    output_box.delete(1.0, tk.END)
    visualizer_box.config(state=tk.NORMAL)
    visualizer_box.delete(1.0, tk.END)
    visualizer_box.insert(tk.END, ">>> ARDUINO HARDWARE MATH VISUALIZER <<<\n\n")

    # 2. SEND TO ARDUINO
    arduino.write((message + '\n').encode('utf-8'))
    time.sleep(0.1) # Wait for physical hardware to calculate

    # 3. READ FROM ARDUINO
    scrambled_word = arduino.readline().decode('utf-8', errors='ignore').strip()

    if not scrambled_word or len(scrambled_word) != len(message):
        visualizer_box.insert(tk.END, "ERROR: Data lost in hardware transmission.\n")
        return

    # 4. MATH TRICK: Deduce the hardware key the Arduino used! (Key = Plaintext XOR Ciphertext)
    actual_key = ord(message[0]) ^ ord(scrambled_word[0])
    
    # 5. VISUALIZE THE HARDWARE'S MATH
    for i in range(len(message)):
        char_val = ord(message[i])
        result_val = ord(scrambled_word[i])
        
        bin_char = format(char_val, '08b')
        bin_key = format(actual_key, '08b')
        bin_res = format(result_val, '08b')

        visualizer_box.insert(tk.END, f"Char '{message[i]}' : {bin_char}\n")
        visualizer_box.insert(tk.END, f"HW Key {actual_key} : {bin_key}\n")
        visualizer_box.insert(tk.END, f"XOR        : --------\n")
        visualizer_box.insert(tk.END, f"Result '{scrambled_word[i]}': {bin_res}\n\n")

    # 6. Update Output Box
    output_box.insert(tk.END, scrambled_word)
    output_box.config(state=tk.DISABLED)

    # 7. Update System Log
    log_box.config(state=tk.NORMAL)
    log_box.insert(tk.END, f"[SYSTEM] Processed {len(message)} bytes.\n")
    log_box.insert(tk.END, f" > In : {message}\n > Out: {scrambled_word}\n")
    log_box.see(tk.END)
    log_box.config(state=tk.DISABLED)
    visualizer_box.config(state=tk.DISABLED)


# --- RESPONSIVE LAYOUT ENGINE ---
current_layout = ""

def adjust_layout(event):
    global current_layout
    
    if str(event.widget) == str(root):
        width = event.width
        
        if width < 850 and current_layout != "vertical":
            frame_log.pack_forget()
            frame_vis.pack_forget()
            frame_input.pack_forget()
            
            frame_input.pack(side=tk.TOP, fill=tk.X, padx=15, pady=5)
            frame_vis.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=15, pady=5)
            frame_log.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=15, pady=5)
            current_layout = "vertical"
            
        elif width >= 850 and current_layout != "horizontal":
            frame_log.pack_forget()
            frame_vis.pack_forget()
            frame_input.pack_forget()
            
            frame_log.pack(side=tk.LEFT, fill=tk.Y, padx=(15, 5), pady=15)
            frame_vis.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=15)
            frame_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 15), pady=15)
            current_layout = "horizontal"

# --- MODERN GUI SETUP ---
root = tk.Tk()
root.title("CRYPTOSHIELD - Hardware Encryption")
root.geometry("1100x550") 
root.configure(bg="#0D0D0D") 

FONT_HEADER = ("Segoe UI", 12, "bold")
FONT_CODE = ("Consolas", 11)
COLOR_SURFACE = "#1A1A1A"
COLOR_ACCENT = "#00E5FF" 
COLOR_TEXT = "#E0E0E0"
COLOR_MATRIX = "#00FF41" 

# ==========================================
# 1. LEFT PANEL (System Log)
# ==========================================
frame_log = tk.Frame(root, bg=COLOR_SURFACE, bd=0)
tk.Label(frame_log, text="SYSTEM TERMINAL", font=FONT_HEADER, bg=COLOR_SURFACE, fg=COLOR_TEXT).pack(pady=(15,5))

# Add Hardware Status to the Log Panel
tk.Label(frame_log, text=hardware_status, font=("Consolas", 10, "bold"), bg=COLOR_SURFACE, fg=status_color).pack(pady=(0,10))

log_box = tk.Text(frame_log, font=FONT_CODE, bg="#050505", fg=COLOR_TEXT, bd=0, state=tk.DISABLED, width=30)
log_box.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

# ==========================================
# 2. CENTER PANEL (Visualizer)
# ==========================================
frame_vis = tk.Frame(root, bg=COLOR_SURFACE, bd=0)
tk.Label(frame_vis, text="XOR BINARY PROCESSOR", font=FONT_HEADER, bg=COLOR_SURFACE, fg="#FFAA00").pack(pady=(15,5))
visualizer_box = tk.Text(frame_vis, font=FONT_CODE, bg="#000000", fg="#FFAA00", bd=0, state=tk.DISABLED)
visualizer_box.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

# ==========================================
# 3. RIGHT PANEL (Data Entry)
# ==========================================
frame_input = tk.Frame(root, bg=COLOR_SURFACE, bd=0)
tk.Label(frame_input, text="1. DATA ENTRY", font=FONT_HEADER, bg=COLOR_SURFACE, fg=COLOR_ACCENT).pack(anchor="w", pady=(15,5), padx=10)
input_box = tk.Text(frame_input, height=4, width=30, font=FONT_CODE, bg="#262626", fg="white", bd=0, insertbackground="white")
input_box.pack(padx=10, pady=5, fill=tk.X)

action_btn = tk.Button(frame_input, text="ENCRYPT / DECRYPT", font=("Segoe UI", 12, "bold"), 
                       bg=COLOR_ACCENT, fg="black", activebackground="#00B3CC", bd=0, cursor="hand2", command=process_data)
action_btn.pack(pady=15, fill=tk.X, padx=10, ipady=5)

tk.Label(frame_input, text="2. SECURE OUTPUT", font=FONT_HEADER, bg=COLOR_SURFACE, fg=COLOR_ACCENT).pack(anchor="w", pady=(5,5), padx=10)
output_box = tk.Text(frame_input, height=4, width=30, font=FONT_CODE, bg="#262626", fg=COLOR_MATRIX, bd=0, state=tk.DISABLED)
output_box.pack(padx=10, pady=(5, 15), fill=tk.X)

root.bind("<Configure>", adjust_layout)
root.mainloop()