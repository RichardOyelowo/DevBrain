# for the quuestion API scraping
import requests
from bs4 import BeautifulSoup
from config import API_KEY


class Questions:

    DEFAULT_TOPICS = [
        "Linux", "Docker", "bash", "php", "Kubernetes", "Python",
        "JavaScript", "HTML", "CSS", "SQL", "React", "NodeJS"
    ]
    
    def fetch_quiz_topics(self) -> list:
        try:
            response = requests.get('https://quizapi.io/categories', timeout=5)
            response.raise_for_status()
        except requests.RequestException:
            return self.DEFAULT_TOPICS

        soup = BeautifulSoup(response.text, 'html.parser')
        topics_cards = soup.find_all('div', class_='card card-body border text-center')

        topics = []
        for card in topics_cards:
            h5_tag = card.find('h5')
            if h5_tag:
                topics.append(h5_tag.get_text(strip=True))

        return topics or self.DEFAULT_TOPICS 
    

    def get_questions(self, topic: str = "uncategorized", limit: int = 10, difficulty: str = 'Easy') -> dict:
        url = f'https://quizapi.io/api/v1/questions?apiKey={API_KEY}&category={topic}&limit={limit}&difficulty={difficulty}&single_answer_only=true'
       
        response = requests.get(url)

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except requests.RequestException:
            return {"error": "HTTP Error or network issue"}
        
        questions_data = response.json()

        if not questions_data:
            return {"error": "No questions"}

        questions = [] # Question List

        # list of tuples (questions, answers_list, correct_answer, explanation)
        for item in questions_data:
            desc = item.get("description", "")
            question_text = f"{item['question']}"
            answers_list = {k:v for k, v in item.get("answers", {}).items() if v is not None}
            explanation = item.get("explanation", "")

            correct_answer = None  # initialize before using
            for key, value in item.get("correct_answers", {}).items():
                if str(value).lower() == "true":
                    correct_answer = answers_list.get(key.replace("_correct", ""))
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

        if not questions:
            return {"error": "No valid questions found"}


        return {"questions": questions}
