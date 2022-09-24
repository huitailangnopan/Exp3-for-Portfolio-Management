from cProfile import label
import exp3_trading
import pandas as pd
import numpy as np
import get_data_port
import matplotlib.pyplot as plt

backtest_data = get_data_port.get_data()
final_v = []
test_num = 50
for i in range(test_num):
    S = exp3_trading.backtest_portfolio_full(backtest_data)
    final_v.append(S)
final_v = np.array(final_v)
#print(final_v)

returns = (backtest_data - backtest_data.shift(1))/backtest_data.shift(1)
#diff = diff.mean(axis=0)
returns = returns[1:]
mean = returns.mean(axis=1)
baseline_value = []
for i in range(1,1440):
    if i==1:
        baseline_value.append(10000*(mean[1]+1))
    else:
        baseline_value.append((1+mean[i])*baseline_value[i-2])
#print(baseline_value)
strategy_return = {}
for i in range(test_num):
    strategy_return[i] = []
    for k in range(len(final_v[i])):
        strategy_return[i].append((final_v[i][k])*10000)


for i in range(test_num):
    plt.plot(strategy_return[i], label = str(i))
plt.plot(baseline_value, label = "baseline",linewidth = 5)
plt.legend()
plt.show()

num_more_base = 0
for i in range(test_num):
    if strategy_return[i][-1]>baseline_value[-1]:
        num_more_base = num_more_base+1
percent_more_base = num_more_base/test_num

strategy_return = pd.DataFrame.from_dict(strategy_return, orient='index')
sd = np.power(np.std((strategy_return.iloc[-1]-10000)/10000),1/4)
avg_return = np.power(np.mean((strategy_return.iloc[-1]-10000)/10000),1/4)
risk_free = 0.024
sharpe_ratio = (avg_return - risk_free)/sd
lowest_drawback = min((strategy_return.min()))
highest_value = max((strategy_return.max()))
print(f"sd: {sd},avg_return: {avg_return}, sharpe_ratio: {sharpe_ratio}, percent_more_base: {percent_more_base},lowest_drawback:{lowest_drawback}, highest_value:{highest_value}")
#print(exp3_return)

