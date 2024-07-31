from models import db
from functools import wraps
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from flask import Flask, make_response,jsonify,session,request, current_app, jsonify
from flask_restful import Resource, Api
import bcrypt
from datetime import datetime, timedelta

from config import app,db,api
from models import db, Admin, Donor,Charity


# Views go here!
class checkSession(Resource):
    @jwt_required()
    def get(self):
        claims = get_jwt_identity()
        if claims:
            return {"user is logged in": "True"},200
        else:
            return {"message": "Invalid token user not logged in"}, 401
        
from models import db, Admin, Donor, Donation,Charity,CharityApplication,Beneficiary,Inventory,Story

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt_identity()
            if claims['role'] != 'admin':
                return jsonify(msg='Admins only!'), 403
            else:
                return fn(*args, **kwargs)
        return decorator
    return wrapper

def donor_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt_identity()
            if claims['role'] != 'donor':
                return jsonify(msg='Donors only!'), 403
            else:
                return fn(*args, **kwargs)
        return decorator
    return wrapper

def charity_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt_identity()
            if claims['role'] != 'charity':
                return jsonify(msg='Charities only!'), 403
            else:
                return fn(*args, **kwargs)
        return decorator
    return wrapper

def admin_or_donor_or_charity_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt_identity()
            if claims['role'] not in ['admin', 'donor', 'charity']:
                return jsonify(msg='Unauthorized'), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

from datetime import timedelta

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {'message': 'Username and password are required'}, 400

        donor = Donor.query.filter_by(username=username).first()
        charity = Charity.query.filter_by(username=username).first()
        admin = Admin.query.filter_by(username=username).first()

        if donor:
            if donor.authenticate(password):
                access_token = create_access_token(
                    identity={'id': donor.id, 'role': 'donor'},
                    expires_delta=timedelta(days=4)
                )
                session['id'] = donor.id
                return {'access_token': access_token}, 200
            else:
                return {'message': 'Invalid password for donor'}, 401
        elif charity:
            if charity.authenticate(password):
                access_token = create_access_token(
                    identity={'id': charity.id, 'role': 'charity'},
                    expires_delta=timedelta(days=4)
                )
                session['id'] = charity.id
                return {'access_token': access_token}, 200
            else:
                return {'message': 'Invalid password for charity'}, 401    
        elif admin:
            if admin._password_hash is None:
                return {'message': 'Admin password not set'}, 500
            if admin.authenticate(password):
                access_token = create_access_token(
                    identity={'id': admin.id, 'role': 'admin'},
                    expires_delta=timedelta(days=4)
                )
                return {'access_token': access_token, 'role': 'admin'}, 200
            else:
                return {'message': 'Invalid password for admin'}, 401
        else:
            return {'message': 'User not found'}, 404
        
class Charities(Resource):
    @jwt_required()
    def get(self):
        charities = Charity.query.all()
        return jsonify([charity.to_dict() for charity in charities])

    @jwt_required()
    def post(self):
        data = request.get_json()
        new_charity = Charity(
            username=data['username'],
            email=data['email'],
            name=data['name'],
            description=data.get('description'),
            needed_donation=data.get('needed_donation')
        )
        new_charity.password_hash = data['password']
        db.session.add(new_charity)
        db.session.commit()
        return new_charity.to_dict(), 201
    


class CharityApplications(Resource):
    @admin_required()
    def get(self):
        applications = CharityApplication.query.all()
        return jsonify([app.to_dict() for app in applications])

    @jwt_required()
    def post(self):
        data = request.get_json()
        new_application = CharityApplication(
            name=data['name'],
            email=data['email'],
            description=data['description']
        )
        db.session.add(new_application)
        db.session.commit()
        return new_application.to_dict(), 201

    @admin_required()
    def put(self, id):
        application = CharityApplication.query.get_or_404(id)
        data = request.get_json()
        application.status = data['status']
        application.reviewed_by = get_jwt_identity()['id']
        application.review_date = datetime.utcnow()

        if data['status'] == 'approved':
            new_charity = Charity(
                username=application.name.lower().replace(' ', '_'),
                email=application.email,
                name=application.name,
                description=application.description
            )
            db.session.add(new_charity)

        db.session.commit()
        return application.to_dict(), 200
    

 
class AdminDashboard(Resource):
    @admin_required()
    def get(self):
        total_donations = db.session.query(db.func.sum(Donation.amount)).scalar() or 0
        charity_count = Charity.query.count()
        donor_count = Donor.query.count()
        recent_donations = Donation.query.order_by(Donation.date.desc()).limit(10).all()
        pending_applications = CharityApplication.query.filter_by(status='pending').count()

        return {
            'total_donations': total_donations,
            'charity_count': charity_count,
            'donor_count': donor_count,
            'recent_donations': [donation.to_dict() for donation in recent_donations],
            'pending_applications': pending_applications
        }   


class Donations(Resource):
    # Retrieve all donations
    def get(self, donor_id=None, charity_id=None):
        if donor_id is not None:
            return self.get_donation_by_donor_id(donor_id)
        elif charity_id is not None:
            return self.get_donation_by_charity_id(charity_id)
        else:
            all_donations = Donation.query.all()
            donations_json = [donation.to_dict() for donation in all_donations]
            return donations_json

    # Retrieve donations by donor id and the sum
    def get_donation_by_donor_id(self, donor_id):
        donor_donations = Donation.query.filter_by(donor_id=donor_id).all()
        if donor_donations:
            donations_json = [donation.to_dict() for donation in donor_donations]
            total_amount = sum(donation.amount for donation in donor_donations)
            return {
                'donations': donations_json,
                'total_amount': total_amount
            }
        else:
            return {'message': 'No donations found for this donor'}, 404
        
    # Retrieve donations by charity id and the sum
    def get_donation_by_charity_id(self, charity_id):
        charity_donations = Donation.query.filter_by(charity_id=charity_id).all()
        if charity_donations:
            donations_json = [donation.to_dict() for donation in charity_donations]
            total_amount = sum(donation.amount for donation in charity_donations)
            return {
                'donations': donations_json,
                'total_amount': total_amount
            }
        else:
            return {'message': 'No donations found for this charity'}, 404.
    
    # Create a new donation
    def post(self):
        data = request.get_json()
        date = datetime.strptime(data['date'], '%Y-%m-%d')
        new_donation = Donation(
            donor_id=data['donor_id'],
            charity_id=data['charity_id'],
            amount=data['amount'],
            date=date,
            is_anonymous=data['is_anonymous'],
            is_recurring=data['is_recurring'],
            recurring_frequency=data['recurring_frequency']
        )
        db.session.add(new_donation)
        db.session.commit()
        return new_donation.to_dict()
    
    # Updating a donation
    def put(self, id):
        data = request.get_json()
        donation = Donation.query.get(id)
        if donation:
            donation.donor_id = data['donor_id']
            donation.charity_id = data['charity_id']
            donation.amount = data['amount']
            donation.date = datetime.strptime(data['date'], '%Y-%m-%d')
            donation.is_anonymous = data['is_anonymous']
            donation.is_recurring = data['is_recurring']
            donation.recurring_frequency = data['recurring_frequency']
            db.session.commit()
            return donation.to_dict()
        else:
            return {'message': 'Donation not found'}, 404
    
# Routes
api.add_resource(Login, '/login');    
api.add_resource(Donations, '/donations','/donations/<int:id>', '/donations/donor/<int:donor_id>', '/donations/charity/<int:charity_id>')
api.add_resource(Charities, '/charities')  
api.add_resource(CharityApplications, '/charity-applications', '/charity-applications/<int:id>')   
api.add_resource(AdminDashboard, '/admin-dashboard')


if __name__ == '__main__':
    app.run(debug=True)
