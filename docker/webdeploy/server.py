import subprocess
from flask import Flask
from flask import request
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def deploy():   
    if request.method == 'POST':
        print(subprocess.check_output('/usr/bin/ssh -i /home/fido/.ssh/deploy_yt yt_analysis@dickenson.dreamhost.com'))
        return 'OK'
    else:
        return "Nothing interesting here"
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
