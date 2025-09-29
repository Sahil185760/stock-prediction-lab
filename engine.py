"""Expanding-window next-session return regression with a zero-return baseline."""
import math
from datetime import date
from models import finite, fit_ridge, predict, mean


def features(returns, i):
    trailing=returns[i-5:i]
    return [returns[i-1],mean(trailing),math.sqrt(mean([(r-mean(trailing))**2 for r in trailing]))]


def run(data):
    cutoff=date.fromisoformat(data['as_of'])
    observations=data['observations']
    days=[date.fromisoformat(r['date']) for r in observations]
    if any(day>cutoff for day in days):raise ValueError('Price after historical cutoff rejected')
    if any(a>=b for a,b in zip(days,days[1:])):raise ValueError('Price dates must be unique and ascending')
    prices=[finite(r['close'],'price') for r in observations]
    if not 80 <= len(prices) <= 1500 or min(prices)<=0:
        raise ValueError('Supply 80–1500 positive closing prices, oldest first')
    returns=[prices[i]/prices[i-1]-1 for i in range(1,len(prices))]
    x=[features(returns,i) for i in range(5,len(returns))]
    y=returns[5:]
    split=max(40,int(len(x)*.7))
    estimates=[]
    for i in range(split,len(x)):
        model=fit_ridge(x[:i],y[:i],2)
        estimates.append(predict(model,x[i]))
    actual=y[split:]
    model=fit_ridge(x,y,2)
    next_return=predict(model,features(returns,len(returns)))
    errors=[a-b for a,b in zip(actual,estimates)]
    return {'metrics':{'Walk-forward MAE':mean([abs(e) for e in errors]),'Zero-return baseline MAE':mean([abs(a) for a in actual]),'Directional accuracy':mean([float((a>0)==(b>0)) for a,b in zip(actual,estimates)]),'Next-session estimated return':next_return},'series':{'Actual return':actual,'Predicted return':estimates},'rows':[{'date':observations[split+i+6]['date'],'actual_return':a,'predicted_return':p} for i,(a,p) in enumerate(zip(actual,estimates))],'details':{'historical_as_of':data['as_of'],'latest_price_date':observations[-1]['date'],'provenance':data.get('provenance',{}),'training_rows_final':len(x),'test_rows':len(actual),'model':model,'estimated_next_close':prices[-1]*(1+next_return),'method':'Ridge regression, penalty 2; last return, trailing 5-return mean and volatility. Refit on past rows before each prediction. No future rows enter scaling or training. No trading profitability claim.'}}
