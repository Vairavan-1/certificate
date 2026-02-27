import tkinter as tk
import serial
import serial.tools.list_ports
import time
import ctypes

# --- FIX BLURRY GRAPHICS ON WINDOWS ---
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# ==========================================
# --- BOOT SEQUENCE: COM PORT RADAR ---
# ==========================================
print("\n" + "="*40)
print("🔍 SCANNING FOR HARDWARE...")
ports = serial.tools.list_ports.comports()
if not ports:
    print("❌ NO USB DEVICES FOUND. PLUG IN ARDUINO!")
else:
    print("✅ PLUGGED IN DEVICES:")
    for port, desc, hwid in sorted(ports):
        print(f" -> {port} : {desc}")
print("="*40 + "\n")

# --- HARDWARE CONFIGURATION ---
ARDUINO_PORT = 'COM8'  # <--- Change this tomorrow if needed!
BAUD_RATE = 9600

# --- CONNECT TO ARDUINO ---
try:
    arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=0.1)
    time.sleep(2) 
    arduino.reset_input_buffer() 
    hardware_status = f"[ HARDWARE LINKED: {ARDUINO_PORT} ]"
    status_color = "#00FF41" # Neon Green
    is_connected = True
except Exception as e:
    arduino = None
    hardware_status = f"[ OFFLINE: NO HARDWARE ON {ARDUINO_PORT} ]"
    status_color = "#FF0000" # Red
    is_connected = False

# --- MODERN GUI SETUP ---
root = tk.Tk()
root.title("MATH EXPO: PRO DIGITAL TWIN")
root.geometry("1100x650") 
root.configure(bg="#0D0D0D") 

FONT_HEADER = ("Segoe UI", 12, "bold")
FONT_CODE = ("Consolas", 11)
COLOR_SURFACE = "#1A1A1A"
COLOR_ACCENT = "#00E5FF" 
COLOR_TEXT = "#E0E0E0"
COLOR_MATRIX = "#00FF41" 
COLOR_TRIG = "#FF0055"

# ==========================================
# 0. COMMAND CONTROL BAR (Always Visible)
# ==========================================
frame_controls = tk.Frame(root, bg="#111111", highlightthickness=1, highlightbackground="#333333")
frame_controls.pack(fill=tk.X, padx=10, pady=10)

def send_sync():
    if is_connected: arduino.write(b"CMD:SYNC\n")

def force_crypto():
    if is_connected: arduino.write(b"CMD:FORCE_CRYPTO\n")

def force_trig():
    if is_connected: arduino.write(b"CMD:FORCE_TRIG\n")

tk.Label(frame_controls, text="SYSTEM OVERRIDE CONTROLS:", font=("Segoe UI", 10, "bold"), bg="#111111", fg="#AAAAAA").pack(side=tk.LEFT, padx=10)

btn_sync = tk.Button(frame_controls, text="🔄 SYNC DASHBOARD", font=("Segoe UI", 10, "bold"), bg="#333333", fg="white", cursor="hand2", command=send_sync)
btn_sync.pack(side=tk.LEFT, padx=5, pady=5)

btn_crypt = tk.Button(frame_controls, text="🔀 FORCE CRYPTO", font=("Segoe UI", 10, "bold"), bg="#FFAA00", fg="black", cursor="hand2", command=force_crypto)
btn_crypt.pack(side=tk.LEFT, padx=5, pady=5)

btn_trig = tk.Button(frame_controls, text="🔀 FORCE TRIG", font=("Segoe UI", 10, "bold"), bg=COLOR_TRIG, fg="white", cursor="hand2", command=force_trig)
btn_trig.pack(side=tk.LEFT, padx=5, pady=5)

tk.Label(frame_controls, text=hardware_status, font=("Consolas", 10, "bold"), bg="#111111", fg=status_color).pack(side=tk.RIGHT, padx=10)


# ==========================================
# 1. CRYPTO VAULT UI (The Full Math Engine)
# ==========================================
container_crypto = tk.Frame(root, bg="#0D0D0D")

frame_log = tk.Frame(container_crypto, bg=COLOR_SURFACE, bd=0)
tk.Label(frame_log, text="SYSTEM TERMINAL", font=FONT_HEADER, bg=COLOR_SURFACE, fg=COLOR_TEXT).pack(pady=(15,5))
log_box = tk.Text(frame_log, font=FONT_CODE, bg="#050505", fg=COLOR_TEXT, bd=0, state=tk.DISABLED, width=35)
log_box.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

frame_vis = tk.Frame(container_crypto, bg=COLOR_SURFACE, bd=0)
tk.Label(frame_vis, text="XOR BINARY PROCESSOR", font=FONT_HEADER, bg=COLOR_SURFACE, fg="#FFAA00").pack(pady=(15,5))
visualizer_box = tk.Text(frame_vis, font=FONT_CODE, bg="#000000", fg="#FFAA00", bd=0, state=tk.DISABLED)
visualizer_box.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

frame_input = tk.Frame(container_crypto, bg=COLOR_SURFACE, bd=0)
tk.Label(frame_input, text="DATA ENTRY", font=FONT_HEADER, bg=COLOR_SURFACE, fg=COLOR_ACCENT).pack(anchor="w", pady=(15,5), padx=10)
input_box = tk.Text(frame_input, height=4, width=30, font=FONT_CODE, bg="#262626", fg="white", bd=0, insertbackground="white")
input_box.pack(padx=10, pady=5, fill=tk.X)

# --- THE HARDCORE MATH ENGINE ---
is_processing_crypto = False 

def process_crypto():
    global is_processing_crypto
    if not is_connected: return

    message = input_box.get(1.0, tk.END).strip()
    if not message: return

    is_processing_crypto = True 

    output_box.config(state=tk.NORMAL)
    output_box.delete(1.0, tk.END)
    visualizer_box.config(state=tk.NORMAL)
    visualizer_box.delete(1.0, tk.END)
    visualizer_box.insert(tk.END, ">>> ARDUINO HARDWARE MATH VISUALIZER <<<\n\n")

    arduino.write((message + '\n').encode('utf-8'))
    time.sleep(0.5) 

    raw_lines = []
    while arduino.in_waiting > 0:
        line = arduino.readline().decode('utf-8', errors='ignore').strip()
        if line: raw_lines.append(line)

    scrambled_word = ""
    for line in raw_lines:
        if "CIPHERTEXT:" in line:
            scrambled_word = line.split(":", 1)[1].strip()

    if not scrambled_word and raw_lines:
        scrambled_word = raw_lines[-1] 

    if scrambled_word:
        try: actual_key = ord(message[0]) ^ ord(scrambled_word[0])
        except: actual_key = 5

        for i in range(len(message)):
            char_val = ord(message[i])
            result_val = ord(scrambled_word[i]) if i < len(scrambled_word) else 0
            
            bin_char = format(char_val, '08b')
            bin_key = format(actual_key, '08b')
            bin_res = format(result_val, '08b')

            visualizer_box.insert(tk.END, f"Char '{message[i]}' : {bin_char}\n")
            visualizer_box.insert(tk.END, f"HW Key {actual_key} : {bin_key}\n")
            visualizer_box.insert(tk.END, f"XOR        : --------\n")
            res_char = scrambled_word[i] if i < len(scrambled_word) else '?'
            visualizer_box.insert(tk.END, f"Result '{res_char}': {bin_res}\n\n")

        output_box.insert(tk.END, scrambled_word)
        
        log_box.config(state=tk.NORMAL)
        log_box.insert(tk.END, f"[SYSTEM] Intercepted {len(raw_lines)} lines:\n")
        for line in raw_lines:
            log_box.insert(tk.END, f" > {line}\n")
        log_box.insert(tk.END, "-" * 30 + "\n")
        log_box.see(tk.END)
        log_box.config(state=tk.DISABLED)

    output_box.config(state=tk.DISABLED)
    visualizer_box.config(state=tk.DISABLED)
    is_processing_crypto = False 

action_btn = tk.Button(frame_input, text="ENCRYPT / DECRYPT", font=("Segoe UI", 12, "bold"), 
                       bg=COLOR_ACCENT, fg="black", activebackground="#00B3CC", bd=0, cursor="hand2", command=process_crypto)
action_btn.pack(pady=15, fill=tk.X, padx=10, ipady=5)

tk.Label(frame_input, text="ENCRYPTED/DECRYPTED OUTPUT:", font=FONT_HEADER, bg=COLOR_SURFACE, fg=COLOR_ACCENT).pack(anchor="w", pady=(5,5), padx=10)
output_box = tk.Text(frame_input, height=4, width=30, font=FONT_CODE, bg="#262626", fg=COLOR_MATRIX, bd=0, state=tk.DISABLED)
output_box.pack(padx=10, pady=(5, 15), fill=tk.X)
# ==========================================
# 2. TRIGONOMETRY ENGINE (Digital Twin)
# ==========================================
container_trig = tk.Frame(root, bg="#0D0D0D")
tk.Label(container_trig, text="LIVE GEOMETRY SOLVER (SOH CAH TOA)", font=("Segoe UI", 18, "bold"), bg="#0D0D0D", fg=COLOR_ACCENT).pack(pady=10)

# --- INCREASED CANVAS SIZE: width=1050, height=500 ---
canvas = tk.Canvas(container_trig, width=1050, height=500, bg="#111111", highlightthickness=1, highlightbackground="#333333")
canvas.pack(pady=10)

def draw_triangle(hyp, opp, adj):
    canvas.delete("all")
    SCALE = 10 # 1cm = 10 pixels (Kept exactly as requested!)
    
    # --- PUSHED THE STARTING POINT DOWN TO MATCH THE BIGGER BOX ---
    start_x, start_y = 50, 450 
    
    end_x = start_x + (adj * SCALE)
    end_y = start_y - (opp * SCALE)
    
    canvas.create_line(start_x, start_y, end_x, end_y, fill=COLOR_TRIG, width=6) # Hypotenuse
    canvas.create_line(end_x, end_y, end_x, start_y, fill=COLOR_MATRIX, width=6) # Opposite
    canvas.create_line(start_x, start_y, end_x, start_y, fill="#FFAA00", width=6) # Adjacent
    
    canvas.create_text(start_x+(adj*SCALE)/2 - 40, start_y-(opp*SCALE)/2 - 30, text=f"Hyp: {hyp:.1f}cm", fill="white", font=("Consolas", 14, "bold"))
    canvas.create_text(end_x + 80, start_y-(opp*SCALE)/2, text=f"Opp:\n{opp:.1f}cm", fill=COLOR_MATRIX, font=("Consolas", 14, "bold"))
    canvas.create_text(start_x+(adj*SCALE)/2, start_y+30, text=f"Adj: {adj:.1f}cm", fill="#FFAA00", font=("Consolas", 14, "bold"))
# ==========================================
# 3. SMART HARDWARE LISTENER LOOP
# ==========================================
current_mode = "NONE"

def update_loop():
    global current_mode
    if is_connected and not is_processing_crypto and arduino.in_waiting > 0:
        line = arduino.readline().decode('utf-8', errors='ignore').strip()
        
        # UI SWAP LOGIC (Driven by Arduino's confirmation)
        if "SYS_MODE:CRYPTO" in line and current_mode != "CRYPTO":
            container_trig.pack_forget()
            container_crypto.pack(fill=tk.BOTH, expand=True)
            current_mode = "CRYPTO"
            
        elif "SYS_MODE:TRIG" in line and current_mode != "TRIG":
            container_crypto.pack_forget()
            container_trig.pack(fill=tk.BOTH, expand=True)
            current_mode = "TRIG"
            
        elif "DATA_TRIG:" in line and current_mode == "TRIG":
            try:
                v = line.split(":")[1].split(",")
                draw_triangle(float(v[0]), float(v[1]), float(v[2]))
            except: pass

    root.after(50, update_loop) 

# --- RESPONSIVE LAYOUT ENGINE (Crypto Vault) ---
def adjust_layout(event):
    if str(event.widget) == str(root) and current_mode == "CRYPTO":
        if event.width < 850:
            frame_log.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
            frame_vis.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
            frame_input.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        else:
            frame_log.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
            frame_vis.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            frame_input.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

# Start by asking the Arduino what mode it's currently in to sync up instantly
if is_connected: arduino.write(b"CMD:SYNC\n")

root.bind("<Configure>", adjust_layout)
root.after(50, update_loop)
root.mainloop()