import pandas as pd
from matplotlib import pyplot as plt
import csv

#Intake data
all_data = pd.read_csv('customer_data.csv')

#Potential validations (add later) - bad data could throw off decisions
'''
-Outlying prices/dates
    -what do $0 orders mean? (leave in for now)
-Refund exceeds price
-Duplicate orders (checked, none)
-Customer order count validation (checked, issue exp: cust id: 5271629267013 has two orders both labelled '2' -> it's total order count rather than "orders by the time the order was created")
-Customer total spent validation -> total of order prices less refunds (checked, issue exp: cust_id 5272038473797 has same $ value twice -> it's total order revenue rather than "revenue by the time the order was created")

Note: some checks might be fine for this data, but not in future datasets from other companies
'''

#Get data frame for each company
companies = all_data['company_id'].unique()

df_array = []
for company in companies:
    df_array.append(all_data[all_data['company_id']==company])

#Do calculations and add new relevant columns
df_array_temp = df_array #temp copy of company array for iteration
for index, company_data in enumerate(df_array_temp):
    with pd.option_context('mode.chained_assignment', None): #hide warning

    #Reformat date/get month
        df_array[index]['new_date'] = pd.to_datetime(company_data['created_at'])
        df_array[index]['month'] = + pd.to_datetime(company_data['created_at']).dt.year.astype(str) + ' ' + pd.to_datetime(company_data['created_at']).dt.month.astype(str)

    #Get cumulative customer order count (correct column that has issues when vetted - exp: cust id: 5271629267013 has two orders both labelled '2')
        df_array[index]['cust_company'] = company_data['customer_id'].astype(str) + company_data['company_id'] #get combination key for grouping, in case cut_id is duplicated across diff. companies
        #Customer order sequential count starting at 0
        df_array[index]['order_count'] =  company_data.sort_values(by=['company_id', 'customer_id', 'new_date'], ascending = True).groupby('cust_company').cumcount()

    #Get customer spend before the order
        df_array[index]['past_customer_revenue'] = company_data.sort_values(by=['company_id', 'customer_id', 'new_date'], ascending = True).groupby('cust_company')['total_price'].cumsum() - company_data['total_price']

    #Get customer spend after the order
        df_array[index]['future_customer_revenue'] =  company_data.sort_values(by=['company_id', 'customer_id', 'new_date'], ascending = False).groupby('cust_company')['total_price'].cumsum() - company_data['total_price']

    #Get order frequency before the order
    #Get order frequency after the order
        #(Add later if time)
        
        df_array[0].to_csv("test.csv")
    
    #VIEWS
        the_months = []
        for month in df_array[index]['month'].unique():
            the_months.append(month)
        the_months.sort()

        fig, axes = plt.subplots(2, 3)
        fig.tight_layout(pad=4)


        #1 - Monthly revenue and orders
        plt.subplot(2, 3, 1)
            
        plt.title("Monthly Revenue")
        plt.xlabel("Month")
        plt.ylabel("Revenue")
        plt.xticks([])

        plt.bar(the_months, df_array[index].sort_values(by=['month'], ascending = True).groupby('month')['total_price'].sum() - df_array[index].sort_values(by=['month'], ascending = True).groupby('month')['order_refunds'].sum(), color='green')

        plt.subplot(2, 3, 4)

        plt.title("Monthly Orders")
        plt.xlabel("Month")
        plt.ylabel("Orders")
        plt.xticks([])

        plt.plot(the_months, df_array[index].sort_values(by=['month'], ascending = True).groupby('month')['order_id'].count(), color='blue')

        #2 - Monthly refund $ and refund rate
        plt.subplot(2, 3, 2)
        
        plt.title("Monthly Refund $")
        plt.xlabel("Month")
        plt.ylabel("Refund $")
        plt.xticks([])

        plt.bar(the_months, df_array[index].sort_values(by=['month'], ascending = True).groupby('month')['order_refunds'].sum(), color='red')

        plt.subplot(2, 3, 5)

        plt.title("Monthly Refund Rate")
        plt.xlabel("Month")
        plt.ylabel("Refund Rate")
        plt.xticks([])

        refunded_orders = df_array[index][df_array[index]['order_refunds'] > 0]
        plt.plot(the_months, refunded_orders.sort_values(by=['month'], ascending = True).groupby('month')['order_id'].count() / df_array[index].sort_values(by=['month'], ascending = True).groupby('month')['order_id'].count(), color='blue')

        #3 - Customer count and new customer rate
        plt.subplot(2, 3, 3)
            
        plt.title("Monthly Customers")
        plt.xlabel("Month")
        plt.ylabel("Customers")
        plt.xticks([])
        
        plt.bar(the_months, df_array[index].sort_values(by=['month'], ascending = True).groupby('month')['customer_id'].count(), color='green')

        plt.subplot(2, 3, 6)

        plt.title("New Customer Rate")
        plt.xlabel("Month")
        plt.ylabel("New Customer Rate")
        plt.xticks([])

        new_customers = df_array[index][df_array[index]['order_count'] == 0]
        plt.plot(the_months, new_customers.sort_values(by=['month'], ascending = True).groupby('month')['customer_id'].count() / df_array[index].sort_values(by=['month'], ascending = True).groupby('month')['customer_id'].count(), color='blue')

        #4 - Payment pending rate
        #plt.subplot(3, 3, 7)
        
        #plt.title("Payment Pending Rate")
        #plt.xlabel("Month")
        #plt.ylabel("Payment Pending Rate")
        #plt.xticks([])

        #payment_pending_orders = df_array[index][df_array[index]['status'] == 'pending']
        #plt.plot(the_months, new_customers.sort_values(by=['month'], ascending = True).groupby('month')['order_id'].count() / df_array[index].sort_values(by=['month'], ascending = True).groupby('month')['order_id'].count(), color='blue')


        #Title
        plt.suptitle(str(df_array[index]['company_id'].unique()[0]))
        
        #Get name of output file for company
        file_name = str(df_array[index]['company_id'].unique()[0]) + '.png'

        #Output charts to .png file
        plt.savefig(file_name)

        plt.clf() #clear plot to start fresh for next company in loop
