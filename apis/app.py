from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource, fields
from datetime import datetime
import joblib
import re

# Initialize the Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy and Flask-RESTX API
db = SQLAlchemy(app)
api = Api(app, version='1.0', title='Phishing Blocklist API',
          description='A simple API to manage a phishing URL blocklist and detection using ML',
          doc='/swagger')  # Swagger UI is accessible at /swagger

# Define the BlocklistEntry model
class BlocklistEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False, unique=True)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)

# Define the API model for the BlocklistEntry
blocklist_entry_model = api.model('BlocklistEntry', {
    'id': fields.Integer(readonly=True, description='The unique identifier of the blocklist entry'),
    'url': fields.String(required=True, description='The URL that is blocked'),
    'added_on': fields.DateTime(description='The time the URL was added to the blocklist')
})

# Initialize the database (create tables if they don't exist)
with app.app_context():
    db.create_all()

# Define the Blocklist Resource for GET and POST methods
@api.route('/blocklist')
class Blocklist(Resource):
    @api.doc('Get all blocked URLs')
    @api.marshal_list_with(blocklist_entry_model)
    def get(self):
        """Fetch all URLs in the blocklist."""
        entries = BlocklistEntry.query.all()
        return entries, 200

    @api.doc('Add a new URL to the blocklist')
    @api.expect(blocklist_entry_model)
    def post(self):
        """Add a new URL to the blocklist."""
        data = request.get_json()
        url = data.get('url')
        if not url:
            return {'error': 'URL is required'}, 400

        if BlocklistEntry.query.filter_by(url=url).first():
            return {'error': 'URL already exists in blocklist'}, 409

        new_entry = BlocklistEntry(url=url)
        db.session.add(new_entry)
        db.session.commit()
        return {'message': 'URL added to blocklist', 'url': url}, 201

# Define the BlocklistEntry Resource for DELETE by ID method
@api.route('/blocklist/<int:id>')
class BlocklistEntryResource(Resource):
    @api.doc('Remove a URL from the blocklist')
    def delete(self, id):
        """Remove a URL from the blocklist by ID."""
        entry = BlocklistEntry.query.get(id)
        if not entry:
            return {'error': 'Blocklist entry not found'}, 404

        db.session.delete(entry)
        db.session.commit()
        return {'message': 'URL removed from blocklist', 'id': id}, 200

# Define the check URL route
@api.route('/blocklist/check')
class CheckURL(Resource):
    @api.doc('Check if a URL is in the blocklist or flagged as phishing')
    def post(self):
        """Check if a URL is blocked or flagged as phishing by the model."""
        data = request.get_json()
        url = data.get('url')
        if not url:
            return {'error': 'URL is required'}, 400

        # Check against the blocklist
        entry = BlocklistEntry.query.filter_by(url=url).first()
        if entry:
            return {'message': 'URL is blocked', 'url': url}, 200

        # Perform dynamic detection if model is loaded (commented out here for demo)
        # if phishing_model:
        #     prediction = phishing_model.predict([extract_features(url)]))
        #     if prediction[0] == 1:  # Assuming 1 means phishing
        #         return {'message': 'URL is flagged as phishing by the model', 'url': url}, 200

        return {'message': 'URL is safe', 'url': url}, 200

# Helper function for feature extraction (optional for future model usage)
def extract_features(url):
    """Extract features from a URL for phishing detection."""
    features = []
    features.append(len(url))  # Length of the URL
    features.append(int(bool(re.search(r'https://', url))))  # Uses HTTPS
    features.append(int(bool(re.search(r'\d', url))))  # Contains digits
    # Add more feature extraction logic as needed
    return features

if __name__ == '__main__':
    app.run(debug=True)
