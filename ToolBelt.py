import requests as r
import pyodbc
from time import sleep
import urllib
import argparse as a
from xml.dom.minidom import parse, parseString
from gooey import Gooey
from bs4 import BeautifulSoup


@Gooey(program_name="Recovery Team Toolbelt",
       default_size=(710, 700),
       navigation='TABBED',
       header_bg_color='#F5610D',
       body_bg_color='#FFF900')
def main():
    parser = a.ArgumentParser(description='Recovery Team Toolbelt By JamesP.')
    parser.add_argument('-a', '--Add', help='Add New Card to Realex', required=False, nargs='+')
    parser.add_argument('-e', '--Edit', help='Edit Existing Card', required=False, nargs='+')
    parser.add_argument('-d', '--Delete', help='Delete Existing Card (Cannot be Undone!)', required=False, nargs='+')
    parser.add_argument('-ex', '--Exception', help='Add Policy number from app (including year) to exception list for tags', required=False, nargs='+')
    parser.add_argument('-ac', '--add Claim', help='Add Single Claim', required=False, nargs='+')
    parser.add_argument('-ec', '--Edit Claim', help='Update Existing Claim', required=False, nargs='+')
    parser.add_argument('-dc', '--Delete Claim', help='Remove Existing Claim', required=False, nargs='+')

    args = vars(parser.parse_args())

    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=MyServerName;'
                          'Database=MyDatabase;'
                          "Trusted_Connection=No"
                          )
    conn.autocommit = True
    cursor = conn.cursor()

    if args['Add']:
        sql = 'exec [Payments].[AddCust] ?'
        values = (args['Add'])
        cursor.execute(sql, values)
        row = cursor.fetchone()
        xml = str(row[0])
        dom = parseString(xml)
        xml_str = dom.toprettyxml(indent="  ")
        uri = "https://api.realexpayments.com/epage-remote.cgi"
        response = r.post(uri, data=xml_str)
        # print(response.content)
        x = response.content
        y = BeautifulSoup(x, "html.parser")
        msg = (str(y))
        emsg = parseString(msg)
        xml_msg = emsg.toprettyxml(indent="  ")
        orderid = y.orderid.text
        cmessage = y.message.text
        sleep(2)
        custresponse = 'exec Payments.CustResponse @orderid=?, @result=?, @msg=?'
        params = (orderid, cmessage, xml_msg)
        cursor.execute(custresponse, params)
        print(y)
        addcard = 'exec [Payments].[AddCard] ?'
        cursor.execute(addcard, values)
        row = cursor.fetchone()
        xml = str(row[0])
        dom = parseString(xml)
        xml_str = dom.toprettyxml(indent="  ")
        uri = "https://api.realexpayments.com/epage-remote.cgi"
        cardresponse = r.post(uri, data=xml_str)
        # print(cardresponse.content)
        x = cardresponse.content
        y = BeautifulSoup(x, "html.parser")
        msg = (str(y))
        emsg = parseString(msg)
        xml_msg = emsg.toprettyxml(indent="  ")
        orderid = y.orderid.text
        cmessage = y.message.text
        sleep(2)
        custresponse = 'exec Payments.CustResponse @orderid=?, @result=?, @msg=?'
        params = (orderid, cmessage, xml_msg)
        cursor.execute(custresponse, params)
        print(y)
        if str(cmessage) == "Successful":
            print("Claim number: " + str(values) + " was added sucessfully!")
        else:
            print("Danger Will Robinson!! Contact James to investigate")
    if args['Edit']:
        sql = 'exec [Payments].[editcard] ?'
        values = (args['Edit'])
        cursor.execute(sql, values)
        row = cursor.fetchone()
        xml = str(row[0])
        dom = parseString(xml)
        xml_str = dom.toprettyxml(indent="  ")
        uri = "https://api.realexpayments.com/epage-remote.cgi"
        response = r.post(uri, data=xml_str)
        x = response.content
        y = BeautifulSoup(x, "html.parser")
        msg = (str(y))
        emsg = parseString(msg)
        xml_msg = emsg.toprettyxml(indent="  ")
        orderid = y.orderid.text
        cmessage = y.message.text
        sleep(2)
        custresponse = 'exec Payments.CustResponse @orderid=?, @result=?, @msg=?'
        params = (orderid, cmessage, xml_msg)
        cursor.execute(custresponse, params)
        print(y)
        if str(cmessage) == "Successful":
            print("Claim number: " + str(values) + " was edited sucessfully!")
        else:
            print("Danger Will Robinson!! Contact James to investigate")
    if args['Delete']:
        sql = 'exec [Payments].[deletecard] ?'
        values = (args['Delete'])
        cursor.execute(sql, values)
        row = cursor.fetchone()
        xml = str(row[0])
        dom = parseString(xml)
        xml_str = dom.toprettyxml(indent="  ")
        uri = "https://api.realexpayments.com/epage-remote.cgi"
        response = r.post(uri, data=xml_str)
        x = response.content
        y = BeautifulSoup(x, "html.parser")
        msg = (str(y))
        emsg = parseString(msg)
        xml_msg = emsg.toprettyxml(indent="  ")
        orderid = y.orderid.text
        cmessage = y.message.text
        sleep(2)
        custresponse = 'exec Payments.CustResponse @orderid=?, @result=?, @msg=?'
        params = (orderid, cmessage, xml_msg)
        cursor.execute(custresponse, params)
        if str(cmessage) == "Successful":
            print("Claim number: " + str(values) + " was deleted sucessfully!")
        else:
            print("Danger Will Robinson!! Contact James to investigate")
        print(y)
    if args['Exception']:
        sql = 'exec [dbo].[TagsException]  ?'
        fudge = str(args['Exception'])
        values = fudge
        cursor.execute(sql, values)
        cursor.commit()
        print("Policy number: " + str(values) + " was added to Exclusion List for Tags!")
    if args['add Claim']:
        sql = 'exec [debt].[PopulateNewSingleDebt] ?'
        values = (args['add Claim'])
        cursor.execute(sql, values)
        print("Claim added successfully")


    if args['Edit Claim']:
        sql = 'exec [debt].[UpdateSingleExistingDebt] ?'
        values = (args['Edit Claim'])
        cursor.execute(sql, values)
        print("Claim updated successfully")


    if args['Delete Claim']:
        sql = 'exec Debt.RemoveDebtClaim ?'
        values = (args['Delete Claim'])
        cursor.execute(sql, values)
        print("Claim Removed Successfully")




main()
# print(row[0])

# print(xml_str)
