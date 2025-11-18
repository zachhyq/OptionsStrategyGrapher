# ============================================================
# 1. Imports
# ============================================================

import numpy as np
import matplotlib.pyplot as plt


# Later you can add Pandas, Plotly, QuantLib, etc. if you want.
# A. Payoff logic in OptionContract.payoff()
# Max/Min intrinsic logic
# Adjustment for long/short
# Adding/subtracting premium
# Multiplying by quantity
#
# B. Strategy aggregation logic
# Replace the placeholder pass with real accumulation
#
# C. Optional: Parity logic
# Build synthetic equivalents
# Compare strategy price vs parity-implied value
# Everything else (flow, structure, plotting) is ready for you.

# ============================================================
# 2. Contract Class
# ============================================================

class OptionContract:
    def __init__(self, option_type, position, strike, premium, quantity=1, rate=0.0, maturity=1.0):
        """
        option_type: 'call' or 'put' or 'underlying'
        position: 'long' or 'short'
        strike: K
        premium: option premium paid/received
        quantity: number of contracts (can be negative instead of using position)
        rate: risk-free rate (for parity calculations)
        maturity: time to expiry (for parity or discounting)
        """
        self.option_type = option_type
        self.position = position
        self.strike = strike
        self.premium = premium
        self.quantity = quantity
        self.rate = rate
        self.maturity = maturity

    def payoff(self, S):
        """
        Compute payoff array for this contract.
        * Implement the actual payoff logic here.
        * S will be a NumPy array of underlying prices.

        Return a NumPy array of same length as S.
        """

        # e.g., intrinsic = np.maximum(S - self.strike, 0) for calls
        # then subtract the premium
        # then flip if short
        # then adjust for quantity

        # Determine shape of the payoff graph
        if self.option_type == 'call':
            intrinsic = np.maximum(S - self.strike, 0)
        elif self.option_type == 'put':
            intrinsic = np.maximum(self.strike - S, 0)
        else:
            intrinsic = S - self.strike

        #Premium
        intrinsic = intrinsic - self.premium

        # Position (reflect in x-axis if it's a short)
        if self.position == 'short':
            intrinsic *= -1

        intrinsic *= self.quantity

        return intrinsic


# ============================================================
# 3. Strategy Class
# ============================================================

class OptionStrategy:
    def __init__(self, contracts):
        """
        contracts: list of OptionContract objects
        """
        self.contracts = contracts

    def total_payoff(self, S):
        """
        Sum payoffs of all contracts to get the strategy payoff.
        """
        # Initialize accumulator
        total = np.zeros_like(S, dtype=float)

        # Loop through contracts and add their individual payoff arrays
        for c in self.contracts:
            # TODO: add c.payoff(S) to total once payoff() is implemented
            total += c.payoff(S)

        return total

    def parity_value(self, S):
        """
        (Optional) Compute put–call parity-based value of strategy.
        - You can implement a conversion of all legs into synthetic equivalents.
        - Or compute C - P vs S - K*exp(-rT), depending on your design.

        Return array same length as S.
        """
        # TODO: implement strategy-level parity logic if desired.
        pass


# ============================================================
# 4. Graphing / Plotting
# ============================================================

def plot_strategy(S, payoff, parity=None):
    """
    Basic plotting function.

    S: price grid
    payoff: total payoff array
    parity: optional array for parity comparison
    """
    plt.figure(figsize=(10, 6))

    # Plot payoff line
    plt.plot(S, payoff, label="Strategy Payoff", linewidth=2)

    # Optional parity line
    if parity is not None:
        plt.plot(S, parity, label="Parity Value", linestyle='--')

    # Add labels and styling
    plt.title("Options Strategy Payoff / Parity Graph")
    plt.xlabel("Underlying Price (S)")
    plt.ylabel("Profit / Loss")
    plt.grid(True)
    plt.legend()
    plt.show()


# ============================================================
# 5. Main Program Flow
# ============================================================

def main():
    # Step 1: Create the underlying price grid
    # TODO: adjust range as needed
    S = np.linspace(50, 150, 500)

    # Step 2: Define contracts
    # TODO: modify these with real values or load dynamically
    c1 = OptionContract("call", "long", 95, premium=6.25)
    c2 = OptionContract("call", "short", 105, premium=1.75)
    c3 = OptionContract("put", "short", 105, premium=7.75, quantity=2)
    c4 = OptionContract("underlying", "short", 98, premium=0, quantity=2)


    # Step 3: Build strategy
    strategy = OptionStrategy([c1, c2, c3, c4])

    # Step 4: Compute payoffs
    payoff = strategy.total_payoff(S)

    # Optional: compute parity comparison line
    # parity = strategy.parity_value(S)
    parity = None

    # Step 5: Plot
    plot_strategy(S, payoff, parity)


# ============================================================
# 6. Entry Point
# ============================================================

if __name__ == "__main__":
    main()