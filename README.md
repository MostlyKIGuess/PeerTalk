# PeerTalk

## Video Demo

[![Demo Video](https://img.youtube.com/vi/2nsq_EA75ZY/0.jpg)](https://www.youtube.com/watch?v=2nsq_EA75ZY)


PeerTalk is an AI-powered mental health support platform designed to assist users in managing their mental health concerns. The platform leverages advanced natural language processing models to provide empathetic and informative guidance.

## Features

- **Emotion and Sentiment Analysis**: Interpret the sentiment or emotional polarity of user inputs.
- **Named Entity Recognition (NER)**: Identify phrases related to mental health concerns.
- **Mental Health Classification**: Map user concerns to predefined mental health categories and assess severity.
- **Conversational Assistant**: Generate follow-up questions based on user responses.
- **Persona Management**: Update user personas based on conversation history.
- **Personalized Recommendations**: Provide actionable recommendations for coping strategies and mental health resources.

## Getting Started

### Backend

1. **Navigate to the backend directory**:
    ```sh
    cd backend
    ```

2. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Run the server**:
    ```sh
    uvicorn server:app --reload
    ```

### Frontend

1. **Navigate to the frontend directory**:
    ```sh
    cd frontend
    ```

2. **Install dependencies**:
    ```sh
    npm install
    ```

3. **Run the development server**:
    ```sh
    npm run dev
    ```

4. **Open your browser**:
    Visit [http://localhost:3000](http://localhost:3000) to see the result.



## Templates

The backend uses various templates for different functionalities:

- **Polarity Template**: [prompt_template.py](backend/prompt_template.py)
- **Keywords Template**: [prompt_template.py](backend/prompt_template.py)
- **Category Template**: [prompt_template.py](backend/prompt_template.py)
- **Next Question Template**: [prompt_template.py](backend/prompt_template.py)
- **Persona Template**: [prompt_template.py](backend/prompt_template.py)
- **Timeshift Persona Template**: [prompt_template.py](backend/prompt_template.py)
- **Recommendation Template**: [prompt_template.py](backend/prompt_template.py)


## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.
