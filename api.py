# ps -fA | grep python
from flask import Flask, jsonify, request, abort, send_from_directory
from werkzeug.utils import secure_filename
import xml.etree.ElementTree as ET
import csv
import json
import os

ALLOWED_EXTENSIONS = set(['xml'])
Upload_Folder = "/home/junaid/Desktop/api_uploaded_files"
To_csv_Folder = "/home/junaid/Desktop/api_uploaded_files_csv"
To_json_Folder = "/home/junaid/Desktop/api_uploaded_files_json"


def analyser(sub):
    d = []
    count = 0
    if sub.text == None:
        return ' '
    else:
        for x in sub.iter():
            count = count + 1
            d.append(str(x.text))
        if count == 1:
            return ''.join(d)
        else:
            #removed_spaces = [i.strip() for i in d ]
            del d[0]
            rt = ' '.join(d)
            return rt

def file_names():
  fpath = os.getcwd()
  files = os.listdir(fpath)
  files.remove('api.py')
  files.remove('merged.json')
  files.remove('new.py')
  files.remove('.git')
  return files

# Allowed Extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Returns Dictionary
def json_data(name):
   with open(name,'r') as h:
    #json_string = h.read()
    jdata = json.loads(h.read())
    return jdata



# Simple Flask APP
app = Flask(__name__)


#Showing Files in Current Working Directory
@app.route('/home',methods = ['GET'])
def show_files():
  files = file_names()
  return jsonify(files)  



#Finding Cui Number for Specified Diseases
@app.route('/<disease>',methods=['GET'])
def find_value(disease):
  jdata = json_data('merged.json')
  for key in jdata:
    if key == disease:
      return jsonify (jdata[key]['cui'])

#Merging Exitting JSON files in Current Directory
@app.route('/content', methods = ['GET'])
def add_data():
  jdata = json_data('merged.json')
  """data = request.get_json()
  new_data = {
             'key': data['key']
  }
  jdata['key'] = data['key']
  return jsonify(new_data)"""
  return jsonify(jdata)
  
    
# Merge all json files in Current Working Directory  
@app.route('/merge',methods = ['GET'])
def show_content():
  files = file_names()
  data1 = {}
  for name in files:
    jdata = json_data(name)
    #fpath = os.path.join(os.getcwd(),name)
    for key in jdata:
      #json.load() json file to object.
      #json.loads() str to object.
      data1[key] = jdata[key]
  with open('merged.json','a+') as f1:
    json.dump(data1,f1,indent=6)
  return jsonify('Successfully Merged Files')


#Uploading Single or Multiple XML Files.
@app.route('/upload', methods = ['POST'])
def post_file():
  if request.method == 'POST':
    non_allowed = []
    #file = request.files['file']
    files = request.files.getlist('file') 
    
  #filename = secure_filename(file.filename)
  #file.save(os.path.join(Upload_Folder, filename))
    for file in files:
      if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(Upload_Folder, filename))
      else:
        non_allowed.append(file.filename)
    if len(non_allowed)>0:
      return ({'Followinig Files Not Uploaded':non_allowed})
    else:
      return jsonify('Files Uploaded Successfully')

#Converting Uploaded XML files into CSV format.
@app.route('/tocsv',methods = ['GET'])
def tocsv():
  files = os.listdir(Upload_Folder)
  for file in files:
    tree = ET.parse(os.path.join(Upload_Folder,file))
    root = tree.getroot()
    new_filename = file.rstrip('.xml')
    xml_data = open(os.path.join(To_csv_Folder,new_filename+'.csv'), 'w')
    csvwriter = csv.writer(xml_data)
    file_headers = [x.tag for x in root[1]]
    csvwriter.writerow(file_headers)
    for child in root:
      data = []
      for sub_child in child:
        dt = analyser(sub_child)
        data.append(dt)
      csvwriter.writerow(data)
    xml_data.close()
  return jsonify('Uploaded File Converted to CSV Successfully')

#Converting CSV to Json format
@app.route('/tojson',methods = ['GET'])
def tojson():
  files = os.listdir(To_csv_Folder)
  for filename in files:
    with open(os.path.join(To_csv_Folder, filename), 'r') as f1:
       l1 = {}
       l2 = {}
       data = {}
       first_key = ''
       r1 = csv.DictReader(f1)
       
       count = 0
       for r2 in r1:
           data[r2['condition']] = {"cui":r2['condition_cui'],
                                    "have_had":{},
                                    "looking_for":{}
                                    }
           first_key = str(r2['condition'])
           count += 1
           if (count == 2):
               break
       with open(os.path.join(To_csv_Folder, filename), 'r') as f2:
           reader = csv.DictReader(f2)
           for row in reader:
               if(row['label_bucket'] == 'have_had'):
                   l1[str(row['label'])]={
                        "cui":str(row['label_cui']),
                        "score":str(row['label_score']) ,
                        "label_semantic_types":str(row['label_semantic_types']) ,
                        "label_ncts_counts": str(row['label_ncts_count']),
                        "ncts": str(row['label_ncts'])
                }
               else:
                    l2[str(row['label'])]={
                        "cui":str(row['label_cui']),
                        "score":str(row['label_score']) ,
                        "label_semantic_types":str(row['label_semantic_types']) ,
                        "label_ncts_counts": str(row['label_ncts_count']),
                        "ncts": str(row['label_ncts'])
                                           }
       data[first_key]['have_had'] = l1
       data[first_key]['looking_for'] = l2
       new_filename = filename.rstrip('.csv')
       with open(os.path.join(To_json_Folder,new_filename+'.json'),'w') as f2:
           f2.write(json.dumps(data,indent=4))
  return jsonify("Uploaded File Converted to JSON Successfully")



if __name__=='__main__':
  app.run(debug=True)
