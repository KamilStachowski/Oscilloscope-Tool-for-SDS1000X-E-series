from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename, askopenfilename, askdirectory
import pyvisa
import os
import time
import sys
import threading
from PIL import ImageTk, Image
from io import BytesIO
import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
import configparser


def millis():
    return round(time.time() * 1000)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def change_color_bright(color, value):
    _color = ""
    for i in color:
        if i in "0123456789abcdefABCDEF":
            _color += hex(min(max(int(i, 16) + value, 0), 15))[2:]
        else:
            _color += i
    return _color


# config
channel_colors = {1: "#dede00", 2: "#de00de", 3: "#00dede", 4: "#00de00"}
additional_visa_instruments = []
autoconnect_device = ""

if os.path.isfile("config.ini"):
    config = configparser.ConfigParser()
    try:
        config.read('config.ini')
    except:
        messagebox.showerror("Confing load error", "Damaged config file!\nFix or delete it.")
        sys.exit()
    try:
        for i in range(1, 5):
            channel_colors[i] = config["channels_colors"][f"{i}"]
        autoconnect_device = config["autoconnect"]["device_address"]
    except:
        messagebox.showerror("Confing load error", "Damaged config file!\nFix or delete it.")
        sys.exit()
    try:
        for i in config["additional_visa_instruments"]:
            instr_addr = config["additional_visa_instruments"][i]
            if instr_addr != "":
                additional_visa_instruments.append(instr_addr)
    except:
        pass

else:
    config = configparser.ConfigParser()
    config["channels_colors"] = {}
    for i in range(1, 5):
        config["channels_colors"][f"{i}"] = channel_colors[i]

    config["autoconnect"] = {}
    config["autoconnect"]["device_address"] = ""

    config["additional_visa_instruments"] = {}
    config["additional_visa_instruments"]["instr_1"] = ""
    config["additional_visa_instruments"]["instr_2"] = ""

    with open('config.ini', mode='w') as configfile:
        config.write(configfile)
        configfile.close()

    messagebox.showinfo("Config", f"Config file created.\nPath: {os.path.abspath('config.ini')}")
    sys.exit()

btn_color = {"black": {"fg": "#fff", "bg": "#333", "activeforeground": "#fff", "activebackground": "#111"},
             "blue": {"fg": "#fff", "bg": "#33c", "activeforeground": "#fff", "activebackground": "#11a"},
             "orange": {"fg": "#fff", "bg": "#e63", "activeforeground": "#fff", "activebackground": "#c41"},
             "cyan": {"fg": "#fff", "bg": "#3aa", "activeforeground": "#fff", "activebackground": "#188"},
             "fg_red": {"fg": "#c00", "bg": "#333", "activeforeground": "#c00", "activebackground": "#111"},
             "fg_green": {"fg": "#0c0", "bg": "#333", "activeforeground": "#0c0", "activebackground": "#111"},
             "fg_yellow": {"fg": "#cc0", "bg": "#333", "activeforeground": "#cc0", "activebackground": "#111"},
             "fg_cyan": {"fg": "#0cc", "bg": "#333", "activeforeground": "#0cc", "activebackground": "#111"}}
# button channel color
btn_cc = {1: {"fg": "#000", "bg": channel_colors[1], "activeforeground": "#000",
              "activebackground": change_color_bright(channel_colors[1], -2)},
          2: {"fg": "#000", "bg": channel_colors[2], "activeforeground": "#000",
              "activebackground": change_color_bright(channel_colors[2], -2)},
          3: {"fg": "#000", "bg": channel_colors[3], "activeforeground": "#000",
              "activebackground": change_color_bright(channel_colors[3], -2)},
          4: {"fg": "#000", "bg": channel_colors[4], "activeforeground": "#000",
              "activebackground": change_color_bright(channel_colors[4], -2)}}

label_color = {"flat": {"fg": "#fff", "bg": "#000"},
               "raised_fat": {"fg": "#fff", "bg": "#000", "bd": 3, "relief": "raised"},
               "raised": {"fg": "#fff", "bg": "#000", "bd": 2, "relief": "raised"}}

entry_color = {"bg": "#222", "fg": "#fff", "insertbackground": "#ddd", "disabledbackground": "#000", "disabledforeground": "#ddd"}

optionmenu_color = {"bg": "#333", "activebackground": "#333", "fg": "#eee", "activeforeground": "#eee",
                    "highlightbackground": "#000"}

radiobtn_color = {
    "ch1": {"fg": channel_colors[1], "bg": "#000", "activeforeground": change_color_bright(channel_colors[1], -2),
            "activebackground": "#000", "selectcolor": "#333"},
    "ch2": {"fg": channel_colors[2], "bg": "#000", "activeforeground": change_color_bright(channel_colors[2], -2),
            "activebackground": "#000", "selectcolor": "#333"},
    "ch3": {"fg": channel_colors[3], "bg": "#000", "activeforeground": change_color_bright(channel_colors[3], -2),
            "activebackground": "#000", "selectcolor": "#333"},
    "ch4": {"fg": channel_colors[4], "bg": "#000", "activeforeground": change_color_bright(channel_colors[4], -2),
            "activebackground": "#000", "selectcolor": "#333"},
    "purple": {"fg": "#88f", "bg": "#000", "activeforeground": "#66c", "activebackground": "#000",
               "selectcolor": "#333"},
    "black": {"fg": "#fff", "bg": "#000", "activeforeground": "#ccc", "activebackground": "#000",
              "selectcolor": "#333"}}


def check_is_number(text):
    try:
        float(text)
        return True
    except:
        return False


def to_si_string(number, dec=2):
    if number == 0:
        return f"{round(number, dec)}"
    elif abs(number) >= 1000000000:
        return f"{round(number / 1000000000, dec)}G"
    elif abs(number) >= 1000000:
        return f"{round(number / 1000000, dec)}M"
    elif abs(number) >= 1000:
        return f"{round(number / 1000, dec)}k"
    elif abs(number) >= 1:
        return f"{round(number, dec)}"
    elif abs(number) >= 0.001:
        return f"{round(number * 1000, dec)}m"
    elif abs(number) >= 0.000001:
        return f"{round(number * 1000000, dec)}µ"
    else:
        return f"{round(number * 1000000000, dec)}n"


visa_rm = pyvisa.ResourceManager()

vdiv_options = ["500µV", "1mV", "2mV", "5mV", "10mV", "20mV", "50mV", "100mV", "200mV", "500mV", "1V", "2V", "5V",
                "10V"]
tdiv_options = ["1ns", "2ns", "5ns", "10nS", "20ns", "50ns", "100ns", "200ns", "500ns",
                "1µs", "2µs", "5µs", "10µs", "20µs", "50µs", "100µs", "200µs", "500µs",
                "1ms", "2ms", "5ms", "10ms", "20ms", "50ms", "100ms", "200ms", "500ms",
                "1s", "2s", "5s", "10s", "20s", "50s", "100s"]


def get_visa_instruments_list():
    instr_list = list(visa_rm.list_resources())
    if len(instr_list) == 0:
        instr_list = ["None"]

    i = 0
    for instr in additional_visa_instruments:
        instr_list.insert(i, instr)
        i += 1

    return instr_list


class StatusLabel:
    def __init__(self, root, x, y):
        self.status = StringVar()
        self.status.set("Idle")
        self.label = Label(root, textvariable=self.status, justify=LEFT, anchor=W, font=("Arial", 10, "bold"))
        self.label.place(x=x, y=y, width=50)
        self.label['fg'] = "#0b0"

    def set_busy(self):
        self.status.set("Busy")
        self.label['fg'] = "#a00"

    def set_idle(self):
        self.status.set("Idle")
        self.label['fg'] = "#0b0"


class Textarea:
    def __init__(self, root, x, y, width, height, fg="#4287f5", bg="#111", ibg="#fff"):
        self.frame = Frame(root)
        self.textarea_sb = Scrollbar(self.frame)
        self.textarea_sb.pack(side=RIGHT, fill='y')
        self.textarea = Text(self.frame, height=30, width=45, background=bg, foreground=fg, insertbackground=ibg, yscrollcommand=self.textarea_sb.set)
        self.textarea_sb.config(command=self.textarea.yview)
        self.textarea.pack(side=LEFT, expand=True, fill='both')
        self.frame.place(x=x, y=y, width=width, height=height)
        self.textarea.config(state=DISABLED)

    def insert(self, text):
        self.textarea.config(state=NORMAL)
        self.textarea.insert(END, text)
        self.textarea.config(state=DISABLED)

    def see(self, index=END):
        self.textarea.see(index)

    def get(self):
        return self.textarea.get('1.0', END)

    def erase(self, header=None):
        self.textarea.config(state=NORMAL)
        self.textarea.delete('1.0', END)
        self.textarea.config(state=DISABLED)

        if header is not None:
            self.insert(header)



class Oscilloscope:
    def __init__(self, master, place_x, place_y, name="Oscilloscope"):
        self.name = name
        self.visa_instr = None  # visa oscilloscope instrument

        self.instrument_selector_frame = Frame(master, bg="#000")
        self.instrument_selector_frame.place(x=place_x, y=place_y, width=350, height=85)

        self.visa_instr_list = get_visa_instruments_list()
        self.selected_visa_instrument = StringVar(master)
        self.selected_visa_instrument.set(self.visa_instr_list[0])

        Label(self.instrument_selector_frame, text="VISA instrument:", justify=LEFT, font=("Arial", 9, "bold"),
              **label_color["flat"]).place(x=3, y=0)
        self.refresh_visa_instruments_list_button = Button(self.instrument_selector_frame, text="Refresh",
                                                           **btn_color["black"],
                                                           command=lambda: self.refresh_visa_instruments_list())
        self.refresh_visa_instruments_list_button.place(x=288, y=3, width=60, height=18)

        self.visa_instrument_selector = OptionMenu(self.instrument_selector_frame, self.selected_visa_instrument,
                                                   *self.visa_instr_list)
        self.visa_instrument_selector.configure(**optionmenu_color)
        self.visa_instrument_selector.place(x=0, y=22, width=350)

        # connect visa btn
        self.connect_visa_btn = Button(self.instrument_selector_frame, text="Connect", **btn_color["fg_green"],
                                       command=lambda: self.visa_connect(self.selected_visa_instrument.get()))
        self.connect_visa_btn.place(x=2, y=55, width=170, height=30)

        self.disconnect_visa_btn = Button(self.instrument_selector_frame, text="Disconnect", **btn_color["fg_red"],
                                          command=lambda: self.visa_disconnect())
        self.disconnect_visa_btn.place(x=178, y=55, width=170, height=30)
        self.disconnect_visa_btn["state"] = "disable"

        self.var_visa_device_name = StringVar(gui)
        self.var_visa_device_name.set("None")

    def instrument_name(self, master, x, y):
        Label(master, text="Connected Instrument:", justify=LEFT, font=("Arial", 9, "bold"),
              **label_color["flat"]).place(x=x, y=y)
        Label(master, textvariable=self.var_visa_device_name, justify=CENTER, **label_color["flat"], bd=3,
              relief="sunken", padx=5).place(x=x, y=y + 20, width=350)

    def refresh_visa_instruments_list(self, visa_instruments_list=None):
        if visa_instruments_list is None:
            visa_instruments_list = get_visa_instruments_list()

        self.selected_visa_instrument.set(visa_instruments_list[0])
        _menu = self.visa_instrument_selector['menu']
        _menu.delete(0, "end")
        for string in visa_instruments_list:
            _menu.add_command(label=string,
                              command=lambda value=string: self.selected_visa_instrument.set(value))

    def visa_connect(self, resource):
        try:
            self.visa_instr = visa_rm.open_resource(resource)

            self.connect_visa_btn["state"] = "disable"
            self.disconnect_visa_btn["state"] = "normal"
            self.visa_instrument_selector["state"] = "disable"
            self.refresh_visa_instruments_list_button["state"] = "disable"
            data = self.visa_instr.query("*IDN?")
            data = data.split(",")
            self.var_visa_device_name.set(f"{data[1]} ({data[0]})")

        except:
            messagebox.showerror("Error", "Failed to connect VISA device!")
            self.visa_disconnect()

    def visa_disconnect(self):
        if self.visa_instr is not None:
            try:
                self.visa_instr.close()
            except:
                pass
            self.visa_instr = None
        self.connect_visa_btn["state"] = "normal"
        self.disconnect_visa_btn["state"] = "disable"
        self.visa_instrument_selector["state"] = "normal"
        self.refresh_visa_instruments_list_button["state"] = "normal"
        self.var_visa_device_name.set("None")

    def is_connected(self):
        return True if self.visa_instr is not None else False

    def query(self, query):
        if self.is_connected():
            try:
                return self.visa_instr.query(query).strip()
            except:
                return None
        return False

    def write(self, cmd):
        if self.is_connected():
            try:
                self.visa_instr.write(cmd)
                return True
            except:
                return False
        return False

    def dump_screen(self):
        if self.is_connected():
            self.visa_instr.write("SCDP")
            response = self.visa_instr.read_raw()
            return Image.open(BytesIO(response))
        else:
            return None

    def transfer_waveform(self, channel):
        if self.is_connected():
            vdiv = float(self.visa_instr.query(f"c{channel}:vdiv?")[8:-2])  # V/div
            ofst = float(self.visa_instr.query(f"c{channel}:ofst?")[8:-2])  # V offset
            tdiv = float(self.visa_instr.query("tdiv?")[5:-2])  # time/div
            sara = float(self.visa_instr.query("sara?")[5:-5])  # sampling rate

            self.visa_instr.write(f"c{channel}:wf? dat2")
            time.sleep(0.1)
            raw = self.visa_instr.read_raw()


            if raw[raw.index(b','):raw.index(b',') + 3] == b',#9' and raw[-2:] == b'\n\n' and int(
                    raw[raw.index(b'#') + 2:raw.index(b'#') + 11]) > 0:  # check data is valid

                volt_values = list(raw[raw.index(b'#') + 11:-2])
                time_values = []


                for idx in range(len(volt_values)):
                    if volt_values[idx] > 127:
                        volt_values[idx] = float(volt_values[idx] - 256)  # 255
                    else:
                        volt_values[idx] = float(volt_values[idx])

                for idx in range(0, len(volt_values)):
                    volt_values[idx] = round(volt_values[idx] / 25 * vdiv - ofst, 10)
                    time_values.append((-(tdiv * 14 / 2) + idx * (1 / sara)) * 1000000)  # time values in us * 1000000

                return {"volt_values": volt_values, "time_values": time_values,  # time values in us
                        "v_div": vdiv, "v_offset": ofst, "t_div": tdiv, "sampling_rate": sara}
            else:
                return None
        else:
            return None

    def fft(self, volt_values, sampling_rate):
        fft_result = np.fft.fft(volt_values)
        fft_freqs = np.fft.fftfreq(len(volt_values), 1.0 / sampling_rate)
        norm_fft_result = 2 * np.abs(fft_result) / len(fft_result)

        return {"fft_freqs": fft_freqs[:-int(len(norm_fft_result) / 2)],
                "fft_result": np.abs(norm_fft_result[:-int(len(norm_fft_result) / 2)])}


class Trace_Info:
    def __init__(self, master, x, y, channel, color):
        self.frame = Frame(master, bg="#444", bd=3, relief="raised")
        self.frame.place(x=x, y=y, width=130, height=63)

        self.coupling = StringVar()
        self.probe = StringVar()
        self.vdiv = StringVar()
        self.vofst = StringVar()

        self.coupling.set("OFF")
        self.probe.set("1X")
        self.vdiv.set("1.00V/")
        self.vofst.set("0.0V")

        Label(self.frame, text=f"CH{channel}", justify=LEFT, anchor=W, bd=1, relief="raised", padx=5, fg=color,
              bg="#000", font=("Arial", 11, "bold")).place(x=-3, y=-3, width=40)
        Label(self.frame, textvariable=self.coupling, justify=CENTER, bd=1, relief="raised", padx=5, bg=color).place(
            x=74, y=0, width=50)
        Label(self.frame, textvariable=self.probe, justify=LEFT, anchor=W, bg="#444", fg="#fff",
              font=("Arial", 10, "bold")).place(x=0, y=20, width=60)
        Label(self.frame, textvariable=self.vdiv, justify=RIGHT, anchor=E, bd=1, bg="#444", fg="#fff").place(x=64, y=20,
                                                                                                             width=60)
        Label(self.frame, textvariable=self.vofst, justify=RIGHT, anchor=E, bd=1, bg="#444", fg="#fff").place(x=64,
                                                                                                              y=38,
                                                                                                              width=60)

    def set_cpl(self, coupling):
        coupling = coupling.upper()
        if coupling == "GND" or coupling == "OFF":
            self.coupling.set(coupling)
        elif "A" in coupling:
            self.coupling.set(coupling.replace("A", "AC"))
        else:
            self.coupling.set(coupling.replace("D", "DC"))

    def set_probe(self, probe_attenuation):
        if probe_attenuation < 1:
            self.probe.set(f"{probe_attenuation}X")
        elif probe_attenuation < 1000:
            self.probe.set(f"{round(probe_attenuation)}X")
        else:
            self.probe.set(f"{round(probe_attenuation / 1000)}kX")

    def set_vdiv(self, vdiv):
        self.vdiv.set(f"{to_si_string(vdiv)}V/")

    def set_vofsr(self, vofst):
        self.vofst.set(f"{to_si_string(vofst)}V")


osc_thread = None  # oscilloscope thread


def run_osc_thread(target, ignore_cont_meas = False):
    global osc_thread
    if (osc_thread is None or osc_thread.is_alive() == False) and (ignore_cont_meas or cont_measure_start_btn["state"] == "normal"):  # if thread is free and continuous measure is not running
        osc_status.set_busy()
        osc_thread = threading.Thread(target=target)
        osc_thread.daemon = True
        osc_thread.start()
        gui.after(10, lambda: update_osc_status())
    else:
        messagebox.showerror("Error", "Device is busy! Try again later!")


def update_osc_status():
    global osc_thread
    if (osc_thread is None or osc_thread.is_alive() == False) and cont_measure_start_btn["state"] == "normal":
        osc_status.set_idle()
    else:
        gui.after(10, lambda: update_osc_status())


continuous_measure_step = 0
continuous_measure_last_trigger = 0
continuous_measure_log_file = ""
continuous_measure_screenshots_dir = ""

def start_continuous_measure():
    global continuous_measure_step, continuous_measure_last_trigger, continuous_measure_log_file, continuous_measure_screenshots_dir
    if not osc.is_connected():
        messagebox.showerror("Error", "Device is not connected!")
        return

    if not (osc_thread is None or osc_thread.is_alive() == False):
        messagebox.showerror("Error", "Device is busy! Try again later!")
        return

    if not os.path.isdir(var_cont_meas_log_save_path.get()):
        messagebox.showerror("Error", "Please select correct folder!")
        return

    #walidacja z kanałami
    osc_status.set_busy()
    gui.after(10, lambda: update_osc_status())


    date_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    filename_header = input_cont_meas_filename_header.get()
    if filename_header != "":
        filename_header = filename_header + "_"
    continuous_measure_log_file = f"{var_cont_meas_log_save_path.get()}\\{filename_header}{date_time}.csv"
    var_cont_meas_log_filename.set(f"{filename_header}{date_time}.csv")

    continuous_measure_step = 1
    continuous_measure_last_trigger = 0

    cont_measure_start_btn["state"] = "disable"
    cont_measure_stop_btn["state"] = "normal"
    for chbtn in var_cont_meas_type_checkbox:
        var_cont_meas_type_checkbox[chbtn]['state'] = "disable"
    btn_cont_meas_select_dir['state'] = "disable"
    input_cont_meas_filename_header['state'] = "disable"
    input_cont_meas_min_trig_interval['state'] = "disable"

    cont_measure_log.erase()

    header = "Date and Time"

    for ch in range(1, 5):
        for i in range(len(measure_types_cmd)):
            if var_cont_meas_type_enable[f"{ch}_{measure_types_cmd[i]}"].get():
                header += f", CH{ch}:{measure_types_name[i]}"
    if var_cont_meas_type_enable["screenshot"].get():
        continuous_measure_screenshots_dir = f"{var_cont_meas_log_save_path.get()}\\{filename_header}{date_time}_screens"
        os.makedirs(continuous_measure_screenshots_dir)
        header += f", screenshot_name"
    cont_measure_log.insert(f"{header}\n")

    with open(continuous_measure_log_file, "w") as log:
        log.write(f"{header}\n")
        log.close()

    gui.after(10, lambda: run_continuous_measure())


def stop_continuous_measure():
    global continuous_measure_step, continuous_measure_last_trigger
    continuous_measure_step = 0 # 0 = Stop

    cont_measure_start_btn["state"] = "normal"
    cont_measure_stop_btn["state"] = "disable"


def perform_measure():
    global continuous_measure_log_file, continuous_measure_screenshots_dir
    try:
        now = datetime.datetime.now()
        data = now.strftime("%Y_%m_%d_%H_%M_%S.") + now.strftime("%f")[0:2]
        for ch in range(1, 5):
            for i in range(len(measure_types_cmd)):
                if var_cont_meas_type_enable[f"{ch}_{measure_types_cmd[i]}"].get():
                    value = float(osc.query(f"C{ch}:PAVA? {measure_types_cmd[i]}").split(",")[1].strip()[:-1].replace("H", "").replace("***", "Nan"))
                    data += ", " + str(value)
        if var_cont_meas_type_enable["screenshot"].get():
            if os.path.isdir(continuous_measure_screenshots_dir):
                data += ", " + now.strftime("%Y_%m_%d_%H_%M_%S.") + now.strftime("%f")[0:2] + ".png"
                screen = osc.dump_screen()
                if screen:
                    screen.save(f"{continuous_measure_screenshots_dir}\\screen_" + now.strftime("%Y_%m_%d_%H_%M_%S.") + now.strftime("%f")[0:2] + ".png")
            else:
                stop_continuous_measure()
                messagebox.showerror("Error", "Screenshot folder not found!")
                return

        cont_measure_log.insert(f"{data}\n")
        cont_measure_log.see(END)
        with open(continuous_measure_log_file, "a") as log:
            log.write(f"{data}\n")
            log.close()
    except:
        stop_continuous_measure()
        messagebox.showerror("Error", "Problem with communication with oscilloscope")


def run_continuous_measure():
    global continuous_measure_step, continuous_measure_last_trigger

    if not osc.is_connected():
        messagebox.showerror("Error", "Device is disconnected!\nContinuous measure interrupted!")
        stop_continuous_measure()
        return

    if continuous_measure_step == 0:    # stop
        pass
        for chbtn in var_cont_meas_type_checkbox:
            var_cont_meas_type_checkbox[chbtn]['state'] = "normal"
        btn_cont_meas_select_dir['state'] = "normal"
        input_cont_meas_filename_header['state'] = "normal"
        input_cont_meas_min_trig_interval['state'] = "normal"

    elif continuous_measure_step == 1:  # wait for trigger interval and trigger
        if millis() - continuous_measure_last_trigger >= round(float(input_cont_meas_min_trig_interval.get()) * 1000):
            continuous_measure_last_trigger = millis()
            osc_write_cmd("arm")
            continuous_measure_step += 1    #go to next step
            gui.after(10, lambda: run_continuous_measure())
        else:
            gui.after(10, lambda: run_continuous_measure())

    elif continuous_measure_step == 2:  # wait for acquisition
        if osc.query("trmd?").split()[1].strip() == "STOP":
            run_osc_thread(lambda: perform_measure(), True)
            continuous_measure_step += 1  # go to next step
            gui.after(10, lambda: run_continuous_measure())
        else:
            gui.after(10, lambda: run_continuous_measure())

    elif continuous_measure_step == 3:  # wait for finis measure
        if osc_thread is None or osc_thread.is_alive() == False:
            continuous_measure_step = 1  # back to trigger
            gui.after(10, lambda: run_continuous_measure())
        else:
            gui.after(10, lambda: run_continuous_measure())


def cont_meas_select_dir():
    var_cont_meas_log_save_path.set(askdirectory())


def osc_write_cmd(cmd):
    if not osc.write(cmd):
        messagebox.showerror("Error", "Device is not connected!")

osc_screen_shot_done = False

def get_osc_screen():
    global oscilloscope_screen_image, oscilloscope_screen_image_widget, osc_screen_shot_done

    if not osc.is_connected():
        messagebox.showerror("Error", "Device is not connected!")
        return

    screen = osc.dump_screen()
    if screen:
        oscilloscope_screen_image = screen
        oscilloscope_screen_image_widget = ImageTk.PhotoImage(oscilloscope_screen_image)
        oscilloscope_screen.config(image=oscilloscope_screen_image_widget)
        osc_screen_shot_done = True


def save_osc_screen():
    global oscilloscope_screen_image, osc_screen_shot_done
    if not osc_screen_shot_done:
        messagebox.showerror("Error", "First take a screenshot!")
        return

    datetime_now = datetime.datetime.now().strftime("%Y_%m_%d %H_%M_%S")
    file = asksaveasfilename(initialfile=f"screen_{datetime_now}.png", defaultextension=".png",
                             filetypes=[("PNG images", "*.png")])
    if file is not None:
        oscilloscope_screen_image.save(file)


def wf_setup_plot():
    wf_ax.set_xlabel("Time [µs]", color="#888")
    wf_ax.set_ylabel(ylabel="Voltage [div]", color="#888")
    wf_ax.grid(color='#aaa', linestyle='--', linewidth=1)
    wf_ax.set_ylim(-4, 4)
    wf_canvas.draw_idle()


def wf_plot_clear():
    wf_ax.cla()
    for i in range(1, 5):
        wf_trace[i].cla()
        wf_trace[i].set_axis_off()
    wf_setup_plot()


def fft_setup_plot():
    fft_ax.set_xlabel("Frequency [Hz]", color="#888")
    fft_ax.set_ylabel(ylabel="Amplitude [V]", color="#888")
    fft_ax.grid(color='#aaaaaa', linestyle='--', linewidth=1)
    fft_ax.set_yscale("log" if fft_sett_log_yscale.get() else "linear")
    fft_ax.set_xlim(fft_sett_x_start.get(), fft_sett_x_stop.get())
    fft_canvas.draw_idle()


def fft_plot_clear():
    fft_ax.cla()
    fft_setup_plot()


def fft_set_y_scale(scale):
    fft_sett_log_yscale.set(1 if scale == "log" else 0)
    fft_ax.set_yscale(scale)
    fft_canvas.draw_idle()


def get_trace(channel, calc_fft=False):
    global fft_cursor
    if not osc.is_connected():
        messagebox.showerror("Error", "Device is not connected!")
        return
    if osc.query(f"c{channel}:tra?") != f"C{channel}:TRA ON":
        messagebox.showerror("Error", f"Channel {channel} is not active!")
        return

    wf_plot_clear()
    fft_plot_clear()
    wf_canvas.draw()
    fft_canvas.draw()

    data = osc.transfer_waveform(channel)
    hpos = float(osc.query(f"trdl?")[5:-1]) * 1000000

    wf_ax.set_xlim(data["time_values"][0], data["time_values"][len(data["time_values"]) - 1])
    wf_trace[channel].set_ylim(data["v_div"] * -4 - data["v_offset"], data["v_div"] * 4 - data["v_offset"])
    wf_trace[channel].plot(data["time_values"], data["volt_values"], color=channel_colors[channel], linewidth=1)
    wf_trace[channel].plot([data["time_values"][0], data["time_values"][len(data["time_values"]) - 1]], [0, 0],
                           color=channel_colors[channel], linewidth=0.5, linestyle='--')

    wf_ax.plot([data["time_values"][0], data["time_values"][len(data["time_values"]) - 1]], [0, 0], color='#eee',
               linestyle='--', linewidth=1)
    wf_ax.plot([hpos, hpos], [-4, 4], color='#0099cd', linestyle='--', linewidth=1)
    wf_ax.plot(hpos, 4, marker=11, color='#0099cd')
    wf_canvas.draw_idle()

    for i in range(1, 5):
        if i == channel:
            attn = float(osc.query(f"c{channel}:attn?")[8:])
            cpl = osc.query(f"c{channel}:cpl?")[7:]

            wf_trace_info[i].set_cpl(cpl)
            wf_trace_info[i].set_probe(attn)
            wf_trace_info[i].set_vdiv(data["v_div"])
            wf_trace_info[i].set_vofsr(data["v_offset"])

            wf_info_sara.set(to_si_string(data["sampling_rate"]) + "Sa/s")
            wf_info_curr.set(to_si_string(len(data["volt_values"])) + "pts")
        else:
            wf_trace_info[i].set_cpl("OFF")
            wf_trace_info[i].set_probe(1)
            wf_trace_info[i].set_vdiv(1)
            wf_trace_info[i].set_vofsr(0)

    if calc_fft:
        fft_data = osc.fft(data["volt_values"], data["sampling_rate"])
        fft_ax.plot(fft_data["fft_freqs"], fft_data["fft_result"], color=channel_colors[channel], linewidth=1)
        fft_canvas.draw_idle()


def get_all_active_trace(calc_fft=False):
    if not osc.is_connected():
        messagebox.showerror("Error", "Device is not connected!")
        return

    wf_plot_clear()
    fft_plot_clear()
    wf_canvas.draw()
    fft_canvas.draw()

    data = {}

    for channel in range(1, 5):
        if osc.query(f"c{channel}:tra?") != f"C{channel}:TRA ON":
            data[channel] = None
        else:
            data[channel] = osc.transfer_waveform(channel)

    if data[1] is not None or data[2] is not None or data[3] is not None or data[4] is not None:
        hpos = float(osc.query(f"trdl?")[5:-1]) * 1000000

        x_axis_set = False
        for channel in range(1, 5):
            if data[channel] is not None:

                if x_axis_set is False:
                    x_axis_set = True
                    wf_ax.set_xlim(data[channel]["time_values"][0],
                                   data[channel]["time_values"][len(data[channel]["time_values"]) - 1])
                    wf_ax.plot([data[channel]["time_values"][0],
                                data[channel]["time_values"][len(data[channel]["time_values"]) - 1]], [0, 0],
                               color='#eee', linestyle='--', linewidth=1)
                    wf_ax.plot([hpos, hpos], [-4, 4], color='#0099cd', linestyle='--', linewidth=1)
                    wf_ax.plot(hpos, 4, marker=11, color='#0099cd')

                    wf_info_sara.set(to_si_string(data[channel]["sampling_rate"]) + "Sa/s")
                    wf_info_curr.set(to_si_string(len(data[channel]["volt_values"])) + "pts")
                wf_trace[channel].set_ylim(data[channel]["v_div"] * -4 - data[channel]["v_offset"],
                                           data[channel]["v_div"] * 4 - data[channel]["v_offset"])
                wf_trace[channel].plot(data[channel]["time_values"], data[channel]["volt_values"],
                                       color=channel_colors[channel], linewidth=1)
                wf_trace[channel].plot([data[channel]["time_values"][0],
                                        data[channel]["time_values"][len(data[channel]["time_values"]) - 1]], [0, 0],
                                       color=channel_colors[channel], linewidth=0.5, linestyle='--')

                attn = float(osc.query(f"c{channel}:attn?")[8:])
                cpl = osc.query(f"c{channel}:cpl?")[7:]

                wf_trace_info[channel].set_cpl(cpl)
                wf_trace_info[channel].set_probe(attn)
                wf_trace_info[channel].set_vdiv(data[channel]["v_div"])
                wf_trace_info[channel].set_vofsr(data[channel]["v_offset"])

                if calc_fft:
                    fft_data = osc.fft(data[channel]["volt_values"], data[channel]["sampling_rate"])
                    fft_ax.plot(fft_data["fft_freqs"], fft_data["fft_result"], color=channel_colors[channel],
                                linewidth=1)
            else:
                wf_trace_info[channel].set_cpl("OFF")
                wf_trace_info[channel].set_probe(1)
                wf_trace_info[channel].set_vdiv(1)
                wf_trace_info[channel].set_vofsr(0)

        wf_canvas.draw_idle()

        if calc_fft:
            fft_canvas.draw_idle()

    else:
        messagebox.showerror("Error", "All channels is off!")


def plot_save(fig, name):
    datetime_now = datetime.datetime.now().strftime("%Y_%m_%d %H_%M_%S")
    plot_file = asksaveasfilename(initialfile=f"{name}_{datetime_now}.png",
                                  defaultextension=".png",
                                  filetypes=[("PNG images", "*.png"), ("PDF file", "*.pdf")])
    if plot_file is not None:
        fig.savefig(plot_file)


def get_int_num_from_entry(entry):
    input = entry.get()
    if input == "":
        entry.delete(0, END)
        entry.insert(END, "0")
        return 0
    elif check_is_number(input):
        number = int(round(float(input)))
        entry.delete(0, END)
        entry.insert(END, f"{number}")
        return number
    elif check_is_number(input[0:-1]) and input[len(input) - 1] in "kM":
        number = float(input[0:-1])
        number *= 1000 if input[len(input) - 1] == "k" else 1000000
        return int(round(number))
    else:
        return 0


def fft_set_x_scale():
    start = get_int_num_from_entry(fft_sett_x_start_input)
    stop = get_int_num_from_entry(fft_sett_x_stop_input)

    if start >= stop:
        messagebox.showerror("Error", "Stop value must be greater than start value!")
        return
    fft_sett_x_start.set(start)
    fft_sett_x_stop.set(stop)

    fft_ax.set_xlim(start, stop)
    fft_canvas.draw_idle()


def validate_fft_number_input(input):
    if len(input) > 8:
        return False
    if check_is_number(input) or input == "":
        return True
    elif len(input) > 1 and check_is_number(input[0:-1]) and input[len(input) - 1] in "kM":
        return True
    else:
        return False


def validate_float_number_input(input):
    if len(input) > 8:
        return False
    if check_is_number(input) or input == "":
        return True
    else:
        return False


def validate_filename_input(input):
    if len(input) > 40:
        return False
    for i in input:
        if i not in "ABCDEFGHIJKLMNOPQRSTUWXYZabcdefghijklmnopqrstuwxyz0123456789_-":
            return False
    return True


# instrument setting functions
def osc_set_rest_channels_as(channel):
    if not osc.is_connected():
        messagebox.showerror("Error", "Device is not connected!")
        return

    if osc.query(f"c{channel}:tra?") != f"C{channel}:TRA ON":
        messagebox.showerror("Error", f"Channel {channel} is not active!")
        return

    cpl = osc.query(f"c{channel}:cpl?")[7:]
    bwl = osc.query(f"c{channel}:bwl?")[7:]
    attn = osc.query(f"c{channel}:attn?")[8:]
    vdiv = osc.query(f"c{channel}:vdiv?")[7:]
    ofst = osc.query(f"c{channel}:ofst?")[8:]

    for i in range(1, 5):
        if i != channel and osc.query(f"c{i}:tra?") == f"C{i}:TRA ON":
            osc.write(f"c{i}:cpl {cpl}")
            osc.write(f"bwl c{i}, {bwl}")
            osc.write(f"c{i}:attn {attn}")
            osc.write(f"c{i}:vdiv {vdiv}")
            osc.write(f"c{i}:ofst {ofst}")


def osc_write_cmd_if_ch_is_on(channel, cmd):
    if not osc.is_connected():
        messagebox.showerror("Error", "Device is not connected!")
        return
    if osc.query(f"c{channel}:tra?") != f"C{channel}:TRA ON":
        messagebox.showerror("Error", f"Channel {channel} is not active!")
        return

    if not osc.write(cmd):
        messagebox.showerror("Error", "Device is not connected!")


def osc_set_vdiv(channel):
    if not osc.is_connected():
        messagebox.showerror("Error", "Device is not connected!")
        return
    if osc.query(f"c{channel}:tra?") != f"C{channel}:TRA ON":
        messagebox.showerror("Error", f"Channel {channel} is not active!")
        return

    attn = float(osc.query(f"c{channel}:attn?")[8:])

    vdiv = var_set_vdiv.get()[:-1]

    if "µ" in vdiv:
        vdiv = float(vdiv[:-1]) * 0.000001
    elif "m" in vdiv:
        vdiv = float(vdiv[:-1]) * 0.001
    else:
        vdiv = float(vdiv)

    osc_write_cmd(f"c{channel}:vdiv {vdiv * attn}V")


def osc_set_vofst(channel, div):
    if not osc.is_connected():
        messagebox.showerror("Error", "Device is not connected!")
        return
    if osc.query(f"c{channel}:tra?") != f"C{channel}:TRA ON":
        messagebox.showerror("Error", f"Channel {channel} is not active!")
        return

    vdiv = float(osc.query(f"c{channel}:vdiv?")[8:-1])

    ofst = vdiv * div

    osc_write_cmd(f"c{channel}:ofst {ofst}V")


def si_to_float(si_number):
    if "n" in si_number:
        return float(si_number[:-1]) * 0.000000001
    elif "µ" in si_number:
        return float(si_number[:-1]) * 0.000001
    elif "m" in si_number:
        return float(si_number[:-1]) * 0.001
    else:
        return float(si_number)


def osc_set_tdiv(dir=None):
    if not osc.is_connected():
        messagebox.showerror("Error", "Device is not connected!")
        return
    si_to_float("10")
    if dir is not None:
        actual_tdiv = float(osc.query("tdiv?")[5:-1])
        for opt in tdiv_options:

            if opt[:-1] == to_si_string(actual_tdiv).replace(".0", ""):

                index = tdiv_options.index(opt)
                if dir == "DECR":
                    if index > 0:
                        var_set_tdiv.set(tdiv_options[index - 1])
                    else:
                        var_set_tdiv.set(tdiv_options[index])
                        messagebox.showerror("Error", "Horizontal scale limit!")

                elif dir == "INCR":
                    if index < len(tdiv_options) - 1:
                        var_set_tdiv.set(tdiv_options[index + 1])
                    else:
                        var_set_tdiv.set(tdiv_options[index])
                        messagebox.showerror("Error", "Horizontal scale limit!")
                break

    tdiv = var_set_tdiv.get()[:-1]
    if "n" in tdiv:
        tdiv = float(tdiv[:-1]) * 0.000000001
    elif "µ" in tdiv:
        tdiv = float(tdiv[:-1]) * 0.000001
    elif "m" in tdiv:
        tdiv = float(tdiv[:-1]) * 0.001
    else:
        tdiv = float(tdiv)

    osc_write_cmd(f"tdiv {tdiv}s")


def osc_set_trdl(div):  #TRDL - trigger delay
    if not osc.is_connected():
        messagebox.showerror("Error", "Device is not connected!")
        return

    tdiv = float(osc.query("tdiv?")[5:-1])
    ofst = tdiv * div
    osc_write_cmd(f"trdl {ofst}s")


def osc_set_trigger():
    if not osc.is_connected():
        messagebox.showerror("Error", "Device is not connected!")
        return
    if var_set_tr_src.get() != "LINE":
        if osc.query(f"{var_set_tr_src.get()}:tra?") != f"{var_set_tr_src.get()}:TRA ON":
            messagebox.showerror("Error", f"Channel {var_set_tr_src.get()[1]} is not active!")
            return

    if var_set_tr_src.get() == "LINE":
        osc.write("LINE:TRLV 0V")
    else:
        osc.write(f"{var_set_tr_src.get()}:TRLV {input_set_tr_level.get()}V")

    osc.write(f"{var_set_tr_src.get()}:TRCP {var_set_tr_cpl.get()}")
    osc.write(f"{var_set_tr_src.get()}:TRSL {var_set_tr_slope.get()}")


def osc_save_preset():
    if not osc.is_connected():
        messagebox.showerror("Error", "Device is not connected!")
        return
    datetime_now = datetime.datetime.now().strftime("%Y_%m_%d %H_%M_%S")
    filename = asksaveasfilename(initialfile=f"preset_{datetime_now}.sds", defaultextension=".sds",
                                 filetypes=[("SDS preset", "*.sds")])
    if filename != '':
        preset = configparser.ConfigParser()

        for channel in range(1, 5):
            if osc.query(f"c{channel}:tra?") == f"C{channel}:TRA ON":
                preset[f"Channel{channel}"] = {}
                preset[f"Channel{channel}"]["coupling"] = osc.query(f"c{channel}:cpl?")[7:]
                preset[f"Channel{channel}"]["bandwidth_limit"] = osc.query(f"c{channel}:bwl?")[7:]
                preset[f"Channel{channel}"]["attention"] = osc.query(f"c{channel}:attn?")[8:]
                preset[f"Channel{channel}"]["volt_div"] = osc.query(f"c{channel}:vdiv?")[7:]
                preset[f"Channel{channel}"]["volt_ofst"] = osc.query(f"c{channel}:ofst?")[8:]

        preset["Horizontal"] = {}
        preset["Horizontal"]["time_div"] = osc.query("tdiv?")[5:]
        preset["Horizontal"]["trig_delay"] = osc.query(f"trdl?")[5:]

        preset["Trigger"] = {}
        trlv = osc.query(f"trlv?").split(":")
        preset["Trigger"]["source"] = trlv[0]
        preset["Trigger"]["level"] = trlv[1][5:]
        preset["Trigger"]["coupling"] = osc.query("trcp?")[5:]
        preset["Trigger"]["slope"] = osc.query(f"{trlv[0]}:trsl?").split(":")[1][5:]

        with open(filename, mode='w') as presetfile:
            preset.write(presetfile)
            presetfile.close()


def osc_load_preset():
    if not osc.is_connected():
        messagebox.showerror("Error", "Device is not connected!")
        return
    filename = askopenfilename(defaultextension=".sds", filetypes=[("SDS preset", "*.sds")])
    if filename != '':
        preset = configparser.ConfigParser()
        try:
            preset.read(filename)
        except:
            messagebox.showerror("Preset load error", "Incorrect preset file!")
            return

        #preset validation
        for channel in range(1, 5):
            if f"Channel{channel}" in preset:
                if not ("coupling" in preset[f"Channel{channel}"] and
                        "bandwidth_limit" in preset[f"Channel{channel}"] and
                        "attention" in preset[f"Channel{channel}"] and
                        "volt_div" in preset[f"Channel{channel}"] and
                        "volt_ofst" in preset[f"Channel{channel}"]):
                    messagebox.showerror("Preset load error", "Incorrect preset file!")
                    return

        if not ("Horizontal" in preset and
                "time_div" in preset["Horizontal"] and
                "trig_delay" in preset["Horizontal"]):
            messagebox.showerror("Preset load error", "Incorrect preset file!")
            return

        if not ("Trigger" in preset and
                "source" in preset["Trigger"] and
                "level" in preset["Trigger"] and
                "coupling" in preset["Trigger"] and
                "slope" in preset["Trigger"]):
            messagebox.showerror("Preset load error", "Incorrect preset file!")
            return

        #preset OK
        for channel in range(1, 5):
            if f"Channel{channel}" in preset:
                osc.write(f"c{channel}:tra on")
                osc.write(f"c{channel}:cpl {preset[f'Channel{channel}']['coupling']}")
                osc.write(f"bwl c{channel}, {preset[f'Channel{channel}']['bandwidth_limit']}")
                osc.write(f"c{channel}:attn {preset[f'Channel{channel}']['attention']}")
                osc.write(f"c{channel}:vdiv {preset[f'Channel{channel}']['volt_div']}")
                osc.write(f"c{channel}:ofst {preset[f'Channel{channel}']['volt_ofst']}")
            else:
                osc.write(f"c{channel}:tra off")

        osc.write(f"tdiv {preset['Horizontal']['time_div']}")
        osc.write(f"trdl {preset['Horizontal']['trig_delay']}")

        osc.write(f"{preset['Trigger']['source']}:trlv {preset['Trigger']['level']}")
        osc.write(f"{preset['Trigger']['source']}:trcp {preset['Trigger']['coupling']}")
        osc.write(f"{preset['Trigger']['source']}:trsl {preset['Trigger']['slope']}")


def osc_autoconnect():
    if autoconnect_device != "":
        if autoconnect_device in osc.visa_instr_list:
            osc.selected_visa_instrument.set(autoconnect_device)
            osc.visa_connect(autoconnect_device)
        else:
            messagebox.showerror("Error", "Autoconnect failed! Device not found")


def on_closing():
    global osc_thread
    if cont_measure_stop_btn["state"] == "normal":
        messagebox.showwarning("Warning", "First STOP continuous measure!")
        return
    if osc_thread is not None and osc_thread.is_alive():
        messagebox.showwarning("Warning", "Wait until communication with the oscilloscope ends!")
        return

    if not messagebox.askyesno("Exit", "Are you sure you want to exit?"):
        return

    try:
        osc.visa_disconnect()  # close connection with oscilloscope
        visa_rm.close()  # close visa resources manager
    except:
        pass
    gui.quit()  # stops mainloop
    gui.destroy()  # destroy window
    # sys.exit()


gui = Tk()
gui.title("Oscilloscope Tool v1.1.0 for SDS1000X-E series")
gui.geometry("1000x600")
gui.resizable(False, False)
try:
    gui.iconbitmap(resource_path("icon.ico"))
except:
    pass


# menubar
menubar = Menu(gui, background="#000")
menu_file = Menu(menubar, tearoff=0)
menu_file.add_command(label="Exit", command=lambda: on_closing())
menu_file.add_separator()
menu_file.add_command(label="Terminate", command=lambda: sys.exit("Terminated"))
menubar.add_cascade(label="File", menu=menu_file)

menu_preset = Menu(menubar, tearoff=0)
menu_preset.add_command(label="Load", command=lambda: run_osc_thread(lambda: osc_load_preset()))
menu_preset.add_separator()
menu_preset.add_command(label="Save", command=lambda: run_osc_thread(lambda: osc_save_preset()))

menubar.add_cascade(label="Preset", menu=menu_preset)

gui.config(menu=menubar)

dark_style = ttk.Style(gui)
dark_style.configure("DARK.TFrame", foreground="#fff", background="#000")

tabCtrl = ttk.Notebook(gui, style="DARK.TNotebook")
tab_instrument = ttk.Frame(tabCtrl, style="DARK.TFrame")  # visa instrument tab
tab_osc_screen = ttk.Frame(tabCtrl, style="DARK.TFrame")  # oscilloscope screen tab
tab_osc_waveform = ttk.Frame(tabCtrl, style="DARK.TFrame")  # waveform plot tab
tab_osc_fft = ttk.Frame(tabCtrl, style="DARK.TFrame")  # fft tab
tab_measure = ttk.Frame(tabCtrl, style="DARK.TFrame")  # fft tab

tabCtrl.add(tab_instrument, text='Instrument')
tabCtrl.add(tab_osc_screen, text='Screen')
tabCtrl.add(tab_osc_waveform, text='Waveform plot')
tabCtrl.add(tab_osc_fft, text='Math FFT plot')
tabCtrl.add(tab_measure, text='Measure')
tabCtrl.place(x=0, y=0, width=1000, height=600)


# Status label
Label(gui, text="Oscilloscope status:", justify=RIGHT, anchor=E, font=("Arial", 10, "bold")).place(x=800, y=0, width=150)
osc_status = StatusLabel(gui, 950, 0)


# Instrument tab
osc = Oscilloscope(tab_instrument, 5, 5)
osc.instrument_name(tab_instrument, 5, 90)

frame_osc_setting = Frame(tab_instrument, bg="#000")
frame_osc_setting.place(x=5, y=170, width=990, height=260)


# Vertical settings
var_set_vdiv = StringVar(gui)
var_set_vdiv.set("1V")

Label(frame_osc_setting, text="Vertical", font=("Arial", 10, "bold"), **label_color["raised_fat"]).place(x=0, y=0, width=990)

Label(frame_osc_setting, text="Channel", font=("Arial", 9, "bold"), **label_color["raised"]).place(x=35, y=27, width=75)
Label(frame_osc_setting, text="Coupling", font=("Arial", 9, "bold"), **label_color["raised"]).place(x=120, y=27,  width=85)
Label(frame_osc_setting, text="BW Limit", font=("Arial", 9, "bold"), **label_color["raised"]).place(x=215, y=27, width=75)
Label(frame_osc_setting, text="Probe", font=("Arial", 9, "bold"), **label_color["raised"]).place(x=300, y=27, width=175)
Label(frame_osc_setting, text="Scale V/div", font=("Arial", 9, "bold"), **label_color["raised"]).place(x=485, y=27, width=125)
Label(frame_osc_setting, text="Voltage offset (div)", font=("Arial", 9, "bold"), **label_color["raised"]).place(x=620, y=27, width=250)

opt_menu1 = OptionMenu(frame_osc_setting, var_set_vdiv, *vdiv_options)
opt_menu1.configure(**optionmenu_color)
opt_menu1.place(x=485, y=62, width=80)
Label(frame_osc_setting, text="x probe", **label_color["flat"]).place(x=485, y=93, width=80)

for i in range(1, 5):
    y = 50 + 20 * (i - 1)
    Label(frame_osc_setting, text=f"CH{i}", **btn_cc[i], font=("Arial", 8, "bold")).place(x=0, y=y, width=30, height=18)
    Button(frame_osc_setting, text="ON", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(lambda: osc_write_cmd(f"c{channel}:tra on"))).place(x=35, y=y, width=35, height=18)
    Button(frame_osc_setting, text="OFF", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(lambda: osc_write_cmd(f"c{channel}:tra off"))).place(x=75, y=y, width=35, height=18)

    Button(frame_osc_setting, text="DC1M", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(
               lambda: osc_write_cmd_if_ch_is_on(channel, f"c{channel}:cpl d1m"))).place(x=120, y=y, width=40, height=18)
    Button(frame_osc_setting, text="AC1M", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(
               lambda: osc_write_cmd_if_ch_is_on(channel, f"c{channel}:cpl a1m"))).place(x=165, y=y, width=40, height=18)

    Button(frame_osc_setting, text="ON", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(
               lambda: osc_write_cmd_if_ch_is_on(channel, f"bwl c{channel}, on"))).place(x=215, y=y, width=35, height=18)
    Button(frame_osc_setting, text="OFF", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(
               lambda: osc_write_cmd_if_ch_is_on(channel, f"bwl c{channel}, off"))).place(x=255, y=y, width=35, height=18)

    Button(frame_osc_setting, text="0.1X", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(
               lambda: osc_write_cmd_if_ch_is_on(channel, f"c{channel}:attn 0.1"))).place(x=300, y=y, width=40, height=18)
    Button(frame_osc_setting, text="1X", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(
               lambda: osc_write_cmd_if_ch_is_on(channel, f"c{channel}:attn 1"))).place(x=345, y=y, width=40, height=18)
    Button(frame_osc_setting, text="10X", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(
               lambda: osc_write_cmd_if_ch_is_on(channel, f"c{channel}:attn 10"))).place(x=390, y=y, width=40, height=18)
    Button(frame_osc_setting, text="100X", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(
               lambda: osc_write_cmd_if_ch_is_on(channel, f"c{channel}:attn 100"))).place(x=435, y=y, width=40, height=18)

    Button(frame_osc_setting, text="Set", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(lambda: osc_set_vdiv(channel))).place(x=570, y=y, width=40, height=18)

    Button(frame_osc_setting, text="HIGH", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(lambda: osc_set_vofst(channel, 3.8))).place(x=620, y=y, width=35, height=18)
    Button(frame_osc_setting, text="3", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(lambda: osc_set_vofst(channel, 3))).place(x=660, y=y, width=20, height=18)
    Button(frame_osc_setting, text="2", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(lambda: osc_set_vofst(channel, 2))).place(x=685, y=y, width=20, height=18)
    Button(frame_osc_setting, text="1", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(lambda: osc_set_vofst(channel, 1))).place(x=710, y=y, width=20, height=18)
    Button(frame_osc_setting, text="0", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(lambda: osc_set_vofst(channel, 0))).place(x=735, y=y, width=20, height=18)
    Button(frame_osc_setting, text="-1", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(lambda: osc_set_vofst(channel, -1))).place(x=760, y=y, width=20, height=18)
    Button(frame_osc_setting, text="-2", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(lambda: osc_set_vofst(channel, -2))).place(x=785, y=y, width=20, height=18)
    Button(frame_osc_setting, text="-3", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(lambda: osc_set_vofst(channel, -3))).place(x=810, y=y, width=20, height=18)
    Button(frame_osc_setting, text="LOW", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(lambda: osc_set_vofst(channel, -3.8))).place(x=835, y=y, width=35, height=18)

    Button(frame_osc_setting, text=f"Set rest as CH{i}", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(lambda: osc_set_rest_channels_as(channel))).place(x=880, y=y, width=110, height=18)

# Horizontal settings
Label(frame_osc_setting, text="Horizontal", font=("Arial", 10, "bold"), **label_color["raised_fat"]).place(x=0, y=140, width=478)
Label(frame_osc_setting, text="TIME", font=("Arial", 10, "bold"), **label_color["raised"], wraplength=1).place(x=0, y=165, width=25, height=75)
var_set_tdiv = StringVar(gui)
var_set_tdiv.set("1ms")

Label(frame_osc_setting, text="s/div", font=("Arial", 9, "bold"), **label_color["raised"]).place(x=30, y=167, width=140)
opt_menu2 = OptionMenu(frame_osc_setting, var_set_tdiv, *tdiv_options, command=lambda x: run_osc_thread(lambda: osc_set_tdiv()))
opt_menu2.configure(**optionmenu_color)
opt_menu2.place(x=60, y=190, width=80, height=50)
Button(frame_osc_setting, text=f"<", **btn_color["blue"], font=("Arial", 8, "bold"),
       command=lambda: run_osc_thread(lambda: osc_set_tdiv("DECR"))).place(x=30, y=190, width=30, height=52)
Button(frame_osc_setting, text=f">", **btn_color["blue"], font=("Arial", 8, "bold"),
       command=lambda: run_osc_thread(lambda: osc_set_tdiv("INCR"))).place(x=140, y=190, width=30, height=52)

Label(frame_osc_setting, text="Trigger delay (div)", font=("Arial", 9, "bold"), **label_color["raised"]).place(x=180, y=167, width=298)
for i in range(-7, 8):
    Button(frame_osc_setting, text=f"{i}", **btn_color["cyan"], font=("Arial", 8, "bold"),
           command=lambda div=i: run_osc_thread(lambda: osc_set_trdl(div))).place(x=180 + 20 * (i + 7), y=190, width=18, height=52)


# Trigger settings
Label(frame_osc_setting, text="Trigger", font=("Arial", 10, "bold"), **label_color["raised_fat"]).place(x=490, y=140, width=500)

var_set_tr_src = StringVar(gui)
var_set_tr_src.set("C1")
var_set_tr_cpl = StringVar(gui)
var_set_tr_cpl.set("DC")
var_set_tr_slope = StringVar(gui)
var_set_tr_slope.set("POS")

Label(frame_osc_setting, text="Trigger source", font=("Arial", 9, "bold"), **label_color["raised"]).place(x=490, y=167, width=100)
Radiobutton(frame_osc_setting, text="CH1", variable=var_set_tr_src, value="C1", **radiobtn_color["ch1"],
            font=("Arial", 8, "bold")).place(x=490, y=190, width=50)
Radiobutton(frame_osc_setting, text="CH2", variable=var_set_tr_src, value="C2", **radiobtn_color["ch2"],
            font=("Arial", 8, "bold")).place(x=490, y=210, width=50)
Radiobutton(frame_osc_setting, text="CH3", variable=var_set_tr_src, value="C3", **radiobtn_color["ch3"],
            font=("Arial", 8, "bold")).place(x=540, y=190, width=50)
Radiobutton(frame_osc_setting, text="CH4", variable=var_set_tr_src, value="C4", **radiobtn_color["ch4"],
            font=("Arial", 8, "bold")).place(x=540, y=210, width=50)
Radiobutton(frame_osc_setting, text="AC line", variable=var_set_tr_src, value="LINE", **radiobtn_color["purple"],
            font=("Arial", 8, "bold")).place(x=490, y=230, width=100)

Label(frame_osc_setting, text="Coupling", font=("Arial", 9, "bold"), **label_color["raised"]).place(x=600, y=167, width=100)
Radiobutton(frame_osc_setting, text="DC", variable=var_set_tr_cpl, value="DC", **radiobtn_color["black"],
            font=("Arial", 8, "bold")).place(x=600, y=190, width=50)
Radiobutton(frame_osc_setting, text="AC", variable=var_set_tr_cpl, value="AC", **radiobtn_color["black"],
            font=("Arial", 8, "bold")).place(x=650, y=190, width=50)
Radiobutton(frame_osc_setting, text="LF reject", variable=var_set_tr_cpl, value="LFREJ", **radiobtn_color["black"],
            font=("Arial", 8, "bold")).place(x=600, y=210, width=100)
Radiobutton(frame_osc_setting, text="HF reject", variable=var_set_tr_cpl, value="HFREJ", **radiobtn_color["black"],
            font=("Arial", 8, "bold")).place(x=600, y=230, width=100)

Label(frame_osc_setting, text="Slope", font=("Arial", 9, "bold"), **label_color["raised"]).place(x=710, y=167, width=80)
Radiobutton(frame_osc_setting, text="Rising", variable=var_set_tr_slope, justify=LEFT, anchor=W, value="POS",
            **radiobtn_color["black"], font=("Arial", 8, "bold")).place(x=710, y=190, width=80)
Radiobutton(frame_osc_setting, text="Falling", variable=var_set_tr_slope, justify=LEFT, anchor=W, value="NEG",
            **radiobtn_color["black"], font=("Arial", 8, "bold")).place(x=710, y=210, width=80)
Radiobutton(frame_osc_setting, text="Altering", variable=var_set_tr_slope, justify=LEFT, anchor=W, value="WINDOW",
            **radiobtn_color["black"], font=("Arial", 8, "bold")).place(x=710, y=230, width=80)

Label(frame_osc_setting, text="Level", font=("Arial", 9, "bold"), **label_color["raised"]).place(x=800, y=167, width=80)
vcmd_float_number = gui.register(validate_float_number_input)
input_set_tr_level = Entry(frame_osc_setting, justify='right', **entry_color, validate='key', validatecommand=(vcmd_float_number, '%P'))
input_set_tr_level.place(x=800, y=190, width=65)
input_set_tr_level.insert(END, "1")
Label(frame_osc_setting, text="V", **label_color["flat"]).place(x=866, y=190, width=15)

Button(frame_osc_setting, text=f"Set", **btn_color["blue"], font=("Arial", 8, "bold"),
       command=lambda: run_osc_thread(lambda: osc_set_trigger())).place(x=890, y=167, width=30, height=90)

Button(frame_osc_setting, text=f"Set 50%", **btn_color["blue"], font=("Arial", 8, "bold"),
       command=lambda: run_osc_thread(lambda: osc_set_trigger())).place(x=930, y=167, width=58, height=90)


# Screen Tab
oscilloscope_screen_image = Image.open(resource_path("screen_image.png"))
oscilloscope_screen_image_widget = ImageTk.PhotoImage(oscilloscope_screen_image)

oscilloscope_screen = Label(tab_osc_screen, image=oscilloscope_screen_image_widget, background="#000")
oscilloscope_screen.place(x=0, y=0)

# side
frame_screen_tab_side_menu = Frame(tab_osc_screen, bg="#000")
frame_screen_tab_side_menu.place(x=805, y=0, width=185, height=555)
Label(frame_screen_tab_side_menu, text="Channels", font=("Arial", 9, "bold"), **label_color["raised"]).place(x=0, y=5, width=185)
for i in range(1, 5):
    y = 30 + 20 * (i - 1)
    Label(frame_screen_tab_side_menu, text=f"CH{i}", **btn_cc[i], font=("Arial", 8, "bold")).place(x=0, y=y, width=30, height=18)
    Button(frame_screen_tab_side_menu, text=f"ON", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(lambda: osc_write_cmd(f"c{channel}:tra on"))).place(x=35, y=y,  width=30, height=18)
    Button(frame_screen_tab_side_menu, text=f"OFF", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(lambda: osc_write_cmd(f"c{channel}:tra off"))).place(x=70, y=y, width=30, height=18)
    Button(frame_screen_tab_side_menu, text="1X", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(lambda: osc_write_cmd_if_ch_is_on(channel, f"c{channel}:attn 1"))).place(x=110, y=y, width=35, height=18)
    Button(frame_screen_tab_side_menu, text="10X", **btn_cc[i], font=("Arial", 8, "bold"),
           command=lambda channel=i: run_osc_thread(lambda: osc_write_cmd_if_ch_is_on(channel, f"c{channel}:attn 10"))).place(x=150, y=y, width=35, height=18)

Label(frame_screen_tab_side_menu, text="Time s/div", font=("Arial", 9, "bold"), **label_color["raised"]).place(x=0, y=125, width=185)
opt_menu3 = OptionMenu(frame_screen_tab_side_menu, var_set_tdiv, *tdiv_options, command=lambda x: run_osc_thread(lambda: osc_set_tdiv()))
opt_menu3.configure(**optionmenu_color)
opt_menu3.place(x=50, y=150, width=85, height=50)

Button(frame_screen_tab_side_menu, text=f"<", **btn_color["blue"], font=("Arial", 8, "bold"),
       command=lambda: run_osc_thread(lambda: osc_set_tdiv("DECR"))).place(x=0, y=150, width=50, height=52)
Button(frame_screen_tab_side_menu, text=f">", **btn_color["blue"], font=("Arial", 8, "bold"),
       command=lambda: run_osc_thread(lambda: osc_set_tdiv("INCR"))).place(x=135, y=150, width=50, height=52)

Label(frame_screen_tab_side_menu, text="Trigger", font=("Arial", 9, "bold"), **label_color["raised"]).place(x=0, y=215,
                                                                                                            width=185)
Button(frame_screen_tab_side_menu, text="Auto", **btn_color["fg_green"], font=("Arial", 10, "bold"),
       command=lambda: run_osc_thread(lambda: osc_write_cmd("trmd auto"))).place(x=0, y=240, width=90, height=25)
Button(frame_screen_tab_side_menu, text="Normal", **btn_color["fg_green"], font=("Arial", 10, "bold"),
       command=lambda: run_osc_thread(lambda: osc_write_cmd("trmd norm"))).place(x=95, y=240, width=90, height=25)
Button(frame_screen_tab_side_menu, text="Single", **btn_color["fg_yellow"], font=("Arial", 10, "bold"),
       command=lambda: run_osc_thread(lambda: osc_write_cmd("trmd single"))).place(x=0, y=270, width=185, height=25)
Button(frame_screen_tab_side_menu, text="Stop", **btn_color["fg_red"], font=("Arial", 10, "bold"),
       command=lambda: run_osc_thread(lambda: osc_write_cmd("stop"))).place(x=0, y=300, width=90, height=25)
Button(frame_screen_tab_side_menu, text="Arm", **btn_color["fg_cyan"], font=("Arial", 10, "bold"),
       command=lambda: run_osc_thread(lambda: osc_write_cmd("arm"))).place(x=95, y=300, width=90, height=25)

Button(frame_screen_tab_side_menu, text="Hide Menu", **btn_color["blue"],
       command=lambda: run_osc_thread(lambda: osc_write_cmd("menu off"))).place(x=0, y=385, width=90, height=25)
Button(frame_screen_tab_side_menu, text="Show Menu", **btn_color["blue"],
       command=lambda: run_osc_thread(lambda: osc_write_cmd("menu on"))).place(x=95, y=385, width=90, height=25)
Button(frame_screen_tab_side_menu, text="Dump Screen", **btn_color["orange"],
       command=lambda: run_osc_thread(lambda: get_osc_screen())).place(x=0, y=415, width=185, height=30)
Button(frame_screen_tab_side_menu, text="Save Screen", **btn_color["blue"], command=lambda: save_osc_screen()).place(
    x=0, y=450, width=185, height=30)

# Waveform plot tab
wf_plotting_frame = Frame(tab_osc_waveform)
plt.style.use("dark_background")
plt.margins(x=0)
wf_fig, wf_ax = plt.subplots()

wf_trace = {}
for i in range(1, 5):
    wf_trace[i] = wf_ax.twinx()
    wf_trace[i].set_axis_off()

wf_canvas = FigureCanvasTkAgg(wf_fig, master=wf_plotting_frame)
wf_canvas.get_tk_widget().place(x=0, y=0, width=860, height=500)

wf_canvas.draw()
wf_plotting_frame.place(x=0, y=0, width=860, height=500)

wf_setup_plot()
wf_info_sara = StringVar(gui)
wf_info_curr = StringVar(gui)

wf_info_sara.set("0Sa/s")
wf_info_curr.set("0kpts")

wf_info_frame = Frame(tab_osc_waveform, bg="#222", bd=3, relief="ridge")
wf_info_frame.place(x=865, y=20, width=130, height=50)

Label(wf_info_frame, text="SaRa:", justify=LEFT, anchor=W, fg="#fff", bg="#222", font=("Arial", 10, "bold")).place(x=0, y=0)
Label(wf_info_frame, textvariable=wf_info_sara, justify=RIGHT, anchor=E, fg="#fff", bg="#222").place(x=60, y=0, width=63)

Label(wf_info_frame, text="Curr:", justify=LEFT, anchor=W, fg="#fff", bg="#222", font=("Arial", 10, "bold")).place(x=0, y=22)
Label(wf_info_frame, textvariable=wf_info_curr, justify=RIGHT, anchor=E, fg="#fff", bg="#222").place(x=60, y=22, width=63)

wf_trace_info = {}
for channel in range(1, 5):
    wf_trace_info[channel] = Trace_Info(tab_osc_waveform, x=865, y=100 + 65 * (channel - 1), channel=channel,
                                        color=channel_colors[channel])

Button(tab_osc_waveform, text="Get CH1", **btn_cc[1], font=("Arial", 10, "bold"),
       command=lambda: run_osc_thread(lambda: get_trace(1, True))).place(x=0, y=500, width=80, height=30)
Button(tab_osc_waveform, text="Get CH2", **btn_cc[2], font=("Arial", 10, "bold"),
       command=lambda: run_osc_thread(lambda: get_trace(2, True))).place(x=80, y=500, width=80, height=30)
Button(tab_osc_waveform, text="Get CH3", **btn_cc[3], font=("Arial", 10, "bold"),
       command=lambda: run_osc_thread(lambda: get_trace(3, True))).place(x=160, y=500, width=80, height=30)
Button(tab_osc_waveform, text="Get CH4", **btn_cc[4], font=("Arial", 10, "bold"),
       command=lambda: run_osc_thread(lambda: get_trace(4, True))).place(x=240, y=500, width=80, height=30)
Button(tab_osc_waveform, text="Get all active channels", **btn_color["black"],
       command=lambda: run_osc_thread(lambda: get_all_active_trace(True))).place(x=0, y=530, width=320, height=25)

# FFT tab
fft_plotting_frame = Frame(tab_osc_fft)
plt.style.use("dark_background")
fft_fig, fft_ax = plt.subplots()
fft_canvas = FigureCanvasTkAgg(fft_fig, master=fft_plotting_frame)
fft_canvas.get_tk_widget().place(x=0, y=0, width=860, height=500)
fft_canvas.draw()
fft_plotting_frame.place(x=0, y=0, width=860, height=500)

# fft settings
fft_sett_log_yscale = IntVar(gui)
fft_sett_x_start = IntVar(gui)
fft_sett_x_stop = IntVar(gui)
fft_sett_log_yscale.set(1)
fft_sett_x_start.set(0)
fft_sett_x_stop.set(10000)

fft_setup_plot()

Button(tab_osc_fft, text="Get CH1", **btn_cc[1], font=("Arial", 10, "bold"),
       command=lambda: run_osc_thread(lambda: get_trace(1, True))).place(x=0, y=500, width=80, height=30)
Button(tab_osc_fft, text="Get CH2", **btn_cc[2], font=("Arial", 10, "bold"),
       command=lambda: run_osc_thread(lambda: get_trace(2, True))).place(x=80, y=500, width=80, height=30)
Button(tab_osc_fft, text="Get CH3", **btn_cc[3], font=("Arial", 10, "bold"),
       command=lambda: run_osc_thread(lambda: get_trace(3, True))).place(x=160, y=500, width=80, height=30)
Button(tab_osc_fft, text="Get CH4", **btn_cc[4], font=("Arial", 10, "bold"),
       command=lambda: run_osc_thread(lambda: get_trace(4, True))).place(x=240, y=500, width=80, height=30)
Button(tab_osc_fft, text="Get all active channels", **btn_color["black"],
       command=lambda: run_osc_thread(lambda: get_all_active_trace(True))).place(x=0, y=530, width=320, height=25)

Label(tab_osc_fft, text="Vertical Scale:", **label_color["flat"], font=("Arial", 10, "bold")).place(x=865, y=0,
                                                                                                    width=125)
Button(tab_osc_fft, text="Log Y Scale", **btn_color["blue"], command=lambda: fft_set_y_scale("log")).place(x=865, y=23, width=125, height=25)
Button(tab_osc_fft, text="Linear Y Scale", **btn_color["blue"], command=lambda: fft_set_y_scale("linear")).place(x=865, y=50, width=125, height=25)

Label(tab_osc_fft, text="Horizontal Scale:", **label_color["flat"], font=("Arial", 10, "bold")).place(x=865, y=100, width=125)

vcmd_si_number = gui.register(validate_fft_number_input)
Label(tab_osc_fft, text="Start:", **label_color["flat"]).place(x=865, y=122, width=40)
fft_sett_x_start_input = Entry(tab_osc_fft, justify='right', **entry_color, validate='key', validatecommand=(vcmd_si_number, '%P'))
fft_sett_x_start_input.place(x=905, y=122, width=65)
fft_sett_x_start_input.insert(END, "0")
Label(tab_osc_fft, text="Hz", **label_color["flat"]).place(x=970, y=122, width=20)

Label(tab_osc_fft, text="Stop:", **label_color["flat"]).place(x=865, y=140, width=40)
fft_sett_x_stop_input = Entry(tab_osc_fft, justify='right', **entry_color, validate='key', validatecommand=(vcmd_si_number, '%P'))
fft_sett_x_stop_input.place(x=905, y=142, width=65)
fft_sett_x_stop_input.insert(END, "10k")
Label(tab_osc_fft, text="Hz", **label_color["flat"]).place(x=970, y=142, width=20)
Button(tab_osc_fft, text="Set", **btn_color["blue"], command=lambda: fft_set_x_scale()).place(x=865, y=162, width=125, height=20)

Button(tab_osc_fft, text="Save Plot", **btn_color["blue"], command=lambda: plot_save(fft_fig, "fft")).place(x=865, y=525, width=125, height=25)


# measure tab
Label(tab_measure, text="Settings", font=("Arial", 10, "bold"), **label_color["raised_fat"]).place(x=5, y=5, width=355)

var_cont_meas_log_save_path = StringVar(gui)
var_cont_meas_log_save_path.set("")
var_cont_meas_log_filename = StringVar(gui)
var_cont_meas_log_filename.set("")

Label(tab_measure, text="Save directory:", font=("Arial", 9, "bold"), anchor=W, **label_color["flat"]).place(x=5, y=30, width=200)
Label(tab_measure, textvariable=var_cont_meas_log_save_path, anchor=W, **label_color["flat"], bd=3, relief="sunken", padx=5).place(x=5, y=50, width=300)
btn_cont_meas_select_dir = Button(tab_measure, text="Select", **btn_color["blue"], command=lambda: cont_meas_select_dir())
btn_cont_meas_select_dir.place(x=305, y=50, width=50, height=24)

vcmd_filename = gui.register(validate_filename_input)
Label(tab_measure, text="Filename header:", font=("Arial", 9, "bold"), anchor=W, **label_color["flat"]).place(x=5, y=80, width=110)
input_cont_meas_filename_header = Entry(tab_measure, justify='left', **entry_color, validate='key', validatecommand=(vcmd_filename, '%P'))
input_cont_meas_filename_header.place(x=115, y=81, width=240)

Label(tab_measure, text="Minimum trigger interval:", **label_color["flat"]).place(x=2, y=110, width=140)
input_cont_meas_min_trig_interval = Entry(tab_measure, justify='right', **entry_color, validate='key', validatecommand=(vcmd_float_number, '%P'))
input_cont_meas_min_trig_interval.place(x=142, y=110, width=65)
input_cont_meas_min_trig_interval.insert(END, "1")
Label(tab_measure, text="s", **label_color["flat"]).place(x=207, y=110, width=15)

measure_types_cmd = ["RMS", "PKPK", "AMPL", "MIN", "MAX", "FREQ", "RISE", "FALL"]
measure_types_name = ["RMS", "Pk-Pk", "Amplitude", "Min", "Max", "Frequency", "Rise Time", "Fall Time"]

var_cont_meas_type_enable = {}
var_cont_meas_type_checkbox = {}

Label(tab_measure, text="Measure", font=("Arial", 9, "bold"), **label_color["raised"]).place(x=5, y=150, width=200)
frame_cmt = Frame(tab_measure, bg="#000")
frame_cmt.place(x=5, y=180, width=200, height=215)
Label(frame_cmt, text="Type:", **label_color["flat"], font=("Arial", 8, "bold")).place(x=0, y=0, width=80)
for i in range(1, 5):
    Label(frame_cmt, text=f"CH{i}", **btn_cc[i], font=("Arial", 8, "bold")).place(x=80+(30*(i-1)), y=0, width=30)

for i in range(len(measure_types_cmd)):
    Label(frame_cmt, text=f"{measure_types_name[i]}", **label_color["flat"], font=("Arial", 8, "bold")).place(x=0, y=22+22*i, width=80)
    for ch in range(1, 5):
        var_cont_meas_type_enable[f"{ch}_{measure_types_cmd[i]}"] = IntVar(gui)
        var_cont_meas_type_enable[f"{ch}_{measure_types_cmd[i]}"].set(0)
        var_cont_meas_type_checkbox[f"{ch}_{measure_types_cmd[i]}"] = Checkbutton(frame_cmt, variable=var_cont_meas_type_enable[f"{ch}_{measure_types_cmd[i]}"], onvalue=1, offvalue=0, **radiobtn_color["black"])
        var_cont_meas_type_checkbox[f"{ch}_{measure_types_cmd[i]}"].place(x=80+(30*(ch-1)), y=20+22*i, width=30)
Label(frame_cmt, text=f"Screen shot", **label_color["flat"], font=("Arial", 8, "bold")).place(x=0, y=198, width=80)
var_cont_meas_type_enable[f"screenshot"] = IntVar(gui)
var_cont_meas_type_enable[f"screenshot"].set(0)
var_cont_meas_type_checkbox[f"screenshot"] = Checkbutton(frame_cmt, variable=var_cont_meas_type_enable[f"screenshot"], onvalue=1, offvalue=0, **radiobtn_color["black"])
var_cont_meas_type_checkbox[f"screenshot"].place(x=80, y=195, width=30)

Label(tab_measure, text="Control", font=("Arial", 10, "bold"), **label_color["raised_fat"]).place(x=5, y=400, width=355)

cont_measure_start_btn = Button(tab_measure, text="Start", **btn_color["fg_green"], command=lambda: start_continuous_measure())
cont_measure_start_btn.place(x=5, y=430, width=175, height=30)
cont_measure_stop_btn =  Button(tab_measure, text="Stop", **btn_color["fg_red"], command=lambda: stop_continuous_measure())
cont_measure_stop_btn.place(x=185, y=430, width=175, height=30)
cont_measure_stop_btn["state"] = "disabled"

Label(tab_measure, text="Output", font=("Arial", 10, "bold"), **label_color["raised_fat"]).place(x=5, y=480, width=355)

Label(tab_measure, text="Logfile name:", font=("Arial", 9, "bold"), anchor=W, **label_color["flat"]).place(x=5, y=505, width=200)
Label(tab_measure, textvariable=var_cont_meas_log_filename, anchor=W, **label_color["flat"], bd=3, relief="sunken", padx=5).place(x=5, y=525, width=350)

Label(tab_measure, text="Log", font=("Arial", 10, "bold"), **label_color["raised_fat"]).place(x=370, y=5, width=620)
cont_measure_log = Textarea(tab_measure, 370, 30, 620, 520)


gui.after(100, lambda: osc_autoconnect())

gui.protocol("WM_DELETE_WINDOW", on_closing)
gui.mainloop()
