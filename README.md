# Reaction Screening and Solubility Graph Visualiser

This is a Streamlit based application for the visualisation of reaction screening, solubility studies and time course plots from Excel data. The tool allows for quick and easy generation of Python graphs from UPLC data tables, time course data etc. without having to write code.

Link to [Streamlit Graph Visualiser](https://graph-visualisation.streamlit.app/) 

# Features 
## Reaction Screening :bar_chart:
Reaction screening data visualisation can be displayed in three different ways:
1. Stacked bar chart - Impurities Combined
2. Stacked bar chart - Specific
3. Pie chart - Impurities combined

The _impurities combined_ option automatically combines columns that begin with 'Imp', 'imp', 'Unk' and 'unk'. The combined impurities bars default name is _'Impurities'_, however, this can be updatd by the user.

If the  _impurities combined_ option is not wanted or required the specific option can be selected instead and each compount can be plotted individually.

Optional LCAP labelling of each bar is available in all modes.


## Solubility Studies 🧪
Solubility study option is used to display solubility data (as a concentration) in bar chart form.

Multiple temperatures can be plotted and compared at once.

Able to add solubility values to the top of each bar and modify font size.

Able to add threshold line at desired concentration.


## Time Course and Line Plots :chart_with_upwards_trend:
Time course data and line plots are primarily used as time course plots but can be used to plot most data.

Multiple line plots can be added at once.

Able to customise figure size and axis limits.

Able to adjust legend labelling.

## HTS Visualisation 🥧📈
HTS Visualisation is used for generating pie charts for 24-96 well reactions (can also be used on smaller reaction screens).

Has an automatic _'Others'_ segment for any unselected columns.

Condition based grouping, for example if multiple bases or solvents are detected it will group them under the same column.

# How to Use
Each graph type has instructions of how to use them on the [graph visualiser page](https://graph-visualisation.streamlit.app/) along with a downloadable excel template that can be filled out by the user. this is the general format of the instructions:
1. Select _Graph Type_
2. Download associated _Excel Template_
3. Fill template with user results
4. Upload completed _Excel Template_
5. Customise number of variables, labels, colours, font sizes etc.
6. Graph will be generated from results.

 



