# -*- coding: utf-8 -*-
"""
=============================================================================
Created on: 05-09-2021 03:33 PM
Created by: Digiotai
=============================================================================
Project Name: EMO
File Name: graphs.py
Description: Graphs used for EMO
Version: 1.0
Revision: None
=============================================================================
"""
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


def graph(train):
    data = pd.read_csv('completed.csv', index_col=0)
    new_data = data[data['train_no'] == (train)][
        ['train_no', 'WAGONS', "RT", "TONS", "tons_minute", 'LT', 'ST', 'tons_wagon', 'departure_day',
         "departure_date"]]
    for i in new_data.columns.tolist()[1:-2]:
        new_data1 = new_data.sort_values(i)
        new_data1 = new_data1[["departure_date", i]]
        index = new_data1['departure_date'].values.tolist()
        sz = new_data1[i].shape[0]

        median = []
        if (sz % 2) == 0:
            median.append(new_data1.iloc[(sz // 2) - 1, 0])
            median.append(new_data1.iloc[(sz // 2), 0])
        else:
            median.append(new_data1.iloc[(sz // 2), 0])
        fig, ax = plt.subplots(figsize=(22, 10))
        ax.set_xticklabels(labels=index, rotation=90, ha='right')
        clrs = ['red' if (x in median) else 'green' for x in
                new_data1['departure_date']]
        sns.barplot(x='departure_date', y=i, data=new_data1, palette=clrs)

        if i == 'RT':
            ax.set_ylabel('Robot Detach Time', fontsize=15)
            ax.set_title('Train NO ' + train + " Robot Detach Time", fontsize=18)
        elif i == 'LT':
            ax.set_ylabel('Total Load Time', fontsize=15)
            ax.set_title('Train NO ' + train + " Total Load Time", fontsize=18)
        elif i == 'ST':
            ax.set_ylabel('Train Start Time', fontsize=15)
            ax.set_title('Train NO ' + train + " Train Start Time", fontsize=18)
        else:
            ax.set_ylabel(i, fontsize=15)
            ax.set_title('Train NO ' + train + " " + i, fontsize=18)
        ax.set_xlabel('Departure Date', fontsize=15)
        plt.savefig('aat/static/graphs/train_' + i + '.png', format="png")
