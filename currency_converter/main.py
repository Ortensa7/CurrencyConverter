"""
Currency Converter Application
A GUI-based currency converter with historical rate visualization
using the Frankfurter API.
"""

import customtkinter as ctk 
import requests 

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter, DayLocator


from datetime import date, datetime, timedelta

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


fallback_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'NZD']  

def fetch_available_currencies():

    """
    Pulls the current list of supported currrency codes from the 
    Frankfurter API instead of relying on a manyally entered & hardcoded list. 
    Falls back to a pre-defined list if the request fails.
    """
    
    try:
        response = requests.get('https://api.frankfurter.app/currencies', timeout=5)
        response.raise_for_status()
        data = response.json()

        return sorted(data.keys())
    except requests.RequestException:
        return fallback_currencies


class CurrencyConverter:

    """
    A GUI currency converter built with customtkinter.
    Handles user input, API calls, and historical chart rendering.
    """

    def __init__(self):
        # --- Window Setup ---
        self.root = ctk.CTk()
        self.root.title('Currency Converter')
        self.root.geometry('500x800')
        self.root.configure(fg_color="white")
        self.root.grid_columnconfigure(0, weight = 1)
        self.root.grid_columnconfigure(1, weight = 1)

        # --- Empty space at the top
        self.empty_space = ctk.CTkLabel(self.root, text='')
        self.empty_space.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        # --- Currency Selector

        available_currencies = fetch_available_currencies()
        self.from_var = ctk.StringVar(self.root)
        self.from_var.set('USD')
        self.from_menu = ctk.CTkOptionMenu(self.root, variable = self.from_var, values = available_currencies)
        self.from_menu.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.to_var = ctk.StringVar(self.root)
        self.to_var.set('EUR')
        self.to_menu = ctk.CTkOptionMenu(self.root, variable = self.to_var, values = available_currencies)
        self.to_menu.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # --- Amount Input ---
        self.amount_label = ctk.CTkLabel(self.root, text='Amount: ')
        self.amount_label.grid(row=3, column=0, padx=10, pady=5, sticky='ew')

        self.amount_entry = ctk.CTkEntry(self.root)
        self.amount_entry.grid(row=3, column=1, padx=10, pady=5, sticky='ew')

        self.convert_button = ctk.CTkButton(self.root, text='Convert', command=self.convert_currency)
        self.convert_button.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky='ew')

        # --- Result and Chart ---
        self.result_label = ctk.CTkLabel(self.root, text="")
        self.result_label.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        self.fig = Figure(figsize = (5,4), dpi=100)
        self.fig.set_facecolor('#f0f0f0')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#f0f0f0')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

        self.root.mainloop()

    def convert_currency(self):

        """
        Fetches the latest exchange rate from the Frankfurter API
        and updates the result label with the converted amount.
        """

        try:
            from_currency = self.from_var.get()
            to_currency = self.to_var.get()
            amount = float(self.amount_entry.get())

            url = f'https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}'
            response = requests.get(url)
            data = response.json()

            converted_amount = data['rates'][to_currency]
            self.result_label.configure(text=f'{amount: .2f} {from_currency} = {converted_amount:.2f} {to_currency}')

        except ValueError:
            self.result_label.configure(text='Please enter a valid number!')
        except Exception:
            self.result_label.configure(text='Error occured!')
        
        self.plot_historical()

    def plot_historical(self):

        """
        Fetches 90 days of historical rates for the selected "
        currency pair and renders a line chart in the GUI
        """
        
        end_date = date.today()
        start_date = end_date - timedelta(days=90)

        from_currency = self.from_var.get()
        to_currency = self.to_var.get()

        self.ax.clear()

        if from_currency == to_currency:
            self.ax.text(0.5, 0.5, 'Choose two different currencies',
                         ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return

        url = f'https://api.frankfurter.app/{start_date}..{end_date}?from={from_currency}&to={to_currency}'
        response = requests.get(url)
        data = response.json()

        dates = list(data['rates'].keys())
        rates = [data['rates'][d][to_currency] for d in dates]

        parsed = [datetime.strptime(d, '%Y-%m-%d') for d in dates]

        self.ax.set_title(f'{from_currency} -> {to_currency} - Last 90 Days')
        self.ax.plot(parsed, rates, color = "blue")
        self.ax.xaxis.set_major_formatter(DateFormatter('%d/%m/%Y'))
        self.ax.xaxis.set_major_locator(DayLocator(interval=20))
        self.fig.autofmt_xdate(rotation=45)
        self.canvas.draw()

if __name__ == '__main__':
    CurrencyConverter()