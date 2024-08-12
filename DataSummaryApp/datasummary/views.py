from django.shortcuts import render
from django.http import HttpResponse
from .forms import UploadFileForm
import pandas as pd

from dotenv import load_dotenv
import google.generativeai as genai
import os
import markdown

load_dotenv()

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

template = '''
    Generate a summary for the following csv/excel file data. Keep it in a proper structure. 
    It must include the information like number of rows, headings, and other things. It should be in proper structure.  
    Here is the data : {data}
    '''

def get_summary_from_llm(data):
    formated_data = template.format(data=data)
    response = model.generate_content(formated_data, 
        generation_config = genai.GenerationConfig(
            max_output_tokens=1000,
            temperature=0.7,
    ))
    print(response.text)
    structured_response = markdown.markdown(response.text)
    return structured_response

def generateSummary(file):
    
    try:
        file_name = file.name
        file_extension = file_name.split('.')[-1].lower()
        
        if file_extension in ['xls', 'xlsx']:
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(file)
        
        # print(df)
        renamed_columns = {col: col.strip().replace(' ', '_') for col in df.columns}
        df.rename(columns=renamed_columns, inplace=True)
        
        llm_summary = get_summary_from_llm(df)
        
        return df.to_dict(orient='records'), llm_summary
    
    except Exception as e:
        print(e)
        return None

def uploadFile(request):
    if request.method == 'POST':
        file = UploadFileForm(request.POST, request.FILES)
        if file.is_valid():
            uploaded_file = request.FILES['file']
            # print(uploaded_file)
            data = generateSummary(uploaded_file)
            # print(data)
            
            if data is None:
                return HttpResponse("Something went wrong, try again...")
            else:
                return render(request, "file_summary.html", {'data' : data[0], 'LLM_Summarization' : data[1]})
            
            
        else:
            return HttpResponse("Please upload a csv/excel file")
    else:
        form = UploadFileForm()
    
    return render(request, "file_upload.html", {'form': form})
