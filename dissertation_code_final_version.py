import pydot
import json
import requests
import os
import functools
import graphviz as gv
import time
from graphviz import Source


#this initial code was taken from Kevin Perlow. Original available at https://github.com/kevinperlow/SANS-DFIR-2017/blob/master/bitcoinmapping.py
z = 0
i = 0
website = "https://blockchain.info/rawaddr/"
bitcoinaddress = input("Please type in the address of interest: ")
initialrequest = website + bitcoinaddress

firstjson = (requests.get(initialrequest)).json()


addresslist = []
usedaddresslist = []
senderlist = []
receiverlist = []
graphvizlines = []

addresslist.append(bitcoinaddress)
usedaddresslist.append(bitcoinaddress)



while i < 2:
	if z is 1:
		initialrequest = website + addresslist[i]
		firstjson = (requests.get(initialrequest)).json()
    

	for transaction in firstjson['txs']:
		payerlist = []
		recipientlist = []


		for item in transaction["inputs"]:
			payerlist.append(item["prev_out"]["addr"])
			if item["prev_out"]["addr"] not in addresslist:
				addresslist.append(item["prev_out"]["addr"])

		for target in transaction["out"]:
			recipientlist.append(target["addr"])
			if target["addr"] not in addresslist:
				addresslist.append(target["addr"])



		for payer in payerlist:
			for recipient in recipientlist:
					a = '"' + payer + '"' + " -> " + '"' + recipient + '"' + ";"
					if a not in graphvizlines:
						graphvizlines.append(a)




	i = i + 1    
	z = 1
        

#initial code that wasn't written by me ends here
#creating the graph with graphviz
save_path_graph = "informationfetched/graphcreate.txt"
graph_generate = open(save_path_graph,'w')

graph_generate.write('digraph {\nrankdir=LR;\n')

for each in graphvizlines:
	graph_generate.write(str(each) + '\n')

graph_generate.write('}\n')

graph_generate.close()



thefile = open(save_path_graph,'r')
data = ""
for line in thefile:
	data+= line

thefile.close()


s = Source(data, filename="informationfetched/transactionsvisualised", format="png")
s.view()





# Writing information about the specified address to a text file for inspection
save_path_infoaboutaddress = 'informationfetched/infoaboutaddress.txt'
information = open(save_path_infoaboutaddress,'w') 



#a second request to gather miscellaneous information about every address involved from blockchain.info's API
for address in addresslist:
	blockchain_com_site = website + address
	blockchain_com_request = (requests.get(blockchain_com_site)).json()

	bitcoinwhoswho = "http://bitcoinwhoswho.com/api/url/45ce482b-b686acba-ac3b2bf7-a00e836a?address="
	bitcoinwhoswho_site = bitcoinwhoswho + address
	bitcoinwhoswho_com_request = (requests.get(bitcoinwhoswho_site)).json()

	json_address = blockchain_com_request['address']
	information.write('Address of interest: ' + str(json_address) + '\n')

	json_n_tx = blockchain_com_request['n_tx']
	information.write('Number of transactions: ' + str(json_n_tx) + '\n')

	json_total_received = blockchain_com_request['total_received']
	information.write('Total amount of Bitcoin received: ' + str(format(float((json_total_received)/100000000.0))) + '\n')

	json_total_sent = blockchain_com_request['total_sent']
	information.write('Total amount of Bitcoin spent: ' + str(format(float((json_total_sent)/100000000.0))) + '\n')

	json_final_balance = blockchain_com_request['final_balance']
	information.write('Current balance of Bitcoin: ' + str(format(float((json_final_balance)/100000000.0))) + '\n')

	information.write('\n')
	
	information.write('Transaction history of the specified address: \n')

	for transaction in blockchain_com_request['txs']:
		json_transaction = transaction['hash']
		json_date = transaction['time']
		json_date_new = time.ctime(json_date)
		json_total_transaction = transaction['result']
		information.write(str(json_transaction) + ' made on ' + str(json_date_new) + ' for a total of ' + str(format(float((json_total_transaction)/100000000.0))) + ' BTC'+ '\n')

	information.write('\n')


#looking for matches in bitcoinwhoswho API for mentions
	for match in bitcoinwhoswho_com_request["urls"]:
		information.write("Success! A mention of " + str(address) + " has been found here: " + "\n")
		information.write("Link: " + str(match["url"]) + '\n')
		information.write("Title of the webpage: " + str(match["page_title"]) + '\n')
		information.write("Meta description of the page: " + str(match["meta_description"]) + '\n')
		information.write('\n')
		information.write('\n')

	information.write('------------------------------------------------------------------------------------------------------------------')
	information.write('\n')
	information.write('\n')

information.close()


#Done
print('Done! The data that was collected can be found in the folder "informationfetched". It contains a graph of all transactions and a text file that contains information about all addresses involved.')

