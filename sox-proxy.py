from flask import Flask, request, Response
import json
import requests
import base64
import os
import tempfile
import shutil

api = Flask(__name__)

@api.route('/ping', methods=['GET'])
def ping():
    return json.dumps( 'pong' )

@api.route('/', methods=['GET', 'POST'])
def get():
    speechoid_url = request.values.get('speechoidUrl', os.getenv('SPEECHOID_URL', 'http://wikispeech-server:10001/'))
    params = dict(request.values)
    print('Incoming request with parameters ' + json.dumps(params))
    params.pop('speechoidUrl', None)
    response = requests.get(url = speechoid_url, params = params)
    data = json.loads(response.text)
    data['audio_data'] = post_process_audio(data['audio_data'], [
        # Compressor with low threshold, low attack, high ratio to normalize all audio, including potential click.
        'compand 0.02,0.20 5:-60,-40,-10 -5 -90 0.1',
        # 50 ms long logarithmic fade-in to remove potential click.
        'fade 0.05'
    ])
    return Response(response=json.dumps(data), content_type='application/json', status=200)


def post_process_audio(input_base64_opus_audio, command_chain):
    # create temporary directory
    tempdir = tempfile.mkdtemp()
    try:
        # Decode base64 and save as file input.opus
        opus_audio = base64.b64decode(input_base64_opus_audio)
        write_file(tempdir, 'input.opus', opus_audio)
        # Convert to WAV as SOX does not handle ogg/opus encoded data.
        convert_opus_to_wav(tempdir, 'input.opus', 'input.wav')

        chain_input_file = 'input.wav'
        for num, command in enumerate(command_chain, start=1):
            output_file = 'sox_chain_' + str( num ) + '.wav'
            sox(tempdir, chain_input_file, output_file, command)
            chain_input_file = output_file

        # Convert back to ogg/opus.
        convert_wav_to_opus(tempdir, chain_input_file, 'output.opus')

        # Read processed output.opus, encode with base64 and use in json response.
        processed_opus_audio = read_file(tempdir, 'output.opus')
        base64_encoded_processed_opus_audio = base64.b64encode(processed_opus_audio)
        return base64_encoded_processed_opus_audio.decode('ascii')
    finally:
        # delete temporary directory
        shutil.rmtree(tempdir)

def convert_opus_to_wav(directory, input_filename, output_filename):
    input_path = os.path.join(directory, input_filename)
    output_path = os.path.join(directory, output_filename)
    os.system('opusdec --force-wav %s %s' % (input_path, output_path))

def sox(directory, input_filename, output_filename, sox_parameters):
    input_path = os.path.join(directory, input_filename)
    output_path = os.path.join(directory, output_filename)
    os.system('sox %s %s %s' % (input_path, output_path, sox_parameters))

def convert_wav_to_opus(directory, input_filename, output_filename):
    input_path = os.path.join(directory, input_filename)
    output_path = os.path.join(directory, output_filename)
    os.system('opusenc %s %s' % (input_path, output_path))

def write_file(directory, filename, data):
    filepath = os.path.join(directory, filename)
    with open(filepath, 'wb') as file:
        file.write(data)

def read_file(directory, filename):
    filepath = os.path.join(directory, filename)
    with open(filepath, 'rb') as file:
        return file.read()

if __name__ == '__main__':
    api.run(host='0.0.0.0')
