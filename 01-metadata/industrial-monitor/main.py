import asyncio
from datetime import datetime, timedelta
import yaml
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

# UI Libraries
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout

# Drivers (Assuming these are in your drivers/ folder)
from drivers.modbus_client import ModbusDriver
from drivers.opcua_client import OpcUaDriver

# Load Configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

class MonitorApp:
    def __init__(self):
        self.modbus = ModbusDriver(config['modbus_connection'], config['modbus_tags'])
        self.opcua = OpcUaDriver(config['opcua_connection'], config['opcua_tags'])
        
        # Buffers for plotting
        self.history_timestamps = []
        self.history_mb = {"cpu": [], "fan": [], "amb": []}
        self.history_ua = {"cpu": [], "fan": [], "amb": []}
        
        self.window_delta = timedelta(minutes=5)

        # Initialize Matplotlib Figure with 1 row, 2 columns for Side-by-Side comparison
        plt.style.use('dark_background')
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Helper to setup identical styling for both protocol plots
        def setup_pi_plot(ax, title, color_cpu, color_amb):
            ax.set_ylim(10, 75)
            ax.set_ylabel("Temperature °C")
            ax.set_title(title)
            ax.grid(True, alpha=0.1)
            ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
            
            line_cpu, = ax.plot([], [], label="CPU Temp", color=color_cpu, linewidth=2)
            line_amb, = ax.plot([], [], label="Ambient Temp", color=color_amb, linewidth=1.5, linestyle='--')
            
            # Fan Status on Secondary Axis
            ax_fan = ax.twinx()
            ax_fan.set_ylim(-0.1, 1.1)
            ax_fan.set_yticks([0, 1])
            ax_fan.set_yticklabels(['OFF', 'ON'])
            line_fan, = ax_fan.step([], [], label="Fan", color="#FFD700", linewidth=2, where='post')
            
            ax.legend(loc="upper left", fontsize='small')
            return line_cpu, line_amb, line_fan, ax_fan

        # Setup Modbus Plot (Left)
        self.ln_mb_cpu, self.ln_mb_amb, self.ln_mb_fan, self.ax_mb_fan = \
            setup_pi_plot(self.ax1, "Modbus Pi", "#00CED1", "#008B8B")
            
        # Setup OPC UA Plot (Right)
        self.ln_ua_cpu, self.ln_ua_amb, self.ln_ua_fan, self.ax_ua_fan = \
            setup_pi_plot(self.ax2, "OPC UA Pi", "#FF4500", "#CD5C5C")

        self.fig.tight_layout()

    def make_layout(self) -> Layout:
        """Defines the visual structure of the dashboard."""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", size=12),
            Layout(name="info", size=3)
        )
        layout["main"].split_row(
            Layout(name="modbus_pane"),
            Layout(name="opcua_pane")
        )
        return layout

    def generate_table(self, data):
        """Unified table format - UI is protocol-agnostic."""
        table = Table(expand=True, border_style="white", box=None)
        if not data:
            table.add_row("Connecting...", "", "")
            return table

        table.add_column("Parameter", style="cyan")
        table.add_column("Value", justify="right", style="bold green")
        table.add_column("Unit", style="dim")

        unit_map = {"Ambient Temp": "°C", "Humidity": "%", "CPU Temp": "°C"}

        for d in data:
            if "Gas" in d.name: continue # Hide gas as requested
                
            if isinstance(d.value, bool):
                val_str = "RUNNING" if d.value else "STOPPED"
                if "Status" not in d.name and "Fan" not in d.name: 
                    val_str = "ENABLED" if d.value else "PAUSED"
                style = "bold green" if d.value else "bold red"
                table.add_row(d.name, val_str, "", style=style)
            else:
                unit = unit_map.get(d.name, "")
                table.add_row(d.name, f"{d.value:.1f}", unit)
        return table

    async def run(self):
        layout = self.make_layout()
        plt.ion()
        plt.show()
        
        with Live(layout, refresh_per_second=2, screen=True) as live:
            while True:
                now = datetime.now()
                mb_data = self.modbus.read_all()
                ua_data = await self.opcua.read_all()
                
                # Update Plot Buffers
                self.history_timestamps.append(now)
                
                def get_val(data, key):
                    return next((d.value for d in data if key in d.name), 0)

                if mb_data:
                    self.history_mb["cpu"].append(get_val(mb_data, "CPU"))
                    self.history_mb["fan"].append(1 if get_val(mb_data, "Fan") else 0)
                    self.history_mb["amb"].append(get_val(mb_data, "Ambient"))

                if ua_data:
                    self.history_ua["cpu"].append(get_val(ua_data, "CPU"))
                    self.history_ua["fan"].append(1 if get_val(ua_data, "Fan") else 0)
                    self.history_ua["amb"].append(get_val(ua_data, "Ambient"))
                else:
                    self.history_ua["cpu"].append(0)
                    self.history_ua["fan"].append(0)
                    self.history_ua["amb"].append(0)
                
                # Trim Window (5 mins)
                cutoff = now - self.window_delta
                while self.history_timestamps and self.history_timestamps[0] < cutoff:
                    self.history_timestamps.pop(0)
                    for buf in [self.history_mb, self.history_ua]:
                        buf["cpu"].pop(0); buf["fan"].pop(0); buf["amb"].pop(0)

                # Update Matplotlib Lines
                if self.history_timestamps:
                    self.ln_mb_cpu.set_data(self.history_timestamps, self.history_mb["cpu"])
                    self.ln_mb_amb.set_data(self.history_timestamps, self.history_mb["amb"])
                    self.ln_mb_fan.set_data(self.history_timestamps, self.history_mb["fan"])
                    self.ln_ua_cpu.set_data(self.history_timestamps, self.history_ua["cpu"])
                    self.ln_ua_amb.set_data(self.history_timestamps, self.history_ua["amb"])
                    self.ln_ua_fan.set_data(self.history_timestamps, self.history_ua["fan"])
                    
                    self.ax1.set_xlim(now - self.window_delta, now)
                    self.ax2.set_xlim(now - self.window_delta, now)
                    self.fig.canvas.draw()
                    self.fig.canvas.flush_events()

                # Update Rich UI
                layout["header"].update(Panel(f"Dual Protocol Monitor | {now.strftime('%H:%M:%S')}", style="bold white on blue"))
                layout["modbus_pane"].update(Panel(self.generate_table(mb_data), title="MODBUS TCP"))
                layout["opcua_pane"].update(Panel(self.generate_table(ua_data), title="OPC UA"))
                
                await asyncio.sleep(1)

if __name__ == "__main__":
    app = MonitorApp()
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        plt.close()