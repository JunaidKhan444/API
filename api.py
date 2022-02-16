from flask import Flask, jsonify, request
import json
import os


def json_data(name):
   with open(name,'r') as h:
    #json_string = h.read()
    jdata = json.loads(h.read())
    return jdata

app = Flask(__name__)

@app.route('/')
def example():
  return 'Hello This Is Blank Page.'

@app.route('/home',methods = ['GET'])
def show_files():
  fpath = os.getcwd()
  files = os.listdir(fpath)
  files.remove('api.py')
  return jsonify(files)  




@app.route('/home/find/<name>/<have_had>/<disease>/<ncts>',methods=['GET'])
def find_value(name,have_had,disease,ncts):
  jdata = json_data(name)
  for keylist in jdata:
    for keys in jdata[keylist]:
      if keys == 'have_had':
        return jsonify(jdata[keylist][keys][disease]['ncts'])
      elif keys == 'looking_for':
        return jsonify(jdata[keylist][keys][disease]['ncts'])


@app.route('/home/add/<name>', methods = ['POST'])
def add_data(name):
  jdata = json_data(name)
  data = request.get_json()
  new_data = {
             'key': data['key']
  }
  jdata['key'] = data['key']
  return jsonify(new_data)
  

      
  
      
  
    

@app.route('/home/content/<name>',methods = ['GET'])
def show_content(name):
  fpath = os.path.join(os.getcwd(),name)
  with open(fpath,'r') as resp:
    data = resp.read()
  return eval(data)





if __name__=='__main__':
  app.run(debug=True)