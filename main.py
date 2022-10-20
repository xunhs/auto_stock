import akshare as ak
from datetime import datetime, timedelta
import numpy as np
import datetime
import pandas as pd

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



def get_line(title_str, data_df, support_line):
    one_day = get_yesterday(10)
    first = data_df.loc[0, 'date']
    if first < one_day:
        data_df = data_df[data_df['date'] >= one_day]
    
    date_list = data_df['date'].tolist()
    line = Line(init_opts=opts.InitOpts(width="1500px",
                                              height="600px",
                                              theme=ThemeType.LIGHT
                                              ))
    line.add_xaxis(xaxis_data=date_list)
    
    

    line.add_yaxis(
        series_name="收盘价",
        y_axis=data_df['close'].tolist(),
        markline_opts=opts.MarkLineOpts(data=[
            opts.MarkLineItem(y=support_line, name="支撑位"),
        ]),
    )

    _index = 0
    _offset = 55
    for idx, (fc, fn) in enumerate(zip(fund_code, fund_name)):
        _index += 1
        line.extend_axis(yaxis=opts.AxisOpts(type_="value", 
                                             position="left",
                                             offset= (idx + 1) * _offset,))
        line.add_yaxis(
            series_name=fn,
            y_axis=data_df[fn].tolist(), 
            yaxis_index=_index)

    for idx, pe_column in enumerate(['市盈率', '市净率', '股息率']):
        _index += 1
        line.extend_axis(yaxis=opts.AxisOpts(type_="value", 
                                             position="right",
                                             offset=idx * _offset,))
        if pe_column == '股息率':
            _mlitem = opts.MarkLineItem(y=data_df[pe_column].quantile(0.75), name="Max+10%")
        else:
            _mlitem = opts.MarkLineItem(y=data_df[pe_column].quantile(0.25), name="Min+10%")
        line.add_yaxis(
            series_name=pe_column,
            y_axis=data_df[pe_column].tolist(), 
            markline_opts=opts.MarkLineOpts(data=[
                _mlitem,
                opts.MarkLineItem(type_="average", name="Average"),
        ]),
            yaxis_index=_index)
    
    line.set_global_opts(
        title_opts=opts.TitleOpts(subtitle=title_str),
        # 十字准星指示器
        tooltip_opts = opts.TooltipOpts(is_show = True, trigger_on = "mousemove | click", axis_pointer_type='cross'),
        # 放大缩小
        datazoom_opts=opts.DataZoomOpts(orient="horizontal", range_start=0,range_end=100), 
    )
    return line




stock_code = 'sh000300'
stock_name = '沪深300'
support_line = 3500

fund_code = ['050002']
fund_name = ['博时沪深300指数']

stock_zh_index_daily_df = ak.stock_zh_index_daily_tx(symbol=stock_code)
merge_df = stock_zh_index_daily_df
for fc, fn in zip(fund_code, fund_name):
    fund_open_fund_info_em_df = ak.fund_open_fund_info_em(fund=fc, indicator="单位净值走势")
    merge_df = pd.merge(merge_df, fund_open_fund_info_em_df,
                        left_on='date', right_on='净值日期', how='left')
    merge_df.rename(columns={'单位净值': fn}, inplace=True,)

for _indicator in ['市盈率', '市净率', '股息率']:
    index_value_hist_funddb_df = ak.index_value_hist_funddb(symbol=stock_name, indicator=_indicator)
    merge_df = pd.merge(merge_df, index_value_hist_funddb_df,
                        left_on='date', right_on='日期', how='left')



title_str = f'{stock_name}-{stock_code}'
print(title_str)
line = get_line(title_str, merge_df, support_line)
line.render(f'{title_str}.html')




stock_code = 'sh000905'
stock_name = '中证500'
support_line = 4800

fund_code = ['161017', '160119']
fund_name = ['富国中证500指数增强(LOF)', '南方中证500ETF联接']

stock_zh_index_daily_df = ak.stock_zh_index_daily_tx(symbol=stock_code)


merge_df = stock_zh_index_daily_df
for fc, fn in zip(fund_code, fund_name):
    fund_open_fund_info_em_df = ak.fund_open_fund_info_em(fund=fc, indicator="单位净值走势")
    merge_df = pd.merge(merge_df, fund_open_fund_info_em_df,
                        left_on='date', right_on='净值日期', how='left')
    merge_df.rename(columns={'单位净值': fn}, inplace=True,)

for _indicator in ['市盈率', '市净率', '股息率']:
    index_value_hist_funddb_df = ak.index_value_hist_funddb(symbol=stock_name, indicator=_indicator)
    merge_df = pd.merge(merge_df, index_value_hist_funddb_df,
                        left_on='date', right_on='日期', how='left')
title_str = f'{stock_name}-{stock_code}'
merge_df.to_csv(title_str + '.csv', header=True, index=False)
print(title_str)
line = get_line(title_str, merge_df, support_line)
line.render(f'{title_str}.html')





stock_code = 'sh000852'
stock_name = '中证1000'
support_line = 5800

fund_code = ['005313', '006486']
fund_name = ['万家中证1000指数增强', '广发中证1000指数A']

stock_zh_index_daily_df = ak.stock_zh_index_daily_tx(symbol=stock_code)


merge_df = stock_zh_index_daily_df
for fc, fn in zip(fund_code, fund_name):
    fund_open_fund_info_em_df = ak.fund_open_fund_info_em(fund=fc, indicator="单位净值走势")
    merge_df = pd.merge(merge_df, fund_open_fund_info_em_df,
                        left_on='date', right_on='净值日期', how='left')
    merge_df.rename(columns={'单位净值': fn}, inplace=True,)

for _indicator in ['市盈率', '市净率', '股息率']:
    index_value_hist_funddb_df = ak.index_value_hist_funddb(symbol=stock_name, indicator=_indicator)
    merge_df = pd.merge(merge_df, index_value_hist_funddb_df,
                        left_on='date', right_on='日期', how='left')
title_str = f'{stock_name}-{stock_code}'
merge_df.to_csv(title_str + '.csv', header=True, index=False)
print(title_str)
line = get_line(title_str, merge_df, support_line)
line.render(f'{title_str}.html')




stock_code = 'hkHSI'
stock_name = '恒生指数'
fund_code = '000071'
fund_name = '华夏恒生ETF联接'
support_line = 18000

fund_code = ['000071', '164705']
fund_name = ['华夏恒生ETF联接', '汇添富恒生指数A']

stock_zh_index_daily_df = ak.stock_zh_index_daily_tx(symbol=stock_code)
merge_df = stock_zh_index_daily_df
for fc, fn in zip(fund_code, fund_name):
    fund_open_fund_info_em_df = ak.fund_open_fund_info_em(fund=fc, indicator="单位净值走势")
    merge_df = pd.merge(merge_df, fund_open_fund_info_em_df,
                        left_on='date', right_on='净值日期', how='left')
    merge_df.rename(columns={'单位净值': fn}, inplace=True,)

for _indicator in ['市盈率', '市净率', '股息率']:
    index_value_hist_funddb_df = ak.index_value_hist_funddb(symbol=stock_name, indicator=_indicator)
    merge_df = pd.merge(merge_df, index_value_hist_funddb_df,
                        left_on='date', right_on='日期', how='left')
title_str = f'{stock_name}-{stock_code}'
merge_df.to_csv(title_str + '.csv', header=True, index=False)
print(title_str)
line = get_line(title_str, merge_df, support_line)
line.render(f'{title_str}.html')





stock_code = 'sh000922'
stock_name = '中证红利'
support_line = 0

fund_code = ['100032', ]
fund_name = ['富国中证红利指数增强', ]

stock_zh_index_daily_df = ak.stock_zh_index_daily_tx(symbol=stock_code)
merge_df = stock_zh_index_daily_df
for fc, fn in zip(fund_code, fund_name):
    fund_open_fund_info_em_df = ak.fund_open_fund_info_em(fund=fc, indicator="单位净值走势")
    merge_df = pd.merge(merge_df, fund_open_fund_info_em_df,
                        left_on='date', right_on='净值日期', how='left')
    merge_df.rename(columns={'单位净值': fn}, inplace=True,)

for _indicator in ['市盈率', '市净率', '股息率']:
    index_value_hist_funddb_df = ak.index_value_hist_funddb(symbol=stock_name, indicator=_indicator)
    merge_df = pd.merge(merge_df, index_value_hist_funddb_df,
                        left_on='date', right_on='日期', how='left')
title_str = f'{stock_name}-{stock_code}'
merge_df.to_csv(title_str + '.csv', header=True, index=False)
print(title_str)
line = get_line(title_str, merge_df, support_line)
line.render(f'{title_str}.html')




stock_code = 'sh000991'
stock_name = '全指医药'
support_line = 9700

fund_code = ['001180', '501009']
fund_name = ['广发医药卫生联接', '汇添富中证生物科技指数A']

stock_zh_index_daily_df = ak.stock_zh_index_daily_tx(symbol=stock_code)
merge_df = stock_zh_index_daily_df
for fc, fn in zip(fund_code, fund_name):
    fund_open_fund_info_em_df = ak.fund_open_fund_info_em(fund=fc, indicator="单位净值走势")
    merge_df = pd.merge(merge_df, fund_open_fund_info_em_df,
                        left_on='date', right_on='净值日期', how='left')
    merge_df.rename(columns={'单位净值': fn}, inplace=True,)

for _indicator in ['市盈率', '市净率', '股息率']:
    index_value_hist_funddb_df = ak.index_value_hist_funddb(symbol=stock_name, indicator=_indicator)
    merge_df = pd.merge(merge_df, index_value_hist_funddb_df,
                        left_on='date', right_on='日期', how='left')
title_str = f'{stock_name}-{stock_code}'
merge_df.to_csv(title_str + '.csv', header=True, index=False)
print(title_str)
line = get_line(title_str, merge_df, support_line)
line.render(f'{title_str}.html')





stock_code = 'sz399989'
stock_name = '中证医疗'
support_line = 7900

fund_code = ['002708', '502056',]
fund_name = ['大摩健康产业混合', '广发中证医疗指数(LOF)A',]

stock_zh_index_daily_df = ak.stock_zh_index_daily_tx(symbol=stock_code)
merge_df = stock_zh_index_daily_df
for fc, fn in zip(fund_code, fund_name):
    fund_open_fund_info_em_df = ak.fund_open_fund_info_em(fund=fc, indicator="单位净值走势")
    merge_df = pd.merge(merge_df, fund_open_fund_info_em_df,
                        left_on='date', right_on='净值日期', how='left')
    merge_df.rename(columns={'单位净值': fn}, inplace=True,)

for _indicator in ['市盈率', '市净率', '股息率']:
    index_value_hist_funddb_df = ak.index_value_hist_funddb(symbol='医疗器械', indicator=_indicator)
    merge_df = pd.merge(merge_df, index_value_hist_funddb_df,
                        left_on='date', right_on='日期', how='left')
title_str = f'{stock_name}-{stock_code}'
merge_df.to_csv(title_str + '.csv', header=True, index=False)
print(title_str)
line = get_line(title_str, merge_df, support_line)
line.render(f'{title_str}.html')



stock_code = 'sh000990'
stock_name = '全指消费'
support_line = 11700

fund_code = ['110022', '004424']
fund_name = ['易方达消费行业股票', '汇添富文体娱乐混合A']

stock_zh_index_daily_df = ak.stock_zh_index_daily_tx(symbol=stock_code)
merge_df = stock_zh_index_daily_df
for fc, fn in zip(fund_code, fund_name):
    fund_open_fund_info_em_df = ak.fund_open_fund_info_em(fund=fc, indicator="单位净值走势")
    merge_df = pd.merge(merge_df, fund_open_fund_info_em_df,
                        left_on='date', right_on='净值日期', how='left')
    merge_df.rename(columns={'单位净值': fn}, inplace=True,)

for _indicator in ['市盈率', '市净率', '股息率']:
    index_value_hist_funddb_df = ak.index_value_hist_funddb(symbol=stock_name, indicator=_indicator)
    merge_df = pd.merge(merge_df, index_value_hist_funddb_df,
                        left_on='date', right_on='日期', how='left')
title_str = f'{stock_name}-{stock_code}'
merge_df.to_csv(title_str + '.csv', header=True, index=False)
print(title_str)
line = get_line(title_str, merge_df, support_line)
line.render(f'{title_str}.html')





stock_code = 'sz399967'
stock_name = '中证军工'
support_line = 5800

fund_code = ['163115', '161024']
fund_name = ['申万菱信中证军工指数A', '富国中证军工指数(LOF)A']

stock_zh_index_daily_df = ak.stock_zh_index_daily_tx(symbol=stock_code)
merge_df = stock_zh_index_daily_df
for fc, fn in zip(fund_code, fund_name):
    fund_open_fund_info_em_df = ak.fund_open_fund_info_em(fund=fc, indicator="单位净值走势")
    merge_df = pd.merge(merge_df, fund_open_fund_info_em_df,
                        left_on='date', right_on='净值日期', how='left')
    merge_df.rename(columns={'单位净值': fn}, inplace=True,)

for _indicator in ['市盈率', '市净率', '股息率']:
    index_value_hist_funddb_df = ak.index_value_hist_funddb(symbol='国防军工(申万)', indicator=_indicator)
    merge_df = pd.merge(merge_df, index_value_hist_funddb_df,
                        left_on='date', right_on='日期', how='left')
title_str = f'{stock_name}-{stock_code}'
merge_df.to_csv(title_str + '.csv', header=True, index=False)
print(title_str)
line = get_line(title_str, merge_df, support_line)
line.render(f'{title_str}.html')





stock_code = 'hkHSTECH'
stock_name = '恒生科技指数'
support_line = 0

fund_code = ['012348']
fund_name = ['天弘恒生科技指数']

stock_zh_index_daily_df = ak.stock_zh_index_daily_tx(symbol=stock_code)
merge_df = stock_zh_index_daily_df
for fc, fn in zip(fund_code, fund_name):
    fund_open_fund_info_em_df = ak.fund_open_fund_info_em(fund=fc, indicator="单位净值走势")
    merge_df = pd.merge(merge_df, fund_open_fund_info_em_df,
                        left_on='date', right_on='净值日期', how='left')
    merge_df.rename(columns={'单位净值': fn}, inplace=True,)

for _indicator in ['市盈率', '市净率', '股息率']:
    index_value_hist_funddb_df = ak.index_value_hist_funddb(symbol=stock_name, indicator=_indicator)
    merge_df = pd.merge(merge_df, index_value_hist_funddb_df,
                        left_on='date', right_on='日期', how='left')
merge_df.to_csv(title_str + '.csv', header=True, index=False)

title_str = f'{stock_name}-{stock_code}'
print(title_str)
line = get_line(title_str, merge_df, support_line)
line.render(f'{title_str}.html')




stock_code = 'sh000993'
stock_name = '全指信息'
support_line = 4500

fund_code = ['000942', '001513']
fund_name = ['广发信息技术联接A', '易方达信息产业混合']

stock_zh_index_daily_df = ak.stock_zh_index_daily_tx(symbol=stock_code)
merge_df = stock_zh_index_daily_df
for fc, fn in zip(fund_code, fund_name):
    fund_open_fund_info_em_df = ak.fund_open_fund_info_em(fund=fc, indicator="单位净值走势")
    merge_df = pd.merge(merge_df, fund_open_fund_info_em_df,
                        left_on='date', right_on='净值日期', how='left')
    merge_df.rename(columns={'单位净值': fn}, inplace=True,)

for _indicator in ['市盈率', '市净率', '股息率']:
    index_value_hist_funddb_df = ak.index_value_hist_funddb(symbol=stock_name, indicator=_indicator)
    merge_df = pd.merge(merge_df, index_value_hist_funddb_df,
                        left_on='date', right_on='日期', how='left')
merge_df.to_csv(title_str + '.csv', header=True, index=False)

title_str = f'{stock_name}-{stock_code}'
print(title_str)
line = get_line(title_str, merge_df, support_line)
line.render(f'{title_str}.html')



