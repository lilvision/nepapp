from concurrent.futures import ThreadPoolExecutor
import datetime
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup


def id_today():
  headers = {'X-Requested-With': 'XMLHttpRequest'}
  url = 'https://www.sharesansar.com/today-share-price'

  response = requests.get(url, headers=headers)
  page = BeautifulSoup(response.content, 'html.parser')
  script_tag = page.find('script', string=lambda text: text and 'var cmpjson =' in text)
  cmpjson_text = script_tag.text.strip().split('=', 1)[1].strip().rstrip(';')
  data_list = json.loads(cmpjson_text)
  tyy=data_list

  dftyy=pd.DataFrame(tyy)
  dftyy=dftyy.rename(columns = {'symbol':'sym'})


  urls = 'https://www.sharesansar.com/today-share-price'

  rr = requests.get(urls)
  htmll = rr.text

  soup = BeautifulSoup(htmll,"html.parser")
  text = soup.find(id="headFixed").get_text()
  splitted=text.split()


  sn=31
  sy=32
  cl=37

  df = pd.DataFrame(columns=['SYMBOL','Closing Price'])
  newlist = splitted[31:]
  nn=int(len(newlist)/21)
  for j in range(nn):
      no=splitted[sn]
      s_names=splitted[sy]
      s_close=splitted[cl]
      data = [[s_names,s_close]]

      dfn = pd.DataFrame(data, columns = ['SYMBOL','Closing Price'])
      df = pd.concat([df, dfn])

      sn=sn+21
      sy=sy+21
      cl=cl+21

  df = df.replace(',','', regex=True)
  df['Closing Price'] = df['Closing Price'].astype(float)

  dfstocks=df
  dfstocks=dfstocks.rename(columns = {'SYMBOL':'sym'})


  df_merged = dftyy.merge(dfstocks)
  return df_merged



def ogen_df(company,days):
    comp=company
    day=days
    num=0
    payload = {'_': '1639245456705','columns[0][data]': 'DT_Row_Index','columns[0][searchable]': 'false','columns[0][orderable]': 'false','columns[0][search][regex]': 'false','columns[1][data]': 'transaction','columns[1][searchable]': 'true','columns[1][orderable]': 'false','columns[1][search][regex]': 'false','columns[2][data]': 'buyer','columns[2][searchable]': 'true','columns[2][orderable]': 'false','columns[2][search][regex]': 'false','columns[3][data]': 'seller','columns[3][searchable]': 'true','columns[3][orderable]': 'false','columns[3][search][regex]': 'false','columns[4][data]': 'quantity','columns[4][searchable]': 'true','columns[4][orderable]': 'false','columns[4][search][regex]': 'false','columns[5][data]': 'rate','columns[5][searchable]': 'true','columns[5][orderable]': 'false','columns[5][search][regex]': 'false','columns[6][data]': 'amount','columns[6][searchable]': 'true','columns[6][orderable]': 'false','columns[6][search][regex]': 'false','columns[7][data]': 'date_','columns[7][searchable]': 'true','columns[7][orderable]': 'false','columns[7][search][regex]': 'false',
               'company': comp,'draw': '1','date': day,'length': '500','search[regex]': 'false','start': num,}

    headers = {'X-Requested-With': 'XMLHttpRequest'}
    url = 'https://www.sharesansar.com/floorsheet'

    response = requests.get(url, params=payload, headers=headers)
    data = response.json()

    if data['recordsFiltered'] % 500 == 0:
        n=int(data['recordsFiltered']/500)
    else:
        n=(data['recordsFiltered']//500)+1
    num=0
    df=pd.DataFrame()
    for i in range(n):

        payload = {'_': '1639245456705','columns[0][data]': 'DT_Row_Index','columns[0][searchable]': 'false','columns[0][orderable]': 'false','columns[0][search][regex]': 'false','columns[1][data]': 'transaction','columns[1][searchable]': 'true','columns[1][orderable]': 'false','columns[1][search][regex]': 'false','columns[2][data]': 'buyer','columns[2][searchable]': 'true','columns[2][orderable]': 'false','columns[2][search][regex]': 'false','columns[3][data]': 'seller','columns[3][searchable]': 'true','columns[3][orderable]': 'false','columns[3][search][regex]': 'false','columns[4][data]': 'quantity','columns[4][searchable]': 'true','columns[4][orderable]': 'false','columns[4][search][regex]': 'false','columns[5][data]': 'rate','columns[5][searchable]': 'true','columns[5][orderable]': 'false','columns[5][search][regex]': 'false','columns[6][data]': 'amount','columns[6][searchable]': 'true','columns[6][orderable]': 'false','columns[6][search][regex]': 'false','columns[7][data]': 'date_','columns[7][searchable]': 'true','columns[7][orderable]': 'false','columns[7][search][regex]': 'false',
                   'company': comp,'draw': '1','date': day,'length': '500','search[regex]': 'false','start': num,}
        response = requests.get(url, params=payload, headers=headers)
        data = response.json()
        lis=data['data']
        dff = pd.DataFrame.from_records(lis)
        num=num+500
        df = pd.concat([df, dff])

    return df


def ocsv(file):

    fl=file.drop(columns=['company','transaction', 'date_', 'DT_Row_Index','Unnamed: 0'], errors='ignore')
    fl=fl.reset_index(drop=True)
    dtype_dict = {'buyer': str,
                    'seller': str,
                    'quantity': float,
                    'rate': float,
                    'amount': float,
                    }
    fl = fl.astype(dtype_dict)

    df = fl
    buy_group = df.groupby('buyer').agg({
        'quantity': 'sum',
        'amount': 'sum'
    }).reset_index().rename(columns={
        'buyer': 'Broker',
        'quantity': 'bqty',
        'amount': 'Buy Amount'
    })

    sell_group = df.groupby('seller').agg({
        'quantity': 'sum',
        'amount': 'sum'
    }).reset_index().rename(columns={
        'seller': 'Broker',
        'quantity': 'sqty',
        'amount': 'Sell Amount'
    })

    stoc = pd.merge(buy_group, sell_group, on='Broker', how='outer').fillna(0)

    bqt=stoc['bqty'].sum()
    sqt=stoc['sqty'].sum()

    stoc = stoc.dropna(axis=0, how = 'all')
    stoc['brate']=(stoc['Buy Amount']/stoc['bqty'])
    stoc['srate']=(stoc['Sell Amount']/stoc['sqty'])

    stoc['buyPercentage']=(stoc['bqty']/bqt)*100
    stoc['sellPercentage']=(stoc['sqty']/sqt)*100
    stoc['diff']=(stoc['buyPercentage']-stoc['sellPercentage'])
    stoc['holding'] = stoc['bqty']-stoc['sqty']
    stoc['percetageHold'] = (stoc['holding']/bqt)*100
    stoc['wacchold'] = (stoc['Buy Amount']-stoc['Sell Amount'])/(stoc['bqty']-stoc['sqty'])

    total_row = stoc.sum(numeric_only=True).to_dict()
    total_row['Broker'] = 'Total'
    stoc = pd.concat([stoc, pd.DataFrame([total_row])], ignore_index=True)

    stoc=stoc.sort_values(by=['holding'], key=abs, ascending=False)

    stoc = stoc.reindex(columns=['Broker','bqty','sqty','brate','srate','buyPercentage','sellPercentage','holding','percetageHold','wacchold'])
    stoc=stoc.round(2)
    return stoc




def oextract_csv(iid,uno,start):
    floorsheet_df=pd.DataFrame()
    ii=0
    iii=0
    for i in range(0, 10000):
        day=(start - datetime.timedelta(i)).isoformat()
        nabil=ogen_df(iid,day)
        floorsheet_df = pd.concat([floorsheet_df, nabil])
        if nabil.any().empty == False:
            iii=0
            ii=ii+1

        else:
          iii=iii+1

        dayy = datetime.datetime.strptime(day, '%Y-%m-%d').date()

        if isinstance(uno, int):
            if ii==uno or iii==35:
                break
            else:
                pass


        elif dayy <= uno:
            break
        else:
            pass

    return floorsheet_df

