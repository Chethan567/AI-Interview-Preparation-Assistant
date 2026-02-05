from groq import Groq
from config import Config

client = Groq(api_key=Config.GROQ_API_KEY)

class InterviewEngine:
    def __init__(self):
        self.conversation_history = []
        self.current_role = None
        self.question_count = 0
        
    def generate_questions(self, role, experience_level, num_questions):
        """Generate interview questions for a specific role"""
        try:
            prompt = f"""Generate {num_questions} technical interview questions for a {experience_level} {role} position.
            
Requirements:
- Questions should be appropriate for {experience_level} level
- Mix of technical, behavioral, and situational questions
- Questions should be clear and specific
- Return ONLY the questions, numbered 1, 2, 3, etc.

Generate the questions now:"""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            questions_text = response.choices[0].message.content
            
            # Parse questions
            questions = []
            for line in questions_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Remove numbering
                    question = line.lstrip('0123456789.-•) ').strip()
                    if question:
                        questions.append(question)
            
            return questions[:num_questions]
            
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            return [f"Error generating questions: {str(e)}"]
    
    def start_interview(self, job_role):
        """Start a new interview session"""
        self.current_role = job_role
        self.question_count = 0
        self.conversation_history = []
        
        try:
            prompt = f"""You are conducting a job interview for a {job_role} position. 
            
Your role:
- Act as a professional interviewer
- Ask ONE relevant technical or behavioral question
- Keep questions clear and focused
- Be encouraging and professional

Start the interview by asking the first question. Just ask the question directly, no preamble."""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            question = response.choices[0].message.content.strip()
            
            self.conversation_history.append({
                "role": "assistant",
                "content": question
            })
            
            self.question_count += 1
            
            return question
            
        except Exception as e:
            print(f"Error starting interview: {str(e)}")
            return f"Welcome! Let's start the interview. Tell me about your experience with {job_role}?"
    
    def process_answer(self, answer):
        """Process candidate's answer and generate next question"""
        try:
            # Add user's answer to history
            self.conversation_history.append({
                "role": "user",
                "content": answer
            })
            
            # Determine if we should continue or wrap up
            if self.question_count >= 5:
                # Final feedback
                prompt = f"""Based on this interview for a {self.current_role} position, provide brief final feedback.

Conversation so far:
{self._format_history()}

Provide:
1. Brief positive feedback on their answers
2. One area for improvement
3. Thank them for their time

Keep it concise and professional."""

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=300
                )
                
                feedback = response.choices[0].message.content.strip()
                
                return {
                    "response": feedback,
                    "next_question": None,
                    "interview_complete": True
                }
            
            else:
                # Generate feedback and next question
                prompt = f"""You are interviewing for a {self.current_role} position.

Conversation so far:
{self._format_history()}

Now:
1. Give brief (2-3 sentences) feedback on their last answer
2. Ask ONE new relevant interview question

Format your response as:
[Feedback on their answer]

[Next question]

Be professional and encouraging."""

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=400
                )
                
                ai_response = response.choices[0].message.content.strip()
                
                # Split into feedback and question
                parts = ai_response.split('\n\n')
                
                if len(parts) >= 2:
                    feedback = parts[0].strip()
                    next_question = parts[1].strip()
                else:
                    feedback = ai_response
                    next_question = "Can you tell me more about your experience?"
                
                self.conversation_history.append({
                    "role": "assistant",
                    "content": feedback + "\n\n" + next_question
                })
                
                self.question_count += 1
                
                return {
                    "response": feedback,
                    "next_question": next_question,
                    "interview_complete": False
                }
                
        except Exception as e:
            print(f"Error processing answer: {str(e)}")
            return {
                "response": "Thank you for your answer. Let me ask you another question.",
                "next_question": "What interests you most about this role?",
                "interview_complete": False
            }
    
    def evaluate_answer(self, question, answer):
        """Evaluate a single answer"""
        try:
            prompt = f"""Evaluate this interview answer:

Question: {question}

Answer: {answer}

Provide evaluation including:
1. Strengths of the answer
2. Areas for improvement
3. Suggestions for a better response
4. Overall rating (Poor/Fair/Good/Excellent)

Be constructive and specific."""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            evaluation = response.choices[0].message.content.strip()
            return evaluation
            
        except Exception as e:
            print(f"Error evaluating answer: {str(e)}")
            return f"Error evaluating answer: {str(e)}"
    
    def _format_history(self):
        """Format conversation history for prompts"""
        formatted = []
        for msg in self.conversation_history[-6:]:  # Last 3 exchanges
            role = "Interviewer" if msg["role"] == "assistant" else "Candidate"
            formatted.append(f"{role}: {msg['content']}")
        return "\n\n".join(formatted)