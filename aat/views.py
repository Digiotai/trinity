from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
import pandas as pd
from django.contrib.auth.decorators import login_required  # for login authentication for veiwing next pages after login
from .forms import CreateUserForm
from django.contrib import messages
import openpyxl
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import json
from datetime import datetime, timedelta
from django.core.files.storage import default_storage
from os import path
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from .graphs import graph

months = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August',
          9: 'September', 10: 'October', 11: 'November', 12: 'December'}
token = "u4zBlWLuV4Ud7xhjwtpzB3UpHD1BBis3HFRsiYYZqb8VE82SBuskzSTBTfoygX8CX1_LaFzftrWit4G_vmxKOQ=="

org = "sumanth.a@digiotai.com"
bucket = "BaltaSoundDT"

options = {'0': 'select a value', 'Balta_Sound': 'Balta_Sound'}


# request page
def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for' + user)
                return redirect('login')
        context = {'form': form}
        return render(request, 'accounts/register.html', context)


##login page
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('fileupload')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            # chek user exist
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.info(request, 'User Name or Password is incorrect')
        context = {}
        return render(request, 'accounts/login.html', context)


# logoutpage
def logoutUser(request):
    path = 'uploads/' + str(request.session.get('uploadedFileName'))
    if os.path.isfile(path):
        os.remove(path)
    logout(request)
    request.session.clear()
    return redirect('login')


th_props = [
    ('font-size', '11px'),
    ('text-align', 'center'),
    ('font-weight', 'bold'),
    ('color', '#6d6d6d'),
    ('background-color', '#f7f7f9')
]

# Set CSS properties for td elements in dataframe
td_props = [
    ('font-size', '11px')
]

# Set table styles
styles = [
    dict(selector="th", props=th_props),
    dict(selector="td", props=td_props)
]


def highlight(cell):
    threshold = cell.median()
    print(threshold)
    colorlst = []
    for i in cell:
        if i > threshold:
            colorlst.append('color: red')
        elif i < threshold:
            colorlst.append('color: limegreen')
        elif i == threshold:
            colorlst.append('background-color: #add8e6')
        else:
            colorlst.append('color: black')
    return colorlst

@login_required(login_url='login')
##overview html page
def RF(request):
    ## reading the xlsx fles
    if request.method == 'GET':
        return render(request, 'accounts/overview.html', {"options": options.items(),'val':'Off'})
    if request.method == 'POST':
        kpi = request.POST.get('kpis', None)
        status = request.POST.get('checkbox', None)
        # data = pd.read_csv('Custemor_analysisV2.csv', index_col=0)
        option = {kpi: options[kpi]}
        for i in options:
            if i != '0' and i not in option:
                option[i] = options[i]
        val = 'Off'
        if status:
            val = 'On'
        if kpi != '1':
            data = {}
            for key, value in months.items():
                data[f'{value}'] = f'../../static/images/{kpi}/RF_{value}_{val}.png'
            return render(request, 'accounts/overview.html', {'data': data.items(), 'options': option.items(),'val':val})

@login_required(login_url='login')
def arima(request):
    if request.method == 'GET':
        with InfluxDBClient(url="https://us-east-1-1.aws.cloud2.influxdata.com", token=token, org=org) as client:
            results = []
            query_api = client.query_api()
            query = ' from(bucket:"BaltaSoundDT")\
          |> range(start: -150m)\
          |> filter(fn:(r) => r._measurement == "BaltaSound")'
            result = query_api.query(org=org, query=query)
            for table in result:
                for record in table.records:
                    print(record.values)
                    results.append([record.values['Location'], record.values['DHI'], record.values['GHI'], record.values['Dewpoint_2m'],
                                    record.values['Precipitation'], record.values['Pressure'],
                                    record.values['SUNANGLE'], record.values['Temp_2m'], record.values['_value']])
        df = pd.DataFrame(results)
        if df.shape[0]>0:
            df.columns = ['Location', 'DHI', 'GHI', 'Dewpoint_2m', 'Precipitation', 'Pressure', 'SUNANGLE', 'Temp_2m', 'BHI']
        return render(request, 'accounts/overview2.html', {'data1':df.to_html(index=False, classes='output_table', table_id="my_id")})
    if request.method == 'POST':
        kpi = request.POST.get('kpis', None)
        # data = pd.read_csv('Custemor_analysisV2.csv', index_col=0)
        option = {kpi: options[kpi]}
        for i in options:
            if i != '0' and i not in option:
                option[i] = options[i]
        if kpi != '0':
            data = {}
            for key, val in months.items():
                data[f'{val}'] = f'../../static/images/{kpi}/Arima_{val}.png'
            return render(request, 'accounts/overview2.html', {'data': data.items(), 'options': option.items()})

@login_required(login_url='login')
##overview html page
def XGB(request):

    if request.method == 'GET':
        return render(request, 'accounts/day.html', {'options': options.items(),'val':'Off'})
    if request.method == 'POST':
        kpi = request.POST.get('kpis', None)
        status = request.POST.get('checkbox', None)
        # data = pd.read_csv('Custemor_analysisV2.csv', index_col=0)
        option = {kpi: options[kpi]}
        for i in options:
            if i != '0' and i not in option:
                option[i] = options[i]
        val = 'Off'
        if status:
            val = 'On'
        if kpi != '1':
            data = f'../../static/images/Balta_Sound_Insights.png'
            return render(request, 'accounts/day.html', {'data': data,'options': options.items(),})


@login_required(login_url='login')
##overview html page
def dashboard(request):
    if request.method == 'GET':
        BullPoint= f'../../static/images/BullPointLightHouse.png'
        BaltaSound = f'../../static/images/BaltaSoundLightHouse.png'
        return render(request, 'accounts/dashboard.html', {'BaltaSound': BaltaSound})
    else:
        kpi = request.POST.get('kpis', None)
        option = {kpi: options[kpi]}
        for i in options:
            if i != '0' and i not in option:
                option[i] = options[i]

        return render(request, 'accounts/location.html',
                      {'b1': f'../../static/images/{kpi}.png',
                       "options": option.items()}
                      )
