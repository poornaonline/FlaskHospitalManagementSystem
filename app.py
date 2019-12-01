from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap
from flask_datepicker import datepicker
from flask_wtf import Form
from wtforms.fields import DateField
import os
import requests
from constant.serverapi import *

app = Flask(__name__)
Bootstrap(app)
datepicker(app)
app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))


@app.route('/')
def index():
    """
    Home Page for Smart Office - MAPS
    :return:
    """
    return render_template('index.html')


# Patient Routes


@app.route("/patients/pick_patient")
def pick_patient():
    """
    Pick a Patient
    :return:
    """
    response = requests.get(server_url + 'patient/get_all_patients')
    patient_list = response.json()
    return render_template('patients/pick_patient.html', result=patient_list)


@app.route("/patients/dashboard", methods=['GET', 'POST'])
def patient_dashboard():
    """
    Patients Dashboard, for booking appointments, viewing medical records from doctor
    :return:
    """
    patient_email = request.args.get('pick_patient')

    # Fetching the APIs
    response_appointments_for_patient = requests.post(server_url + 'patient/get_all_appointments_for_patient', json={
        'patient_email': patient_email
    })
    response_get_patient_details = requests.post(server_url + 'doctor/get_patient_details', json={
        'patient_email': patient_email
    })
    response_get_all_doctors = requests.get(server_url + 'doctor/get_all_doctors')
    response_get_medical_records_for_patient = requests.post(server_url + 'doctor/get_all_medical_records_for_patient',
                                                             json={
                                                                 'patient_email': patient_email
                                                             })

    patient_appointments_list = response_appointments_for_patient.json()
    patient_details = response_get_patient_details.json()
    doctors_list = response_get_all_doctors.json()
    medical_records = response_get_medical_records_for_patient.json()

    return render_template('patients/dashboard.html', patient_appointments_list=patient_appointments_list,
                           patient_details=patient_details, doctors_list=doctors_list, medical_records=medical_records)


@app.route("/patients/registration", methods=['GET', 'POST'])
def patient_registration():
    """
    Registration for Patient
    :return:
    """
    if request.method == 'POST':
        patient_email = request.form['patient_email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        age = request.form['age']

        response = requests.post(server_url + 'patient/create_new_patient', json={
            'patient_email': patient_email,
            'first_name': first_name,
            'last_name': last_name,
            'age': age
        })
        response = response.json()

        if response.get('Status') == "SUCCESS":
            return render_template('patients/registration_success.html')
        else:
            return render_template('patients/registration_failed.html')
    else:
        return render_template('patients/registration.html')


@app.route("/create_patient_appointment", methods=['GET', 'POST'])
def create_patient_appointment():
    """
    Booking an Apppintment for Patient
    :return:
    """
    if request.method == 'POST':
        patient_email = request.form['patient_email']
        doctor_email = request.form['doctor_email']
        date = request.form['date']
        time = request.form['time']

        response = requests.post(server_url + 'patient/create_appointment', json={
            'patient_email': patient_email,
            'doctor_email': doctor_email,
            'date': date,
            'time': time
        })

        response = response.json()

        if response.get('Status') == "DOCTOR_HAS_AN_APPOINTMENT_SELECTED_TIME_SLOT":
            return render_template('patients/appointment_failed.html')
        elif response.get('Status') == "DOCTOR_IS_NOT_AVAILABLE_AT_THAT_TIME":
            return render_template('patients/appointment_failed.html')
        elif response.get('Status') == "INVALID_PATIENT_EMAIL":
            return render_template('patients/appointment_failed.html')
        elif response.get('Status') == "INVALID_DOCTOR_EMAIL":
            return render_template('patients/appointment_failed.html')
        else:
            referer = request.referrer
            return redirect(referer, code=302)
    else:
        return render_template('patients/dashboard.html')


@app.route("/delete_patient_appointment", methods=['GET', 'POST'])
def delete_patient_appointment():
    """
    Deleting an Appointment for Patient
    :return:
    """
    if request.method == 'POST':
        appointment_id = request.form['appointment_id']
        response_delete_patient_appointment = requests.post(server_url + 'patient/delete_appointment', json={
            'appointment_id': appointment_id
        })
        response_delete_patient_appointment = response_delete_patient_appointment.json()
        if response_delete_patient_appointment.get('Status') == 'SUCCESS':
            referer = request.referrer
            return redirect(referer, code=302)
        else:
            return "An error occurred deleting the appointment"


# Doctor Routes


@app.route("/doctors/pick_doctor")
def pick_doctor():
    """
    Choosing a Doctor to Begin
    :return:
    """
    response = requests.get(server_url + 'doctor/get_all_doctors')
    doctor_list = response.json()
    return render_template('doctors/pick_doctor.html', result=doctor_list)


@app.route("/doctors/dashboard", methods=['GET', 'POST'])
def doctor_dashboard():
    """
    Doctor's Dashboard for Adding an Availability, and creating Medical Records for Patients
    :return:
    """
    doctor_email = request.args.get('pick_doctor')

    # Fetching the APIs
    response_get_doctor_details = requests.post(server_url + 'doctor/get_doctor', json={
        'email': doctor_email
    })
    response_get_patients_appointments = requests.post(server_url + 'doctor/get_all_appointments_with_patients', json={
        'doctor_email': doctor_email
    })

    doctor_details = response_get_doctor_details.json()
    patients_appointments_list = response_get_patients_appointments.json()

    return render_template('doctors/dashboard.html', doctor_details=doctor_details,
                           patients_appointments_list=patients_appointments_list)


@app.route("/create_new_availability", methods=['GET', 'POST'])
def create_new_availability():
    """
    Doctor Adding an Availability time for the Patient
    :return:
    """
    if request.method == 'POST':
        doctor_email = request.form['doctor_email']
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']

        response_add_availability = requests.post(server_url + 'doctor/add_availability', json={
            'doctor_email': doctor_email,
            'date': date,
            'start_time': start_time,
            'end_time': end_time
        })
        response_add_availability = response_add_availability.json()

        if response_add_availability.get('Status') == "ALREADY_AVAILABILITY_SET":
            return render_template('doctors/availability_failed.html')
        else:
            referer = request.referrer
            return render_template('doctors/availability_success.html', referer=referer)
    else:
        return render_template('doctors/dashboard.html')


@app.route("/doctors/patient_profile")
def patient_profile():
    """
    Doctor Visit Patient's profile for Adding a Medical Record and Diagnosis
    :return:
    """
    patient_email = request.args.get('pick_patient')

    # Fetching the APIs
    response_get_patient_details = requests.post(server_url + 'doctor/get_patient_details', json={
        'patient_email': patient_email
    })
    response_get_records_for_patient = requests.post(server_url + 'doctor/get_all_medical_records_for_patient', json={
        'patient_email': patient_email
    })
    patient_details = response_get_patient_details.json()
    medical_records = response_get_records_for_patient.json()

    return render_template('doctors/patient_profile.html', patient_details=patient_details,
                           medical_records=medical_records)


@app.route("/patient/create_medical_record", methods=['GET', 'POST'])
def create_medical_record_for_patient():
    """
    Doctor Adds Medical Information, Diagnosis for Patient
    :return:
    """
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        description = request.form['description']

        response_create_medical_record = requests.post(server_url + 'doctor/create_medical_record', json={
            'patient_id': patient_id,
            'description': description
        })
        response_create_medical_record = response_create_medical_record.json()
        if response_create_medical_record.get('Status') == "INVALID_PATIENT_ID":
            return render_template('doctors/create_record_failed.html')
        else:
            referer = request.referrer
            return redirect(referer, code=302)
    else:
        return render_template('/doctors/patient_profile.html')


@app.route("/patient/delete_medical_record", methods=['GET', 'POST'])
def delete_medical_record_for_patient():
    """
    Doctor Deletes a Medical Record for Patient
    :return:
    """
    if request.method == 'POST':
        medical_record_id = request.form['medical_record_id']

        response_delete_medical_record = requests.post(server_url + 'doctor/delete_medical_record', json={
            'medical_record_id': medical_record_id
        })
        response_delete_medical_record = response_delete_medical_record.json()
        if response_delete_medical_record.get('Status') == "SUCCESS":
            referer = request.referrer
            return redirect(referer, code=302)
        else:
            return "An error occurred deleting the appointment"


# Clerk Routes

@app.route("/clerks/home", methods=['GET', 'POST'])
def clerk_home():
    """
    Medical Clerk's Home, where he/she can book the appointment for Patient / Mark the Patient - Check In
    :return:
    """
    response_doctors = requests.post(server_url + 'doctor/all_doctors_and_all_appointments', json={})
    doctors = response_doctors.json()

    response_get_all_patients = requests.get(server_url + 'patient/get_all_patients')
    patients = response_get_all_patients.json()

    return render_template('clerks/home.html', patients=patients, doctors=doctors)


@app.route("/clerk/create_patient_appointment", methods=['GET', 'POST'])
def clerk_create_appointment():
    """
    Medical Clerk Creates an Appointment for Patient
    :return:
    """
    if request.method == 'POST':
        patient_email = request.form['patient_email']
        doctor_email = request.form['doctor_email']
        date = request.form['date']
        time = request.form['time']

        response_clerk_create_appointment = requests.post(server_url + 'medical_clerk/create_appointment', json={
            'patient_email': patient_email,
            'doctor_email': doctor_email,
            'date': date,
            'time': time
        })
        response_clerk_create_appointment = response_clerk_create_appointment.json()

        if response_clerk_create_appointment.get('Status') == "INVALID_DOCTOR_EMAIL":
            return render_template('clerks/clerk_appointment_failed.html')
        elif response_clerk_create_appointment.get('Status') == "INVALID_PATIENT_EMAIL":
            return render_template('clerks/clerk_appointment_failed.html')
        elif response_clerk_create_appointment.get('Status') == "DOCTOR_IS_NOT_AVAILABLE_AT_THAT_TIME":
            return render_template('clerks/clerk_appointment_failed.html')
        elif response_clerk_create_appointment.get('Status') == "DOCTOR_HAS_AN_APPOINTMENT_SELECTED_TIME_SLOT":
            return render_template('clerks/clerk_appointment_failed.html')
        else:
            referer = request.referrer
            return redirect(referer, code=302)
    else:
        return render_template('clerks/home.html')


@app.route("/clerk/delete_appointment", methods=['GET', 'POST'])
def clerk_delete_appointment():
    """
    Medical Clerk Deletes an Appointment for Patient
    :return:
    """
    if request.method == 'POST':
        appointment_id = request.form['appointment_id']

        response_clerk_delete_appointment = requests.post(server_url + 'medical_clerk/delete_appointment', json={
            'appointment_id': appointment_id
        })
        response_clerk_delete_appointment = response_clerk_delete_appointment.json()

        if response_clerk_delete_appointment.get('Status') == "SUCCESS":
            referer = request.referrer
            return redirect(referer, code=302)
        else:
            return "An error occurred deleting the appointment"


@app.route("/patient/mark_patient_visited", methods=['GET', 'POST'])
def mark_patient_visited():
    """
    Medical Clerk marks Patient - CHECK IN
    :return:
    """
    if request.method == 'POST':
        patient_email = request.form['patient_email']
        doctor_email = request.form['doctor_email']
        appointment_id = request.form['appointment_id']

        response_mark_patient_visited = requests.post(server_url + 'patient/mark_patient_visited', json={
            'patient_email': patient_email,
            'doctor_email': doctor_email,
            'appointment_id': appointment_id
        })
        response_mark_patient_visited = response_mark_patient_visited.json()

        if response_mark_patient_visited.get('Status') == "INVALID_DOCTOR_EMAIL":
            return "Invalid Doctor Email"
        elif response_mark_patient_visited.get('Status') == "INVALID_PATIENT_EMAIL":
            return "Invalid Patient Email"
        elif response_mark_patient_visited.get('Status') == "APPOINTMENT_NOT_BELONG_TO_THE_PATIENT":
            return "Appointment ID is not found for this patient"
        else:
            referer = request.referrer
            return redirect(referer, code=302)


@app.route("/analysis")
def analysis():
    """
    Hospital Visualisation with Doctor's Availability and his Appointments
    :return:
    """

    response_all_doctors_and_appointments = requests.post(server_url + 'doctor/all_doctors_and_all_appointments')
    doctors_and_appointments = response_all_doctors_and_appointments.json()

    return render_template('clerks/analysis.html', doctors_and_appointments=doctors_and_appointments)


if __name__ == '__main__':
    # host = os.popen('hostname -I').read()
    app.run(port=9000)
    # app.run()
