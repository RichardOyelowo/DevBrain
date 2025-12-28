# for the quuestion API scraping
import requests
from bs4 import BeautifulSoup
from config import API_KEY


class Questions:
    
    
    def fetch_quiz_topics(self):
            response = requests.get('https://quizapi.io/categories')
            html_content = response.content # Use .content to help with character encoding

            soup = BeautifulSoup(html_content, 'html.parser')
            topics_card= soup.find_all('div', class_= 'card card-body border text-center')

            topics = []
            for topic in topics_card:
                topic_name = topic.find('h5').text.strip()
                topics.append(topic_name)

            return topics 
    

    def get_questions(self, topic: str = "uncategorized", limit: int = 10, difficulty: str = 'Easy'):
        url = f'https://quizapi.io/api/v1/questions?apiKey={API_KEY}&category={topic}&limit={limit}&difficulty={difficulty}&single_answer_only=true'
       
        response = requests.get(url)

        if response.status_code != 200:
            return {"error": "HTTP Error"}
        
        questions_data = response.json()

        if questions_data == []:
            return {"error": "No questions"}


        questions = [] # Question List

        # list of tuples (questions, answers_list, correct_answer, explanation)
        for item in questions_data:
            desc = item.get("description", "")
            question_text = f"{item['question']}"
            answers_list = item.get("answers", {})
            explanation = item.get("explanation", "")

            correct_answer = None  # initialize before using
            for key, value in item.get("correct_answers", {}).items():
                if value == "true":
                    answer_key = key.replace("_correct", "")
                    correct_answer = answers_list.get(answer_key)
                    break

            if correct_answer is None:
                return {"error": "Invalid question: no correct answer"}

            questions.append({
                "text" : question_text, 
                "description" : desc,
                "answers" : answers_list, 
                "correct_answer" : correct_answer, 
                "explanation" : explanation
            })

        return {"questions": questions}
 