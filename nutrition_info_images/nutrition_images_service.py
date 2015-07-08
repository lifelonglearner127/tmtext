from flask import Flask, request, jsonify, render_template
from classify_text_images import classifier_predict_one, load_classifier
app = Flask(__name__)

image_classifier = load_classifier()

@app.route('/results', methods=['GET'])
def results():
    # example request: 
    # http://127.0.0.1:5000/is_nutrition_image?image=http://i5.walmartimages.com/dfw/dce07b8c-bf9c/k2-_f6770975-97a9-474c-a3c8-8edc3a4a14e1.v1.jpg&image=http://i5.walmartimages.com/dfw/dce07b8c-9417/k2-_6275bca7-da12-4925-9afd-048eea86da73.v1.jpg
    request_arguments = dict(request.args)
    image_urls = request_arguments['image'][0].split()
    return render_template('results_template.html', \
        results={image : True if classifier_predict_one(image, image_classifier)==1 else False for image in image_urls})

@app.route('/nutrition_image_UI', methods=['GET'])
def nutrition_image_UI():
    return render_template('input_template.html')

@app.route('/nutrition_image', methods=['GET'])
def is_nutrition_image():
    pass

if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)
