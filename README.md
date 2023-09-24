# GPT Nurse

This application processes a medical report in PDF format and uses the GPT-4 engine to answer a series of questions based on the report.

## Dependencies

The application relies on the following Python libraries:

- pdfminer
- openai
- pandas
- json
- os
- re

Additionally, Docker needs to be installed on your machine to build and run the application inside a Docker container.

## Classes

### gptNurse

This class performs the following:

1. Initializes the GPT model and processes the provided medical report.
2. Extracts text from the PDF report along with its font details.
3. Converts the extracted PDF content to a dictionary format.
4. Initializes the GPT model with API credentials.
5. Uses the GPT model to answer a given question based on the report.

## Methods

### extract_text_with_font

Extracts text characters from a PDF along with their font name and size.

### pdf2dict

Processes the extracted text and groups it into sections based on identified header fonts. This results in a dictionary where each section of the PDF is represented as a key-value pair.

### initGPT

Initializes the GPT model using API credentials from a provided JSON configuration.

### answer_question

Uses the GPT model to answer a given question based on the medical report. The question is provided in a predefined JSON format.

## How to Use

1. Ensure you have Docker installed on your machine.
2. Place your medical report in the root directory and name it `medical-record.pdf`.
3. Place the `task.json` configuration in the root directory.
4. List your questions in `questions.txt`, placing each question on a new line.

### Docker Commands

To build and run the Docker image:

```bash
docker build -t gpt-nurse .
docker run gpt-nurse
