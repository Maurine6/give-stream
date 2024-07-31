#DONORS 
# app.py for donors 
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, Donor

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///donation_platform.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Database initialized")

# Create a new donor
@app.route('/donors', methods=['POST'])
def create_donor():
    data = request.json
    new_donor = Donor(username=data['username'], email=data['email'])
    db.session.add(new_donor)
    db.session.commit()
    return jsonify({'message': 'Donor created successfully', 'donor_id': new_donor.id}), 201

# Get all donors
@app.route('/donors', methods=['GET'])
def get_all_donors():
    donors = Donor.query.all()
    return jsonify([{'id': donor.id, 'username': donor.username, 'email': donor.email} for donor in donors]), 200

# Get a specific donor
@app.route('/donors/<int:donor_id>', methods=['GET'])
def get_donor(donor_id):
    donor = Donor.query.get_or_404(donor_id)
    return jsonify({'id': donor.id, 'username': donor.username, 'email': donor.email}), 200

# Update a donor
@app.route('/donors/<int:donor_id>', methods=['PUT'])
def update_donor(donor_id):
    donor = Donor.query.get_or_404(donor_id)
    data = request.json
    donor.username = data.get('username', donor.username)
    donor.email = data.get('email', donor.email)
    db.session.commit()
    return jsonify({'message': 'Donor updated successfully'}), 200

# Delete a donor
@app.route('/donors/<int:donor_id>', methods=['DELETE'])
def delete_donor(donor_id):
    donor = Donor.query.get_or_404(donor_id)
    db.session.delete(donor)
    db.session.commit()
    return jsonify({'message': 'Donor deleted successfully'}), 200

# Get all donations for a donor
@app.route('/donors/<int:donor_id>/donations', methods=['GET'])
def get_donor_donations(donor_id):
    donor = Donor.query.get_or_404(donor_id)
    donations = [{'id': d.id, 'amount': d.amount, 'date': d.date, 'charity_id': d.charity_id} for d in donor.donations]
    return jsonify(donations), 200

if __name__ == '__main__':
    app.run(debug=True)