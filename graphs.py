import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import io
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import os

# print(os.getcwd()) # finds files path of repository

# Name of Script
st.title('Data Visualisation of Solubility Graphs')  # Replace with your script name

# Description
st.markdown('''
    This application helps to visulise Solubility data
    ''')

# Making template file

data = {
    "Solvent": ["Solvent A", "Solvent B", "Solvent C"],
    "Solubility (mg/ml)": [10, 15, 20],
    "Temperature": [25, 50, 25]
}

excel_template = pd.DataFrame(data)

excel_file = io.BytesIO()


with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
    excel_template.to_excel(writer, index=False, sheet_name='Sheet1')

    
excel_file.seek(0)

# Downloader for template file

st.download_button(
            label="Download Solubility Sheet Template.xlsx ",
            data=excel_file,
            file_name="Solubility_Template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# expander for instructions or something similar
with st.expander("Quick instruction📝"): 
    st.markdown('''
                1. Download solubility sheet template
                2. Fill in sheet with solvents/solvent systems, solubility values and temperature
                3. Drag and drop solubility excel file to submit
                4. Fill out Labels and Titles
                5. Generate your Solubility Graph :)
                ''')
    

# File uploader:

file = st.file_uploader("Choose an '.xlsx' (excel) File", type = ['xlsx'])

# load century gothic font:

font_path = "/mount/src/solubility-graphs/GOTHIC.TTF" 
font_prop = fm.FontProperties(fname=font_path)

# Apply the font globally for all plots
plt.rcParams['font.family'] = font_prop.get_name()

if file:
    df = pd.read_excel(file)  # reads the file into the dataframe using pandas
    st.write(df.head()) # displays dataframe in the streamlit application

    
    label_1 = st.text_input('Enter Temperature 1', '25 °C') # collects user inputs for labels using streamlit widget
    label_2 =  st.text_input('Enter Temperature 2', '50 °C')
    title = st.text_input('Enter chart title', 'Solubility Study at 25°C and 50°C') # collects user inputs for title using streamlit widget
    label_3 = st.text_input('Enter x_axis label', 'Solvent')

    colours = ['#39beea', '#ffa42e'] # specifis the colours, popped in a list so that it stays in order and doesn't assign it randomly

    if not df.empty: # command checks if the dataframe is empty or not, if it's not it will progress with plotting the barchart
    
        fig, ax = plt.subplots()
        ax = sns.barplot(x='Solvent', y='Solubility (mg/ml)', hue='Temperature', data=df, palette=colours)
        plt.xticks(rotation=90, fontproperties=font_prop)
        plt.yticks(fontproperties=font_prop)
        plt.title(title, fontproperties=font_prop)
        plt.axhline(y=20, color='#84848b', linestyle='--', linewidth=0.7)

        handles, labels = ax.get_legend_handles_labels() # gets the existing legend but need to define the ax first (see above) and also place this after the graph has been plotted!
        new_labels = [label_1, label_2] # defining labels from the user inputs
        ax.legend(handles=handles, labels=new_labels, loc='upper right', bbox_to_anchor=(1.2,1), prop=font_prop) #handles is the original legend and colours that you have defined previously, and then labels is the new thing you have defined

        st.pyplot(fig) # plots the bar chart
    else: # if the dataframe is empty the else pharse will occur
        st.write('Please upload an excel file to proceed')
