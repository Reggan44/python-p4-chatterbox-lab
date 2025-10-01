from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        # Get all messages ordered by created_at ascending
        messages = Message.query.order_by(Message.created_at.asc()).all()
        return jsonify([message.to_dict() for message in messages]), 200
    
    elif request.method == 'POST':
        # Create a new message from JSON data
        data = request.get_json()
        
        try:
            new_message = Message(
                body=data['body'],
                username=data['username']
            )
            
            db.session.add(new_message)
            db.session.commit()
            
            return jsonify(new_message.to_dict()), 201
        
        except Exception as e:
            return jsonify({'error': str(e)}), 400

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()
    
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    if request.method == 'PATCH':
        # Update the message body
        data = request.get_json()
        
        try:
            if 'body' in data:
                message.body = data['body']
            
            db.session.commit()
            return jsonify(message.to_dict()), 200
        
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    elif request.method == 'DELETE':
        # Delete the message
        try:
            db.session.delete(message)
            db.session.commit()
            return jsonify({'message': 'Message deleted successfully'}), 200
        
        except Exception as e:
            return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=5000, debug=True)
