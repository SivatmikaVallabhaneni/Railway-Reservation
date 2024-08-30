#Railway Reservation System using sqlite and streamlit Python

#import packages
import streamlit as st
import sqlite3
import pandas as pd
conn =sqlite3.connect('railway.db')
current_page = 'Login or Sign Up'
c= conn.cursor()

#import database
def create_db():
    c.execute("CREATE TABLE IF NOT EXISTS users ( username TEXT, password TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS employees (employee_id TEXT, password TEXT , designation TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS trains(train_number TEXT, train_name TEXT, departure_date, start_destination TEXT, end_destination TEXT)")

    create_db()


#Search train
def search_train(train_number):
    train_query = c.execute("SELECT * FROM trains WHERE train_number=?", (train_number,))
    train_data = train_query.fetchone()
    return train_data


#train destination search:
def train_destination(start_destination, end_destination):
    train_query = c.execute("SELECT * FROM trains WHERE start_destination=?, end_destination=?", (start_destination, end_destination))
    train_data = train_query.fetchone()
    return train_data


#add train for our project
def add_train(train_number, train_name, departure_date, start_destination, end_destination):
    c.execute("INSERT INTO trains (train_number, train_name, departure_date, start_destination, end_destination) values( ? , ? , ? , ? , ?);", (train_number, train_name, departure_date, start_destination, end_destination))
    conn.commit()
    create_seat_table(train_number)


#creating seat table in our train
def create_seat_table(train_number):
    c.execute(f"CREATE TABLE IF NOT EXISTS seats_{train_number}"
              f"(seat_number INTEGER PRIMARY KEY"
              f"seat_type TEXT"
              f"booked INTEGER"
              f"passenger_name TEXT"
              f"passenger_age INTEGER"
              f"passenger_gender TEXT")

    for i in range(1, 51):
        val = categorize_seat(i)
        c.execute(f'''INSERT INTO seats_{train_number}(seat_number, seat_type, booked, passenger_name, passenger_age,passenger_gender) VALUES(?,?,?,?,?,?)''' (i , val, 0, ''','''))
        conn.commit()


def book_tickets(train_number, passenger_name, passenger_gender, passenger_age, seat_type):
    train_query = c.execute("SELECT * FROM trains WHERE train_number =? ", (train_number,))
    train_data = train_query.fetchone()

    if(train_data):
        seat_number = allocate_next_available_seat(train_number, seat_type)

        if seat_number:
            c.execute("UPDATE seats_{train_number} SET booked=1, seat_type=?, passenger_name=? , passenger_age=? , passenger_gender=? "
                      f"WHERE seat_number=?",(seat_type, passenger_name, passenger_age, passenger_gender, seat_number[0]))
            conn.commit()
            st.success(f"BOOKED SUCCESSFULLY !!")




#allocate_next_available_seat

def allocate_next_available_seat(train_number, seat_type):
    seat_query = c.execute(f"SELECT seat_number FROM seats_{train_number} WHERE booked=0 and seat_type=?"
                           f"ORDER BY seat_number asc", (seat_type,))
    result = seat_query.fetchall()

    if result:
        return [0]

#categorize seat in train
def categorize_seat(seat_number):
    if (seat_number % 10) in [0,4,5,9]:
        return "Window"
    elif (seat_number % 10) in [2,3,6,7]:
        return "Aisle"
    else:
        return "Middle"


#view seats:
def view_seats(train_number):
    train_query = c.execute("SELECT * FROM trains WHERE train_number=?", (train_number,))
    train_data = train_query.fetchone()

    if train_data:
        seat_query = c.execute(f'''SELECT 'Number: ' || seat_number, '\n Type:' || seat_type, '\n Name' || passenger_name, '\n Age:' || passenger_age, '\n Gender: ' || passenger_gender as Details, booked  FROM seats_{train_number}
        ORDER BY seat_number asc''')

        result = seat_query.fetchall()

        if result:
            st.dataframe(data = result)


#cancel_tickets:

def cancel_tickets(train_number, seat_number):
    train_query = c.execute("SELECT * FROM trains WHERE train_number=?", (train_number))
    train_data = train_query.fetchone()
    if train_data:
        c.execute(f"UPDATE seats_{train_number} SET booked=0, passenger_name='', passenger_age= '', passenger_gender='' WHERE seat_number=?",
                  (seat_number,))
        conn.commit()
        st.success(f"Ticket Cancelled SUCCESSFULLY !!")


#delete train
def delete_train(train_number, departure_date):
    train_query = c.execute("SELECT * FROM trains WHERE train_number=?", (train_number,))
    train_data = train_query.fetchone()
    if train_data:
        c.execute("DELETE FROM trains WHERE train_number=? AND departure_date=?", (train_number,departure_date))
        conn.commit()
        st.success(f"Train DELETED SUCCESSFULLY !!")




#apply all functions

def train_functions():

    st.title("Train Administrator")
    functions = st.sidebar.selectbox("select train functions", ["Add train", "View train", "Search train", "Delete train", "Book ticket", "Cancel ticket", "View seats"])
    if functions == "Add train":
        st.header("add new train")
        with st.form(key='new_train_details'):
            train_number = st.text_input("Train number")
            train_name = st.text_input("Train name")
            departure_date = st.text_input("Date")
            start_destination = st.text_input("Start destination")
            end_destination = st.text_input("End destination")
            submitted = st.form_submit_button("add train")
            if submitted and train_number != "" and train_name != "" and start_destination!="" and end_destination!="":
                add_train(train_number, train_name, departure_date, start_destination, end_destination)

                st.success("Train Added Successfully")


    elif functions == "View train":
        st.title("View all train details")
        train_query = c.execute("SELECT * FROM trains")
        train_data = train_query.fetchall()

    elif functions == "Book ticket":
        st.title("Book Train Ticket")
        train_number = st.text_input("Train number")
        seat_type = st.selectbox("seat type", ["Aisle", "Middle", "Window"], index=0)
        passenger_name = st.text_input("Passenger name")
        passenger_age = st.number_input("Passenger age", min_value=1)
        passenger_gender = st.selectbox("passenger gender", ["Male", "Female"], index=0)

        if st.button("book ticket"):
            if train_number and passenger_name and passenger_gender and passenger_age:
                book_tickets(train_number, passenger_name, passenger_gender, passenger_age, seat_type)


    elif functions== "Cancel ticket":
        st.title("Cancel Ticket")
        train_number = st.text_input("Train number")
        seat_number = st.number_input("Seat number", min_value=1)
        if st.button("cancel ticket"):
            if train_number and seat_number:
                cancel_tickets(train_number, seat_number)


    elif functions == "View seats":
        st.title("View seats")
        train_number = st.text_input("Train number")
        if st.button("view seats"):
            if train_number:
                view_seats(train_number)



    elif functions == "Delete train":
        st.title("Delete train")
        train_number = st.text_input("Train number")
        departure_date = st.text_input("Departure date")
        if st.button("delete train"):
            if train_number:
                c.execute(f"DROP TABLE IF EXISTS seats_{train_number}")
                delete_train(train_number, departure_date)