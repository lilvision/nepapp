import requests
import json
import numpy as np
import pandas as pd
from django.shortcuts import render
from .funs import idstock
from .ofun import oextract_csv, id_today, ocsv
import datetime
from django.http import JsonResponse


def get_stock_data(request):
    df = idstock()
    data = df.to_dict(orient='records')
    return JsonResponse({'data': data})

def get_floor_data(request):
    comp = request.GET.get('comp')
    start = request.GET.get('start')
    end = request.GET.get('end')
    interval = request.GET.get('interval')
 
    if comp != 'None' and start != 'None' and interval != 'None':
        print('condition 1')
        start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
        interval = int(interval)

        idx = id_today()
        contain_values = idx[idx['sym'].str.contains(comp.upper())]
        exact_match = contain_values[contain_values['sym'] == comp.upper()]
        idd = exact_match['id'].values[0] if not exact_match.empty else None

        if idd:
            stock = oextract_csv(idd, interval, start)
            if stock.empty:
                return JsonResponse({'error': 'No Data found for the date desired'}, status=404)
            else:
                conc = ocsv(stock)
                conc.replace({0: None, 1: None, np.nan: None, -np.inf: None, np.inf: None}, inplace=True)
                df = conc
                data = df.to_dict(orient='records')
                return JsonResponse({'data': data})
        else:
            return JsonResponse({'error': 'Company not found'}, status=404)



    elif comp != 'None' and start != 'None' and end != 'None':
        print('condition 2')
        start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
        end = datetime.datetime.strptime(end, '%Y-%m-%d').date()

        idx = id_today()
        contain_values = idx[idx['sym'].str.contains(comp.upper())]
        exact_match = contain_values[contain_values['sym'] == comp.upper()]
        idd = exact_match['id'].values[0] if not exact_match.empty else None

        if idd:
            stock = oextract_csv(idd, end, start)
            if stock.empty:
                return JsonResponse({'error': 'No Data found for the date desired'}, status=404)
            else:
                conc = ocsv(stock)
                conc.replace({0: None, 1: None, np.nan: None, -np.inf: None, np.inf: None}, inplace=True)
                df = conc
                data = df.to_dict(orient='records')
                return JsonResponse({'data': data})
        else:
            return JsonResponse({'error': 'Company not found'}, status=404)
        
    else:
        return JsonResponse({'error': 'Invalid input'}, status=400)
        

def display_stocks(request):
    return render(request, 'stocks/display.html')


def display_floor(request):
    comp = request.GET.get('comp')
    start = request.GET.get('start')
    end = request.GET.get('end')
    interval = request.GET.get('interval')

    context = {
        'comp': comp,
        'start': start,
        'end': end,
        'interval': interval
    }
    return render(request, 'stocks/floor.html', context)



def homepage(request):
    return render(request, 'stocks/homepage.html')
