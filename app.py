import os
from app import create_app, db

# Load the configuration depending on the environment variable
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

# Ensure database tables are created automatically
with app.app_context():
    from app.models.user import User
    from app.models.resume import Resume
    from app.models.readiness import PlacementReadiness
    from app.models.interview import Question, Bookmark, InterviewHistory
    db.create_all()
    
    # Preload interview questions if empty
    if Question.query.count() == 0:
        import json
        json_path = os.path.join(app.root_path, '../questions/questions.json')
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                questions_data = json.load(f)
                for q in questions_data:
                    new_q = Question(
                        category=q['category'],
                        difficulty=q['difficulty'],
                        question_text=q['question_text'],
                        answer_reveal=q['answer_reveal']
                    )
                    db.session.add(new_q)
            db.session.commit()

if __name__ == '__main__':
    # Defaulting to 0.0.0.0 and port 5000 for standard local development & Docker configurations
    app.run(host='0.0.0.0', port=5000)
