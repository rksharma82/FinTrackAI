import pandas as pd
import random
from datetime import date, timedelta

# Constants
START_DATE = date(2025, 1, 1)
END_DATE = date(2025, 11, 30)
SALARY_ANNUAL = 250000
TAX_RATE = 0.35 # Approximate deductions
NET_SALARY = SALARY_ANNUAL * (1 - TAX_RATE)
BIWEEKLY_NET = NET_SALARY / 26
BOA_SPLIT = 0.30
BAXTER_SPLIT = 0.70

# Helper to generate bi-weekly pay dates (Starting Jan 3, 2025)
def get_biweekly_pay_dates(start_date, end_date):
    pay_dates = []
    current = date(2025, 1, 3) # First Friday of 2025
    while current <= end_date:
        if current >= start_date:
            pay_dates.append(current)
        current += timedelta(weeks=2)
    return pay_dates

pay_dates = get_biweekly_pay_dates(START_DATE, END_DATE)

# ---------------------------------------------------------
# 1. Bank of America (BoA) - Checking
# Format: Date, Description, Amount
# ---------------------------------------------------------
boa_data = []

# Income
for d in pay_dates:
    amount = round(BIWEEKLY_NET * BOA_SPLIT, 2)
    boa_data.append([d, "DES: PAYROLL DEPOSIT ID: 998877", amount])

# Expenses & Transfers
current = START_DATE
while current <= END_DATE:
    # Random Daily Expenses
    if random.random() < 0.4: # 40% chance
        amt = -round(random.uniform(20, 150), 2)
        desc = random.choice(["WALMART GROCERY", "KROGER #443", "STARBUCKS COFFEE", "UBER EATS"])
        boa_data.append([current, desc, amt])
    
    if random.random() < 0.1: # 10% chance
        amt = -round(random.uniform(50, 200), 2)
        desc = random.choice(["CITY WATER BILL", "NETFLIX COM", "AMZN Mktp US", "TARGET"])
        boa_data.append([current, desc, amt])
    
    # Monthly Transfer to Investment Account
    if current.day == 15: 
        amt = -500.00
        boa_data.append([current, "Online Transfer to Fidelity Inv", amt])

    current += timedelta(days=1)

df_boa = pd.DataFrame(boa_data, columns=["Date", "Description", "Amount"])
df_boa.sort_values("Date", inplace=True)
df_boa.to_csv('boa_transactions_2025.csv', index=False)
print("Generated boa_transactions_2025.csv")


# ---------------------------------------------------------
# 2. Baxter Credit Union (BCU) - Main Savings/Mortgage
# Format: Posted Date, Transaction Details, Debit, Credit
# ---------------------------------------------------------
baxter_data = []

# Income
for d in pay_dates:
    amount = round(BIWEEKLY_NET * BAXTER_SPLIT, 2)
    baxter_data.append([d, "DIRECT DEP ACME CORP", 0, amount])

# Monthly Mortgage & Transfers
current = START_DATE
while current <= END_DATE:
    if current.day == 1:
        baxter_data.append([current, "MORTGAGE PAYMENT 4432", 3200.00, 0])
    
    # Monthly Transfer to Roth IRA
    if current.day == 5: 
        baxter_data.append([current, "TRANSFER TO FIDELITY ROTH IRA", 600.00, 0])
        
    current += timedelta(days=1)

df_baxter = pd.DataFrame(baxter_data, columns=["Posted Date", "Transaction Details", "Debit", "Credit"])
df_baxter.sort_values("Posted Date", inplace=True)
df_baxter.to_csv('baxter_cu_transactions_2025.csv', index=False)
print("Generated baxter_cu_transactions_2025.csv")


# ---------------------------------------------------------
# 3. Fidelity Individual Investment (Non-Retirement)
# Format: Run Date, Action, Symbol, Description, Amount
# ---------------------------------------------------------
fid_inv_data = []

current = START_DATE
while current <= END_DATE:
    # Receive Transfer from BoA (Day 16)
    if current.day == 16:
        fid_inv_data.append([current, "EFT", "", "ELECTRONIC FUNDS TRANSFER RECEIVED (CASH)", 500.00])
        
        # Invest money 2 days later (Day 18)
        buy_date = current + timedelta(days=2)
        if buy_date <= END_DATE:
            fid_inv_data.append([buy_date, "BUY", "FXAIX", "FIDELITY 500 INDEX FUND", -490.00])
            
    current += timedelta(days=1)

df_fid_inv = pd.DataFrame(fid_inv_data, columns=["Date", "Action", "Symbol", "Description", "Amount"])
df_fid_inv.to_csv('fidelity_individual_2025.csv', index=False)
print("Generated fidelity_individual_2025.csv")


# ---------------------------------------------------------
# 4. Fidelity Roth IRA
# Format: Run Date, Account, Action, Symbol, Security Description, Quantity, Price, Amount
# ---------------------------------------------------------
fid_roth_data = []

current = START_DATE
while current <= END_DATE:
    # Receive Transfer from Baxter (Day 6)
    if current.day == 6:
        fid_roth_data.append([current, "Roth IRA", "EFT RECEIVED", "", "Cash Contribution", "", "", 600.00])
        
        # Buy Stocks (Day 7)
        buy_date = current + timedelta(days=1)
        if buy_date <= END_DATE:
            fid_roth_data.append([buy_date, "Roth IRA", "YOU BOUGHT", "NVDA", "NVIDIA CORP", 2, 140.00, -280.00])
            fid_roth_data.append([buy_date, "Roth IRA", "YOU BOUGHT", "TSLA", "TESLA INC", 1, 250.00, -250.00])
    
    current += timedelta(days=1)

df_fid_roth = pd.DataFrame(fid_roth_data, columns=["Run Date", "Account", "Action", "Symbol", "Security Description", "Quantity", "Price", "Amount"])
df_fid_roth.to_csv('fidelity_roth_2025.csv', index=False)
print("Generated fidelity_roth_2025.csv")