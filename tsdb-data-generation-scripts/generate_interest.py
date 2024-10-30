import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
def calculate_borrow_rate(utilization_ratio, y0=0.052, y1=0.8, y_min=0.03, x_min=0.8):
    """
    Calculate the borrowing interest rate based on the utilization ratio.
    
    Parameters:
    -----------
    utilization_ratio : float
        The pool utilization ratio between 0 and 1
    y0 : float
        The interest rate when utilization is 0 (initial rate = 5.2%)
    y1 : float
        The interest rate when utilization is 1 (maximum rate = 200%)
    y_min : float
        The minimum interest rate at optimal utilization (set to 4.5%)
    x_min : float
        The optimal utilization ratio (0.8 = 80%)
        
    Returns:
    --------
    float
        The calculated borrowing interest rate
    """
    if not 0 <= utilization_ratio <= 1:
        raise ValueError("Utilization ratio must be between 0 and 1")
    
    alpha = 0.5 * (y0 - y_min)
    beta = 0.5 * (y1 - y0)
    kappa = 0.5 * (y0 + y_min)
    n = -1 / np.log2(x_min)
    
    X = 2 * np.pi * utilization_ratio ** n
    theta = 1.0 if utilization_ratio > x_min else 0.0
    
    rate = (alpha * np.cos(X) + 
           beta * (np.cos(X) + 1) * theta + 
           kappa)
    
    return rate

def calculate_lend_rate(borrow_rate, utilization_ratio, min_spread=0.12):
    """
    Calculate the lending interest rate based on the borrowing rate.
    Maintains a minimum spread below the borrowing rate.
    
    Parameters:
    -----------
    borrow_rate : float
        The borrowing interest rate
    utilization_ratio : float
        The pool utilization ratio between 0 and 1
    min_spread : float
        The minimum spread between borrow and lend rates (default 10% = 0.10)
        
    Returns:
    --------
    float
        The calculated lending interest rate
    """
    # Lending rate is borrowing rate * utilization ratio, but never closer than min_spread to borrow rate
    lend_rate = borrow_rate * utilization_ratio
    max_lend_rate = borrow_rate * (1 - min_spread)
    
    return min(lend_rate, max_lend_rate)

def plot_interest_rate_curves(points=101):
    """
    Plot both lending and borrowing interest rate curves.
    
    Parameters:
    -----------
    points : int
        Number of points to plot
    
    Returns:
    --------
    matplotlib.figure.Figure
        The generated plot figure
    """
    util_ratios = np.linspace(0, 1, points)
    util_ratios_nat = np.arange(0, points)  # Generate integers from 0 to 100
    borrow_rates = [calculate_borrow_rate(u) for u in util_ratios]
    lend_rates = [calculate_lend_rate(br, u) for br, u in zip(borrow_rates, util_ratios)]
    
    plt.figure(figsize=(12, 7))
    
    # Convert rates to percentages for clearer visualization
    borrow_rates_pct = [r * 100 for r in borrow_rates]
    lend_rates_pct = [r * 100 for r in lend_rates]
    df = pd.DataFrame({
        "utilization_rate": util_ratios_nat,
        "borrow_apy": borrow_rates,
        "supply_apy": lend_rates
    })
    df.to_csv("utilization_data.csv", index=False)
    print("CSV file 'utilization_data.csv' generated successfully!")

    plt.plot(util_ratios, borrow_rates_pct, 'b-', linewidth=2, label='Borrow Rate')
    plt.plot(util_ratios, lend_rates_pct, 'g-', linewidth=2, label='Lend Rate')
    plt.axvline(x=0.8, color='r', linestyle='--', alpha=0.5, label='Optimal Utilization (80%)')
    plt.grid(True, alpha=0.3)
    plt.xlabel('Utilization Ratio')
    plt.ylabel('Interest Rate (%)')
    plt.title('Lending Pool Interest Rate Model')
    plt.legend()
    
    # Add key points annotations
    plt.plot([0], [5.2], 'bo')
    plt.annotate('Base Borrow: 5.2%', xy=(0, 5.2), xytext=(0.05, 10),
                arrowprops=dict(facecolor='black', shrink=0.05))
    
    plt.plot([1], [80], 'bo')
    plt.annotate('Max Borrow: 80%', xy=(1, 80), xytext=(0.8, 90),
                arrowprops=dict(facecolor='black', shrink=0.05))
    
    # Add spread annotation at 80% utilization
    borrow_80 = calculate_borrow_rate(0.8)
    lend_80 = calculate_lend_rate(borrow_80, 0.8)
    plt.annotate(f'Spread at 80%: {(borrow_80 - lend_80)*100:.1f}%', 
                xy=(0.8, lend_80*100), xytext=(0.5, 50),
                arrowprops=dict(facecolor='black', shrink=0.05))
    
    return plt.gcf()

# Example usage and testing
if __name__ == "__main__":
    test_utilizations = [0, 0.2, 0.5, 0.8, 0.9, 0.95, 1.0]
    
    print("Interest rates at different utilization ratios:")
    print("Utilization | Borrow Rate | Lend Rate | Spread")
    print("-" * 55)
    
    for util in test_utilizations:
        borrow_rate = calculate_borrow_rate(util)
        lend_rate = calculate_lend_rate(borrow_rate, util)
        spread = borrow_rate - lend_rate
        print(f"{util:10.1%} | {borrow_rate:10.1%} | {lend_rate:9.1%} | {spread:6.1%}")
    
    # Plot the curves
    fig = plot_interest_rate_curves()
    plt.show()
