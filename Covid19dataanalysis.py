import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QTextEdit, QMessageBox
)

class CovidAnalysisApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("COVID-19 Data Analysis (USA)")
        self.setGeometry(100, 100, 800, 600)

        self.data_loaded = False
        self.df_us = None

        
        self.load_button = QPushButton("Load & Analyze Data")
        self.summary_button = QPushButton("Show Summary")
        self.plot1_button = QPushButton("Plot Total Cases Over Time")
        self.plot2_button = QPushButton("Plot Daily New Cases")
        self.plot3_button = QPushButton("Show Correlation Heatmap")
        self.plot4_button = QPushButton("Plot Total Cases vs Deaths")
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.load_button)
        layout.addWidget(self.summary_button)
        layout.addWidget(self.plot1_button)
        layout.addWidget(self.plot2_button)
        layout.addWidget(self.plot3_button)
        layout.addWidget(self.plot4_button)
        layout.addWidget(self.output)
        self.setLayout(layout)


        self.load_button.clicked.connect(self.load_and_prepare_data)
        self.summary_button.clicked.connect(self.show_summary)
        self.plot1_button.clicked.connect(self.plot_total_cases)
        self.plot2_button.clicked.connect(self.plot_new_cases)
        self.plot3_button.clicked.connect(self.plot_correlation)
        self.plot4_button.clicked.connect(self.plot_bar)

    def load_and_prepare_data(self):
        try:
            confirmed_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
            deaths_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"

            df_confirmed = pd.read_csv(confirmed_url)
            df_deaths = pd.read_csv(deaths_url)

            df_confirmed_us = df_confirmed[df_confirmed['Country/Region'] == 'US'].copy()
            df_deaths_us = df_deaths[df_deaths['Country/Region'] == 'US'].copy()

            df_confirmed_us = df_confirmed_us.drop(['Province/State', 'Lat', 'Long'], axis=1, errors='ignore')
            df_deaths_us = df_deaths_us.drop(['Province/State', 'Lat', 'Long'], axis=1, errors='ignore')

            df_confirmed_us = df_confirmed_us.melt(id_vars=['Country/Region'], var_name='date', value_name='total_cases')
            df_deaths_us = df_deaths_us.melt(id_vars=['Country/Region'], var_name='date', value_name='total_deaths')

            df_confirmed_us['date'] = pd.to_datetime(df_confirmed_us['date'], format="%m/%d/%y")
            df_deaths_us['date'] = pd.to_datetime(df_deaths_us['date'], format="%m/%d/%y")


            df_us = pd.merge(df_confirmed_us[['date', 'total_cases']], df_deaths_us[['date', 'total_deaths']], on='date')
            df_us['new_cases'] = df_us['total_cases'].diff().fillna(0)
            df_us['new_deaths'] = df_us['total_deaths'].diff().fillna(0)
            df_us['new_cases'] = df_us['new_cases'].clip(lower=0)
            df_us['new_deaths'] = df_us['new_deaths'].clip(lower=0)
            df_us.fillna(0, inplace=True)

            self.df_us = df_us
            self.data_loaded = True
            self.output.setText("✅ Data loaded and analyzed successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data:\n{str(e)}")

    def show_summary(self):
        if not self.data_loaded:
            self.output.setText("⚠️ Please load the data first.")
            return

        total_cases = self.df_us['total_cases'].max()
        total_deaths = self.df_us['total_deaths'].max()
        avg_new_cases = self.df_us['new_cases'].mean()

        summary = (
            f"📊 Summary of Findings (JHU Data):\n"
            f"- Total Cases in US: {int(total_cases):,}\n"
            f"- Total Deaths in US: {int(total_deaths):,}\n"
            f"- Average Daily New Cases: {avg_new_cases:.2f}\n\n"
            f"📈 Line plots show case trends with peaks.\n"
            f"🔥 Heatmap shows correlation between metrics."
        )
        self.output.setText(summary)

    def plot_total_cases(self):
        if self.data_loaded:
            plt.figure(figsize=(10, 6))
            plt.plot(self.df_us['date'], self.df_us['total_cases'], label='Total Cases', color='blue')
            plt.title('Total COVID-19 Cases in United States (JHU Data)')
            plt.xlabel('Date')
            plt.ylabel('Total Cases')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.legend()
            plt.show()

    def plot_new_cases(self):
        if self.data_loaded:
            plt.figure(figsize=(10, 6))
            plt.plot(self.df_us['date'], self.df_us['new_cases'], label='New Cases', color='orange')
            plt.title('Daily New COVID-19 Cases in United States (JHU Data)')
            plt.xlabel('Date')
            plt.ylabel('New Cases')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.legend()
            plt.show()

    def plot_correlation(self):
        if self.data_loaded:
            plt.figure(figsize=(8, 6))
            corr = self.df_us[['total_cases', 'new_cases', 'total_deaths', 'new_deaths']].corr()
            sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
            plt.title('Correlation Between COVID-19 Metrics')
            plt.tight_layout()
            plt.show()

    def plot_bar(self):
        if self.data_loaded:
            total_cases = self.df_us['total_cases'].max()
            total_deaths = self.df_us['total_deaths'].max()
            plt.figure(figsize=(8, 6))
            sns.barplot(x=['Total Cases', 'Total Deaths'], y=[total_cases, total_deaths])
            plt.title('Total Cases vs Total Deaths (US)')
            plt.ylabel('Count')
            plt.tight_layout()
            plt.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CovidAnalysisApp()
    window.show()
    sys.exit(app.exec_())
