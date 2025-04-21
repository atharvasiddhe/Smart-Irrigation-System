from flask import Flask, request, render_template
import joblib
import numpy as np
import csv
import os

app = Flask(__name__)

# Check if model exists before loading
MODEL_FILE = 'crop_model.pkl'
if os.path.exists(MODEL_FILE):
    model = joblib.load(MODEL_FILE)
else:
    model = None

# Store past predictions
prediction_history = []

# CSV file to store contact messages
MESSAGE_FILE = "messages.csv"

# Ensure CSV file exists
if not os.path.exists(MESSAGE_FILE):
    with open(MESSAGE_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Email", "Message"])  # Column headers

@app.route('/')
def home():
    """Render crop prediction home page."""
    return render_template('index.html', history=prediction_history)

@app.route('/predict', methods=['POST'])
def predict():
    """Handle crop prediction based on user input."""
    if model is None:
        return render_template('index.html', prediction_text="❌ Model not found!", history=prediction_history)

    try:
        # Validate input
        required_fields = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'soil_type']
        if not all(field in request.form and request.form[field] for field in required_fields):
            return render_template('index.html', prediction_text="⚠️ Please fill in all fields!", history=prediction_history)

        # Convert form inputs to float
        data = [float(request.form[key]) for key in ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
        soil_type = request.form.get('soil_type')

        # Soil type adjustment factor
        soil_factor = {"sandy": 0.9, "loamy": 1.0, "clay": 0.85, "black": 0.95, "red": 0.88}
        if soil_type not in soil_factor:
            return render_template('index.html', prediction_text="❌ Invalid Soil Type", history=prediction_history)

        # Adjust input data based on soil type
        data = [x * soil_factor[soil_type] for x in data]

        # Make prediction
        prediction = model.predict([data])[0]

        # Store latest prediction, limit to last 5
        prediction_history.insert(0, f"{prediction} (Soil: {soil_type})")
        prediction_history[:] = prediction_history[:5]

        return render_template('index.html', prediction_text=f"🌾 Recommended Crop: {prediction}", history=prediction_history)
    
    except Exception as e:
        return render_template('index.html', prediction_text=f"❌ Error: {str(e)}", history=prediction_history)

@app.route('/seedBank')
def seedbank():
    """Render the Seed Bank of Maharashtra page."""
    seed_banks = [
        {"name": "Pune Seed Bank", "location": "Pune, Maharashtra", "map_url":"https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d3784.0038044700595!2d73.86548577183774!3d18.48348687031254!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!5e0!3m2!1sen!2sin!4v1742632805893!5m2!1sen!2sin"},
        {"name": "Nagpur Seed Bank", "location": "Nagpur, Maharashtra", "map_url": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3721.338383296648!2d79.09282417195038!3d21.138927783992!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3bd4c1170e142483%3A0x46c2d5699c49d547!2sNational%20Seeds%20Corporation%20Ltd.Nagpur!5e0!3m2!1sen!2sin!4v1742633155791!5m2!1sen!2sin"},
        {"name": "Nashik Seed Bank", "location": "Nashik, Maharashtra", "map_url": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3749.3901356859387!2d73.79260847189975!3d19.99213422258078!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3bddeb013af2e74b%3A0x93092e5db554ae96!2sNational%20Seeds%20Corporation%20Limited!5e0!3m2!1sen!2sin!4v1742633273462!5m2!1sen!2sin"},
        {"name": "Solapur Seed Bank", "location": "Solapur, Maharashtra", "map_url": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d60822.265470464896!2d75.82354782167968!3d17.67895200000001!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3bc5d100324b70ef%3A0x9679bc43c0d51ce8!2sMahabeej%20District%20Office%20Solapur!5e0!3m2!1sen!2sin!4v1742633813975!5m2!1sen!2sin"},
        {"name": "Ch. Sambhaji Nagar Seed Bank", "location": "Ch. Sambhaji Nagar, Maharashtra", "map_url": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3751.777694730783!2d75.37697297068496!3d19.891606812290878!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3bdb9815a369bc63%3A0x6461ed227de4b85c!2sNational%20Seeds%20Corporation%20Ltd!5e0!3m2!1sen!2sin!4v1742633613895!5m2!1sen!2sin"}
    ]
    return render_template('seedBank.html', seed_banks=seed_banks)

@app.route('/contact', methods=['GET'])
def contact():
    """Render the contact page."""
    return render_template('contact.html')

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    """Handle contact form submission and save to CSV."""
    try:
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()

        # Validate input
        if not name or not email or not message:
            return render_template('contact.html', message="⚠️ Please fill in all fields!")

        if len(message) > 500:
            return render_template('contact.html', message="⚠️ Message too long! (Max: 500 characters)")

        # Save message in CSV
        with open(MESSAGE_FILE, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([name, email, message])

        return render_template('contact.html', message="✅ Your message has been sent successfully!")

    except Exception as e:
        return render_template('contact.html', message=f"❌ Error: {str(e)}")



DATA_FILE = "sensor_data.csv"

# Ensure CSV file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Temperature", "Humidity", "Moisture"])

pump_status = "OFF"

@app.route('/update_data', methods=['POST'])
def update_data():
    global pump_status
    try:
        temperature = request.form.get('temperature', type=float)
        humidity = request.form.get('humidity', type=float)
        moisture = request.form.get('moisture', type=int)

        if temperature is None or humidity is None or moisture is None:
            return "Invalid Data", 400

        with open("sensor_data.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([temperature, humidity, moisture])

        if moisture < 500:
            pump_status = "ON"
        else:
            pump_status = "OFF"

        return pump_status  # Send pump status to ESP32

    except Exception as e:
        return str(e), 500

@app.route('/sensor_data')
def sensor_data():
    data = []
    with open(DATA_FILE, "r") as file:
        reader = csv.reader(file)
        next(reader)
        data = list(reader)[-10:]  # Last 10 entries

    return render_template("sensor_data.html", data=data, pump_status=pump_status)

@app.route('/control_pump', methods=['POST'])
def control_pump():
    global pump_status
    pump_status = request.form.get("status")
    return "Pump turned " + pump_status

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')





if __name__ == '__main__':
    app.run(debug=True)
