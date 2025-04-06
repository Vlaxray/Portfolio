import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from tkinter.font import Font

# Configurazione colori e stili
BG_COLOR = "#2E3440"
FG_COLOR = "#D8DEE9"
ACCENT_COLOR = "#5E81AC"
ERROR_COLOR = "#BF616A"
SUCCESS_COLOR = "#A3BE8C"
RED_ICON = "#BF616A"
GREEN_ICON = "#A3BE8C"
BLUE_ICON = "#5E81AC"
YELLOW_ICON = "#EBCB8B"
PURPLE_ICON = "#B48EAD"
CYAN_ICON = "#88C0D0"

FONT = ("Segoe UI", 10)
HEADER_FONT = ("Segoe UI", 10, "bold")

class TradingCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("📈 Advanced Trading Calculator")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("1100x900")
        
        self.emoji_font = Font(family="Segoe UI Emoji", size=12)
        
        self.setups = {}
        self.current_setup = None
        self.load_setups()
        
        self.trade_history = []
        self.cumulative_loss_ticks = 0
        self.cumulative_loss_value = 0
        self.total_commissions = 0
        self.current_trade_number = 1
        self.consecutive_losses = 0
        self.safe_mode = False
        
        self.create_widgets()
        self.setup_style()

    def load_setups(self):
        if os.path.exists("setups.json"):
            try:
                with open("setups.json", "r") as f:
                    self.setups = json.load(f)
            except Exception as e:
                messagebox.showwarning("Warning", f"Could not load setups: {str(e)}")
                self.setups = {}
        else:
            self.setups = {}

    def save_setups_to_file(self):
        try:
            with open("setups.json", "w") as f:
                json.dump(self.setups, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save setups: {str(e)}")

    def setup_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", 
                      background="#3B4252",
                      foreground=FG_COLOR,
                      rowheight=28,
                      fieldbackground="#3B4252",
                      borderwidth=0,
                      font=FONT)
        style.configure("Treeview.Heading", 
                      background=ACCENT_COLOR,
                      foreground=FG_COLOR,
                      font=HEADER_FONT)
        style.map('Treeview', background=[('selected', '#4C566A')])
        style.configure("oddrow.Treeview", background="#3B4252")
        style.configure("evenrow.Treeview", background="#434C5E")
        style.configure("TScale", background=BG_COLOR, troughcolor="#4C566A")
        style.configure("Horizontal.TScale", sliderthickness=15)

    def create_colored_label(self, parent, text, fg_color, font=None):
        lbl = tk.Label(parent, text=text, bg=BG_COLOR, fg=fg_color)
        if font:
            lbl.config(font=font)
        return lbl

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg=BG_COLOR, padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Setup management
        setup_frame = tk.LabelFrame(main_frame, text=" 🛠️ Setup Management ", 
                                 bg=BG_COLOR, fg=FG_COLOR, font=HEADER_FONT, padx=10, pady=10)
        setup_frame.pack(fill=tk.X, pady=(0, 10))

        self.create_colored_label(setup_frame, "Select Setup:", FG_COLOR, FONT).grid(row=0, column=0, sticky="w")
        self.setup_combo = ttk.Combobox(setup_frame, values=list(self.setups.keys()), state="readonly")
        self.setup_combo.grid(row=0, column=1, sticky="ew", padx=5)
        self.setup_combo.bind("<<ComboboxSelected>>", self.load_selected_setup)

        self.create_colored_label(setup_frame, "Setup Name:", FG_COLOR, FONT).grid(row=1, column=0, sticky="w")
        self.setup_name_entry = tk.Entry(setup_frame, bg="#3B4252", fg=FG_COLOR, insertbackground=FG_COLOR)
        self.setup_name_entry.grid(row=1, column=1, sticky="ew", padx=5)

        btn_frame = tk.Frame(setup_frame, bg=BG_COLOR)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=5)
        
        tk.Button(btn_frame, text="💾 Save", command=self.save_setup, 
                bg=ACCENT_COLOR, fg=FG_COLOR, font=self.emoji_font).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🗑️ Delete", command=self.delete_setup, 
                bg=ERROR_COLOR, fg=FG_COLOR, font=self.emoji_font).pack(side=tk.LEFT, padx=5)

        # Trading parameters
        param_frame = tk.LabelFrame(main_frame, text=" ⚙️ Trading Parameters ", 
                                  bg=BG_COLOR, fg=FG_COLOR, font=HEADER_FONT, padx=10, pady=10)
        param_frame.pack(fill=tk.X, pady=(0, 15))

        self.params = {
            "commission": {"label": "€ Commission (ticks):", "color": RED_ICON, "from_": 1, "to": 50, "default": 3},
            "stop_loss": {"label": "🔴 Stop Loss (ticks):", "color": RED_ICON, "from_": 1, "to": 50, "default": 16},
            "take_profit": {"label": "🟢 Take Profit (ticks):", "color": GREEN_ICON, "from_": 1, "to": 50, "default": 19},
            "tick_value": {"label": "💰 Tick Value (€):", "color": YELLOW_ICON, "from_": 0.1, "to": 10, "default": 1.25, "resolution": 0.05},
            "initial_contracts": {"label": "📊 Initial Contracts:", "color": BLUE_ICON, "from_": 1, "to": 20, "default": 1},
            "max_contracts": {"label": "🚦 Max Contracts:", "color": PURPLE_ICON, "from_": 1, "to": 50, "default": 10},
            "safe_after_losses": {"label": "🛡️ Safe after N losses:", "color": CYAN_ICON, "from_": 1, "to": 10, "default": 3},
            "safe_reduction": {"label": "🛡️ Safe reduction (%):", "color": CYAN_ICON, "from_": 10, "to": 90, "default": 50},
            "n_elements": {"label": "🔢 Table Rows:", "color": FG_COLOR, "from_": 1, "to": 100, "default": 10}
        }

        self.sliders = {}
        self.entries = {}
        
        for i, (key, param) in enumerate(self.params.items()):
            lbl = self.create_colored_label(param_frame, param["label"], param["color"], self.emoji_font)
            lbl.grid(row=i, column=0, sticky="w", pady=2)
            
            entry = tk.Entry(param_frame, bg="#3B4252", fg=param.get("color", FG_COLOR), 
                           insertbackground=FG_COLOR, width=8, justify=tk.RIGHT, font=FONT)
            entry.insert(0, str(param["default"]))
            entry.grid(row=i, column=1, padx=5, sticky="w")
            entry.bind("<Return>", self.update_slider_from_entry)
            entry.bind("<FocusOut>", self.update_slider_from_entry)
            self.entries[key] = entry
            
            slider = tk.Scale(param_frame, from_=param["from_"], to=param["to"], 
                            orient=tk.HORIZONTAL, bg=BG_COLOR, fg=param.get("color", FG_COLOR),
                            troughcolor="#4C566A", highlightbackground=BG_COLOR,
                            resolution=param.get("resolution", 1),
                            command=lambda v, k=key: self.update_entry_from_slider(v, k))
            slider.set(param["default"])
            slider.grid(row=i, column=2, sticky="ew", padx=5, pady=2)
            self.sliders[key] = slider

        # Action buttons
        btn_frame = tk.Frame(main_frame, bg=BG_COLOR)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="🔄 Calculate", command=self.calculate, 
                bg=ACCENT_COLOR, fg=FG_COLOR, font=self.emoji_font).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="✅ Win", command=self.record_win, 
                bg=GREEN_ICON, fg=BG_COLOR, font=self.emoji_font).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❌ Loss", command=self.record_loss, 
                bg=ERROR_COLOR, fg=BG_COLOR, font=self.emoji_font).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🔄 Reset", command=self.reset_trades, 
                bg=YELLOW_ICON, fg=BG_COLOR, font=self.emoji_font).pack(side=tk.LEFT, padx=5)
        self.safe_btn = tk.Button(btn_frame, text="🛡️ Safe: OFF", command=self.toggle_safe_mode, 
                                bg=BG_COLOR, fg=CYAN_ICON, font=self.emoji_font)
        self.safe_btn.pack(side=tk.LEFT, padx=5)

        # Info labels
        self.result_label = self.create_colored_label(main_frame, "", FG_COLOR, FONT)
        self.result_label.pack()
        
        self.history_label = self.create_colored_label(main_frame, "Trade History: None", YELLOW_ICON, FONT)
        self.history_label.pack()
        
        self.stats_label = self.create_colored_label(main_frame, 
            "Cumulative Loss: 0 ticks (€0.00) | Next Trade: #1 | Total Commissions: €0.00 | Consecutive Losses: 0", 
            BLUE_ICON, FONT)
        self.stats_label.pack()

        # Results table
        table_frame = tk.Frame(main_frame, bg=BG_COLOR)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        columns = ("Index", "Mode", "Contracts", "Ticks×Contracts", "Total Ticks", "Value (€)", "Risk %")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=14)
        self.table.pack(fill=tk.BOTH, expand=True)

        for col, heading in zip(columns, ["🔢 Index", "🛡️ Mode", "📊 Contracts", "⚖️ Ticks×Contracts", 
                                       "🧮 Total Ticks", "💶 Value (€)", "⚠️ Risk %"]):
            self.table.heading(col, text=heading, anchor="w")
            self.table.column(col, width=90, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.table.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.table.configure(yscrollcommand=scrollbar.set)

        self.table.tag_configure('oddrow', background='#3B4252')
        self.table.tag_configure('evenrow', background='#434C5E')
        self.table.tag_configure('safe', foreground=CYAN_ICON)

    def toggle_safe_mode(self):
        self.safe_mode = not self.safe_mode
        if self.safe_mode:
            self.safe_btn.config(text="🛡️ Safe: ON", bg=CYAN_ICON, fg=BG_COLOR)
        else:
            self.safe_btn.config(text="🛡️ Safe: OFF", bg=BG_COLOR, fg=CYAN_ICON)
        self.calculate()

    def update_entry_from_slider(self, value, key):
        self.entries[key].delete(0, tk.END)
        self.entries[key].insert(0, value)

    def update_slider_from_entry(self, event):
        for key, entry in self.entries.items():
            try:
                value = float(entry.get())
                slider = self.sliders[key]
                if value >= slider.cget("from") and value <= slider.cget("to"):
                    slider.set(value)
            except ValueError:
                pass

    def calculate(self):
        try:
            commission = float(self.entries["commission"].get())
            stop_loss = float(self.entries["stop_loss"].get())
            take_profit = float(self.entries["take_profit"].get())
            tick_value = float(self.entries["tick_value"].get())
            initial_contracts = int(float(self.entries["initial_contracts"].get()))
            max_contracts = int(float(self.entries["max_contracts"].get()))
            safe_after = int(float(self.entries["safe_after_losses"].get()))
            safe_reduction = int(float(self.entries["safe_reduction"].get()))
            n = int(float(self.entries["n_elements"].get()))

            self.table.delete(*self.table.get_children())
            
            for i in range(1, n + 1):
                # Calcola i contratti base
                if self.cumulative_loss_value > 0:
                    recovery_ticks = (self.cumulative_loss_value + (initial_contracts * commission * tick_value)) / tick_value
                    base_contracts = max(initial_contracts, -(-recovery_ticks // take_profit))
                else:
                    base_contracts = initial_contracts
                
                # Applica la modalità safe se attiva e necessario
                mode = "NORMAL"
                contracts = min(max_contracts, base_contracts)
                
                if self.safe_mode and self.consecutive_losses >= safe_after:
                    reduction = safe_reduction / 100
                    safe_contracts = max(1, int(contracts * (1 - reduction)))
                    contracts = min(contracts, safe_contracts)
                    mode = f"SAFE -{safe_reduction}%"
                
                # Calcoli finali
                total_ticks = (stop_loss * contracts) + (commission * contracts)
                total_value = total_ticks * tick_value
                risk_percentage = (total_value / (self.cumulative_loss_value + total_value)) * 100 if (self.cumulative_loss_value + total_value) > 0 else 0
                
                tag = ('evenrow', 'safe') if mode.startswith('SAFE') else ('evenrow',) if i % 2 == 0 else ('oddrow',)
                self.table.insert("", "end", 
                                values=(f"#{i}", 
                                       mode,
                                       f"{contracts}",
                                       f"{stop_loss} × {contracts}",
                                       f"{total_ticks}",
                                       f"€ {total_value:,.2f}",
                                       f"{risk_percentage:.1f}%"), 
                                tags=tag)

            self.result_label.config(text="✅ Calculation completed!", fg=SUCCESS_COLOR)
            self.update_stats_label()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input values: {str(e)}")
            self.result_label.config(text="❌ Error in calculation", fg=ERROR_COLOR)

    def record_win(self):
        try:
            tick_value = float(self.entries["tick_value"].get())
            take_profit = float(self.entries["take_profit"].get())
            contracts = self.calculate_current_contracts()
            
            profit = take_profit * contracts * tick_value
            self.trade_history.append((f"Win (+€{profit:.2f})", self.current_trade_number))
            self.cumulative_loss_ticks = 0
            self.cumulative_loss_value = 0
            self.consecutive_losses = 0
            self.current_trade_number += 1
            self.update_history_label()
            self.update_stats_label()
            self.calculate()
            self.result_label.config(text=f"✅ Trade #{self.current_trade_number-1} recorded as Win (+€{profit:.2f})", fg=SUCCESS_COLOR)
        except ValueError:
            messagebox.showerror("Error", "Invalid parameter values")

    def record_loss(self):
        try:
            commission = float(self.entries["commission"].get())
            stop_loss = float(self.entries["stop_loss"].get())
            tick_value = float(self.entries["tick_value"].get())
            contracts = self.calculate_current_contracts()
            
            loss = (stop_loss + commission) * contracts * tick_value
            self.cumulative_loss_ticks += stop_loss * contracts
            self.cumulative_loss_value += loss
            self.total_commissions += commission * contracts * tick_value
            self.consecutive_losses += 1
            self.trade_history.append((f"Loss (-€{loss:.2f})", self.current_trade_number))
            self.current_trade_number += 1
            self.update_history_label()
            self.update_stats_label()
            self.calculate()
            self.result_label.config(text=f"❌ Trade #{self.current_trade_number-1} recorded as Loss (-€{loss:.2f})", fg=ERROR_COLOR)
        except ValueError:
            messagebox.showerror("Error", "Invalid parameter values")

    def calculate_current_contracts(self):
        try:
            commission = float(self.entries["commission"].get())
            take_profit = float(self.entries["take_profit"].get())
            tick_value = float(self.entries["tick_value"].get())
            initial_contracts = int(float(self.entries["initial_contracts"].get()))
            max_contracts = int(float(self.entries["max_contracts"].get()))
            safe_after = int(float(self.entries["safe_after_losses"].get()))
            safe_reduction = int(float(self.entries["safe_reduction"].get()))
            
            if self.cumulative_loss_value > 0:
                recovery_ticks = (self.cumulative_loss_value + (initial_contracts * commission * tick_value)) / tick_value
                base_contracts = max(initial_contracts, -(-recovery_ticks // take_profit))
            else:
                base_contracts = initial_contracts
            
            contracts = min(max_contracts, base_contracts)
            
            if self.safe_mode and self.consecutive_losses >= safe_after:
                reduction = safe_reduction / 100
                contracts = max(1, int(contracts * (1 - reduction)))
            
            return contracts
        except ValueError:
            return 1

    def reset_trades(self):
        self.trade_history = []
        self.cumulative_loss_ticks = 0
        self.cumulative_loss_value = 0
        self.total_commissions = 0
        self.current_trade_number = 1
        self.consecutive_losses = 0
        self.update_history_label()
        self.update_stats_label()
        self.calculate()
        self.result_label.config(text="🔄 Trade history reset", fg=YELLOW_ICON)

    def update_history_label(self):
        if not self.trade_history:
            self.history_label.config(text="Trade History: None", fg=YELLOW_ICON)
        else:
            history_text = "Trade History: " + ", ".join([f"#{idx}{res}" for res, idx in self.trade_history])
            self.history_label.config(text=history_text, fg=YELLOW_ICON)

    def update_stats_label(self):
        stats_text = (f"Cumulative Loss: {self.cumulative_loss_ticks} ticks (€{self.cumulative_loss_value:.2f}) | "
                     f"Next Trade: #{self.current_trade_number} | "
                     f"Total Commissions: €{self.total_commissions:.2f} | "
                     f"Consecutive Losses: {self.consecutive_losses}")
        self.stats_label.config(text=stats_text, fg=BLUE_ICON)

    def save_setup(self):
        setup_name = self.setup_name_entry.get()
        if not setup_name:
            messagebox.showerror("Error", "Please enter a setup name")
            return
            
        setup_data = {}
        for key in self.params:
            try:
                if key == "tick_value":
                    setup_data[key] = float(self.entries[key].get())
                else:
                    setup_data[key] = int(float(self.entries[key].get()))
            except ValueError:
                messagebox.showerror("Error", f"Invalid value for {key}")
                return
        
        self.setups[setup_name] = setup_data
        self.setup_combo["values"] = list(self.setups.keys())
        self.save_setups_to_file()
        messagebox.showinfo("Success", f"Setup '{setup_name}' saved successfully")
        self.setup_name_entry.delete(0, tk.END)

    def delete_setup(self):
        setup_name = self.setup_combo.get()
        if not setup_name:
            return
            
        if messagebox.askyesno("Confirm", f"Delete setup '{setup_name}'?"):
            del self.setups[setup_name]
            self.setup_combo["values"] = list(self.setups.keys())
            self.setup_combo.set('')
            self.save_setups_to_file()

    def load_selected_setup(self, event=None):
        setup_name = self.setup_combo.get()
        if setup_name in self.setups:
            setup = self.setups[setup_name]
            for key in setup:
                if key in self.entries:
                    self.entries[key].delete(0, tk.END)
                    self.entries[key].insert(0, str(setup[key]))
                if key in self.sliders:
                    self.sliders[key].set(setup[key])

if __name__ == "__main__":
    root = tk.Tk()
    app = TradingCalculator(root)
    root.mainloop()