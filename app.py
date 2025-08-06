from flask import Flask, request, jsonify, render_template, redirect, url_for
import instaloader
import os
from urllib.parse import urlparse, parse_qs
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'downloads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def extract_shortcode(reel_url):
    """Extract shortcode from Instagram Reel URL"""
    parsed = urlparse(reel_url)
    if parsed.netloc == 'www.instagram.com' or parsed.netloc == 'instagram.com':
        path = parsed.path.strip('/')
        if path.startswith('reel/'):
            return path.split('/')[1]
        elif path.startswith('p/'):
            return path.split('/')[1]
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        reel_url = request.form.get('reel_url')
        if not reel_url:
            return render_template('index.html', error="Please enter a valid Instagram Reel URL")
        
        try:
            L = instaloader.Instaloader()
            shortcode = extract_shortcode(reel_url)
            
            if not shortcode:
                return render_template('index.html', error="Invalid Instagram Reel URL")
            
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            if not post.is_video:
                return render_template('index.html', error="The URL doesn't point to a video Reel")
            
            # Download the reel
            filename = f"reel_{shortcode}"
            L.download_post(post, target=os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Find the downloaded file
            for file in os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                if file.endswith('.mp4'):
                    return render_template('index.html', 
                                        success=f"Reel downloaded successfully!",
                                        video_url=url_for('static', filename=f'downloads/{filename}/{file}'))
            
            return render_template('index.html', error="Failed to download the Reel")
        
        except Exception as e:
            return render_template('index.html', error=f"Error: {str(e)}")
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
