# RAE_Forecasting
The main task of this project is to collect data on Renewable Energy Permits for every Greek region from the official site of RAE , visualize them using the appropriate filters and visualization charts, and finally provide an API for your forecast predictions concerning the number of permits or MW production expected in the following period.


### Detailed Objectives

- Identify possible problems within the dataset - Perform an EDA analysis
- Visualize the EDA analysis results using Streamlit (separate page - Exploratory
Analysis)
- Visualize the content of the collected data with appropriate filtering; you can choose
what to visualize and which filters to use (separate page - Observatory). This page
should also include a map of the regions with the numbers of permits accordingly.
- Using the collected data, develop a forecasting methodology that will be able to
predict the number of permits and/or the total MWs production in the forthcoming
weeks/months. Also external datasets that may improve the predictions can be used.
- Develop a simple (no authentication required) API using Python (e.g. Flask, Fast
API) that will include endpoints for providing your predictions.
- Include a separate page for your forecasting solution in your Streamlit App
(Forecasting) that will visualize your predictions and some metrics on the accuracy of
your model/method.

Data Available on RAE Permits page: https://www.rae.gr/ape/adeiodotisi-2/adeies-ape/

### Prerequisites
- You need to have an active conda installation. For installation steps please refer here: https://conda.io/projects/conda/en/latest/user-guide/install/index.html 
- To use the exact develpoment environment in conda you can execute the following in the root directory of the project: <code>conda env create -f environment.yml</code> (you can also use -n <name> to define an env name) (env py3.12 was used for v2 jupyter due to code issues and py3.11 for the rest)
- Activate the new conda environment by executing <code>conda activate <env_name></code>

### Testing

- For testing, you need to start the API Script and the Streamlit Application. 

To start the API, run the following command:

```shell
python3 src/api/app.py
```

To start the Streamlit Application, run the following command:

```shell
streamlit run Navigation_Page.py
```

In the application when prompted to upload a file, please use the: 

```shell
./data/processed_data/all_ape_data_nodup_rsi.csv
```

Current testing has been performed with this dataset extracted from jupyter Notebooks. Future TODOs would include having a more lenient format for uploading (Roadmap :P). 