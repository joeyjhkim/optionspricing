# optionspricing
fair value pricing for options calculator
A Python-based GUI app built with tkinter to help traders evaluate whether an options contract is undervalued, fairly priced, or overvalued—and how likely it is to reach a target profit before expiration.

⸻

Key Features
	•	Black-Scholes Option Pricing
Calculate theoretical fair value of a call option using the Black-Scholes model.
	•	Monte Carlo Simulation
Simulate thousands of price paths to estimate:
	•	Probability of hitting a take-profit threshold
	•	Average time to hit target
	•	Present value of that potential payoff
	•	Smart Verdict System
Compare current option midpoint price to theoretical value and categorize as:
	•	UNDERVALUED
	•	FAIRLY PRICED
	•	OVERVALUED
	•	Live Market Data via Yahoo Finance
Autofills key fields like spot price, dividend yield, and implied volatility.
	•	Visual Verdicts + Auto-Scroll Output
Simulation results are color-tagged for quick decision-making and auto-scroll to latest log.
	•	Input Management
Includes “Clear Inputs” button for fast reset and clean reruns.

⸻

How It Works

Calculations
	•	Black-Scholes Price (C0): Theoretical fair value
	•	Midpoint: Average of bid and ask
	•	Verdict:
	•	If midpoint > C0 + $0.01 → UNDERVALUED
	•	If midpoint < C0 - $0.01 → OVERVALUED
	•	Else → FAIRLY PRICED
	•	Monte Carlo Output:
	•	Hit Probability: % chance of price hitting the take-profit target
	•	Avg Hit Time: Expected time to reach threshold
	•	PV: Discounted value of the payoff if threshold is hit

⸻

Example Use Case
	1.	Enter a ticker and press “Autofill From Ticker”
	2.	Fill in the strike, bid, ask, and expiration
	3.	Choose a Take-Profit Multiple (e.g., 2.0 = double)
	4.	Press “Run Simulation”
	5.	Review the verdict and simulation stats

⸻

Upcoming Features
	•	Greeks Calculator (Delta, Gamma, Theta, Vega, Rho)
	•	ML-Based Implied Volatility Estimator


⸻

Technologies Used
	•	Python 3
	•	tkinter (GUI)
	•	numpy, math (simulations and pricing logic)
	•	yfinance (market data)


How to Run
Install dependencies (in terminal)
  •	pip install yfinance numpy
Run the program
  •	python3 option_analyzer.py
