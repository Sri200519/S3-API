from flask import Flask, jsonify, request, send_file
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import io

app = Flask(__name__)

# AWS S3 configuration
s3_bucket_name = 'beacon-database'
region_name = 'us-east-1'  # Replace with your bucket's region

# Initialize the S3 client
s3 = boto3.client('s3', region_name=region_name)

@app.route('/list-files', methods=['GET'])
def list_files():
    try:
        # List objects in the S3 bucket
        response = s3.list_objects_v2(Bucket=s3_bucket_name)
        files = [obj['Key'] for obj in response.get('Contents', [])]
        return jsonify({'files': files})
    except NoCredentialsError:
        return jsonify({'error': 'Credentials not available'}), 401
    except PartialCredentialsError:
        return jsonify({'error': 'Incomplete credentials provided'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-file/<filename>', methods=['GET'])
def get_file(filename):
    try:
        # Get the object from S3
        obj = s3.get_object(Bucket=s3_bucket_name, Key=filename)
        # Use io.BytesIO to read the file into memory
        file_stream = io.BytesIO(obj['Body'].read())
        # Send the file as an attachment
        return send_file(file_stream, as_attachment=True, download_name=filename)
    except s3.exceptions.NoSuchKey:
        return jsonify({'error': 'File not found'}), 404
    except NoCredentialsError:
        return jsonify({'error': 'Credentials not available'}), 401
    except PartialCredentialsError:
        return jsonify({'error': 'Incomplete credentials provided'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)