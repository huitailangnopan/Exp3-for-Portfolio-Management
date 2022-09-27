# Exp3-for-Portfolio-Management
    Run main to test the performance. 
    Try General Backtest_exp3.ipynb for more realistic backtest and strategy construction.
    
# Intro
We pick 100 stocks in S&P500. We see each stock has an equal chance of profit(uniform distribution). Therefore, initially we set the weight of each stock as 0.01(1/100). In each following timestamp, exp3 will learn more about each stock's return, and therefore adjust the weight based on expected reward of each. 
