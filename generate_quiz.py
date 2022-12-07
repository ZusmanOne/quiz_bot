
def create_quiz():
    with open('quiz.txt', encoding='KOI8-R') as file:
        quiz = file.read()
    split_quiz = quiz.split('\n\n')
    answer_question = {}
    for phrase in split_quiz:
        if 'Вопрос' in phrase:
            question = phrase.strip()
        if 'Ответ' in phrase:
            answer = phrase.strip()
            answer_question[question] = answer
    return answer_question