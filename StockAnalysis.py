import requests
import csv
from multiprocessing import Lock, Process, Queue, current_process, Manager
from fpdf import FPDF


def run_stock_analysis():
    url_data = load_stocks_urls()
    print("url_data : ", url_data)
    print("key data : ", url_data.keys())
    stock_name_list = list(url_data.keys())
    perform_data_collection(stock_name_list,  url_data)
    ##get_stock_data("ITC", "https://priceapi.moneycontrol.com/pricefeed/nse/equitycash/ITC")


def load_stocks_urls():
    url_data = {}
    stock_name_list  = []
    with open('Data.csv') as csvfile:
        read_csv = csv.reader(csvfile, delimiter=',')
        for row in read_csv:
            url_data[row[0]] = row[1]
    return url_data


def perform_data_collection(stock_name_list, url_data):
    print("perform_data_collection")
    manager = Manager()
    return_dict = manager.dict()
    processes = []
    for stock_name in stock_name_list:
        print("URL data details",   stock_name, url_data.get(stock_name))
        p = Process(target=get_stock_data, args=(stock_name, url_data.get(stock_name), return_dict))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
    print("Return dictionary values: ", return_dict.values())
    generate_pdf(return_dict.values())


def generate_pdf(stock_data_list):
    pdf = FPDF('L', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 8)
    epw = pdf.w - 2 * pdf.l_margin
    col_width = epw / 4
    th = pdf.font_size
    header_data = ["Stock Name", "Previous Close", "P/E", "EPS", "Book Value", "52 High", "52 Low",
                   "5 Day Avg", "30 Day Avg", "50 Day Avg", "200 Day Avg"]

    for header in header_data:
        if header == 'Stock Name':
            pdf.cell(40, 2 * th, str(header), border=1)
        else:
            pdf.cell(20, 2 * th, str(header), border=1)

    for row in stock_data_list:
        pdf.ln(2 * th)
        pdf.cell(40, 2 * th, str(row["SC_FULLNM"]), border=1)
        pdf.cell(20, 2 * th, str(row["priceprevclose"]), border=1)
        pdf.cell(20, 2 * th, str(row["PE"]), border=1)
        pdf.cell(20, 2 * th, str(row["PE"]), border=1)
        pdf.cell(20, 2 * th, str(row["SC_TTM"]), border=1)
        pdf.cell(20, 2 * th, str(row["BV"]), border=1)
        pdf.cell(20, 2 * th, str(row["52H"]), border=1)
        pdf.cell(20, 2 * th, str(row["52L"]), border=1)
        pdf.cell(20, 2 * th, str(row["5DayAvg"]), border=1)
        pdf.cell(20, 2 * th, str(row["30DayAvg"]), border=1)
        pdf.cell(20, 2 * th, str(row["50DayAvg"]), border=1)
        pdf.cell(20, 2 * th, str(row["200DayAvg"]), border=1)
    pdf.output('Stock_Analysis.pdf', 'F')


def get_stock_data(name, url, return_dict):
    r = requests.get(url)
    data = r.json()
    print(data["data"])
    return_dict[name] = data["data"]
    return data["data"]


if __name__ == "__main__":
    run_stock_analysis()
