from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
import re
import openai
import json
import pandas as pd
import os

class gptNurse():
    def __init__(self, 
                 task_json_path,
                 file_path,
                 header_fonts = None,
                 gpt_engine = None):
        self.report = None
        self.file_path = file_path
        self.gpt_engine = gpt_engine or 'gpt-4'
        self.json = None
        self.header_fonts = header_fonts or [('AAAAAI+Calibri', 18.0)]
        self.initGPT(task_json_path)
        self.pdf2dict()
        
        
    def extract_text_with_font(self):
        file_path = self.file_path
        for page_layout in extract_pages(file_path):
            for element in page_layout:
                try:
                    if isinstance(element, LTTextContainer):
                        for text_line in element:
                            for char in text_line:
                                if isinstance(char, LTChar):
                                    yield char.get_text(), char.fontname, char.size
                except:
                    continue
                    
    def pdf2dict(self,header_fonts = None,return_dict = False):
        sections = {}
        current_section = []
        header_fonts = header_fonts or self.header_fonts # Adjust based on the actual fonts you identify
        current_header = []
        
        # Regular expression to match punctuation between letters (deal with ti ligature - no unicode pointer)
        pattern = r'(?<=[a-zA-Z])[^a-zA-Z0-9’\s](?=[a-zA-Z])'
        font_contents = list(self.extract_text_with_font())

        for char, font, size in font_contents:
            if (font,size) in header_fonts:
                if current_section:
                    section_name = "".join(current_header)
                    content = "".join(current_section)

                    section_name = re.sub(pattern, 'ti', section_name)
                    section_name = str.strip(re.sub(r'[^\w\s]', '', section_name))
                    content = re.sub(pattern, 'ti', content)
                    content = str.strip(str.replace(content,'\t',' '))

                    sections[section_name] = content
                    current_section = []
                    current_header = []
                current_header.append(char)
            else:
                current_section.append(char)

        if current_section:  # Appending the last section
            section_name = "".join(current_header)
            content = "".join(current_section)

            section_name = re.sub(pattern, 'ti', section_name)
            section_name = str.strip(re.sub(r'[^\w\s]', '', section_name))
            content = re.sub(pattern, 'ti', content)
            content = str.strip(str.replace(content,'\t',' '))

            sections[section_name] = content
        self.report = f'{sections}'
        if return_dict:
            return sections
    
    def initGPT(self,task_json_path, model = None):
        with open(task_json_path, 'r') as f:
            self.json = json.load(f)[0]
        self.api_key = self.json['api_key']['api_key']
        openai.api_key = self.api_key
        return

    
    def answer_question(self,question):
        input_categories = ["Task Description","Medical Report","Input Questions and Task Requirement"]
        ques = [
            input_categories[0] + ': ' + self.json["Input"][input_categories[0]],
            input_categories[1] + ': ' + self.json["Input"][input_categories[1]].format(self.report),
            input_categories[2] + ': ' + self.json["Input"][input_categories[2]].format(question),
        ]
        
        questions=[{"role": "system", "content": q} for q in ques]
        text_variations = openai.ChatCompletion.create(
            model="gpt-4",
            messages = questions)
        return text_variations['choices'][0]['message']['content']

def main():
    assert os.path.isfile("task.json"), "No 'task.json' file present in the root directory ./"
    assert os.path.isfile("medical-record.pdf"), "No 'medical-record.pdf' file present in the root directory ./"
    assert os.path.isfile("questions.txt"), "No 'questions.txt' file present in the root directory ./"
    
    with open("./questions.txt") as file:
        questions = [line.rstrip() for line in file]

    model = gptNurse("./task.json",
                    "./medical-record.pdf")
    print('Inputs processed successfully, prompting chatGPT now...')


    ans = model.answer_question(questions)

    try:
    	output_df = pd.DataFrame.from_dict(json.loads(ans))
    	output_df.to_csv('./question_answers.csv')
    	print('Run successful, output dumped to ./question_answers.csv')
    except:
    	with open("./question_answers.txt", "w") as text_file:
    		text_file.write(ans)
    	print('Run successful, output dumped to ./question_answers.txt')


    
if __name__ == "__main__":
    main()