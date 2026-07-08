"""
Currency Converter Application
A GUI-based currency converter with historical rate visualization
using the Frankfurter API.
"""

import customtkinter as ctk 
import requests 

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from datetime import date, timedelta

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")

common_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'NZD']  

class CurrencyConverter:

    """
    A GUI currency converter built with customtkinter.
    Handles user input, API calls, and historical chart rendering.
    """

    def __init__(self):
        # --- Window Setup ---
        self.root = ctk.CTk()
        self.root.title('Currency Converter')
        self.root.geometry('400x600')
        self.root.grid_columnconfigure(0, weight = 1)
        self.root.grid_columnconfigure(1, weight = 1)

        # --- Currency Selector
        self.from_var = ctk.StringVar(self.root)
        self.from_var.set('USD')
        self.from_menu = ctk.CTkOptionMenu(self.root, variable = self.from_var, values = common_currencies)
        self.from_menu.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.to_var = ctk.StringVar(self.root)
        self.to_var.set('EUR')
        self.to_menu = ctk.CTkOptionMenu(self.root, variable = self.to_var, values = common_currencies)
        self.to_menu.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # --- Amount Input ---
        self.amount_label = ctk.CTkLabel(self.root, text='Amount: ')
        self.amount_label.grid(row=2, column=0, padx=10, pady=5, sticky='ew')

        self.amount_entry = ctk.CTkEntry(self.root)
        self.amount_entry.grid(row=2, column=1, padx=10, pady=5, sticky='ew')

        self.convert_button = ctk.CTkButton(self.root, text='Convert', command=self.convert_currency)
        self.convert_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky='ew')

        # --- Result and Chart ---
        self.result_label = ctk.CTkLabel(self.root, text="")
        self.result_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        self.fig = Figure(figsize = (5,3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky='ew')

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

        url = f'https://api.frankfurter.app/{start_date}..{end_date}?from={from_currency}&to={to_currency}'
        response = requests.get(url)
        data = response.json()

        dates = list(data['rates'].keys())
        rates = [data['rates'][d]['EUR'] for d in dates]

        self.ax.clear()
        self.ax.plot(dates, rates)
        self.canvas.draw()

if __name__ == '__main__':
    CurrencyConverter()