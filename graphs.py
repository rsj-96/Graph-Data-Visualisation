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
#import math

#st.write(print(os.getcwd())) # finds files path of repository

# Name of Script
st.title('Graphs for Reaction Screens and Solubility Studies')  # Replace with your script name
st.subheader('Select Graph Type') # subheader

graph = st.radio('Pick one:', ['Solubility Study', 'Reaction Screen Bar Chart - Impurities Combined', 'Reaction Screen Bar Chart - Specific', 'Reaction Screen Pie Chart - Impurities Combined', 'HTS Pie Chart', 'Line Plot'])

# Description
st.markdown('''
    This application helps to visualise data in graphical forms
    ''')  #Small description of what the application does


font_path = "/mount/src/solubility-graphs/GOTHIC.TTF"
font_prop = fm.FontProperties(fname=font_path)

# Apply the font globally for all plots
plt.rcParams['font.family'] = font_prop.get_name()

# REACTION SCREEN WHERE THE IMPURITIES ARE COMBINED

if graph =='Reaction Screen Bar Chart - Impurities Combined':
    
    #Screen Sheet Download
    
    data = {
            "Conditions": ['Ethanol, xx (5 eq).', 'Me-THF, xx (5 eq.)', 'Toluene, xx (5 eq.)'],
            "SM": [10, 50, 80],
            'Product' : [70, 40, 10],
            'Imp 1' : [5, 3, 10],
            'Imp 2' : [15, 7, 0],
        }  # Random data that can be replaced
    
    excel_template = pd.DataFrame(data) # transformation of the data dictionary to a pandas data frame

    excel_file = io.BytesIO() # in-memory binary stream to store the excel file - will be written into a stream rather than a file to be saved on a disk

    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer: # pd.ExcelWriter is a pandas function for converting data into an excel file
        excel_template.to_excel(writer, index=False, sheet_name='Sheet1') # converts the stream file to an excel file

    
    excel_file.seek(0) #  resets pointer back to the beginning
    
    # Downloader for template file

    st.subheader("Instructions")
       
    with st.expander("Quick instruction📝"): 
        st.markdown('''
                1.	Download Screen Template and fill with UPLC data. The filled Excel sheet must have a column named ‘Conditions’ to work but the conditions column can be filled with any writing.
                2.	For this data visualiser, a column beginning with _Imp_ or _Unk_ will be combined into an ‘Impurities column’. For this reason, _known_ impurities should be named something else if you would like them to be plotted separately.
                3.	If needed alter the _x-axis label_, _Chart title_, _font size_ and _Chart colours_. If you do not want an x-axis or chart title leave the box empty, unaltered colours will be left as the default colour.
                4.	Select the number of _Products/Reagents_ to be plotted. Please note that Product/reagent values need to correspond _exactly_ with what is typed in the spreadsheet to be plotted.
                5.	If you would like a LCAP value for your starting material or product to be added to the chart tick the corresponding checkbox
                6.	A Stacked bar chart of your screening reaction will be generated.
                7.  Any questions or feedback please speak to RJ
                ''')
    
    st.subheader('Upload Screening Data')
    
    file = st.file_uploader("Choose an '.xlsx' (excel) File for Screen Data", type = ['xlsx']) # streamlit file uploader where the excel type is specified
    
    st.download_button(
                label="Download Screen Sheet Template.xlsx ", # needs to change if you copy it somewhere
                data=excel_file,
                file_name="Screening_Template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )  # Makes it so you can download the excel file with the streamlit widget
    
    
    if file:
        try:
            df = pd.read_excel(file)  # reads the file into the dataframe using pandas
            
            st.write('Preview of Excel file')
            st.write(df.head()) # displays dataframe in the streamlit application
    
            st.subheader('Customise Plot Labelling')
            
            x_axis = st.text_input('Enter x-axis Label', 'Conditions') # collects user inputs for labels using streamlit widget
               
            title = st.text_input('Enter chart title', 'Reaction Screen of XX') # collects user inputs for title using streamlit widget
            size = st.number_input('Enter label font size',min_value=1, max_value=20, value=9)
            
            
            st.subheader("Customise Plot Variables")
            
            #Dynamic Variables
            
            variables = []
            num_variables = st.number_input("Number of Products/Reagents", min_value=1, max_value=20, value=2, step=1)
            default_colours = ['#118ab2','#06d6a0','#ffd166','#dabfff','#f48c06', '#ff8fa3']
            colours = []
            
            for x in range(num_variables):
                col1, col2 = st.columns([2,1])
                with col1:
                    var_name = st.selectbox(f'Product/Reagent {x+1} name', df.columns)
                    variables.append(var_name)
                with col2:
                    default = default_colours[x % len(default_colours)]
                    colour = st.color_picker(f'Pick a colour for {x+1}', default)
                    colours.append(colour)
            
                
            col1, col2 = st.columns([2,1])
            with col1: 
                impurities = st.text_input('Rename impurities?', 'Impurities')
            with col2:
                imp_colour = st.color_picker('Pick a colour', '#ff8fa3')
                colours.append(imp_colour)
            
                        
            for var in variables:
                if var in df.columns:
                    pass
                else:
                    st.write(f"Warning: Column '{var}' does not exist in File")
            # Tick boxes for labelling:
            
            st.subheader("Label Variable on Graph?")
            
            labelling = {}
            
            for var in variables:
                labelling[var] = st.checkbox(f"Label {var} LCAP")
                
                    
            labelling_imps = st.checkbox(f"Label {impurities} LCAP")
                
            st.write(' ')
            
            
            legend = variables + [impurities]
            
            #colours_specific = ['#118ab2', '#06d6a0', '#ffd166', '#f48c06', '#ef476f', '#ff8fa3', '#dabfff']
            
            if not df.empty:
               
                df.replace('-', 0, inplace=True)
     
                imp_cols = [col for col in df.columns if col.startswith('imp') or col.startswith('Imp') or col.startswith('imp ') or col.startswith('Imp ') or col.startswith('Unk') or col.startswith('unk')] # select columns starting with a certain word
    
                df[impurities] = df[imp_cols].sum(axis=1) # will create a new column called impurities where the column name starts with imp/unk etc. and will sum this row wise (axis=1) is required
    
                df.drop(columns=imp_cols, inplace=True) # gets rid of the old columns that were used in the combined column
    
                selected_columns = ['Conditions'] + [var for var in variables if var in df.columns] + [impurities]
                df = df.loc[:, selected_columns] # how can I automate this selection?
                
                st.write('Preview of Data for Screen Chart')
                st.write(df.head())
    
                df.plot.bar(x='Conditions', stacked=True, color=colours)
                plt.xlabel(x_axis, fontproperties=font_prop)
                plt.ylabel('LCAP / %', fontproperties=font_prop)
                plt.xticks(fontproperties=font_prop)
                plt.yticks(fontproperties=font_prop)
                plt.legend(loc='upper left', bbox_to_anchor=(1,1), prop=font_prop, labels=legend)
                plt.title(title, fontproperties=font_prop)
    
                bars = []
                
                for var in variables:
                    bar_heights = [row[var] if var in row else 0 for _, row in df.iterrows()]
                    bars.append(bar_heights)
    
                # Automated labeling using the dictionary of labeling preferences
                for idx, var in enumerate(variables):
                    if labelling[var]: 
                        for i, row in df.iterrows():
                            value = row[var]
                        # Calculate cumulative bar height for stacked bars
                            cumulative_height = sum(bars[j][i] for j in range(idx))
                            plt.text(i, (value / 2) + cumulative_height, f'{value:.2f}', ha='center', 
                            fontproperties=font_prop, fontsize=size)
                            
                # For labelling the impurities:
                
                bars_imps = []
                for var in variables + ['Impurities']:
                    bar_imp_heights = [row[var] if var in row else 0 for _, row in df.iterrows()]
                    bars_imps.append(bar_heights)
            
                if labelling_imps:
                    for i, row in df.iterrows():
                # Calculate cumulative height for Impurities
                        cumulative_height_imps = 0
                        for j in range(len(variables)):
                            cumulative_height_imps += row[variables[j]]  # Sum up all the previous bars before Impurities
                            value = row['Impurities']
            
                    # Now we can position the Impurities text on top of the cumulative bar stack
                        plt.text(i, (value / 2) + cumulative_height_imps, f'{value:.2f}', ha='center', fontproperties=font_prop, fontsize=size)
    
                st.pyplot(plt.gcf()) # plots the bar chart
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()


# SPECIFIC REACTION SCREEN - ALL COLUMNS MUST BE SPECIFIED

elif   graph =='Reaction Screen Bar Chart - Specific':
    
    #Screen Sheet Download

    data = {
            "Conditions": ['Ethanol, xx (5 eq).', 'Me-THF, xx (5 eq.)', 'Toluene, xx (5 eq.)'],
            "SM": [10, 50, 80],
            'Product' : [70, 40, 10],
            'Imp 1' : [5, 3, 10],
            'Imp 2' : [15, 7, 0],
        }  # Random data that can be replaced
    
    excel_template = pd.DataFrame(data) # transformation of the data dictionary to a pandas data frame

    excel_file = io.BytesIO() # in-memory binary stream to store the excel file - will be written into a stream rather than a file to be saved on a disk

    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer: # pd.ExcelWriter is a pandas function for converting data into an excel file
        excel_template.to_excel(writer, index=False, sheet_name='Sheet1') # converts the stream file to an excel file

    
    excel_file.seek(0) #  resets pointer back to the beginning
    
    # Downloader for template file

    st.subheader("Instructions")
    
    with st.expander("Quick instruction📝"): 
        st.markdown('''
                1.	Download Screen Template and fill with UPLC data. The filled Excel sheet must have a column named ‘Conditions’ to work but the conditions column can be filled with any writing.
                2.	For this data visualiser, _each individual column of the spreadsheet_ needs to be specified in the Products/Reagents boxes.
                3.	If needed alter the _x-axis label_, _Chart title_, _font size_ and _Chart colours_. If you do not want an x-axis or chart title leave the box empty, unaltered colours will be left as the default colours.
                4.	Select the number of _Products/Reagents_ to be plotted. Please note that Product/reagent values need to correspond _exactly_ with what is typed in the spreadsheet to be plotted.
                5.	If you would like a LCAP value for your starting material or product to be added to the chart tick the corresponding checkbox
                6.	A Stacked bar chart of your screening reaction will be generated.
                7.  Any questions or feedback please speak to RJ
                ''')
    
    
    st.subheader("Upload Screening Data")
    
    file = st.file_uploader("Choose an '.xlsx' (excel) File for Screen Data", type = ['xlsx']) # streamlit file uploader where the excel type is specified
    st.download_button(
                label="Download Screen Sheet Template.xlsx ", # needs to change if you copy it somewhere
                data=excel_file,
                file_name="Screening_Template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )  # Makes it so you can download the excel file with the streamlit widget
    
    if file:
        try:
            df = pd.read_excel(file)  # reads the file into the dataframe using pandas
            
            st.write('Preview of Excel file')
            st.write(df.head()) # displays dataframe in the streamlit application
    
            st.subheader("Customise Plot Labelling")
            
            x_axis = st.text_input('Enter x-axis Label', 'Conditions') # collects user inputs for labels using streamlit widget
               
            title = st.text_input('Enter chart title', 'Reaction Screen of XX') # collects user inputs for title using streamlit widget
            
            size = st.number_input('Enter label font size', min_value=1, max_value=20, value=9)
            
            #Dynamic Variables
            
            st.subheader("Customise Plot Variables")
            
            variables = []
            num_variables = st.number_input("Number of Products/Reagents", min_value=2, max_value=20, value=2, step=1)
            default_colours = ['#118ab2', '#06d6a0', '#ffd166', '#f48c06', '#F54105', '#ef476f', '#ff8fa3','#dabfff', '#B185CD', '#A85BBE', '#5865C5', '#5894C4', '#71B3CB']
            colours = []
            
            for x in range(num_variables):
                col1, col2 = st.columns([2,1])
                with col1:
                    var_name = st.selectbox(f'Product/Reagent {x+1} name', df.columns)
                    variables.append(var_name)
                with col2:
                    default = default_colours[x%len(default_colours)]
                    colour = st.color_picker(f'Pick a colour for {x+1}', default)
                    colours.append(colour)
                
            for var in variables:
                if var in df.columns:
                    pass
                else:
                    st.write(f"Warning: Column '{var}' does not exist in File")
                    
            # Tick boxes:
            
            st.subheader("Label Variable on Graph?")
            
            labelling = {}
            
            for var in variables:
                labelling[var] = st.checkbox(f"Label {var} LCAP")
                
            st.write(' ')
            st.write(' ')
            legend = variables
            
            # colours_specific1 = ['#118ab2', '#06d6a0', '#ffd166', '#f48c06', '#F54105', '#ef476f', '#ff8fa3','#dabfff', '#B185CD', '#A85BBE', '#5865C5', '#5894C4', '#71B3CB']
            
            
            if not df.empty:
               
                df.replace('-', 0, inplace=True)
     
                selected_columns = ['Conditions'] + [var for var in variables if var in df.columns]
                df = df.loc[:, selected_columns] # how can I automate this selection?
                
                st.write('Preview of Data for Screen Chart')
                st.write(df.head())
    
                df.plot.bar(x='Conditions', stacked=True, color=colours)
                plt.xlabel(x_axis, fontproperties=font_prop)
                plt.ylabel('LCAP / %', fontproperties=font_prop)
                plt.xticks(fontproperties=font_prop)
                plt.yticks(fontproperties=font_prop)
                plt.legend(loc='upper left', bbox_to_anchor=(1,1), prop=font_prop, labels=legend)
                plt.title(title, fontproperties=font_prop)
    
                
                
                bars = []
                
                for var in variables:
                    bar_heights = [row[var] if var in row else 0 for _, row in df.iterrows()]
                    bars.append(bar_heights)
    
                # Automated labeling using the dictionary of labeling preferences
                for idx, var in enumerate(variables):
                    if labelling[var]: 
                        for i, row in df.iterrows():
                            value = row[var]
                        # Calculate cumulative bar height for stacked bars
                            cumulative_height = sum(bars[j][i] for j in range(idx))
                            plt.text(i, (value / 2) + cumulative_height, f'{value:.2f}', ha='center', 
                            fontproperties=font_prop, fontsize=size)
                            
                st.pyplot(plt.gcf()) # plots the bar chart
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()
                        
        
# SOLUBILITY GRAPHS        
elif   graph =='Solubility Study':
    
    # Solubility sheet download

    data = {
            "Solvent": ["Solvent A", "Solvent B", "Solvent C"],
            "Solubility (mg/ml)": [10, 15, 20],
            "Temperature": [25, 50, 25]
        }  # Random data that can be replaced
    
    excel_template = pd.DataFrame(data) # transformation of the data dictionary to a pandas data frame

    excel_file = io.BytesIO() # in-memory binary stream to store the excel file - will be written into a stream rather than a file to be saved on a disk

    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer: # pd.ExcelWriter is a pandas function for converting data into an excel file
        excel_template.to_excel(writer, index=False, sheet_name='Sheet1') # converts the stream file to an excel file

    
    excel_file.seek(0) #  resets pointer back to the beginning
    
    st.subheader("Instructions")
    with st.expander("Quick instruction📝"): 
        st.markdown('''
                1. Download solubility sheet template
                2. Fill in sheet with solvents/solvent systems, solubility values and temperature
                3. Drag and drop solubility excel file to submit
                4. Fill out Labels and Titles
                5. Generate your Solubility Graph :)
                6. Any questions please speak with RJ
                ''')
    
    
    st.subheader("Upload Solubility Data")
    
    file = st.file_uploader("Choose an '.xlsx' (excel) File for Solubility Data", type = ['xlsx']) # streamlit file uploader where the excel type is specified
    st.download_button(
                label="Download Solubility Sheet Template.xlsx ",
                data=excel_file,
                file_name="Solubility_Template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )  # Makes it so you can download the excel file with the streamlit widget
    
    if file:
        try:
            df = pd.read_excel(file)  # reads the file into the dataframe using pandas
            st.write('Preview of Excel file')
            st.write(df.head()) # displays dataframe in the streamlit application
    
            for x, row in df.iterrows():  # will iterate of each row and if the value is less than 0 will change value to 0
                if row['Solubility (mg/ml)'] < 0: # if the row of colum solubility is less than 0
                    df.at[x, 'Solubility (mg/ml)'] = 0 # value at that point will = 0
             
            
            st.subheader("Cutomise Plot Labelling")
               
            label_1 = st.text_input('Enter Label 1', '25 °C') # collects user inputs for labels using streamlit widget
            label_2 =  st.text_input('Enter Label 2', '50 °C')
            title = st.text_input('Enter chart title', 'Solubility Study at 25°C and 50°C') # collects user inputs for title using streamlit widget
            x_axis = st.text_input('Enter x-axis title', 'Solvent')
    
            sol = st.checkbox(f"Add solubility threshold line?")
            if sol:
                y= st.number_input('Enter solubility threshold', min_value=1, value=20)
            else:
                pass
            
            labelling = st.checkbox(f"label solubility values on graph?")
            if labelling:
                font= st.number_input('Enter fontsize', min_value=1, value=9)
                rot= st.number_input('Enter rotation', min_value=0, value=0)
            else:
                pass
    
            colours = ['#39beea', '#ffa42e'] # specifies the colours, popped in a list so that it stays in order and doesn't assign it randomly
    
            if not df.empty: # command checks if the dataframe is empty or not, if it's not it will progress with plotting the barchart
                
                
                fig, ax = plt.subplots()
                ax = sns.barplot(x='Solvent', y='Solubility (mg/ml)', hue='Temperature', data=df, palette=colours)
                plt.xlabel(x_axis,fontproperties=font_prop)
                plt.ylabel('Solubility (mg/ml)',fontproperties=font_prop)
                plt.xticks(rotation=90, fontproperties=font_prop)
                plt.yticks(fontproperties=font_prop)
                plt.title(title, fontproperties=font_prop)
                if sol:
                    plt.axhline(y=y, color='#84848b', linestyle='--', linewidth=0.7)
                else:
                    pass
                
                if labelling:
                    for container in ax.containers:
                        ax.bar_label(
                            container, 
                            fmt='%.1f', 
                            label_type='edge', 
                            fontsize=font, 
                            padding=1,
                            rotation = rot
                        )
    
                handles, labels = ax.get_legend_handles_labels() # gets the existing legend but need to define the ax first (see above) and also place this after the graph has been plotted!
                new_labels = [label_1, label_2] # defining labels from the user inputs
                ax.legend(handles=handles, labels=new_labels, loc='upper right', bbox_to_anchor=(1.2,1), prop=font_prop) #handles is the original legend and colours that you have defined previously, and then labels is the new thing you have defined
    
                st.pyplot(fig) # plots the bar chart
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()
            
elif graph == 'Line Plot':
    data = {
            "Time (s)": [0,1,2,3,4,5,6],
            "Condition": [0.0078817,0.0078166,0.0077188,0.0076861,0.0077188,0.0077514,0.0077189],
        }  # Random data that can be replaced
    
    excel_template = pd.DataFrame(data) # transformation of the data dictionary to a pandas data frame

    excel_file = io.BytesIO() # in-memory binary stream to store the excel file - will be written into a stream rather than a file to be saved on a disk

    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer: # pd.ExcelWriter is a pandas function for converting data into an excel file
        excel_template.to_excel(writer, index=False, sheet_name='Sheet1') # converts the stream file to an excel file

    
    excel_file.seek(0) #  resets pointer back to the beginning
    
    st.subheader("Instructions")
    
    with st.expander("Quick instruction📝"): 
        st.markdown('''
                1.	Upload and excel file to the drag and drop area.
                2.  Preview of the data in the file will be displayed.
                3.  Select the number of variables (columns) you want to plot and select columns using the dropdown box.
                4.  Fill out the 'Customise Plot' Section with, Plot tile and x and y axis labels. If you do not want these labelling fill with an empty space.
                5.  If needed chack the 'Define y-axis limits?' box and fill with the appropriate limits.
                6.  Line plot of your data will be generated.
                7.  Any questions or feedback please speak to RJ
                
                ''')
    
    
    st.subheader("Upload Plot Data")
    
    file = st.file_uploader("Choose an '.xlsx' (excel) File for time course plot", type = ['xlsx']) # streamlit file uploader where the excel type is specified
    # Downloader for template file

    st.download_button(
                label="Download Line Plot Template.xlsx ", # needs to change if you copy it somewhere
                data=excel_file,
                file_name="Line Plot.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )  # Makes it so you can download the excel file with the streamlit widget
    
    if file:
        try:
            df = pd.read_excel(file)  # reads the file into the dataframe using pandas
            
            st.write('Preview of Excel file')
            
            edited_df = st.data_editor(df)
            #st.write(df.head()) # displays dataframe in the streamlit application
    
            #Dynamic Variables
            
            default_colours = ['#f48c06','#118ab2','#06d6a0','#ffd166','#dabfff','#ff8fa3']
            
            
            st.subheader("Customise Plot Variables")
            
            x_val = st.selectbox('Enter x-axis Column Name', df.columns)
                   
            variables = []
            num_variables = st.number_input("Number of Variables", min_value=1, max_value=20, value=1, step=1)
            colours = []
            legend_updated = []
            for x in range(num_variables):
                col1, col2, col3 = st.columns([3,1,2]) # inside[] is the column widths
                with col1:
                    var_name = st.selectbox(f'Enter Variable {x+1} name', df.columns)
                    variables.append(var_name)
                
                with col2:
                    default = default_colours[x%len(default_colours)]
                    colour = st.color_picker(f'Pick a colour', default)
                    colours.append(colour)
                
                with col3:
                    leg = st.text_input(f"Change Name of variable {x+1}?", var_name) # update name for legend -- NEED TO UPDATE
                    legend_updated.append(leg)
                
            for var in variables:
                if var in df.columns:
                    pass
                else:
                    st.write(f"Warning: Column '{var}' does not exist in File")
                    
            
            st.subheader('Customise Plot Labelling and Limits')
            
            col1, col2 = st.columns([1,1])
            with col1:
                plot_title = st.text_input('Enter Plot Title', '')
            with col2:
                title_siz = st.number_input("Title Font Size", min_value=1.0, max_value=100.0, value=20.0)
            
            with col1:
                x_axis = st.text_input('Enter x-axis label', x_val)
            with col2:
                x_size = st.number_input("x-axis Font Size", min_value=1.0, max_value=100.0, value=12.0)
            
            with col1:
                rot = st.number_input("x-tick rotation", min_value=-360.0, max_value=360.0, value=0.0)
            with col2:
                tick_size = st.number_input("Tick Font Size", min_value=1.0, max_value=100.0, value=10.0)
            
            with col1:       
                y_axis = st.text_input('Enter y-axis label', 'Variable')
            with col2:
                y_size = st.number_input("y-axis Font Size", min_value=1.0, max_value=100.0, value=12.0)
            
            leg_size = st.number_input("Legend Font Size", min_value=1.0, max_value=100.0, value=10.0)
            
            st.write("Modify Figure Size")
            col1, col2 = st.columns([1,1])
            with col1:
                a = st.number_input("width", min_value=1.0, max_value=100.0, value=6.4)
            with col2:
                b = st.number_input("height", min_value=1.0, max_value=100.0, value=4.8)
            
            
            limits = st.checkbox('Define y-axis limits?')
            
            if limits:
                col1, col2 = st.columns([1,1])
                with col1: 
                    limit_one = st.number_input('Insert lower limit', value=None, placeholder="Type a number...")
                with col2:
                    limit_two = st.number_input('Insert upper limit', value=None, placeholder="Type a number...")
                    
                y_limits = (limit_one, limit_two)
            
            else:
                y_limits = None
    
            if not df.empty:
               
                variables_updated = [var for var in variables if var in df.columns]
                #legend_updated = [var for var in variables_updated]
            
                selected_columns = [x_val] + variables_updated
                df = df[selected_columns] 
                
                st.write('Preview of Data for Time Course Plot') # Change as needed
                st.write(df.head())
                
                
                df.plot.line(x=x_val, y= variables_updated, color = colours, figsize=(a,b))
                plt.xlabel(x_axis, fontproperties=font_prop, fontsize=x_size)
                plt.ylabel(y_axis, fontproperties=font_prop, fontsize=y_size)
                plt.xticks(fontproperties=font_prop, rotation=rot, fontsize= tick_size)
                plt.yticks(fontproperties=font_prop, fontsize= tick_size)            
                plt.legend(loc='upper left', bbox_to_anchor=(1,1), labels=legend_updated, fontsize=leg_size)
                plt.title(plot_title, fontproperties=font_prop, fontsize= title_siz) 
                
                
                if y_limits:
                    plt.ylim(y_limits)
                
                st.pyplot(plt.gcf()) # plots the line plot
    
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()


elif graph == 'Reaction Screen Pie Chart - Impurities Combined':
    data = {
            "Conditions": ['Ethanol, xx (5 eq).', 'Me-THF, xx (5 eq.)', 'Toluene, xx (5 eq.)'],
            "SM": [10, 50, 80],
            'Product' : [70, 40, 10],
            'Imp 1' : [5, 3, 10],
            'Imp 2' : [15, 7, 0],
        }  # Random data that can be replaced
    
    excel_template = pd.DataFrame(data) # transformation of the data dictionary to a pandas data frame

    excel_file = io.BytesIO() # in-memory binary stream to store the excel file - will be written into a stream rather than a file to be saved on a disk

    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer: # pd.ExcelWriter is a pandas function for converting data into an excel file
        excel_template.to_excel(writer, index=False, sheet_name='Sheet1') # converts the stream file to an excel file

    
    excel_file.seek(0) #  resets pointer back to the beginning
    
    st.subheader("Instructions")
    
    with st.expander("Quick instruction📝"): 
        st.markdown('''
                1.	Download Screen Template and fill with UPLC data. The filled Excel sheet must have a column named ‘Conditions’ to work but the conditions column can be filled with any writing and will be the title for each pie chart. If you do not want a tile for the pie chart fill the conditions column with a space(' ').
                2.	For this data visualiser, a column beginning with _Imp_ or _Unk_ will be combined into an ‘Impurities column’. For this reason, _known_ impurities should be named something else if you would like them to be plotted separately.
                3.	If needed alter the _font size_ and _chart colours_. Chart colours will be left as the default if unchanged
                4.	Select the number of _Products/Reagents_ to be plotted. Please note that Product/reagent values need to correspond _exactly_ with what is typed in the spreadsheet to be plotted.
                5.	Pie chart of your screening reaction will be generated.
                6.  Any questions or feedback please speak to RJ
                ''')
    
    st.subheader("Upload Screening Data")
    
    file = st.file_uploader("Choose an '.xlsx' (excel) File for Screen Data", type = ['xlsx']) # streamlit file uploader where the excel type is specified
    # Downloader for template file
    
    st.download_button(
                label="Download Screen Sheet Template.xlsx ", # needs to change if you copy it somewhere
                data=excel_file,
                file_name="Screening_Template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )  # Makes it so you can download the excel file with the streamlit widget
    
    if file:
        try:
            df = pd.read_excel(file)  # reads the file into the dataframe using pandas
            
            st.write('Preview of Excel file')
            st.write(df.head()) # displays dataframe in the streamlit application
    
            #Dynamic Variables
            
            st.subheader("Customise Plot Variables")
            
            default_colours = ['#118ab2','#06d6a0','#ffd166','#dabfff','#f48c06', '#ff8fa3']
            
            variables = []
            num_variables = st.number_input("Number of Products/Reagents", min_value=1, max_value=20, value=2, step=1)
            colours = []
            
            for x in range(num_variables):
                col1, col2 = st.columns([2,1]) # inside[] is the column widths
                with col1:
                    var_name = st.selectbox(f'Product/Reagent {x+1} name', df.columns)
                    variables.append(var_name)
                
                with col2:
                    default = default_colours[x%len(default_colours)]
                    colour = st.color_picker(f'Pick a colour', default)
                    colours.append(colour)
            
            col1, col2 = st.columns([2,1])
            with col1: 
                impurities = st.text_input('Rename impurities?', 'Impurities')
            with col2:
                imp_colour = st.color_picker('Pick a colour', '#ff8fa3')
                colours.append(imp_colour)
            
            for var in variables:
                if var in df.columns:
                    pass
                else:
                    st.write(f"Warning: Column '{var}' does not exist in File")
                    
                   
            # datafram rearrangement (collecting all the imps together):
            
            df.replace('-', 0, inplace=True)
     
            imp_cols = [col for col in df.columns if col.startswith('imp') or col.startswith('Imp') or col.startswith('imp ') or col.startswith('Imp ') or col.startswith('Unk') or col.startswith('unk')] # select columns starting with a certain word
    
            df[impurities] = df[imp_cols].sum(axis=1) # will create a new column called impurities where the column name starts with imp/unk etc. and will sum this row wise (axis=1) is required
    
            df.drop(columns=imp_cols, inplace=True) # gets rid of the old columns that were used in the combined column
    
            selected_columns = ['Conditions'] + [var for var in variables if var in df.columns] + [impurities]
            df = df.loc[:, selected_columns] 
        
            
            st.subheader("Customise Labelling Properties")
            
            #inputs for labels
            
            col1, col2 = st.columns([3,1])
            with col1:
                title_size = st.number_input('Enter Pie title font size', min_value=1, max_value=50, value=22)
            with col2:
                st.write(' ')
                st.write(' ')
                tick = st.checkbox('Include title labels?')
            
            size_label = st.number_input('Enter Pie label font size', min_value=1, max_value=50, value=20)
            
            
            #segment = st.checkbox("Label Segments with")
            
            # Defining plot pies
            num_rows = len(df)
            num_cols = min(num_rows, 4) #max of 4 columns per row # could probablt make a selection thing for this!
            num_subplot_rows = np.ceil(len(df) / 4).astype(int) # calculates
            
    
            # Best to use subplots for pie charts
    
            fig, axes = plt.subplots(num_subplot_rows, num_cols, figsize=(20,5*num_subplot_rows)) # 1 row and df columns
            #fig, axes = returns two objects. fig-overall figure, ax- an array of individual objects (one for each pie chart)
            
            axes = axes.flatten() # makes it so you don't get that numpy error when you want additional rows
    
            labels = df.columns[1:] # gets column names but ignores the first one for labelling
            wedges = [] # empty list to store the pie chart segments
            autotexts_all = []
    
            #colours = ['#118ab2','#06d6a0','#ffd166','#ff8fa3','#dabfff','#f48c06']
    
            
            for r, (index, row) in enumerate(df.iterrows()): # r - index of the row but this whole line loops over each row of df index is row index
                ax = axes[r]
                wedges, texts, autotexts = ax.pie(row[1:], autopct = '%1.1f%%', colors=colours, startangle=360)
                # texts = labels of each wedge, wedges = objects representing pie slices, autotexts = text annotations inside the wedges
                #ax.set_title(row[0],fontsize=32, fontproperties=None)
                if tick:
                    ax.text(0.5, 1, row[0], fontsize=title_size, ha='center', va='bottom', transform=ax.transAxes)
                else:
                    pass
                wedges.extend(wedges) # appends individual wedges into wedges list and is used for making the global legend
                
    
                
                for i, autotext in enumerate(autotexts):
                    value = float(row[i+1])  # Get the value corresponding to this wedge
                    
                    # Set label size and position
                    autotext.set_fontsize(size_label)
                    
            
                    # Adjust position: inside if large enough, outside if too small
                    if value > 5.5: 
                        autotext.set_horizontalalignment("center")
                    else:
                # Move text outside for small segments
                        x, y = autotext.get_position()
                        scaled_x = 2.5 * x
                        scaled_y = 2.5*y
                        
                        autotext.set_position((scaled_x, scaled_y))  # Push it out a bit
                        autotext.set_ha("center")  # Center-align the text
                        ax.annotate(' ', xy=(x, y), xytext=(x*2.1, y*2.1), arrowprops=dict(arrowstyle="-", lw=0.7, color='black')
                        )
                        
            # wedge-pie chart slices, texts-objects representing labels auto texts-obects representing percentages
    
            for r in range(num_rows, len(axes)):  #will hide extra plots
                axes[r].set_visible(False)
            
            fig.legend(wedges[:len(labels)], labels, loc="upper left",bbox_to_anchor=(1,1),fontsize=25)
    
            plt.subplots_adjust(top=1)
            plt.tight_layout(h_pad=5) # change distance between pie plots
            
            st.pyplot(fig)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()
            
#--HTS PIES--
else: # graph == 'HTS Pie Chart'

    data = {
            "SM": [5.43, 8.57, 14.49, 1.25, 5.77, 12.95, 0.48, 5.17, 15.53, 0.48, 5.49, 13.94],
            'Product' : [89.62, 86.65, 81.51, 94.29, 90.41, 84.33, 94.68, 89.49, 81.6, 90.42, 88.17, 80.66],
            'Imp 1' : [2.69, 2.92, 2.2, 2.1, 2.13, 1.22, 1.96, 1.43, 0.74, 0.9, 0.17, 0.11],
            'Imp 2' : [1.24, 1.09, 0.94, 1.03, 1.16, 1.1, 1.14, 3.59, 0.99, 1.13, 1.1, 0.95],
            'x-Conditions' : ['1.5 h', '1.5 h', '1.5 h', '3.5 h', '3.5 h', '3.5 h', '5.5 h', '5.5 h', '5.5 h', '24 h', '24 h', '24 h'],
            'y-Conditions' : ['2.3 eq Base', '1.5 eq Base', '1.1 eq Base', '2.3 eq Base', '1.5 eq Base', '1.1 eq Base', '2.3 eq Base', '1.5 eq Base', '1.1 eq Base', '2.3 eq Base', '1.5 eq Base', '1.1 eq Base']
        }  # Random data that can be replaced 
    
    excel_template = pd.DataFrame(data) # transformation of the data dictionary to a pandas data frame

    excel_file = io.BytesIO() # in-memory binary stream to store the excel file - will be written into a stream rather than a file to be saved on a disk

    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer: # pd.ExcelWriter is a pandas function for converting data into an excel file
        excel_template.to_excel(writer, index=False, sheet_name='Sheet1') # converts the stream file to an excel file

    
    excel_file.seek(0) #  resets pointer back to the beginning
    
    # Downloader for template file

    st.download_button(
                label="Download HTS Pie Template.xlsx ", # needs to change if you copy it somewhere
                data=excel_file,
                file_name="HTS_Pie_Template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )  # Makes it so you can download the excel file with the streamlit widget
    
    with st.expander("How to Use📝"): 
        st.markdown('''
                1.	Upload Excel file to file uploader.
                2.  Use dropdown boxes to select columns to be plotted, and columns not selected in the dropdown boxes with automatically be combined and plotted as 'Others'.
                3.  Select x and y conditions.
                4.  Customise plot with title (if required), font szie, legend positioning and value labelling.
                5.  Wait for plot to be generated.
                6.  Any questions speak with RJ.

                ''')
    
    file = st.file_uploader("Choose an '.xlsx' (excel) File for Screen Data", type = ['xlsx']) # streamlit file uploader where the excel type is specified
    if file:
        try:
            df = pd.read_excel(file)  # reads the file into the dataframe using pandas
            
            st.write('Preview of Excel file')
            st.write(df.head()) # displays dataframe in the streamlit application
            
            df.columns = df.columns.str.strip() # removes any leading or trailiong spaces
            
            #Select columns
            
            st.subheader("Select Data to Include")
            st.write("Please note that this must match the naming of the columns in .xlsx file")
            
            default_colours = ['#118ab2','#06d6a0','#ffd166','#dabfff','#f48c06', '#ff8fa3']
            
            variables = []
            num_variables = st.number_input("Number of Products/Reagents", min_value=1, max_value=20, value=2, step=1)
            colours = []
            
            for x in range(num_variables):
                col1, col2 = st.columns([2,1]) # inside[] is the column widths
                with col1:
                    var_name = st.selectbox(f'Product/Reagent {x+1} name', df.columns)
                    variables.append(var_name)
                
                with col2:
                    default = default_colours[x%len(default_colours)]
                    colour = st.color_picker(f'Pick a colour', default)
                    colours.append(colour)
            
            for var in variables:
                if var in df.columns:
                    pass
                else:
                    st.write(f"Warning: Column '{var}' does not exist in File")
                    
            st.subheader("Select Reaction Conditions")
            st.write("Please note that this must match the naming of the columns in .xlsx file")
            
            x_conditions = st.selectbox("x-conditions", df.columns)
            
            y_conditions=st.selectbox("y-conditions", df.columns)
            
            st.subheader("Customise Plot")
            
            col1, col2 = st.columns([3,1])
            with col1:
                title = st.text_input("Input plot title")
            with col2:
                title_size = st.number_input('Font size', min_value=1, max_value=50, value=20)
            
            col1, col2 = st.columns([3,1])
            with col1:
                size_label = st.number_input('Input x_y labelling font size', min_value=1, max_value=100, value=15)
            with col2:
                dis= st.number_input('Input column padding', min_value=-3, max_value=50, value=20)
            
            col1, col2 = st.columns([3,1])
            with col1:
                legend_size = st.number_input('Input legend font size', min_value=1, max_value=100, value=15)
            with col2:
                pad = st.number_input('Input legend padding', min_value=-3.00, max_value=5.00, value=0.00)
            
            
            all_columns = set(df.columns)
            selected_columns = set(variables + [x_conditions, y_conditions])
            unselected_columns = list(all_columns - selected_columns)
    
            if unselected_columns:
                col1, col2 = st.columns([3,1])
                with col1:
                    others = st.text_input('Rename Others?', 'Others')
                with col2:
                   oth_colour = st.color_picker('Pick a colour', '#ff8fa3')
                
                df[others] = df[unselected_columns].sum(axis=1)
                variables.append(others)
                colours.append(oth_colour)
            else:
                pass
            
            labels = st.checkbox('Include value labelling?')
            if labels:
                label_size = st.number_input('Input label font size', min_value=1, max_value=100, value=15)
            else:
                pass
                
            
            # Select relevant columns
            df = df[variables + [y_conditions, x_conditions]] # combine the columns
    
            # Dynamically detect solvent and condition categories
            solvent_order = sorted(df[y_conditions].dropna().unique())
            condition_order = sorted(df[x_conditions].dropna().unique()) # drops any repeated values or empty values and then orders them alphabetically
    
            # Set categorical ordering
            df[y_conditions] = pd.Categorical(df[y_conditions], categories=solvent_order, ordered=True)
            df[x_conditions] = pd.Categorical(df[x_conditions], categories=condition_order, ordered=True) #sets both columns to be categorical
    
            # Group and average numeric values
            grouped = df.groupby([y_conditions, x_conditions]).mean(numeric_only=True).reset_index() # groups by specific columns and averages numeric data
    
            # Pivot for each component --
            
            pivots = {var: grouped.pivot(index=y_conditions, columns=x_conditions, values=var).fillna(0) for var in variables}
            
            # Build matrix of pie chart slices
            data = [[tuple(pivots[var].loc[y_val, x_val] for var in variables)
                    for x_val in condition_order]
                    for y_val in solvent_order]
    
            # Dynamic sizing
            n_rows = len(solvent_order) # size by number of solvents
            n_cols = len(condition_order) # size by conditions
    
            fig, axs = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(14, 14))
            
            def custom_autopct(pct):
                return f'{pct:.1f}%' if pct > 0 else ''
            
            
            # Generate pie charts and label pie segments (if you've checked labels)
            for i in range(n_rows):
                for j in range(n_cols):
                    ax = axs[i, j]
                    entry = data[i][j]
                    if isinstance(entry, tuple) and any(pd.notna(val) and val > 0 for val in entry):
                        
                        if labels:
                            wedges, texts, autotexts = ax.pie(
                            entry,
                            colors=colours,
                            startangle=90,
                            counterclock=False,
                            wedgeprops={'linewidth': 0.5},
                            autopct=custom_autopct,
                            #radius = 1.3,
                            #pctdistance=0.6
                            )
                        else:
                            wedges, texts = ax.pie(
                                entry,
                                colors=colours,
                                startangle=90,
                                counterclock=False,
                                wedgeprops={'linewidth': 0.5},
                                autopct=None
                            )
                            autotexts = []
                        
                        
    
                    for value, text in zip(entry, autotexts):
                        text.set_fontsize(label_size)
    
                        if value < 15:
                            x, y = text.get_position()
                            text.set_position((x * 2.3, y * 2.3))
                            text.set_ha("center")
                            text.set_color("black")
    
                            ax.annotate(
                                '', xy=(x, y), xytext=(x * 1.9, y * 1.9),
                                arrowprops=dict(arrowstyle='-', color='black', lw=0.5)
                            )
                        else:
                            pass
                    
                    else:
                        ax.set_facecolor('#f0f0f0')
                    ax.set(aspect='equal')
                    ax.axis('off')
                                    
    
            # Label columns and rows
            for j, condition in enumerate(condition_order):
                axs[0, j].set_title(condition, fontsize=size_label, pad=dis)
    
            for i, solvent in enumerate(solvent_order):
                axs[i, 0].annotate(solvent, xy=(-0.4, 0.5), xycoords='axes fraction',
                                ha='right', va='center', fontsize=size_label)
    
            plt.tight_layout()
            plt.subplots_adjust(left=0.15, top=0.92, bottom=0.08)
            plt.suptitle(title, fontsize=title_size) # make an input for this
            
            
            # Add legend
            fig.legend(variables, loc='lower center', bbox_to_anchor=(0.5, pad), ncol=3, fontsize=legend_size, frameon=False)
    
            st.pyplot(fig)
        
    except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()

st.write('Want to generate LC data table? Click below')

st.markdown("""
    <a href="https://lc-data.streamlit.app/" target="_blank">
        <button style="
            background-color:#F0F2F6;
            color: #444352;
            padding: 10px 20px;
            font-size: 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        ">
            Open LC Data App
        </button>
    </a>
""", unsafe_allow_html=True)








