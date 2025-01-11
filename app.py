import streamlit as st
import pandas as pd
from datetime import datetime
import os
import matplotlib.pyplot as plt

# Folder untuk menyimpan data
os.makedirs("data", exist_ok=True)
employee_file = "data/employees.xlsx"
attendance_file = "data/attendance.xlsx"

# Inisialisasi file
if not os.path.exists(employee_file):
    pd.DataFrame(columns=["ID", "Name", "Position"]).to_excel(employee_file, index=False, engine="openpyxl")
if not os.path.exists(attendance_file):
    pd.DataFrame(columns=["ID", "Name", "Date", "Time", "Status", "Photo", "Location"]).to_excel(attendance_file, index=False, engine="openpyxl")

# Load data
employees = pd.read_excel(employee_file, engine="openpyxl")
attendance = pd.read_excel(attendance_file, engine="openpyxl")

# Fungsi untuk membuat dashboard
def generate_dashboard():
    if attendance.empty:
        st.warning("No attendance data available yet.")
        return

    st.subheader("Attendance Dashboard")

    # Tabel jumlah absensi per hari
    attendance["Date"] = pd.to_datetime(attendance["Date"]).dt.date
    daily_summary = attendance.groupby("Date").size().reset_index(name="Total Attendance")
    st.table(daily_summary)

    # Grafik jumlah absensi per hari
    plt.figure(figsize=(10, 5))
    plt.bar(daily_summary["Date"], daily_summary["Total Attendance"], color="skyblue")
    plt.xlabel("Date")
    plt.ylabel("Total Attendance")
    plt.title("Daily Attendance Summary")
    plt.xticks(rotation=45)
    st.pyplot(plt)

# Streamlit layout
st.title("Employee Attendance System")

# Menu
menu = ["Register Employee", "Attendance", "Dashboard", "Manage Data"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register Employee":
    st.header("Register Employee")
    with st.form("register_form"):
        id_employee = st.text_input("Employee ID")
        name_employee = st.text_input("Employee Name")
        position = st.text_input("Position")
        submit = st.form_submit_button("Register")

        if submit:
            if id_employee and name_employee and position:
                new_employee = {"ID": id_employee, "Name": name_employee, "Position": position}
                employees = pd.concat([employees, pd.DataFrame([new_employee])], ignore_index=True)
                employees.to_excel(employee_file, index=False, engine="openpyxl")
                st.success(f"Employee {name_employee} registered successfully!")
            else:
                st.error("All fields are required!")

elif choice == "Attendance":
    st.title("Attendance Form")

    # Form Absensi
    with st.form("attendance_form"):
        # Pilih ID Karyawan dari dropdown
        id_employee = st.selectbox("Employee ID", employees["ID"].unique())

        # Ambil data karyawan berdasarkan ID yang dipilih
        selected_employee = employees[employees["ID"] == id_employee].iloc[0]
        name_employee = selected_employee["Name"]
        position = selected_employee["Position"]
        
        # Menampilkan Nama dan Posisi secara otomatis
        st.write(f"Employee Name: {name_employee}")
        st.write(f"Position: {position}")

        # Tanggal dan Waktu Absensi
        date = st.date_input("Date", value=datetime.now().date())
        time = st.time_input("Time", value=datetime.now().time())
        
        # Status Absensi
        status = st.radio("Status", ["IN", "OUT"])
        
        # Upload Foto
        photo = st.file_uploader("Upload Photo", type=["jpg", "png"])

        # Keterangan Lokasi Manual
        location = st.text_input("Enter Location")

        # Tombol Submit
        submit = st.form_submit_button("Submit")
        if submit:
            if photo and location:
                try:
                    # Menentukan folder untuk menyimpan gambar (folder per ID Karyawan)
                    photo_folder = os.path.join("data", id_employee)
                    os.makedirs(photo_folder, exist_ok=True)  # Membuat folder berdasarkan ID Karyawan

                    # Menggunakan nama file berdasarkan ID dan timestamp
                    file_name = os.path.join(photo_folder, f"{id_employee}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
                    with open(file_name, "wb") as f:
                        f.write(photo.getbuffer())
                    
                    # Menyimpan data absensi
                    new_attendance = {
                        "ID": id_employee,
                        "Name": name_employee,
                        "Date": date,
                        "Time": time,
                        "Status": status,
                        "Photo": file_name,
                        "Location": location,
                    }
                    attendance = pd.concat([attendance, pd.DataFrame([new_attendance])], ignore_index=True)
                    attendance.to_excel(attendance_file, index=False, engine="openpyxl")
                    st.success("Attendance recorded successfully!")
                except Exception as e:
                    st.error(f"Error saving attendance: {e}")
            else:
                st.error("Photo and Location are required!")

elif choice == "Dashboard":
    generate_dashboard()

elif choice == "Manage Data":
    st.header("Manage Attendance Data")

    # Tampilkan data attendance
    if not attendance.empty:
        st.subheader("Current Attendance Data")
        st.dataframe(attendance)

        # Pilih baris yang ingin dihapus berdasarkan ID
        selected_id = st.selectbox("Select ID to delete", attendance["ID"].unique())

        if st.button("Delete Entry"):
            # Hapus data berdasarkan ID yang dipilih
            attendance = attendance[attendance["ID"] != selected_id]
            attendance.to_excel(attendance_file, index=False, engine="openpyxl")
            st.success(f"Entry with ID {selected_id} has been deleted.")
    else:
        st.warning("No attendance data available to manage!")
