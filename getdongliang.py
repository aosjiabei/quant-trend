import ccxt
from datetime import datetime
from datetime import timedelta
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time

huobi_exchange = ccxt.huobipro({'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766569-15aa7b9a-5edd-11e7-9e7f-44791f4ee49c.jpg',
                'api': {
                    'market': 'https://api.huobi.io',
                    'public': 'https://api.huobi.io',
                    'private': 'https://api.huobi.io',
                    'zendesk': 'https://huobiglobal.zendesk.com/hc/en-us/articles',
                },
                'www': 'https://www.huobi.pro',
                'referral': 'https://www.huobi.br.com/en-us/topic/invited/?invite_code=rwrd3',
                'doc': 'https://github.com/huobiapi/API_Docs/wiki/REST_api_reference',
                'fees': 'https://www.huobi.pro/about/fee/',
            }})
huobi_exchange.load_markets()

while True:
    time_now = time.strftime("%H", time.localtime())  # 刷新
    if time_now == "20": #此处设置每天定时的时间

        now = datetime.now()
        if int(now.strftime("%H%M%S")) <= 200000:
            now = now + timedelta(days=-1)
        else:
            pass

        aDay = timedelta(days=-7)
        lastweek = now + aDay
        print(now.strftime('%Y-%m-%d'))
        print(lastweek.strftime('%Y-%m-%d'))
        today_time = now.strftime('%Y-%m-%d') + ' 19:00:00+00:00'   # 20：00的收盘价 是19：00的k线柱
        lastweek_time = lastweek.strftime('%Y-%m-%d') + ' 19:00:00+00:00'

        symbol = ['BTC/USDT', 'BSV/USDT', 'HT/USDT']
        dongliang_list = []
        thisweekclose_list = []

        for symbol in symbol:
            if huobi_exchange.has['fetchOHLCV']:
                kline_data = pd.DataFrame(huobi_exchange.fetch_ohlcv(symbol, timeframe='1h'))
                kline_data.columns = ['Datetime', 'open', 'High', 'Low', 'close', 'vol']
                kline_data = kline_data[['Datetime', 'close']]
                kline_data['Datetime'] = kline_data['Datetime'].apply(huobi_exchange.iso8601)
                kline_data['Datetime'] = pd.to_datetime(kline_data['Datetime']) + pd.Timedelta(hours=8)
                thisweekclose = kline_data[kline_data['Datetime'] == today_time]['close'].values
                lastweekclose = kline_data[kline_data['Datetime'] == lastweek_time]['close'].values
                dongliang = thisweekclose / lastweekclose
                dongliang_list.append(dongliang)
                thisweekclose_list.append(thisweekclose)

                print(now.strftime('%Y-%m-%d'), symbol, thisweekclose)
                print(lastweek.strftime('%Y-%m-%d'), symbol, lastweekclose)
                print(symbol, '动量', dongliang)

        dongliang_btc = dongliang_list[0]
        dongliang_bsv = dongliang_list[1]
        dongliang_ht = dongliang_list[2]
        BTC_price = thisweekclose_list[0]
        BSV_price = thisweekclose_list[1]
        HT_price = thisweekclose_list[2]

        # print(dongliang_btc)
        # print(dongliang_bsv)
        # print(dongliang_ht)

        print('BTC-BSV 轮动组')
        if dongliang_btc > dongliang_bsv:
            print('操作BTC')
            caozuo_btcbsv = '操作BTC'
            price_set_btcbsv = BTC_price
        else:
            print('操作BSV')
            caozuo_btcbsv = '操作BSV'
            price_set_btcbsv = BSV_price

        if dongliang_btc < 0.99 and dongliang_bsv < 0.99:
            price_set_btcbsv = price_set_btcbsv * 1.15
            caozuo_btcbsv = caozuo_btcbsv + '空仓追涨' + str(price_set_btcbsv)
            print('空仓追涨',str(price_set_btcbsv))
        else:
            price_set_btcbsv = price_set_btcbsv * 0.85
            caozuo_btcbsv = caozuo_btcbsv + '持仓止损' + str(price_set_btcbsv)
            print('持仓止损',str(price_set_btcbsv))

        print('BTC-HT 轮动组')
        if dongliang_btc > dongliang_ht:
            print('操作BTC')
            caozuo_btcht = '操作BTC'
            price_set_btcht = BTC_price
        else:
            print('操作HT')
            caozuo_btcht = '操作HT'
            price_set_btcht = HT_price

        if dongliang_btc < 0.99 and dongliang_ht < 0.99:
            price_set_btcht = price_set_btcht * 1.15
            caozuo_btcht = caozuo_btcht + '空仓追涨' + str(price_set_btcht)
            print('空仓追涨',str(price_set_btcht))
        else:
            price_set_btcht = price_set_btcht * 0.85
            caozuo_btcht = caozuo_btcht + '持仓止损' + str(price_set_btcht)
            print('持仓止损',str(price_set_btcht))

        mailserver = 'smtp.qq.com'
        userName_Sendmail = '1234567@qq.com'   #发送邮箱地址
        userName_AuthCode = 'qhpzsesjwtzxcbcg'   #发送邮箱的pop3授权码   在邮箱设置中设置
        received_mail = ['345678@qq.com']   #接受邮箱地址

        content = '\n'.join([now.strftime('%Y-%m-%d'), 'BTC价格', str(BTC_price), 'BTC动量', str(dongliang_btc),
                             'BSV价格', str(BSV_price), 'BSV动量', str(dongliang_bsv), 'HT价格', str(HT_price) ,'HT动量',
                             str(dongliang_ht), 'BTC-BSV 轮动组', caozuo_btcbsv, 'BTC-HT 轮动组', caozuo_btcht])
        email = MIMEText(content, 'plain', 'utf-8')
        email['Subject'] = Header(content, 'utf-8')
        email['From'] = Header("Python机器人", 'utf-8')  #发送人抬头
        email['To'] = Header("helloworld", 'utf-8')   #接受人抬头

        smtp = smtplib.SMTP_SSL(mailserver, port=465)
        smtp.login(userName_Sendmail, userName_AuthCode)
        smtp.sendmail(userName_Sendmail, '1234567@qq.com', email.as_string())    #邮箱可以自己发自己 ，所以收发邮箱可以一样

        smtp.quit()


    time.sleep(60*60)
