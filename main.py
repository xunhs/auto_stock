# -*- coding: utf-8 -*-

import akshare as ak
import yfinance as yf  
from datetime import datetime, timedelta
import numpy as np
import datetime
import pandas as pd
import io
import requests

import pyecharts.options as opts
from pyecharts.charts import Line, Timeline
from pyecharts.globals import ThemeType
from pyecharts.commons.utils import JsCode
# inital
from pyecharts.globals import CurrentConfig, NotebookType

# CurrentConfig.NOTEBOOK_TYPE = NotebookType.JUPYTER_LAB


line = Line()
line.load_javascript()


def get_yesterday(n=10):
    today = datetime.date.today()
    oneday = datetime.timedelta(days=n * 365)
    yesterday = today-oneday
    return yesterday


def get_stock_line(title_str, data_df, support_line):
    
#     one_day = get_yesterday(10)
    date_list = data_df['date'].tolist()
#     first = date_list[0]
#     if first < one_day:
#         data_df = data_df[data_df['date'] >= one_day]
    
    
    line = Line(init_opts=opts.InitOpts(width="900px",
                                        height="500px",
                                        theme=ThemeType.LIGHT
                                        ))
    line.add_xaxis(xaxis_data=date_list)

    stock_values = data_df['close'].tolist()
    line.add_yaxis(
        series_name="收盘价",
        y_axis=stock_values,
    )
    
    
    min_support_line = None
    _list = []
    for (support_name,support_value) in support_line.items():
        if '支撑' in str(support_name) and support_value != None:
            _list.append(support_value)
    if _list != []:
        min_support_line = min(_list)
    
    support_line_70 = max(stock_values) * 0.3
    support_line_80 = max(stock_values) * 0.2
    _max = np.max(stock_values)
    _min = np.min(stock_values)
    now = stock_values[-1]   
    now_per = 100 / (_max - _min) * (now - _min)
    
    if min_support_line == None:
        dis_per = (now-support_line_70)/now * 100
    else:
        dis_per = (now-min_support_line)/now * 100
    subtitle_str = '目前点位{}，所处百分位{}%，距离支撑位{}%'.format(now, round(now_per, 2), round(dis_per,2))
    
    
    line.set_global_opts(
        title_opts=opts.TitleOpts(title=title_str, subtitle=subtitle_str),
        # yaxis_opts=opts.AxisOpts(max_=_max, min_=_min),
        tooltip_opts = opts.TooltipOpts(is_show = True, trigger_on = "mousemove | click", axis_pointer_type='cross'),
        datazoom_opts=opts.DataZoomOpts(orient="horizontal", range_start=0,range_end=100), 
    )

    markline_data = [
                opts.MarkLineItem(y=support_line_70, name="70线", linestyle_opts=opts.LineStyleOpts(type_='dashed',color='rgb(38, 70, 83)')),
                opts.MarkLineItem(y=support_line_80, name="80线", linestyle_opts=opts.LineStyleOpts(type_='dashed',color='rgb(38, 70, 83)')),
            ]
    
    for (support_name,support_value) in support_line.items():
        if '支撑' in str(support_name) and support_value != None:
            _linestyle_opts = opts.LineStyleOpts(type_='dashed',color='rgb(232, 197, 107)')
            _item = opts.MarkLineItem(y=support_value, name=support_name, linestyle_opts=_linestyle_opts)
            markline_data.append(_item)
        elif '压力' in str(support_name) and support_value != None:
            _linestyle_opts = opts.LineStyleOpts(type_='dashed',color='rgb(230, 111, 81)')
            _item = opts.MarkLineItem(y=support_value, name=support_name, linestyle_opts=_linestyle_opts)
            markline_data.append(_item)
        else:
            print(f'{support_name} is {support_value}!')
            

    line.set_series_opts(
        yaxis_opts=opts.AxisOpts(max_='dataMax', min_='dataMin'),
        markline_opts=opts.MarkLineOpts(
            data= markline_data
        ),
    )
    return line


def get_pe_line(title_str, data_df, indicator = "市盈率"):
#     one_day = get_yesterday(10)
    date_list = data_df['date'].tolist()
#     first = date_list[0]
#     if first < one_day:
#         data_df = data_df[data_df['date'] >= one_day]

    line = Line(init_opts=opts.InitOpts(width="900px",
                                        height="500px",
                                        theme=ThemeType.LIGHT
                                        ))
    line.add_xaxis(xaxis_data=date_list)


    
    pe_values = data_df[indicator].tolist()
    line.add_yaxis(
        series_name=indicator,
        y_axis=pe_values,
    )


    _max = np.max(pe_values)
    pe_90 = np.percentile(pe_values,90)
    pe_75 = np.percentile(pe_values,75)
    average = np.mean(pe_values)
    pe_20 = np.percentile(pe_values,20)
    pe_10 = np.percentile(pe_values,10)
    _min = np.min(pe_values)
    now = pe_values[-1]   
    subtitle_str = '目前点位{}，距离20分位{}%, 距离10分位{}%'.format(now, round((now-pe_20)/now * 100,2), round((now-pe_10)/now * 100,2))

    line.set_global_opts(
        title_opts=opts.TitleOpts(title='{}-{}'.format(title_str, indicator), subtitle=subtitle_str),
        yaxis_opts=opts.AxisOpts(max_=_max, min_=_min),
        tooltip_opts = opts.TooltipOpts(is_show = True, trigger_on = "mousemove | click", axis_pointer_type='cross'),
        datazoom_opts=opts.DataZoomOpts(orient="horizontal", range_start=0,range_end=100), 
    )


    line.set_series_opts(
        
        markline_opts=opts.MarkLineOpts(
            data=[
                opts.MarkLineItem(y=pe_90, name="pe_90",linestyle_opts=opts.LineStyleOpts(type_='dashed',color='rgb(230, 111, 81)')),
                opts.MarkLineItem(y=pe_75, name="pe_75",linestyle_opts=opts.LineStyleOpts(type_='dashed',color='rgb(230, 111, 81)')),
                opts.MarkLineItem(y=average, name="average",linestyle_opts=opts.LineStyleOpts(type_='dashed',color='rgb(232, 197, 107)')),
                opts.MarkLineItem(y=pe_20, name="pe_20",linestyle_opts=opts.LineStyleOpts(type_='dashed',color='rgb(41, 157, 144)')),
                opts.MarkLineItem(y=pe_10, name="pe_10",linestyle_opts=opts.LineStyleOpts(type_='dashed',color='rgb(38, 70, 83)')),
            ],
        ),
    )
    return line



'''
获取指数：
目标地址: https://finance.sina.com.cn/realstock/company/sz399552/nc.shtml(示例)
stock_zh_index_daily_df = ak.stock_zh_index_daily(symbol=stock_code)
目标地址: http://gu.qq.com/sh000919/zs
stock_zh_index_daily_df = ak.stock_zh_index_daily_tx(symbol=stock_code)
获取基金：
fund_open_fund_info_em_df = ak.fund_open_fund_info_em(fund=fc, indicator="单位净值走势")
'''

def get_stock_index_his_data(symbol, title_str, tag=1):
    '''
        tag: 1=from 腾讯证券（https://stockapp.finance.qq.com/mstats/）
        tag: 2=from finance.yahoo.com（https://finance.yahoo.com/）
        tag: 3=from sina证券（https://finance.sina.com.cn）
        return stock_index_df
    '''
    stock_index_df = None

    if tag == 1:
        stock_zh_index_daily_df = ak.stock_zh_index_daily_tx(symbol=symbol)
        stock_index_df = stock_zh_index_daily_df
    elif tag == 2:
        today = datetime.date.today()
        yesterday = get_yesterday(n=10)
        stock_index_df = yf.download(symbol,yesterday,today)
        stock_index_df['date'] = stock_index_df.index
        stock_index_df['close'] = stock_index_df['Close']
        stock_index_df = stock_index_df.reset_index()
        if stock_index_df.shape[0] == 0:
            print('get_stock_index_his_data failed, read the cache data')
            _url = f'https://github.com/xunhs/auto_stock/raw/public/data/{title_str}.csv'
            s=requests.get(_url).content
            stock_index_df=pd.read_csv(io.StringIO(s.decode('utf-8')), header=0)
    elif tag == 3:
        stock_zh_index_daily_df = ak.stock_zh_index_daily(symbol=symbol)
        stock_index_df = stock_zh_index_daily_df
        
    # for datetime error
    stock_index_df.to_csv(f'./public/data/{title_str}.csv', header=True, index=False)
    stock_index_df = pd.read_csv(f'./public/data/{title_str}.csv', header=0)
    stock_index_df['date'] = pd.to_datetime(stock_index_df['date']).dt.date
    return stock_index_df
        


def worker(stock_code, stock_name, support_line, tag=1):
    title_str = f'{stock_name}-{stock_code}'
    print(title_str)
    stock_index_df = get_stock_index_his_data(stock_code, title_str, tag)
    
    symbol = stock_name
    indicator = "市盈率"
    hist_eval_pe_df = ak.index_value_hist_funddb(symbol=symbol, indicator=indicator)
    quantile_series = pd.qcut(hist_eval_pe_df['市盈率'], q=[0, 0.2, 0.4, 0.6, 1], labels=['低估','正常','偏高','高估'])
    hist_eval_pe_df['市盈率估值'] = quantile_series
    hist_eval_pe_df = hist_eval_pe_df[['日期', '市盈率', '市盈率估值']]

    indicator = "市净率"
    hist_eval_pb_df = ak.index_value_hist_funddb(symbol=symbol, indicator=indicator)
    quantile_series = pd.qcut(hist_eval_pb_df['市净率'], q=[0, 0.2, 0.4, 0.6, 1], labels=['低估','正常','偏高','高估'])
    hist_eval_pb_df['市净率估值'] = quantile_series
    hist_eval_pb_df = hist_eval_pb_df[['日期', '市净率', '市净率估值']]

    
    merge_df = pd.merge(stock_index_df[['date', 'close']], hist_eval_pe_df, 
            left_on='date', right_on='日期', how='inner')
    merge_df = pd.merge(merge_df[['date', 'close', '市盈率', '市盈率估值']], hist_eval_pb_df, 
            left_on='date', right_on='日期', how='inner')
    merge_df = merge_df.drop(['日期'], axis=1)
    merge_df.to_csv(f'./public/data/{title_str}.csv', header=True, index=False)
    line = get_stock_line(title_str, merge_df, support_line)
    line.render(f'./public/html/{title_str}.html')
    pe_line = get_pe_line(title_str, merge_df)
    pe_line.render(f'./public/html/{title_str}-pe.html')
    pb_line = get_pe_line(title_str, merge_df, indicator="市净率")
    pb_line.render(f'./public/html/{title_str}-pb.html')
    item_html_str = f'''
                <h1>{title_str}</h1>
                <div class="col">
                    <iframe src="./html/{title_str}.html" height="600px" width="1000px"></iframe>
                    <iframe src="./html/{title_str}-pe.html" height="600px" width="1000px"></iframe>
                    <iframe src="./html/{title_str}-pb.html" height="600px" width="1000px"></iframe>
                </div>
    '''
    return merge_df, line, item_html_str


def worker_test(stock_code, stock_name, support_line):
    title_str = f'{stock_name}-{stock_code}'
    print(title_str)
    # stock_zh_index_daily_df = ak.stock_zh_index_daily_tx(symbol=stock_code)
    # symbol = stock_name
    # indicator = "市盈率"
    # hist_eval_pe_df = ak.index_value_hist_funddb(symbol=symbol, indicator=indicator)
    # quantile_series = pd.qcut(hist_eval_pe_df['市盈率'], q=[0, 0.2, 0.4, 0.6, 1], labels=['低估','正常','偏高','高估'])
    # hist_eval_pe_df['市盈率估值'] = quantile_series
    # hist_eval_pe_df = hist_eval_pe_df[['日期', '市盈率', '市盈率估值']]

    # indicator = "市净率"
    # hist_eval_pb_df = ak.index_value_hist_funddb(symbol=symbol, indicator=indicator)
    # quantile_series = pd.qcut(hist_eval_pb_df['市净率'], q=[0, 0.2, 0.4, 0.6, 1], labels=['低估','正常','偏高','高估'])
    # hist_eval_pb_df['市净率估值'] = quantile_series
    # hist_eval_pb_df = hist_eval_pb_df[['日期', '市净率', '市净率估值']]

    # merge_df = pd.merge(stock_zh_index_daily_df[['date', 'close']], hist_eval_pe_df, 
    #         left_on='date', right_on='日期', how='inner')
    # merge_df = pd.merge(merge_df[['date', 'close', '市盈率', '市盈率估值']], hist_eval_pb_df, 
    #         left_on='date', right_on='日期', how='inner')
    # merge_df = merge_df.drop(['日期'], axis=1)
    # merge_df.to_csv(f'./public/data/{title_str}.csv', header=True, index=False)
    merge_df = pd.read_csv(f'./public/data/{title_str}.csv', header=0)
    merge_df['date'] = pd.to_datetime(merge_df['date']).dt.date
    title_str = stock_code 

    line = get_stock_line(title_str, merge_df, support_line)
    line.render(f'./public/html/{title_str}.html')
    item_html_str = f'''
                <h1>{title_str}</h1>
                <div class="col">
                    <iframe src="./{title_str}.html" height="500px" width="900px"></iframe>
                    <iframe src="./{title_str}-pe.html" height="500px" width="900px"></iframe>
                </div>
    '''
    pe_line = get_pe_line(title_str, merge_df)
    pe_line.render(f'./public/html/{title_str}-pe.html')

    return merge_df, line, item_html_str


index_html_str = '''
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- CSS only -->
    <link href="../dist/bootstrap.min.css" rel="stylesheet">
    <title>Auto Stock</title>
    <link href="../dist/autoc.min.css" rel="stylesheet" >
</head>
<body>
    <div class="container">
        <div class="row align-items-start" id="wrap">


'''

stock_code = 'sh000001'
stock_name = '上证指数'
support_line = {'支撑位': 2800, '压力位': 3260}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=1)
index_html_str = '\n'.join([index_html_str, item_html_str])

stock_code = 'sh000300'
stock_name = '沪深300'
support_line = {'支撑位': 3500, '压力位': None}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=1)
index_html_str = '\n'.join([index_html_str, item_html_str])

stock_code = 'sh000905'
stock_name = '中证500'
support_line = {'支撑位': 4800, '压力位': 8100}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=1)
index_html_str = '\n'.join([index_html_str, item_html_str])

stock_code = 'sh000852'
stock_name = '中证1000'
support_line = {'支撑位': 5880, '压力位': None}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=1)
index_html_str = '\n'.join([index_html_str, item_html_str])

stock_code = 'sh000922'
stock_name = '中证红利'
support_line = {'支撑位': 4750, '压力位': None}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=1)
index_html_str = '\n'.join([index_html_str, item_html_str])

stock_code = 'sz399006'
stock_name = '创业板指'
support_line = {'支撑位': 1680, '压力位': 2570}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=1)
index_html_str = '\n'.join([index_html_str, item_html_str])


stock_code = 'hkHSI'
stock_name = '恒生指数'
support_line = {'支撑位1': 18800, '压力位1': 22400, '压力位2': 25500, '压力位3': 33000}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=1)
index_html_str = '\n'.join([index_html_str, item_html_str])


stock_code = '^GSPC'
stock_name = '标普500'
support_line = {'支撑位': 3000, '压力位': None}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=2)
index_html_str = '\n'.join([index_html_str, item_html_str])


stock_code = '^NDX'
stock_name = '纳斯达克100'
support_line = {'支撑位': None, '压力位': None}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=2)
index_html_str = '\n'.join([index_html_str, item_html_str])

# stock_code = '^GDAXI'
# stock_name = '德国DAX'
# support_line = {'支撑位': 8200, '压力位': 11000}
# _, _, item_html_str = worker(stock_code, stock_name, support_line, tag=2)
# index_html_str = '\n'.join([index_html_str, item_html_str])

stock_code = 'sh513030'
stock_name = '德国DAX'
support_line = {'支撑位': None, '压力位': None}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=1)
index_html_str = '\n'.join([index_html_str, item_html_str])



# stock_code = '^N225'
# stock_name = '日经225'
# support_line = {'支撑位': None, '压力位': None}
# _, _, item_html_str = worker(stock_code, stock_name, support_line, tag=2)
# index_html_str = '\n'.join([index_html_str, item_html_str])


stock_code = 'sh513520'
stock_name = '日经225'
support_line = {'支撑位': None, '压力位': None}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=1)
index_html_str = '\n'.join([index_html_str, item_html_str])



# stock_code = '^BSESN'
# stock_name = '印度SENSEX30'
# support_line = {'支撑位': None, '压力位': None}
# _, _, item_html_str = worker(stock_code, stock_name, support_line, tag=2)
# index_html_str = '\n'.join([index_html_str, item_html_str])

stock_code = 'sz164824'
stock_name = '印度SENSEX30'
support_line = {'支撑位': None, '压力位': None}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=1)
index_html_str = '\n'.join([index_html_str, item_html_str])




stock_code = 'sh000991'
stock_name = '全指医药'
support_line = {'支撑位1': 9700, '支撑位2': 11055, '压力位1': 12300, '压力位2': 13500, '压力位3': 17300}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=1)
index_html_str = '\n'.join([index_html_str, item_html_str])

stock_code = 'sz399989'
stock_name = '中证医疗'
support_line = {'支撑位1': 7900, '支撑位2': 10200, '压力位': None}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=1)
index_html_str = '\n'.join([index_html_str, item_html_str])

stock_code = 'sh000990'
stock_name = '全指消费'
support_line = {'支撑位': 11700, '压力位': 17700}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=1)
index_html_str = '\n'.join([index_html_str, item_html_str])

stock_code = 'sz399967'
stock_name = '中证军工'
support_line = {'支撑位': 8300, '压力位': None}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=1)
index_html_str = '\n'.join([index_html_str, item_html_str])

stock_code = 'hkHSTECH'
stock_name = '恒生科技指数'
support_line = {'支撑位': None, '压力位': None}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=1)
index_html_str = '\n'.join([index_html_str, item_html_str])

stock_code = 'sh000993'
stock_name = '全指信息'
support_line = {'支撑位': 4600, '压力位1': 6300, '压力位2': 7500}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=1)
index_html_str = '\n'.join([index_html_str, item_html_str])

stock_code = 'sz399971'
stock_name = '中证传媒'
support_line = {'支撑位1': 931, '支撑位2': 1220, '压力位1': 1400, '压力位2': 1700}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=1)
index_html_str = '\n'.join([index_html_str, item_html_str])

stock_code = 'sh000827'
stock_name = '中证环保'
support_line = {'支撑位1': 1836, '支撑位2': 2020, '压力位': None}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=1)
index_html_str = '\n'.join([index_html_str, item_html_str])


stock_code = 'sz399975'
stock_name = '证券公司'
support_line = {'支撑位': 600, '压力位': None}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=1)
index_html_str = '\n'.join([index_html_str, item_html_str])



stock_code = 'sz399393'
stock_name = '房地产(申万)'
support_line = {'支撑位': None, '压力位': None}
_, _, item_html_str = worker(stock_code, stock_name, support_line, tag=1)
index_html_str = '\n'.join([index_html_str, item_html_str])


html_end_str = '''



            </div>
          </div>

    </div>


    <script type="text/javascript" src="../dist/autoc.min.js"></script>
    <script src="../dist/bootstrap.min.js"></script>
    <script type="text/javascript">
         new AutocJs({
            article: '#wrap',
            title: '文章目录',
            position: 'outside',
        });
    </script>
</body>
</html>


'''

index_html_str = '\n'.join([index_html_str, html_end_str])

with open('./public/index.html', 'w+') as fp:
    fp.write(index_html_str)


###################

# import akshare as ak
# from datetime import datetime, timedelta
# import numpy as np
# import datetime
# import pandas as pd
# import requests
# import json

# import time
# import hmac
# import hashlib
# import base64
# import urllib.parse


# today = datetime.date.today()
# symbols = ['上证50', '沪深300', '中证500', '中证1000', '创业板50', 
#            '标普500', '纳斯达克100', '恒生指数', '道琼斯工业指数', '英国富时100',
#            '全指医药', '全指信息', '全指消费', '中国互联网50', '中证新能源']

# K = 15.0

# def push_report(msg):
#     # 定时任务触发钉钉报告推送

    
#     timestamp = str(round(time.time() * 1000))
#     access_token = '551fed66b9a0e9ed66fb5e97817f2a4262f30e454926e3e398ecaeda6cce73c1'
#     secret = 'SECb8cd017582d26e13fc6fd1c97de505686f36fc16b22435945351275fdecc5f77'
#     secret_enc = secret.encode('utf-8')
#     string_to_sign = '{}\n{}'.format(timestamp, secret)
#     string_to_sign_enc = string_to_sign.encode('utf-8')
#     hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
#     sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
#     web_hook = f"https://oapi.dingtalk.com/robot/send?access_token={access_token}&timestamp={timestamp}&sign={sign}"
    
    
#     header = {
#         "Content-Type": "application/json;charset=UTF-8"
#     }
#     message_body = {
#         "msgtype": "markdown",
#         "markdown": {
#             "title": "ETF",
#             "text": msg
#         },
#         "at": {
#             "atMobiles": [],
#             "isAtAll": False
#         }
#     }
#     send_data = json.dumps(message_body)  # 将字典类型数据转化为json格式
#     ChatBot = requests.post(url=web_hook, data=send_data, headers=header)
#     opener = ChatBot.json()
#     if opener["errmsg"] == "ok":
#         print(u"%s 通知消息发送成功！" % opener)
#     else:
#         print(u"通知消息发送失败，原因：{}".format(opener))

# # msg = "消息推送展示项目：钉钉"
# # push_report(msg)

# today_eval_df = ak.index_value_name_funddb()
# # today_eval_df.head()

# selected_df = today_eval_df[today_eval_df['指数名称'].isin(symbols)]
# selected_df.index = selected_df['指数名称']
# # 按照列表顺序排序
# selected_df = selected_df.loc[symbols]

# _count = 0
# for idx in selected_df.index:
#     PE_pc = selected_df.loc[idx, 'PE分位']
#     PB_pc = selected_df.loc[idx, 'PB分位']
#     if (PE_pc <= K) and (PB_pc <= K):
#         symbol = selected_df.loc[idx, '指数名称']
#         symbol_code = selected_df.loc[idx, '指数代码']
#         update_time = selected_df.loc[idx, '更新时间']
#         info = f'从近10年来看，{symbol}({symbol_code}):市盈率PE分位处于{PE_pc}%，市净率PB分位处于{PB_pc}%，均处于15%分位以下！更新时间:{update_time}'
#         _count += 1
#         print(info)
#         push_report(info)
# if _count == 0:
#     info = '本周观测ETF均处于15%分位以上，切勿操作！'
#     push_report(info)
        
        
