import subprocess
from flask import Flask
from flask import request
app = Flask(__name__)

ssh = '/usr/bin/ssh'
key = '/home/fido/.ssh/deploy_yt'
sshdest = 'yt_analysis@dickenson.dreamhost.com'

@app.route('/', methods=['GET', 'POST'])
def deploy():   
    if request.method == 'POST':
        print(subprocess.check_output('%s -i %s %s' % (ssh, key, sshdest),
                                      shell=True))
        return 'OK'
    else:
        return "Nothing interesting here"
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
