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
