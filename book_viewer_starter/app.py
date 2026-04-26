from flask import Flask, render_template, g, redirect, request

app = Flask(__name__)

@app.before_request
def load_contents():
    with open("book_viewer/data/toc.txt", "r") as file:
        g.contents = file.readlines()

def chapters_matching(query):
    if not query:
        return []

    results = []
    for idx, name in enumerate(g.contents, start=1):
        with open(f"book_viewer/data/chp{idx}.txt", "r") as file:
            chapter_content = file.read()

        matches = {}
        for para_idx, paragraph in enumerate(chapter_content.split('\n\n'), start=1):
            if query.lower() in paragraph.lower():
                matches[para_idx] = paragraph
        if matches:
            results.append({'number': idx, 'name': name, 'paragraphs': matches})

    return results

@app.route("/search")
def search():
    query = request.args.get('query', '')
    results = chapters_matching(query)
    return render_template('search.html',
                           query=query,
                           results=results)


@app.route("/")
def index():
    return render_template("home.html", contents=g.contents)

@app.route("/chapters/<page_num>")
def chapter(page_num):

    with open(f"book_viewer/data/chp{page_num}.txt", "r") as file:
        chapter = file.read()

    chapter_name = g.contents[int(page_num) - 1]
    chapter_title = f"Chapter {page_num}: {chapter_name}"

    return render_template("chapter.html",
                           chapter=chapter,
                           contents=g.contents,
                           chapter_title=chapter_title)

@app.template_filter('in_paragraphs')
def in_paragraphs(text):
    paragraphs = text.split('\n\n')
    formatted_paragraphs = [
        f'<p>{paragraph}</p>'
        for paragraph in paragraphs
        if paragraph
    ]
    return ''.join(formatted_paragraphs)

@app.template_filter('bold')
def bold(text, query):
    return text.replace(query, f'<strong>{query}</strong>')

@app.errorhandler(404)
def page_not_found(_error):
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, port=5003)