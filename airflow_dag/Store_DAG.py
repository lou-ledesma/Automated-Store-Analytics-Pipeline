from airflow import DAG
from airflow.operators import BashOperator
from airflow.operators import PythonOperator
from airflow.operators import MySqlOperator
from airflow.operators import EmailOperator
from datetime import datetime, timedelta
from datacleaner import data_cleaner # Custom library created

# General flow of DAG script [Set default params/args] >> [Instanciate DAG] >> [Create Tasks] >> [Define Dependancies amongst tasks]

yesterday_date = datetime.strftime(datetime.now() - timedelta(1), "%Y-%m-%d")

# Setting default parameters/arguments
default_args = {
	'owner': 'Airflow',
	'start_date': datetime(2024, 9, 18),
	'retries': 1,
	'retry_delay': timedelta(seconds=5)
}

# Instanciating DAG
with DAG('store_dag', default_args = default_args, schedule_interval = '@daily', template_searchpath=['/usr/local/airflow/sql_files'], catchup = False) as dag:

	#Creating Tasks
	# [Check if source file exists] >> [Apply transformations to data] >> [Push data to mysql] >> [Input queries to extract data from MySQL] >> [Email outputs]

	# Task 1 Check if source file exists
	# '~' sign represents the airflow home path
	bash_comm = 'shasum ~/store_files_airflow/raw_store_transactions.csv'
	t1 = BashOperator(
		task_id = 'check_file_exists', 
		bash_command = bash_comm, 
		retries= 2, 
		retry_delay = timedelta(seconds=15))

	# Load and clean the data (apply transformations to data)
	t2 = PythonOperator(
		task_id = 'clean_raw_csv',
		python_callable = data_cleaner) # Custom created library that contains the function needed to clean data

	# Push data to MySQL
	# In MySQL table must already exist before pushing data into it
	# Task 3 we will run a DDL SQL command "CREATE TABLE" in order to have an empty table to push in the csv data cleaned in task 2
	t3 = MySqlOperator(
		task_id = 'create_mysql_table',
		mysql_conn_id = 'mysql_conn',
		sql = 'create_table.sql')

	# Inserting data into table in mysql
	t4 = MySqlOperator(
		task_id = 'insert_into_table',
		mysql_conn_id = 'mysql_conn',
		sql = 'insert_into_table.sql')

	#Bonus - change date to yesterdays date
	bonus_task = MySqlOperator(
		task_id = 'adjust_date',
		mysql_conn_id = 'mysql_conn',
		sql = 'adjust_date.sql')

	# Extracting data from table in mysql
	t5 = MySqlOperator(
		task_id = 'select_from_table',
		mysql_conn_id = 'mysql_conn',
		sql = 'select_from_table.sql')

	# Rename files containing extracted data from task 5 (t5)
	t6 = BashOperator(
		task_id = 'move_file_1',
		bash_command = 'cat ~/store_files_airflow/location_wise_profit.csv && mv ~/store_files_airflow/location_wise_profit.csv ~/store_files_airflow/location_wise_profit_%s.csv' % yesterday_date)

	t7 = BashOperator(
		task_id = 'move_file_2',
		bash_command = 'cat ~/store_files_airflow/store_wise_profit.csv && mv ~/store_files_airflow/store_wise_profit.csv ~/store_files_airflow/store_wise_profit_%s.csv' % yesterday_date)

	# Sending the data files in report format via email
	t8 = EmailOperator(
		task_id = 'send_email',
		to = 'mfermin58@gmail.com',
		cc = 'loubriel.ledesma@gmail.com',
		subject = 'Daily Report Generated',
		html_content= """<h1> Congrats!! Your automated daily report is ready. Please see attached. Thanks! -Automated by Lou Ledesma using Apache Airflow.</h1>""",
		files =['/usr/local/airflow/store_files_airflow/location_wise_profit_%s.csv' % yesterday_date, '/usr/local/airflow/store_files_airflow/store_wise_profit_%s.csv' % yesterday_date])

	# Automating the ingestion of future emails sent for the raw store transactions.
	t9 = BashOperator(
		task_id='rename_raw',
		bash_command= 'mv ~/store_files_airflow/raw_store_transactions.csv ~/store_files_airflow/raw_store_transactions_%s.csv' % yesterday_date)

	# List dependencies
	t1 >> t2 >> t3 >> t4 >> bonus_task >> t5 >> [t6, t7] >> t8 >> t9
