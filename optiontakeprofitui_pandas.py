import tkinter as tk
from datetime import datetime
import yfinance as yf
import math
import numpy as np
import time

# -------------------------------
# Black-Scholes Option Pricing
# -------------------------------
def black_scholes_call(S, K, T, r, sigma, q=0):
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    N = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
    return S * math.exp(-q * T) * N(d1) - K * math.exp(-r * T) * N(d2)

# -------------------------------
# Monte Carlo Simulation
# -------------------------------
def monte_carlo_option_hit(S0, K, T, r, sigma, threshold, q=0, n_paths=20000, n_steps=126):
    dt = T / n_steps
    np.random.seed(42)
    Z = np.random.normal(size=(n_paths, n_steps))
    S = np.zeros_like(Z)
    S[:, 0] = S0
    for t in range(1, n_steps):
        S[:, t] = S[:, t-1] * np.exp((r - q - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z[:, t])

    hit_mask = np.any(S >= threshold, axis=1)
    hit_prob = hit_mask.mean()
    hit_indices = np.argmax(S >= threshold, axis=1)
    hit_times = hit_indices[hit_mask] * dt
    avg_hit_time = hit_times.mean() if hit_times.size > 0 else None

    payoff = np.where(hit_mask, threshold - K, 0)
    PV = np.mean(payoff) * math.exp(-r * T)
    return hit_prob, avg_hit_time, PV

# -------------------------------
# Autofill from Ticker
# -------------------------------
def autofill_from_ticker(ticker):
    info = {}
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        info['spot'] = float(hist['Close'].iloc[-1]) if not hist.empty else None

        fast_info = stock.fast_info
        info['dividend'] = fast_info.get("dividend_yield", 0.0) * 100
        info['volatility'] = fast_info.get("implied_volatility", 0.30) * 100
        info['risk_free'] = 4.5  # Assume fixed 4.5%

        return info
    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# Main App Class
# -------------------------------
class OptionPricerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Option Take-Profit Analyzer")

        self.fields = [
            "Ticker", "Spot Price, S0", "Strike Price, K", "Risk-Free r (%)",
            "Dividend q (%)", "Volatility σ (%)", "Expiration Date (MMDDYYYY)",
            "Take-Profit Multiple", "Bid Price", "Ask Price"
        ]
        self.entries = {}

        for i, field in enumerate(self.fields):
            tk.Label(root, text=field).grid(row=i, column=0)
            entry = tk.Entry(root, width=25)
            entry.grid(row=i, column=1)
            self.entries[field] = entry

        # Buttons (Row = len(self.fields))
        row_offset = len(self.fields)
        tk.Button(root, text="Autofill From Ticker", command=self.autofill).grid(row=row_offset, column=0, pady=10)
        tk.Button(root, text="Run Simulation", command=self.run).grid(row=row_offset, column=1, pady=10)
        tk.Button(root, text="Clear Inputs", command=self.clear_inputs).grid(row=row_offset, column=0, columnspan=2)

        # Output Box (Placed below buttons)
        self.txt = tk.Text(root, height=12, width=85)
        self.txt.grid(row=row_offset+2, column=0, columnspan=2, pady=(10, 0))

    def autofill(self):
        ticker = self.entries["Ticker"].get().strip().upper()
        data = autofill_from_ticker(ticker)
        if "error" in data:
            self.txt.insert(tk.END, f"[!] Error fetching data for {ticker}: {data['error']}\n")
            self.txt.see(tk.END)
            return

        self.entries["Spot Price, S0"].delete(0, tk.END)
        self.entries["Risk-Free r (%)"].delete(0, tk.END)
        self.entries["Dividend q (%)"].delete(0, tk.END)
        self.entries["Volatility σ (%)"].delete(0, tk.END)

        self.entries["Spot Price, S0"].insert(0, str(round(data['spot'], 2)))
        self.entries["Risk-Free r (%)"].insert(0, str(round(data['risk_free'], 2)))
        self.entries["Dividend q (%)"].insert(0, str(round(data['dividend'], 2)))
        self.entries["Volatility σ (%)"].insert(0, str(round(data['volatility'], 2)))

        self.txt.insert(tk.END, f"[✓] Autofilled for {ticker}\n")
        self.txt.see(tk.END)

    def clear_inputs(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.txt.insert(tk.END, "[✓] Inputs cleared.\n")
        self.txt.see(tk.END)

    def run(self):
        try:
            S0 = float(self.entries["Spot Price, S0"].get())
            K = float(self.entries["Strike Price, K"].get())
            r = float(self.entries["Risk-Free r (%)"].get()) / 100
            q = float(self.entries["Dividend q (%)"].get()) / 100
            sigma = float(self.entries["Volatility σ (%)"].get()) / 100
            bid = float(self.entries["Bid Price"].get())
            ask = float(self.entries["Ask Price"].get())
            midpoint = (bid + ask) / 2

            raw_date = self.entries["Expiration Date (MMDDYYYY)"].get().strip()
            if len(raw_date) != 8 or not raw_date.isdigit():
                self.txt.insert(tk.END, "[!] Expiration date must be 8 digits in MMDDYYYY format (e.g., 12202025)\n")
                self.txt.see(tk.END)
                return
            month = int(raw_date[:2])
            day = int(raw_date[2:4])
            year = int(raw_date[4:])
            expiry_date = datetime(year, month, day).date()
            T = (expiry_date - datetime.today().date()).days / 365.0
            if T <= 0:
                self.txt.insert(tk.END, "[!] Expiration must be in the future\n")
                self.txt.see(tk.END)
                return

            multiple = float(self.entries["Take-Profit Multiple"].get())
            threshold = midpoint * multiple

            start = time.time()
            C0 = black_scholes_call(S0, K, T, r, sigma, q)
            hit_prob, avg_hit_time, PV = monte_carlo_option_hit(S0, K, T, r, sigma, threshold, q)
            end = time.time()

            diff = midpoint - C0
            verdict = "FAIRLY PRICED" if abs(diff) < 0.01 else ("UNDERVALUED" if diff > 0 else "OVERVALUED")
            diff_percent = 100 * diff / C0

            self.txt.insert(tk.END, "\n")
            self.txt.insert(tk.END, f"Verdict:         {verdict} ({diff:+.2f}, {diff_percent:+.2f}%)\n")
            self.txt.insert(tk.END, f"Midpoint Price:  {midpoint:.2f} (Bid: {bid}, Ask: {ask})\n")
            self.txt.insert(tk.END, f"BS Fair Value:   {C0:.2f}\n")
            self.txt.insert(tk.END, f"Threshold:       {threshold:.2f}\n")
            self.txt.insert(tk.END, f"PV (sell@thr):   {PV:.2f}\n")
            self.txt.insert(tk.END, f"Hit Probability: {hit_prob*100:.2f}%\n")
            self.txt.insert(tk.END, f"Avg Hit Time:    {avg_hit_time:.2f} yrs\n" if avg_hit_time else "Avg Hit Time:    N/A\n")
            self.txt.insert(tk.END, f"Time to Expiry:  {T:.2f} yrs\n")
            self.txt.insert(tk.END, f"Runtime:         {end-start:.2f} s\n")
            self.txt.see(tk.END)

        except Exception as e:
            self.txt.insert(tk.END, f"[!] Error: {e}\n")
            self.txt.see(tk.END)

# -------------------------------
# Launch the App
# -------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = OptionPricerApp(root)
    root.mainloop()