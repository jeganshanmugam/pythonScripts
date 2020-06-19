import requests
import csv
from multiprocessing import Lock, Process, Queue, current_process, Manager
from fpdf import FPDF


def run_stock_analysis():
    url_data = load_stocks_urls()
    stock_name_list = list(url_data.keys())
    perform_data_collection(stock_name_list,  url_data)


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
        p = Process(target=get_stock_data, args=(stock_name, url_data.get(stock_name), return_dict))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
    generate_pdf(return_dict.values())
    print("Data collection completed")


def generate_pdf(stock_data_list):
    pdf = FPDF('L', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 8)
    epw = pdf.w - 2 * pdf.l_margin
    col_width = epw / 4
    th = pdf.font_size
    header_data = ["Stock Name", "Previous Close", "P/E", "P/B", "EPS", "Book Value", "52 High", "52 Low",
                   "5 Day Avg", "30 Day Avg", "50 Day Avg", "200 Day Avg"]

    for header in header_data:
        if header == 'Stock Name':
            pdf.cell(60, 2 * th, str(header), border=1, align='C')
        else:
            pdf.cell(20, 2 * th, str(header), border=1, align='C')

    for row in stock_data_list:
        previous_price = float(row["priceprevclose"])
        book_value = row["BV"]

        pdf.ln(2 * th)
        pdf.cell(60, 2 * th, str(row["SC_FULLNM"]), border=1, align='C')
        pdf.cell(20, 2 * th, str(row["priceprevclose"]), border=1, align='C')
        pdf.cell(20, 2 * th, str(row["PE"]), border=1, align='C')
        if book_value is None:
            pdf.cell(20, 2 * th, str(""), border=1, align='C')
        else:
            pdf.cell(20, 2 * th, str(round(previous_price / float(book_value),2)), border=1, align='C')

        pdf.cell(20, 2 * th, str(row["SC_TTM"]), border=1, align='C')
        pdf.cell(20, 2 * th, str(row["BV"]), border=1, align='C')
        pdf.cell(20, 2 * th, str(row["52H"]), border=1, align='C')
        pdf.cell(20, 2 * th, str(row["52L"]), border=1, align='C')
        pdf.cell(20, 2 * th, str(row["5DayAvg"]), border=1, align='C')
        pdf.cell(20, 2 * th, str(row["30DayAvg"]), border=1, align='C')
        pdf.cell(20, 2 * th, str(row["50DayAvg"]), border=1, align='C')
        pdf.cell(20, 2 * th, str(row["200DayAvg"]), border=1, align='C')

    pdf.output('Stock_Analysis.pdf', 'F')


def get_stock_data(name, url, return_dict):
    r = requests.get(url)
    data = r.json()
    return_dict[name] = data["data"]
    return data["data"]


if __name__ == "__main__":
    run_stock_analysis()
