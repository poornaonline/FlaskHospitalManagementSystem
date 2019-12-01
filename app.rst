App
===

MAPS Web App Routes
-------------------

- @app.route('/') - (Root of the App)

Patient Routes
---------------

- @app.route("/patients/pick_patient") - (Select Patient)
- @app.route("/patients/dashboard", methods=['GET', 'POST']) - (Patient Dashboard)
- @app.route("/patients/registration", methods=['GET', 'POST']) - (Patient Registration)
- @app.route("/create_patient_appointment", methods=['GET', 'POST']) - (Create Patient Appointment)
- @app.route("/delete_patient_appointment", methods=['GET', 'POST']) - (Delete Patient Appointment)
- @app.route("/patient/create_medical_record", methods=['GET', 'POST']) - (Create medical record by patient)
- @app.route("/patient/delete_medical_record", methods=['GET', 'POST']) - (Delete patient medical record)
- @app.route("/patient/mark_patient_visited", methods=['GET', 'POST']) - (Mark patient as visited)

Doctor Routes
---------------

- @app.route("/doctors/pick_doctor") - (Select Doctor)
- @app.route("/doctors/dashboard", methods=['GET', 'POST']) - (Doctor dashboard)
- @app.route("/create_new_availability", methods=['GET', 'POST']) - (Doctor Availability creation)
- @app.route("/doctors/patient_profile") - (Doctor Patient Profile)

Clerk Routes
---------------

- @app.route("/clerks/home", methods=['GET', 'POST']) - (Clerk home)
- @app.route("/clerk/create_patient_appointment", methods=['GET', 'POST']) - (Create patient appointment by clerk)
- @app.route("/clerk/delete_appointment", methods=['GET', 'POST']) - (Delete appointment by Clerk)
- @app.route("/analysis") - (Hospital Visualisation with Doctor's Availability and his Appointments)