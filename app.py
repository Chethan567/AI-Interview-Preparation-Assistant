from flask import Flask, render_template, request, jsonify, session
from interview_engine import InterviewEngine
from config import Config
import json

app = Flask(__name__)
app.config.from_object(Config)

# Store interview engines per session
interview_engines = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-questions', methods=['POST'])
def generate_questions():
    try:
        data = request.json
        role = data.get('role')
        experience_level = data.get('experience_level', 'Mid Level')
        num_questions = data.get('num_questions', 5)
        
        engine = InterviewEngine()
        questions = engine.generate_questions(role, experience_level, num_questions)
        
        return jsonify({'questions': questions})
    except Exception as e:
        print(f"Error in generate_questions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/start-interview', methods=['POST'])
def start_interview():
    try:
        data = request.json
        job_role = data.get('job_role')
        mode = data.get('mode', 'text')
        
        # Create new interview engine for this session
        session_id = request.cookies.get('session')
        if not session_id:
            session_id = str(hash(job_role + str(id(request))))
        
        engine = InterviewEngine()
        interview_engines[session_id] = engine
        
        # Generate first question
        first_question = engine.start_interview(job_role)
        
        response = jsonify({
            'question': first_question,
            'session_id': session_id
        })
        response.set_cookie('session', session_id)
        
        return response
    except Exception as e:
        print(f"Error in start_interview: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/submit-answer', methods=['POST'])
def submit_answer():
    try:
        data = request.json
        answer = data.get('answer')
        mode = data.get('mode', 'text')
        
        session_id = request.cookies.get('session')
        
        if not session_id or session_id not in interview_engines:
            return jsonify({'error': 'No active interview session'}), 400
        
        engine = interview_engines[session_id]
        
        # Get response and next question
        response_data = engine.process_answer(answer)
        
        return jsonify(response_data)
    except Exception as e:
        print(f"Error in submit_answer: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/reset-interview', methods=['POST'])
def reset_interview():
    try:
        session_id = request.cookies.get('session')
        
        if session_id and session_id in interview_engines:
            del interview_engines[session_id]
        
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error in reset_interview: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/evaluate-answer', methods=['POST'])
def evaluate_answer():
    try:
        data = request.json
        question = data.get('question')
        answer = data.get('answer')
        
        engine = InterviewEngine()
        evaluation = engine.evaluate_answer(question, answer)
        
        return jsonify({'evaluation': evaluation})
    except Exception as e:
        print(f"Error in evaluate_answer: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Run on all network interfaces (0.0.0.0) to allow external access
    # Access from other devices using: http://YOUR_IP_ADDRESS:5000
    app.run(host='0.0.0.0', port=5000, debug=True)