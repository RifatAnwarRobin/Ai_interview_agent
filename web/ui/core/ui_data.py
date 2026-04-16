import streamlit as st
import requests
import psycopg2
import uuid

import os
from dotenv import load_dotenv
load_dotenv()
WEBHOOK_URL =os.getenv("WEBHOOK_URL") 
MINSTRAL_KEY=os.getenv("MISTRAL_KEY") 

def welcome():
	st.header("AI Interview System")
	st.write("Welcome to the new generation Interview preparation platform.\nAI will assist you to teach and evaluate,\nnot distroy your creativity\ninsead it will increase curiosity.")

def user_input_form():
	input_type=st.selectbox("What For?", ["Job Interview", "Understanding check"], index=0)
	jd_text = ""

	if input_type=="Job Interview":
		jd_text = st.text_area("Paste Job Description")
	else:
		jd_text= st.text_input("Enter A Topic","Python")

	difficulty = st.selectbox("Select Difficulty", ["easy", "medium", "hard"], index=1)
	valid_input = (jd_text.strip() != "") and difficulty
	
	if st.button("Generate Questions") and valid_input:
		# row_id=user_raw_input_data_to_psql(input_type, jd_text, difficulty)
		
		user_inp={
				"input_type":input_type,
				"difficulty": difficulty,
				# "row_id":row_id,
				"jd_text":jd_text.strip()
			}

		try:
			response=requests.post(WEBHOOK_URL, json=user_inp)
			if response.status_code == 200:
			    st.success("✅ Successfully posted to n8n!")

			    # Display what n8n sent back
			    st.json(response.json() if response.text else {"status": "Success"})
			else:
			    st.error(f"❌ Error: Received status code {response.status_code}")
		except Exception as e:
			st.error(f"⚠️ Connection failed: {e}")
			st.info("Check if n8n is running and the Webhook node is 'Listening'.")


# def db_connection():
# 	# DB connection
# 	conn = psycopg2.connect(
# 	    host=os.getenv("DB_HOST"),
# 	    database=os.getenv("DB_NAME"),
# 	    user=os.getenv("DB_USER"),
# 	    password=os.getenv("DB_PASS"),
# 	    port=os.getenv("DB_PORT")
# 	)
# 	st.write({
#         "DB_HOST": host,
#         "DB_NAME": db,
#         "DB_USER": user,
#         "DB_PASS_exists": bool(password),
#         "DB_PORT": port,
#     })

# 	print(f"DB Connection status: {conn}")
# 	return conn

# def user_raw_input_data_to_psql(input_type, jd_text, difficulty):
# 	user_id = str(uuid.uuid4())  # session_id for now
# 	conn=db_connection()
# 	processing_status="Pending"
# 	if conn is None:
# 		st.error(f"DB Connection failed, please check Docker/DB status.")

# 	try:
# 		cur = conn.cursor()
# 		sql_query="""
# 		INSERT INTO raw_user_inputs (user_id, input_type, jd_text, difficulty)
# 		VALUES (%s, %s, %s, %s)
# 		RETURNING id;
# 		"""
# 		sql_params=(user_id, input_type, jd_text, difficulty)
# 		cur.execute(sql_query,sql_params)
# 		row_id = cur.fetchone()[0]
# 		conn.commit()
		
# 		cur.close()
# 		conn.close()

# 		st.success(f"Saved! Row ID: {row_id}")
# 		st.session_state["last_id"] = row_id
# 	except Exception as e:
# 		st.error(f"Database Connection error: {e}")

# 	return row_id

def main():
	welcome()
	user_input_form()

if __name__ == '__main__':
	main()