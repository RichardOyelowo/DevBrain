from .extensions import db
from .learning import slugify
from .models import AnswerOption, Language, Question, QuizPreset, Topic


TOPIC_CATALOG = [
    ("Data Structures", "Arrays, maps, sets, stacks, queues, trees, and access tradeoffs."),
    ("Algorithms", "Complexity, searching, sorting, recursion, and problem-solving patterns."),
    ("Web APIs", "HTTP behavior, API contracts, status codes, caching, and pagination."),
    ("Frontend", "Browser UI, accessibility, state, rendering, and user-facing behavior."),
    ("Backend", "Server-side request handling, persistence, services, and application structure."),
    ("Databases", "Relational querying, indexing, transactions, schema design, and persistence."),
    ("React", "Components, hooks, state, rendering, and frontend application patterns."),
    ("Next.js", "React routing, rendering modes, data loading, and full-stack app structure."),
    ("Django", "Python web apps, ORM usage, views, templates, and secure defaults."),
    ("Flask", "Small Python web services, routing, request handling, and app structure."),
    ("Laravel", "PHP web apps, routing, Eloquent, queues, and framework conventions."),
    ("Express", "Node.js HTTP services, middleware, routing, and API design."),
    ("Git", "Version control workflows and repository hygiene."),
    ("Docker", "Container basics, images, and runtime behavior."),
    ("DevOps", "CI/CD, deployment safety, observability, and operational practice."),
    ("Cloud", "Hosted infrastructure, managed services, reliability, and scaling basics."),
    ("Security", "Practical application security fundamentals."),
    ("Testing", "Automated testing and confidence-building practices."),
    ("Architecture", "System design tradeoffs and service boundaries."),
    ("Performance", "Latency, throughput, caching, profiling, and practical optimization tradeoffs."),
]

LANGUAGE_CATALOG = [
    ("Python", "Readable scripting, backend services, automation, and data-heavy code."),
    ("JavaScript", "Browser and Node.js runtime behavior."),
    ("TypeScript", "Typed JavaScript for larger application codebases."),
    ("SQL", "Query language for relational databases."),
    ("PHP", "Server-rendered and framework-backed web applications."),
    ("Java", "Object-oriented backend and enterprise application development."),
    ("C#", ".NET application and backend development."),
    ("C++", "Systems programming and performance-sensitive code."),
    ("C", "Low-level programming and memory-oriented code."),
    ("Go", "Backend services, concurrency, and operational tooling."),
    ("Ruby", "Expressive web application and scripting workflows."),
    ("Rust", "Memory-safe systems programming."),
    ("Swift", "Apple platform application development."),
    ("Kotlin", "Android and JVM application development."),
    ("Shell", "Command-line automation and operational scripts."),
]

DEFAULT_PRESETS = [
    ("Data Structures", "Data Structures", "Lists, maps, sets, stacks, queues, and tradeoffs.", "EASY", 5, "", "mint", 1),
    ("DevOps", "DevOps", "Deployments, CI/CD, containers, observability, and release hygiene.", "MEDIUM", 5, "", "amber", 2),
    ("Security", "Security", "Passwords, CSRF, authorization, and practical app hardening.", "MEDIUM", 5, "", "red", 3),
    ("System Design", "Architecture", "Reliability, idempotency, service boundaries, and scale decisions.", "HARD", 5, "", "blue", 4),
]

DEPRECATED_TOPIC_SLUGS = {"python", "javascript", "sql", "http"}


SEED_DATA = [
    {
        "topic": "Data Structures",
        "description": "Arrays, maps, sets, stacks, queues, trees, and access tradeoffs.",
        "difficulty": "EASY",
        "prompt": "What does len(items) return in this Python snippet?",
        "description_text": "Assume items is a list.",
        "language": "python",
        "code_snippet": "items = [1, 2, 3]\nprint(len(items))",
        "explanation": "len(items) returns the number of elements in the list.",
        "options": [
            ("3", True),
            ("2", False),
            ("1", False),
            ("It raises an error", False),
        ],
    },
    {
        "topic": "Data Structures",
        "description": "Arrays, maps, sets, stacks, queues, trees, and access tradeoffs.",
        "difficulty": "MEDIUM",
        "prompt": "Which data structure is best for first-in, first-out processing?",
        "description_text": "Think about processing work in arrival order.",
        "explanation": "A queue is designed for FIFO behavior: items are removed in the order they were added.",
        "options": [
            ("Queue", True),
            ("Stack", False),
            ("Set", False),
            ("Hash map", False),
        ],
    },
    {
        "topic": "Algorithms",
        "description": "Complexity, searching, sorting, recursion, and problem-solving patterns.",
        "difficulty": "EASY",
        "prompt": "What does O(n) usually mean?",
        "description_text": "Choose the best complexity description.",
        "explanation": "O(n) means the work grows linearly with the input size.",
        "options": [
            ("Work grows linearly with input size", True),
            ("Work is always constant", False),
            ("Work is always impossible to measure", False),
            ("Work ignores input size", False),
        ],
    },
    {
        "topic": "Frontend",
        "description": "Browser UI, accessibility, state, rendering, and user-facing behavior.",
        "difficulty": "EASY",
        "prompt": "Why should buttons have clear accessible labels?",
        "description_text": "Think about screen readers and non-visual navigation.",
        "explanation": "Accessible labels let assistive technologies communicate the button purpose.",
        "options": [
            ("They explain the control to assistive technology", True),
            ("They make CSS load faster", False),
            ("They prevent all runtime errors", False),
            ("They replace semantic HTML", False),
        ],
    },
    {
        "topic": "DevOps",
        "description": "CI/CD, deployment safety, observability, and operational practice.",
        "difficulty": "MEDIUM",
        "prompt": "What is the main value of a CI pipeline?",
        "description_text": "Assume a team pushes code throughout the week.",
        "explanation": "CI pipelines run repeatable checks so problems are caught before or during integration.",
        "options": [
            ("Running repeatable checks on changes", True),
            ("Removing the need for tests", False),
            ("Hiding failed deployments", False),
            ("Editing production data manually", False),
        ],
    },
    {
        "topic": "React",
        "description": "Components, hooks, state, rendering, and frontend application patterns.",
        "difficulty": "EASY",
        "prompt": "What is React state mainly used for?",
        "description_text": "Choose the best frontend behavior.",
        "language": "javascript",
        "explanation": "State stores data that can change over time and cause the component UI to update.",
        "options": [
            ("Tracking data that can update the UI", True),
            ("Replacing all HTML semantics", False),
            ("Running database migrations", False),
            ("Compressing image assets", False),
        ],
    },
    {
        "topic": "Next.js",
        "description": "React routing, rendering modes, data loading, and full-stack app structure.",
        "difficulty": "MEDIUM",
        "prompt": "What problem does file-based routing in Next.js help solve?",
        "description_text": "Think about how pages or app routes are mapped.",
        "language": "javascript",
        "explanation": "File-based routing lets the framework map route files to URLs with less manual router setup.",
        "options": [
            ("Mapping route files to URLs", True),
            ("Hashing user passwords automatically", False),
            ("Replacing every database query", False),
            ("Disabling server rendering", False),
        ],
    },
    {
        "topic": "Django",
        "description": "Python web apps, ORM usage, views, templates, and secure defaults.",
        "difficulty": "EASY",
        "prompt": "What is Django's ORM mainly used for?",
        "description_text": "Choose the best description.",
        "language": "python",
        "explanation": "Django's ORM maps Python models to database tables and helps query data.",
        "options": [
            ("Working with database records through Python models", True),
            ("Styling buttons in the browser", False),
            ("Bundling React components", False),
            ("Creating Git commits", False),
        ],
    },
    {
        "topic": "Flask",
        "description": "Small Python web services, routing, request handling, and app structure.",
        "difficulty": "EASY",
        "prompt": "What does a Flask route connect?",
        "description_text": "Think about request handling.",
        "language": "python",
        "explanation": "A Flask route connects a URL rule and HTTP methods to a Python view function.",
        "options": [
            ("A URL rule to a view function", True),
            ("A CSS variable to a database index", False),
            ("A Git branch to production", False),
            ("An image file to a password hash", False),
        ],
    },
    {
        "topic": "Laravel",
        "description": "PHP web apps, routing, Eloquent, queues, and framework conventions.",
        "difficulty": "MEDIUM",
        "prompt": "What is Eloquent in Laravel?",
        "description_text": "Choose the framework feature.",
        "language": "php",
        "explanation": "Eloquent is Laravel's ORM for working with database records through model classes.",
        "options": [
            ("Laravel's ORM", True),
            ("A JavaScript bundler", False),
            ("A CSS reset", False),
            ("A Docker image registry", False),
        ],
    },
    {
        "topic": "Express",
        "description": "Node.js HTTP services, middleware, routing, and API design.",
        "difficulty": "MEDIUM",
        "prompt": "What is Express middleware commonly used for?",
        "description_text": "Think about code that runs during request handling.",
        "language": "javascript",
        "explanation": "Middleware can inspect, modify, or stop a request before it reaches the final route handler.",
        "options": [
            ("Running logic during the request pipeline", True),
            ("Compiling Python bytecode", False),
            ("Creating SQL indexes automatically", False),
            ("Rendering CSS in the database", False),
        ],
    },
    {
        "topic": "Cloud",
        "description": "Hosted infrastructure, managed services, reliability, and scaling basics.",
        "difficulty": "MEDIUM",
        "prompt": "Why use managed Postgres for an early production app?",
        "description_text": "Consider operations and reliability.",
        "explanation": "Managed databases reduce operational burden by handling hosting, backups, and maintenance concerns.",
        "options": [
            ("It reduces database operations work", True),
            ("It removes the need for schema design", False),
            ("It guarantees every query is free", False),
            ("It replaces application tests", False),
        ],
    },
    {
        "topic": "Data Structures",
        "description": "Arrays, maps, sets, stacks, queues, trees, and access tradeoffs.",
        "difficulty": "EASY",
        "prompt": "What does a Python dictionary optimize for in normal usage?",
        "description_text": "Choose the most accurate description.",
        "explanation": "Dictionaries are hash tables designed for average-case constant-time key lookup.",
        "options": [
            ("Fast lookup by key", True),
            ("Maintaining sorted values", False),
            ("Storing duplicate keys", False),
            ("Avoiding memory allocation", False),
        ],
    },
    {
        "topic": "Data Structures",
        "description": "Arrays, maps, sets, stacks, queues, trees, and access tradeoffs.",
        "difficulty": "MEDIUM",
        "prompt": "What is the output of this code?",
        "description_text": "Read the snippet before answering.",
        "language": "python",
        "code_snippet": "items = []\nfor i in range(3):\n    items.append(lambda: i)\nprint([fn() for fn in items])",
        "explanation": "The lambdas close over the same loop variable, so they all read the final value.",
        "options": [
            ("[2, 2, 2]", True),
            ("[0, 1, 2]", False),
            ("[1, 2, 3]", False),
            ("A TypeError", False),
        ],
    },
    {
        "topic": "Databases",
        "description": "Relational querying, indexing, transactions, schema design, and persistence.",
        "language": "sql",
        "difficulty": "EASY",
        "prompt": "Which SQL clause filters grouped aggregate results?",
        "description_text": "Think about filtering after GROUP BY has been applied.",
        "explanation": "HAVING filters aggregate groups; WHERE filters rows before grouping.",
        "options": [
            ("HAVING", True),
            ("WHERE", False),
            ("ORDER BY", False),
            ("LIMIT", False),
        ],
    },
    {
        "topic": "Web APIs",
        "description": "HTTP behavior, API contracts, status codes, caching, and pagination.",
        "difficulty": "MEDIUM",
        "prompt": "Which status code best fits a valid request that fails authorization?",
        "description_text": "The user is authenticated but does not have permission.",
        "explanation": "403 Forbidden indicates the server understood the request but refuses authorization.",
        "options": [
            ("403", True),
            ("400", False),
            ("404", False),
            ("500", False),
        ],
    },
    {
        "topic": "Frontend",
        "description": "Browser UI, accessibility, state, rendering, and user-facing behavior.",
        "language": "javascript",
        "difficulty": "EASY",
        "prompt": "Which method returns a new array after applying a function to every item?",
        "description_text": "Choose the Array method that transforms values.",
        "explanation": "Array.prototype.map returns a new array with each result from the callback.",
        "options": [
            ("map", True),
            ("forEach", False),
            ("push", False),
            ("splice", False),
        ],
    },
    {
        "topic": "Architecture",
        "description": "System design tradeoffs and service boundaries.",
        "difficulty": "HARD",
        "prompt": "What is the main value of idempotency keys in payment APIs?",
        "description_text": "Assume a client may retry after a network timeout.",
        "explanation": "Idempotency keys let the server safely recognize retried requests and avoid duplicate side effects.",
        "options": [
            ("Preventing duplicate charges during retries", True),
            ("Encrypting payment details", False),
            ("Reducing database indexes", False),
            ("Replacing authentication", False),
        ],
    },
    {
        "topic": "Data Structures",
        "description": "Arrays, maps, sets, stacks, queues, trees, and access tradeoffs.",
        "difficulty": "EASY",
        "prompt": "Which Python structure should you use for a unique collection with fast membership checks?",
        "description_text": "Choose the built-in type that matches the access pattern.",
        "explanation": "A set stores unique values and supports average-case constant-time membership checks.",
        "options": [("set", True), ("list", False), ("tuple", False), ("str", False)],
    },
    {
        "topic": "Backend",
        "description": "Server-side request handling, persistence, services, and application structure.",
        "language": "python",
        "difficulty": "HARD",
        "prompt": "Why can mutable default arguments cause bugs in Python functions?",
        "description_text": "Think about when default values are created.",
        "explanation": "Default arguments are evaluated once when the function is defined, so a mutable object can be shared across calls.",
        "options": [
            ("The same object can be reused across calls", True),
            ("They make function calls asynchronous", False),
            ("They disable keyword arguments", False),
            ("They always raise SyntaxError", False),
        ],
    },
    {
        "topic": "Frontend",
        "description": "Browser UI, accessibility, state, rendering, and user-facing behavior.",
        "language": "javascript",
        "difficulty": "MEDIUM",
        "prompt": "What does Promise.all do when one input promise rejects?",
        "description_text": "Assume several promises are running at the same time.",
        "explanation": "Promise.all rejects as soon as any input promise rejects, using that rejection reason.",
        "options": [
            ("Rejects with that reason", True),
            ("Waits and returns only fulfilled values", False),
            ("Retries the rejected promise", False),
            ("Converts the rejection to null", False),
        ],
    },
    {
        "topic": "Frontend",
        "description": "Browser UI, accessibility, state, rendering, and user-facing behavior.",
        "difficulty": "HARD",
        "prompt": "What is the output of this JavaScript snippet?",
        "description_text": "Read the closure behavior carefully.",
        "language": "javascript",
        "code_snippet": "const fns = [];\nfor (var i = 0; i < 3; i++) {\n  fns.push(() => i);\n}\nconsole.log(fns.map(fn => fn()));",
        "explanation": "var is function-scoped, so every closure reads the final value of i.",
        "options": [("[3, 3, 3]", True), ("[0, 1, 2]", False), ("[1, 2, 3]", False), ("ReferenceError", False)],
    },
    {
        "topic": "Databases",
        "description": "Relational querying, indexing, transactions, schema design, and persistence.",
        "language": "sql",
        "difficulty": "MEDIUM",
        "prompt": "Which index is most useful for a query that frequently filters by email equality?",
        "description_text": "Assume email values should be unique.",
        "explanation": "A unique B-tree index on email supports fast equality lookup and enforces uniqueness.",
        "options": [
            ("A unique index on email", True),
            ("An index on created_at only", False),
            ("No index because email is text", False),
            ("A foreign key on password", False),
        ],
    },
    {
        "topic": "Databases",
        "description": "Relational querying, indexing, transactions, schema design, and persistence.",
        "language": "sql",
        "difficulty": "HARD",
        "prompt": "What problem can a transaction isolation level help control?",
        "description_text": "Think about concurrent reads and writes.",
        "explanation": "Isolation levels define what effects of concurrent transactions can be observed.",
        "options": [
            ("Anomalies from concurrent transactions", True),
            ("Slow DNS resolution", False),
            ("Missing CSS assets", False),
            ("HTTP cache headers", False),
        ],
    },
    {
        "topic": "Web APIs",
        "description": "HTTP behavior, API contracts, status codes, caching, and pagination.",
        "difficulty": "EASY",
        "prompt": "Which HTTP method is normally used to retrieve a resource without changing it?",
        "description_text": "Choose the safe retrieval method.",
        "explanation": "GET is intended for retrieving representations and should not change server state.",
        "options": [("GET", True), ("POST", False), ("PATCH", False), ("DELETE", False)],
    },
    {
        "topic": "Web APIs",
        "description": "HTTP behavior, API contracts, status codes, caching, and pagination.",
        "difficulty": "HARD",
        "prompt": "Why should APIs use pagination for large collections?",
        "description_text": "Consider server load and response size.",
        "explanation": "Pagination keeps responses bounded, improving latency and reducing memory and bandwidth usage.",
        "options": [
            ("To keep response size bounded", True),
            ("To disable authentication", False),
            ("To force every query to scan all rows", False),
            ("To prevent clients from filtering", False),
        ],
    },
    {
        "topic": "Git",
        "description": "Version control workflows and repository hygiene.",
        "difficulty": "EASY",
        "prompt": "Which command shows the current working tree status?",
        "description_text": "Choose the command that lists staged and unstaged changes.",
        "explanation": "git status reports branch state plus staged, unstaged, and untracked files.",
        "options": [("git status", True), ("git push", False), ("git clone", False), ("git tag", False)],
    },
    {
        "topic": "Git",
        "description": "Version control workflows and repository hygiene.",
        "difficulty": "MEDIUM",
        "prompt": "What does a pull request primarily support in a team workflow?",
        "description_text": "Think about collaboration before merging.",
        "explanation": "Pull requests provide a review and discussion point before changes land in a target branch.",
        "options": [
            ("Reviewing changes before merge", True),
            ("Deleting commit history", False),
            ("Encrypting repository files", False),
            ("Installing dependencies", False),
        ],
    },
    {
        "topic": "Docker",
        "description": "Container basics, images, and runtime behavior.",
        "difficulty": "EASY",
        "prompt": "What is a Docker image?",
        "description_text": "Choose the best description.",
        "explanation": "An image is a packaged filesystem and metadata used to create containers.",
        "options": [
            ("A template used to create containers", True),
            ("A running virtual machine only", False),
            ("A database backup", False),
            ("A Git branch", False),
        ],
    },
    {
        "topic": "Docker",
        "description": "Container basics, images, and runtime behavior.",
        "difficulty": "MEDIUM",
        "prompt": "Why are multi-stage Docker builds useful?",
        "description_text": "Think about production image size and build tools.",
        "explanation": "Multi-stage builds let you compile in one stage and copy only runtime artifacts into the final image.",
        "options": [
            ("They keep final images smaller", True),
            ("They require every container to run as root", False),
            ("They disable layer caching", False),
            ("They replace environment variables", False),
        ],
    },
    {
        "topic": "Performance",
        "description": "Latency, throughput, caching, profiling, and practical optimization tradeoffs.",
        "difficulty": "MEDIUM",
        "prompt": "What should you usually do before optimizing a slow endpoint?",
        "description_text": "Think about how to avoid guessing.",
        "explanation": "Measuring first identifies the real bottleneck so optimization work targets the actual cause.",
        "options": [
            ("Measure and profile where time is spent", True),
            ("Rewrite every file immediately", False),
            ("Disable every test", False),
            ("Add random indexes without checking queries", False),
        ],
    },
    {
        "topic": "Security",
        "description": "Practical application security fundamentals.",
        "difficulty": "EASY",
        "prompt": "Why should passwords be hashed instead of stored as plain text?",
        "description_text": "Assume the database could be exposed.",
        "explanation": "Hashing protects users by avoiding direct storage of the original password.",
        "options": [
            ("It avoids storing the original password", True),
            ("It makes login impossible", False),
            ("It removes the need for HTTPS", False),
            ("It exposes fewer database indexes", False),
        ],
    },
    {
        "topic": "Security",
        "description": "Practical application security fundamentals.",
        "difficulty": "MEDIUM",
        "prompt": "What is the purpose of CSRF protection in web forms?",
        "description_text": "Think about unwanted browser-submitted requests.",
        "explanation": "CSRF protection helps verify that state-changing requests came from the intended user flow.",
        "options": [
            ("Preventing forged state-changing requests", True),
            ("Compressing HTML responses", False),
            ("Replacing password hashing", False),
            ("Generating CSS classes", False),
        ],
    },
    {
        "topic": "Testing",
        "description": "Automated testing and confidence-building practices.",
        "difficulty": "EASY",
        "prompt": "What should a focused unit test usually verify?",
        "description_text": "Choose the most practical target.",
        "explanation": "A unit test should verify a small behavior with clear inputs and expected outputs.",
        "options": [
            ("A small behavior with clear expectations", True),
            ("Every possible production path at once", False),
            ("Only visual styling", False),
            ("The operating system version", False),
        ],
    },
    {
        "topic": "Testing",
        "description": "Automated testing and confidence-building practices.",
        "difficulty": "MEDIUM",
        "prompt": "Why are regression tests valuable after fixing a bug?",
        "description_text": "Think about future changes.",
        "explanation": "A regression test proves the bug is fixed and helps catch the same failure if it returns.",
        "options": [
            ("They catch the same bug if it returns", True),
            ("They remove the need for code review", False),
            ("They make failing code pass automatically", False),
            ("They rewrite production data", False),
        ],
    },
]


def seed_question_bank():
    for slug in DEPRECATED_TOPIC_SLUGS:
        topic = Topic.query.filter_by(slug=slug).first()
        if topic:
            topic.is_active = False

    for name, description in TOPIC_CATALOG:
        slug = slugify(name)
        topic = Topic.query.filter_by(slug=slug).first()
        if not topic:
            topic = Topic(name=name, slug=slug, description=description, is_active=True)
            db.session.add(topic)
        else:
            topic.description = topic.description or description
    db.session.flush()

    for name, description in LANGUAGE_CATALOG:
        slug = name.strip().lower()
        language = Language.query.filter_by(slug=slug).first()
        if not language:
            language = Language(name=name, slug=slug, description=description, is_active=True)
            db.session.add(language)
        else:
            language.description = language.description or description
    db.session.flush()

    for title, topic_name, description, difficulty, question_limit, language, accent, position in DEFAULT_PRESETS:
        topic = Topic.query.filter_by(slug=slugify(topic_name)).first()
        if not topic:
            continue
        slug = slugify(title)
        preset = QuizPreset.query.filter_by(slug=slug).first()
        if preset:
            continue
        db.session.add(
            QuizPreset(
                topic_id=topic.id,
                slug=slug,
                title=title,
                description=description,
                difficulty=difficulty,
                question_limit=question_limit,
                language=language or None,
                accent=accent,
                position=position,
                is_active=True,
            )
        )
    db.session.flush()

    for item in SEED_DATA:
        slug = slugify(item["topic"])
        topic = Topic.query.filter_by(slug=slug).first()
        if not topic:
            topic = Topic(name=item["topic"], slug=slug, description=item["description"], is_active=True)
            db.session.add(topic)
            db.session.flush()
        existing = Question.query.filter_by(prompt=item["prompt"], topic_id=topic.id).first()
        if existing:
            continue

        question = Question(
            topic_id=topic.id,
            prompt=item["prompt"],
            description=item.get("description_text", ""),
            explanation=item["explanation"],
            difficulty=item["difficulty"],
            status="published",
            source="seed",
            language=item.get("language"),
            code_snippet=item.get("code_snippet"),
        )
        db.session.add(question)
        db.session.flush()

        for position, (text, is_correct) in enumerate(item["options"]):
            db.session.add(
                AnswerOption(
                    question_id=question.id,
                    text=text,
                    is_correct=is_correct,
                    position=position,
                )
            )
    db.session.commit()
