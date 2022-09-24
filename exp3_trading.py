from pytz import timezone
import csv
import pandas as pd
import numpy as np
import get_data_port


class Backtest:
    def __init__(self,
                 df:pd.DataFrame,   #indexed by time, price df
                 strategy: None,
                 cash: float = 10000,
                 commission: float = .001,
                 future = False):
        # check for NaN
        assert(not df.isnull().values.any())
        # check for time sequence
        if not df.index.is_monotonic_increasing:
            df = df.sort_index()

        self.df = df        # nxm (num_periods, num_assets)
        self.strategy = strategy
        self.stock_pool = self.df.columns
        self.init_cap = cash
        self.cash = cash               #currently used as init cap, need to be changed in realistic case
        self.portfolio_value = 0
        self.value = self.get_value()    #value = portfolio+cash
        self.X = self.get_X()
        self.S = []
        self.bs = []
        self.times = self.df.index
        self.times_X = self.X.index
        self.current_time = self.times[0]
        self.future = future
    def get_value(self):
        self.value = self.cash+self.portfolio_value
        #self.value = self.portfolio_value
        return self.value
    def get_value_array(self):
        return [i * 10000 for i in self.S]

    def get_cash(self):
        return self.cash
    def get_portfolio_value(self):
        return self.portfolio_value
    def get_X(self):
        return (self.df/self.df.shift(1)).dropna()
    def get_S(self):
        return [i for i in self.S]
    def get_transaction_cost_factor(self,bs_change):
        bs_change = [abs(i) for i in bs_change]
        return (1-sum(bs_change)*0.02)
    def algo1(self, verbose=False, trans_fee=False):
        print('-'*90)
        print('Backtest starts! \nInitial Capital = {}'.format(self.value))
        print('\n')

        strat = self.strategy
        self.S.append(1.0)
        self.bs.append(np.ones_like(self.X.iloc[0])/len(self.X.iloc[0]))
        #first period
        self.S.append(self.S[-1]*(self.X.iloc[0].dot(self.bs[0])))
        for i in self.times_X:
            self.current_time = i
            if i == self.times_X[0]:
                continue
            if self.future:
                window = self.X.loc[:i,:]
            else:
                window = self.X.loc[:i-1,:]
            b_temp = strat.compute(window)
            # b_temp = np.ones_like(self.X.iloc[0])/len(self.X.iloc[0])
            transaction_cost_factor = self.get_transaction_cost_factor(b_temp-self.bs[-1])
            self.bs.append(b_temp)
            factor_temp = self.X.loc[i].dot(b_temp)
            self.S.append(self.S[-1]*factor_temp)
            self.portfolio_value = self.S[-1]*self.init_cap
            self.portfolio_value = self.S[-1]*self.init_cap
            self.get_value()
            strat.update(window)
            if verbose:
                print(str(self.current_time)+', the total capital is {}'.format(self.S[-1]*self.init_cap))
        print('\nBacktest ends! \nFinal Capital = {}'.format(self.value))
        print('-'*90)
        return self.S
    def create_timed_portfolio_value(self):
        temp = np.array(self.S)*self.init_cap
        # times_temp = self.times.insert(0,self.times[0]-pd.to_timedelta(1, unit='d') )
        times_temp = self.times
        return pd.DataFrame(temp, index=times_temp, columns = ['portfolio_value'])
    def create_timed_return(self):
        temp = np.array(self.S)
        # times_temp = self.times.insert(0,self.times[0]-pd.to_timedelta(1, unit='d') )
        times_temp = self.times
        res = pd.DataFrame(temp, index=times_temp, columns = ['return'])
        return (res/res.shift(1)-1).dropna()
    def analysis_pf(self):
        #the method takes a series of returns indexed by dates as input, not df

        return pf.create_full_tear_sheet(self.create_timed_return()['return'])
        return pf.create_returns_tear_sheet(self.create_timed_return()['return'])




class Strategy():
    def __init__(self):
        self.cache = {}
    def compute(self, window):
        return np.ones_like(window.iloc[0])/len(window.iloc[0])
    def update(self, window):
        return


class EXP3_trading(Strategy):
    def __init__(self, k, η):
        super(EXP3_trading,self).__init__()
        self.k = k
        self.η = η
        self.S = []
        self.P = []
        self.X = [0]
        self.regret = [0]
        self.A = []
        self.S.append(np.zeros(k))
    def compute(self, window):
        Pt = np.exp(self.η*self.S[-1])/np.exp(self.η*self.S[-1]).sum()
        self.P.append(Pt)
        At = self.draw(Pt)
        self.A.append(At)
        # res = np.zeros(self.k)
        # res[At] = 1
        return Pt
    def update(self, window):
        Xt = np.log(window.iloc[-1,:].values[self.A[-1]])
        self.X.append(self.X[-1]+Xt)
        At = self.A[-1]
        St = self.S[-1]+1
        # print(Xt)
        St[At] = St[At]-(1-Xt)/self.P[-1][At]
        self.S.append(St)
        return
    def draw(self, Pt):
        cut = np.random.uniform(0,1)
        for i in range(len(Pt)):
            cut -= Pt[i]
            if cut < 0:
                break
        return i


def backtest_portfolio_full(data):
    #data = get_data_port.get_data()

    exp3 = EXP3_trading(len(data.columns), 0.3)

    res_df = pd.DataFrame(columns=["exp3"])

    exp3_test = Backtest(data, strategy=exp3)
    final_value = exp3_test.algo1()
    res_df['exp3'] = exp3_test.get_value_array()
    res_df['exp3_weight'] = exp3_test.get_S()

    res_df.to_csv("portfolio_backtest_result.csv",index = False)
    print("done")
    return final_value
'''
def backtest_portfolio():

    data3 = get_data_port.get_data()
    strat = EXP3_trading(len(data3.columns),0.3)
    # strat = Strategy()

    # strat = BAH(np.ones(len(data3.columns))/len(data3.columns))
    a = Backtest(data3, strategy=strat)
    a.algo1()
    #temp = a.analysis_pf()
    return a.S
    exp3_return = (a.S[-1]-1)*100
'''