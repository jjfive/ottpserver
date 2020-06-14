#!/user/bin/python

#Windows Start
#C:\Users\QuanOther\AppData\Local\Programs\Python\Python38-32\python.exe server\server.py --tickers IBM,LVLT,GOOGL --reload filename.cc --minutes 30 --port 8000

##########################
#written with python 3.8
#Created By: Quan Tieu
############################

import sys, getopt, os
import http.server
import socketserver
import signal
import csv

import threading
import time

import numpy as np
import pandas as pd


import requests
from pprint import pprint

from datetime import datetime

import finnhub


##########################
#written with python 3.8
############################

#global setting
server_port = 8000 #default port 8000
minutes_set = 5

#set of tickers ensures unique tickers
tickers_set = {'APPL'}
#store working data
data = {}

use_historical = False
historical_filename = ''

finhub_key = "bri1i5vrh5r807v5lurg"
alphavantage_key = "D9PQJ57TPRK6WIFR"

s2thread = None

####################################
class Stock:
    #helps identify
    #ticker = ''
    
    #helps pull / retrieval
    #source_dictionary = {}
    #signal_dictionary = {}
    
    #keeps order as the data came in
    #source1_data = []
    #source2_data = []
    
    def __init__(self, name):
        
        #variables for historical 
        self.ticker = name
        self.source1_data = []
        self.source2_data = []
        
        self.source_dictionary = {}
        self.signal_dictionary = {}
        
        #variables for calculations
        self.workingDates = []
        self.workingPrices = []
    
    def getTicker(self):
        return self.ticker
    
    def setSource1Data(self, data):
        self.source1_data = data
    
    def setSourceDict(self, data):
        self.source_dictionary = data
        
    def getSourceDict(self):
        return self.source_dictionary
        
    #date is formatted in the string
    def getSourceDictByDate(self, date):
        return self.source_dictionary[date]
    
    def setSource2Data(self, data):
        self.source2_data.append(data)
    
    def getSource1Data(self):
        return self.source1_data
    
    def getSource2Data(self):
        return self.source2_data
    
    def mergeSource2IntoSource1Data(self):
        try:
            print("mergeSource2IntoSource1Data")
        except: 
            print("Error with mergeSource2IntoSource1Data")
            
    def calSignal(self):
        try:
            print("calSignal")
        except:
            print("Error with calSignal")
    
    def calPandL(self, Pos_t_n1, S_t, S_t_n1):
        try:
            Pos_t = Pos_t_n1 * ((S_t / S_t_n1) - 1)
            
            return Pos_t
        except:
            print("Error with calPandL")
            #return None
          
    def splitData(self):
        try:
            #self.average = []
            
            #reset the working data set
            self.workingDates = []
            self.workingPrices = []
            
            #prep the data for working with from source1
            for d in self.source1_data:
                p = d.split(' ')
                #print(p)
                self.workingDates.append(p[0])
                self.workingPrices.append(float(p[1]))
            
            #data was inserted backwards descending
            self.workingDates.reverse()
            self.workingPrices.reverse()
            
            #prep the data for working with from source2  
            #print(self.source2_data)
            for d in self.source2_data:
                
                p = d.split(' ')
                
                #print(p)
                self.workingDates.append(p[0])
                self.workingPrices.append(float(p[1]))
                
            #print(self.workingPrices)
            #print(self.workingDates)

        except:
            print("Error with splitData")
    
    #figure out how many N should be used in the calculation of moving average
    def getNin24Hrs(self):
        try:
            #assumes 7 hours for regular day
            N = (7 * 60) / minutes_set
            
            return N
            
        except:
            print("Error with getNin24Hrs")
    
    def signalCond(self, row, price, avg, sigmat):
        #print(row)
        current = self.carry
        
        #amount holding
        self.pos = self.pos + current
        
        #carry the value into the next t
        if (row[price] > (row[avg] + row[sigmat]) ):
            self.carry = 1
        elif (row[price] < (row[avg] - row[sigmat]) ):
            self.carry = -1
        else: 
            self.carry = current
        
        return current
    
    def signalCondandPos(self, s):
        #print(row)
        current = self.carry
        
        #amount holding
        self.pos = self.pos + current
        
        
        #carry the value into the next t
        if (s['price'] > (s['S_avg'] + s['Sigma_t']) ):
            self.carry = 1
        elif (s['price'] < (s['S_avg'] - s['Sigma_t']) ):
            self.carry = -1
        else: 
            self.carry = current
        
        s['signal'] = current
        s['position'] = self.pos
        s['pnl'] = self.calPandL(self.pos, float(s['price']), self.lastprice)
        self.lastprice = s['price']
        
        return s
    
    def appStrategy(self, n):
        try:
            #print(n)
            d = {"datetime": self.workingDates, "price": self.workingPrices }
            df = pd.DataFrame(data=d)
            df['S_avg'] = df.iloc[:,1].rolling(window=int(n)).mean()
            df['Sigma_t'] = df.iloc[:,1].rolling(window=int(n)).std()
            
            #apply strategy
            #out: dateime, price, signal, pnl
            self.pos = 0
            self.carry = 0
            #temporary fix to avoid division by 0
            self.lastprice = 1
            
            df = df.apply(self.signalCondandPos , axis=1)
            
            #export to csv file
            df.to_csv(os.path.dirname(__file__) + os.path.sep + self.ticker + '_result.csv', columns=['datetime', 'price', 'signal', 'pnl'])
 
            print(df)
            #print(df.head())
            
            self.df = df
            
            
        except:
            print("Error with calMovingAvg")
            
    def calStrategy(self):
        try:
            #prep data for strategy
            n = self.getNin24Hrs()
            self.splitData()
            self.appStrategy(n)
            
            #print(self.strat_data.head())    
        except:
            print("Error with calStrategy")
    
    def getSignalsByDate(self, date):
        try:
            print(date)
            found = self.df[self.df['datetime'].str.match(date)]
        
            return found['signal'].to_string(index=False, header=False)
        except: 
            print("problem in getSignalsByDate")

    def getSignalsCurrent(self):
        try:
            found = self.df.iloc[-1] 
            print(found['signal'])
            
            return found['signal']
        except: 
            print("problem in getSignalsByDate")
    
    
    

#pull source 1 data 1 ticker at a time.
def pullSource1Data(ticker):
    try:
        url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={}&interval={}min&outputsize=full&apikey={}"
        url = url.format(ticker, minutes_set, alphavantage_key)
        
        print(url)
        try:
            r = requests.get(url)
            ret = r.json()
            
            series = 'Time Series ({}min)'
            series = series.format(minutes_set)
            
            
            clean_series = []
            
            for c in ret[series]:
                inner = ret[series][c]
                
                clean_series.append(c + ' ' + inner['4. close'])
                #print(inner['4. close'])
            
            #print(clean_series)
            
            
            #############################################################
            #print(clean_series)
            #write to csv file and collected the newly formatted data
            cleaner_series = []
            cleaner_dictionary = {}
            
            csv_file = os.path.dirname(__file__) + os.path.sep + ticker + '_price.csv'
            
            #print(csv_file)
            
            with open(csv_file, 'w', newline='') as csvfile:
                fieldnames = ['datetime', 'price']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
        
                for d in clean_series:
                    val = d.split(' ')
                    
                    fdate =  val[0] + '-' + val[1][:-3]
                    cleaner_series.append(fdate + ' ' + val[2])
                    cleaner_dictionary[fdate] = val[2]
                    
                    writer.writerow({'datetime': fdate, 'price': val[2]})
                #print(val)
            
            #print(cleaner_dictionary)
            print("setting data")
            data[ticker].setSource1Data(cleaner_series)
            data[ticker].setSourceDict(cleaner_dictionary)
            print("complete")
            #print(data[ticker].getSource1Data())
            #print(data[ticker].getSourceDict())
            ##############################################################
            return 0

        except:
            return 1

    except: 
        print("problems with pullSource1Data")   
        return 1

#source 2 is a thread and awakes or sleeps 
def pullSource2Data(args):
    try:
        
        configuration = finnhub.Configuration(
            api_key={
                'token': finhub_key
            }
        )

        finnhub_client = finnhub.DefaultApi(finnhub.ApiClient(configuration))
        
        #collect data at regular intervals
        for ticker in tickers_set:
            #print(data[ticker].getTicker())
            ret = finnhub_client.quote(ticker)
            
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d-%H:%M")
            
            new_entry = dt_string + " " + str(ret.c)
            #print(type(ret) )
            #print(new_entry)
            
            data[ticker].setSource2Data(new_entry)
            
            #print(data[ticker].getSource2Data())
            
        #return 0
       
        
        #return 2
    except: 
        print("problems with pullSource2Data")   
        return 1
    

#load historical files from extracts 
def useHistoricalData():
    try:
        for ticker in tickers_set:
            data[ticker] = Stock(ticker)
            filename = os.path.dirname(__file__) + os.path.sep + ticker + "_price.csv"
            
            
            with open(filename, newline='') as csvfile:
                content = csv.reader(csvfile, delimiter=',', quotechar='|')
                #ignore first line
                next(content)
                
                d = []
                dic = {}
                for row in content:
                    d.append(row[0] + " " + row[1])
                    dic[row[0]] =  row[1]
                    #print(', '.join(row))
                #print(d)
                #print(dic)
                
                data[ticker].setSource1Data(d)
                data[ticker].setSourceDict(dic)
                
                #print(data[ticker].getSource1Data())
        use_historical == False    
    except:
        print("problem with useHistoricalData")


#clears data and creates new data objects for storage        
def resetAllData():
    try:
        global data
        
        #clear data
        data = {}
        
        print("Reseting Data: ")
    
        #if filename.cc is used instead, we use it to populate the data
        if(use_historical == False):
            print("Downloading new Data")
            for ticker in tickers_set:
                data[ticker] = Stock(ticker)
                
                #repopulate source 1 data
                ###Temporary disabled to conserve 
                pullSource1Data(data[ticker].getTicker())
                
                print(data[ticker].getTicker())
        else:
            print("Using Historical File")
            useHistoricalData()
            
        
        ###############################################
        #start data source 2 collection
        try:
            print("start source 2 real-time collection")
            s2thread_alive = True
            s2thread = threading.Thread(target=pullSource2Data, args=(1,))
            
            s2thread.start()
            #s2thread.join()
        except:
            print("error starting source 2 data")
        
        
        #do strategy calculations for the tickers    
        try:
            for ticker in tickers_set:
                data[ticker].calStrategy()
            
        except:
            print("error in calculations")
        
        #output csv file    
        
        return 0

    except:
        print("problems with resetAllData") 
        return 1

########################################
#detect requests
########################################
def priceRequest(cmd):
    try:
        
        if(cmd[1] == "now"):
            
            try:
                #assumes no data unless data is found
                ret_val = ""
                
                for ticker in tickers_set:
                    d = data[ticker].getSource2Data()
                    #print(d)
                    
                    if(len(d) > 0):
                        d_list = d[len(d)-1].split(' ')
                        ret_val = ret_val + ticker + " " + d_list[1] + "\n" 
                        
                        #print(d_list)
                return ret_val
            
            except:
                return "Server has no data"
        else: 
            
            
            try: 
                ret_val = ""
                for ticker in tickers_set:
                    d = data[ticker].getSourceDictByDate(cmd[1])
                    
                    #print(d)
                    
                    if(d is not None):
                        ret_val = ret_val + ticker + " " + d + "\n" 
                        #print(d)
                return ret_val
            except:
                return "Server has no data"
        

    except: 
        print("problems with priceRequest")   

#return 0, 1, -1
def signalRequest(cmd):
    try:
        
        
        if(cmd[1] == "now"):
            try:
                
                ret_val = ""
                
                for ticker in tickers_set:
                    #print(ticker)
                    ret_val = ret_val + ticker  + " " + str(data[ticker].getSignalsCurrent()) + "\n" 
                
                return ret_val
            except:
                return "Server has no data"

        else: 
            try:
                ret_val = ""
                
                for ticker in tickers_set:
                    #print(ticker)
                    ret_val = ret_val + ticker  + " " + str(data[ticker].getSignalsByDate(cmd[1])) + "\n" 
                
                return ret_val
            except:
                return "Server has no data"

    except: 
        print("problems with signalRequest")   


#returns 0=sucess, 1=error, 2=ticker not found
def delTickerRequest(cmd):
    try:
        global tickers_set
        
        new_set = {cmd[1]}
        
        if(new_set.issubset(tickers_set)):
            tickers_set = tickers_set.difference(new_set)
            #print(new_set)
            #print(tickers_set)
            return '0'
        
        return '2'

    except: 
        print("problems with delTickerRequest") 
        return '1'  


def addTickerRequest(cmd):
    try:
        global tickers_set
        data[cmd[1]] = Stock(cmd[1])
        
        new_set = {cmd[1]}
        
        if (pullSource1Data(cmd[1]) == 0):
            tickers_set = tickers_set.union(new_set)
            data[cmd[1]].calStrategy()
            #print(new_set)
            print(tickers_set)
            
            return '0'
        
        return '2'

    except: 
        print("problems with addTickerRequest")  
        return '1' 

#redownload all data
def resetRequest(cmd):
    try:
        #if successful return 0
        if (resetAllData() == 0):
            #
            return '0'
    
        #if fails return 1
        return '1'
    
    except: 
        print("problems with resetRequest")  
        return '1' 

####################################
#commands

def tickers(cmd):
    try:
        global tickers_set

        new_tickers = cmd[1].split(',')
        tickers_set.clear()
        tickers_set.update(new_tickers)
        
    except: 
        print("problems with tickers")
        
def port(cmd):
    try:
        global server_port
        
        server_port = int(cmd[1])
        
    except: 
        print("problems with port")


def reload(cmd):
    try:
        global use_historical, historical_filename
        
        use_historical = True
        historical_filename = cmd[1]
        
    except: 
        print("problems with reload")


def minutes(cmd):
    try:
        global minutes_set
        
        converted_mins = int(cmd[1])
        valid_minutes = [5,15,30,60]
        
        if(converted_mins in valid_minutes):
            minutes_set = converted_mins
        else:
            print("not valid minutes, use default")
    except: 
        print("problems with minutes")

####################################

def processClientCmd(cmd):
    try:
        if(cmd[0] == "--tickers"):
            tickers(cmd)
        elif(cmd[0] == "--port"):
            port(cmd)
        elif(cmd[0] == "--reload"):
            reload(cmd)
        elif(cmd[0] == "--minutes"):
            minutes(cmd)
        else:
            print("Command Not Found")
    except:
        print("problem with processClientCmd")

#file IO
def write_file(data, filename):
    try:
        print("start file export")
        
        
    except: 
        print("write file error")


class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        
        self.data = self.request.recv(1024).strip()
        cmd = str(self.data.decode('utf-8')).split(' ')
        
        #return message to the user
        ret_value = ""
        
        print(cmd)
        
        #accepting commands
        if(cmd[0] == "--price"):
            ret_value = priceRequest(cmd)
        elif(cmd[0] == "--signal"):
            ret_value = signalRequest(cmd)
        elif(cmd[0] == "--add_ticker"):
            ret_value = addTickerRequest(cmd)
        elif(cmd[0] == "--del_ticker"):
            ret_value = delTickerRequest(cmd)
        elif(cmd[0] == "--reset"):
            ret_value = resetRequest(cmd)
        else: 
            ret_value = "Server: Command Not Recognized"
        
        print(ret_value)
        self.request.sendall(bytes(ret_value, "utf-8"))

        
        
#start server
def start_server(sargs):
    try:
        print("fetch data")

        try:
            Handler = TCPHandler 
            #http.server.SimpleHTTPRequestHandler
            
            input_txt = ""
                
            print("starting server.. use Ctrl C to stop the server")
            with socketserver.TCPServer(("", server_port), Handler) as httpd:
                print("serving at port", server_port)
                httpd.serve_forever()
        except KeyboardInterrupt:
            print("^C received, shutting down the web server, return 0")
            httpd.server_close()  
            return 0
        except:
            httpd.server_close()
            print("server shutdown")
            return 1
            
        
    except:
        print("server failed to launch")
        return -1
        


#finhub API Key: bri1i5vrh5r807v5lurg
def processCmdInputs(args):
    try:
        
        i = 0
        
        if(len(args) % 2 == 0):
            #even parameters
            while i < len(args):
                cmd = [args[i], args[i+1]]
                #print(cmd)
                processClientCmd(cmd)
                i = i + 2
           
            return True
        else:
            #uneven parameters, probably bad input
            return False

    except:
        print("problems with processCmdInputs")




if __name__== "__main__":
    
    #assumes the app is run in the same directory as settings file
    config_file = os.path.dirname(__file__) + os.path.sep + "settings.txt"
    
    #register Signal Handler
    #signal.signal(signal.SIGINT, signal_handler)
  
    #process all input parameters
    no_errors = True
    if(len(sys.argv) > 1):
        no_errors = processCmdInputs(sys.argv[1:])
    
    if (no_errors):
        ####check right parameters and path
        print("***Checking Inputs*******")
        print(config_file)
        print(server_port)
        print(minutes_set)
        print(tickers_set)
        print(use_historical)
        print(historical_filename)
        print("***Done*******")
        #####
        
        resetAllData()
          
        #signalAllByTime("2016-07-29-13:34")
        #server options if needed
        s_args = ()
        
        print(start_server(s_args))
    else:
        print("server configuration incorrect, cannot start server")