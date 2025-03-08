from flask import Flask, render_template, request
import pickle
import numpy as np

# Load the required data
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_ratings'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['post'])
def recommend():
    user_input = request.form.get('user_input')
    
    # Check if user provided any input
    if not user_input:
        return render_template('recommend.html', error="Please enter a book name.")

    # Clean the user input by trimming whitespace
    user_input = user_input.strip()
    
    # Check if the cleaned user input exists in the pivot table index
    if user_input not in pt.index:
        # Try to find a partial match if exact match fails
        potential_matches = [title for title in pt.index if user_input.lower() in title.lower()]
        
        if potential_matches:
            # Provide suggestions if we find partial matches
            suggestions_html = ", ".join([f"<strong>{match}</strong>" for match in potential_matches[:5]])
            return render_template('recommend.html', 
                                  error=f"Book not found. Did you mean one of these? {suggestions_html}",
                                  safe_error=True)
        else:
            return render_template('recommend.html', error="Book not found. Please enter a valid book name.")

    # Get the index
    index = np.where(pt.index == user_input)[0][0]
    
    # Get similar items
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)

    print(data)

    return render_template('recommend.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)