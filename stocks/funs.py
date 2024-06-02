from concurrent.futures import ThreadPoolExecutor
import datetime
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
import concurrent.futures


def idstock():
  headers = {'X-Requested-With': 'XMLHttpRequest'}
  url = 'https://www.sharesansar.com/today-share-price'

  response = requests.get(url, headers=headers)
  page = BeautifulSoup(response.content, 'html.parser')
  script_tag = page.find('script', string=lambda text: text and 'var cmpjson =' in text)
  cmpjson_text = script_tag.text.strip().split('=', 1)[1].strip().rstrip(';')
  data_list = json.loads(cmpjson_text)
  # tyy=data_list

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
#   df_merged = df_merged.drop(columns=['Closing Price'])
  return df_merged



def gen_df(session,company,days):
    comp=company
    day=days
    num=0
    payload = {'_': '1639245456705','columns[0][data]': 'DT_Row_Index','columns[0][searchable]': 'false','columns[0][orderable]': 'false','columns[0][search][regex]': 'false','columns[1][data]': 'transaction','columns[1][searchable]': 'true','columns[1][orderable]': 'false','columns[1][search][regex]': 'false','columns[2][data]': 'buyer','columns[2][searchable]': 'true','columns[2][orderable]': 'false','columns[2][search][regex]': 'false','columns[3][data]': 'seller','columns[3][searchable]': 'true','columns[3][orderable]': 'false','columns[3][search][regex]': 'false','columns[4][data]': 'quantity','columns[4][searchable]': 'true','columns[4][orderable]': 'false','columns[4][search][regex]': 'false','columns[5][data]': 'rate','columns[5][searchable]': 'true','columns[5][orderable]': 'false','columns[5][search][regex]': 'false','columns[6][data]': 'amount','columns[6][searchable]': 'true','columns[6][orderable]': 'false','columns[6][search][regex]': 'false','columns[7][data]': 'date_','columns[7][searchable]': 'true','columns[7][orderable]': 'false','columns[7][search][regex]': 'false',
               'company': comp,'draw': '1','date': day,'length': '500','search[regex]': 'false','start': num,}

    headers = {'X-Requested-With': 'XMLHttpRequest'}
    url = 'https://www.sharesansar.com/floorsheet'

    response = session.get(url, params=payload, headers=headers)
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
        response = session.get(url, params=payload, headers=headers)
        data = response.json()
        lis=data['data']
        dff = pd.DataFrame.from_records(lis)
        num=num+500
        df = pd.concat([df, dff])

    return df





def extract_csv(session,cname,iid,days,start,idd):
    floorsheet_df=pd.DataFrame()
    ii=0
    iii=0

    cid = iid.index(idd)
    coname=cname[cid]

    for i in range(0, 10000):
        day=(start - datetime.timedelta(i)).isoformat()
        nabil=gen_df(session,idd,day)
        floorsheet_df = pd.concat([floorsheet_df, nabil])
        if nabil.any().empty == False:
            iii=0
            ii=ii+1

        else:
          iii=iii+1
        if ii==days or iii==35:
            break
    floorsheet_df["Scrip"] = coname
    return floorsheet_df




def floor(sst,dinterval):
  print('working1')
  ids=idstock()
  lidd=ids['id'].tolist()
  cname=ids['sym'].tolist()

  session = requests.Session()
  num_threads = 4
  start=sst
  days=dinterval

  with ThreadPoolExecutor(max_workers=num_threads) as executor:
    dfs = []
    results = [executor.submit(extract_csv, session, cname, lidd, days, start, idd) for idd in list(lidd[0:len(cname)])]
    for future in concurrent.futures.as_completed(results):
        df = future.result()
        dfs.append(df)

  df = pd.concat(dfs, ignore_index=True)
  return df

