from flask import Flask, render_template_string, request, redirect, url_for
import boto3
import os
import uuid

app = Flask(__name__)

# DynamoDB setup
dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv("AWS_REGION", "eu-central-1")
)
table = dynamodb.Table(os.getenv("BLOG_TABLE", "BlogPosts"))

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>My Blog</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f9f9f9;
            margin: 0;
            padding: 0;
        }

        nav {
            background: #333;
            padding: 10px;
        }

        nav a {
            color: white;
            margin-right: 15px;
            text-decoration: none;
        }

        nav a:hover {
            text-decoration: underline;
        }

        .container {
            max-width: 600px;
            margin: 20px auto;
            padding: 20px;
            background: #fff;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }

        .card {
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 6px;
            background: #fafafa;
            margin-bottom: 20px;  /* space after each card */
            border-bottom: 1px solid #ccc; /* thin gray line */
        }

        .container .card:last-child {
            margin-bottom: 0px;
        }

        .card h2 {
            margin-bottom: 8px;
            border-bottom: 1px solid #ccc; /* thin gray line */
            padding-bottom: 4px;
        }

        .card p {
            white-space: pre-wrap; /* preserves line breaks */
            border-bottom: 1px solid #ccc; /* thin gray line */
            padding-bottom: 18px; /* extra space after content */
            margin-bottom: 5px;  /* optional: space before next element */
        }


        .card .card-actions {
            margin-top: 10px;
            display: flex;
            gap: 10px;
        }

        .form-small input[type="text"],
        .form-small textarea {
            width: 100%;          
            box-sizing: border-box;
            margin-bottom: 15px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 6px;
            font-size: 14px;
            resize: none;
        }

        .form-small button,
        .delete-btn,
        .edit-btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 8px 14px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            flex: 1;
            text-align: center;
            transition: background 0.2s ease-in-out;
        }

        .form-small button:hover,
        .edit-btn:hover,
        .delete-btn:hover {
            background: #0056b3;
        }

        .delete-btn {
            background: #dc3545;
        }

        .delete-btn:hover {
            background: #a71d2a;
        }

        @media (max-width: 600px) {
            .card {
                padding: 10px;
            }
            .card .card-actions {
                flex-direction: column;
            }
            .edit-btn, .delete-btn {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <nav>
        <a href="{{ url_for('index') }}">Home</a>
        <a href="{{ url_for('new_post') }}">New Post</a>
    </nav>

    <div class="container">
        {% if posts %}
            {% for post in posts %}
                <div class="card">
                    <h2>{{ post['title'] }}</h2>
                    <p>{{ post['content'] }}</p>
                    <div class="card-actions">
                        <!-- Delete Button with confirmation -->
                        <form action="{{ url_for('delete_post', post_id=post['id']) }}" method="POST" onsubmit="return confirm('Are you sure you want to delete this post?');">
                            <button type="submit" class="delete-btn">Delete</button> 
                        </form>

                        <!-- Edit Button -->
                        <a href="{{ url_for('edit_post', post_id=post['id']) }}">
                            <button type="button" class="edit-btn">Edit</button>
                        </a>
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <p>No posts yet!</p>
        {% endif %}
    </div>

    {% if form %}
        <div class="container">
            <form method="post" action="{{ form_action }}" class="form-small">
                <h2>{{ 'Edit Post' if edit else 'Add New Post' }}</h2>
                <input type="text" name="title" placeholder="Title" value="{{ post.get('title', '') }}" required>
                <textarea name="content" placeholder="Write your post here..." rows="5" required>{{ post.get('content', '') }}</textarea>
                <button type="submit">{{ 'Update' if edit else 'Publish' }}</button>
            </form>
        </div>
    {% endif %}
</body>
</html>
"""

@app.route("/")
def index():
    response = table.scan()
    posts = response.get("Items", [])
    posts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return render_template_string(HTML_TEMPLATE, posts=posts, form=False)

@app.route("/new", methods=["GET", "POST"])
def new_post():
    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()
        table.put_item(
            Item={
                "id": str(uuid.uuid4()),
                "title": title,
                "content": content,
                "created_at": str(uuid.uuid1())
            }
        )
        return redirect(url_for("index"))

    return render_template_string(
        HTML_TEMPLATE,
        posts=None,
        form=True,
        edit=False,
        post={},
        form_action=url_for("new_post")
    )

@app.route("/edit/<post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        if title and content:
            table.put_item(
                Item={
                    "id": post_id,
                    "title": title,
                    "content": content,
                    "created_at": str(uuid.uuid1())
                }
            )
        return redirect(url_for("index"))

    response = table.get_item(Key={"id": post_id})
    post = response.get("Item", {})
    return render_template_string(
        HTML_TEMPLATE,
        posts=None,
        form=True,
        edit=True,
        post=post,
        form_action=url_for("edit_post", post_id=post_id)
    )

@app.route("/delete/<post_id>", methods=["POST"])
def delete_post(post_id):
    table.delete_item(Key={"id": post_id})
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)