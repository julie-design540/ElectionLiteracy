"""Application entry point for the civic education platform."""

from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, render_template
from sqlalchemy import inspect, text
from werkzeug.security import generate_password_hash

from config import config_by_name
from extensions import csrf, db, login_manager
from models import Artwork, Category, Lesson, User
from routes.admin import admin_bp
from routes.artwork import artwork_bp
from routes.auth import auth_bp
from routes.main import main_bp
from routes.learning import learning_bp


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application."""

    app = Flask(__name__, instance_relative_config=True)
    config_key = config_name or os.getenv("FLASK_CONFIG", "development")
    app.config.from_object(config_by_name[config_key])

    instance_path = Path(app.instance_path)
    upload_dir = Path(app.static_folder or "static") / "uploads"
    profile_dir = upload_dir / "profiles"
    artwork_dir = upload_dir / "artworks"
    lesson_dir = upload_dir / "lessons"
    for directory in (instance_path, upload_dir, profile_dir, artwork_dir, lesson_dir):
        directory.mkdir(parents=True, exist_ok=True)

    app.config["UPLOAD_FOLDER"] = str(upload_dir)
    app.config["PROFILE_UPLOAD_FOLDER"] = str(profile_dir)
    app.config["ARTWORK_UPLOAD_FOLDER"] = str(artwork_dir)
    app.config["LESSON_UPLOAD_FOLDER"] = str(lesson_dir)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(artwork_bp, url_prefix="/artwork")
    app.register_blueprint(learning_bp, url_prefix="/learn")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.context_processor
    def inject_globals() -> dict[str, object]:
        """Make common counts and categories available in every template."""

        return {
            "category_list": Category.query.order_by(Category.name.asc()).all(),
            "featured_count": Artwork.query.filter_by(status="approved").count(),
            "user_count": User.query.count(),
            "lesson_count": Lesson.query.count(),
        }

    @app.errorhandler(404)
    def page_not_found(_error: Exception):
        return render_template("errors/404.html"), 404

    @app.cli.command("seed-data")
    def seed_data() -> None:
        """Populate the database with default categories and an admin user."""

        default_categories = [
            "Peace",
            "Democracy",
            "Voting Process",
            "Youth Participation",
            "Constitution",
            "Leadership",
            "Anti-Corruption",
            "Women's Participation",
            "Disability Inclusion",
            "Election Integrity",
            "Public Participation",
            "County Governance",
            "Budget Accountability",
            "Digital Literacy",
            "Human Rights",
            "National Values",
        ]

        for name in default_categories:
            Category.get_or_create(name=name, description=f"Artwork about {name.lower()}.")

        admin_email = app.config.get("SEED_ADMIN_EMAIL", "admin@civicart.local")
        admin_username = app.config.get("SEED_ADMIN_USERNAME", "admin")
        admin_password = app.config.get("SEED_ADMIN_PASSWORD", "Admin@12345")
        admin = User.query.filter_by(email=admin_email).first()
        if admin is None:
            admin = User(
                username=admin_username,
                email=admin_email,
                role="admin",
                password_hash=generate_password_hash(admin_password),
            )
            db.session.add(admin)
        db.session.commit()
        _seed_lessons()
        print("Seed data created successfully.")

    def _ensure_lesson_columns() -> None:
        """Backfill SQLite columns when the database predates this release."""

        if db.engine.dialect.name != "sqlite":
            return
        lesson_columns = {column["name"] for column in inspect(db.engine).get_columns("lessons")}
        lesson_statements = [
            ("estimated_minutes", "ALTER TABLE lessons ADD COLUMN estimated_minutes INTEGER NOT NULL DEFAULT 10"),
            ("cover_image", "ALTER TABLE lessons ADD COLUMN cover_image VARCHAR(255) NOT NULL DEFAULT ''"),
            (
                "attachment_filename",
                "ALTER TABLE lessons ADD COLUMN attachment_filename VARCHAR(255) NOT NULL DEFAULT ''",
            ),
            (
                "attachment_label",
                "ALTER TABLE lessons ADD COLUMN attachment_label VARCHAR(120) NOT NULL DEFAULT ''",
            ),
            ("user_id", "ALTER TABLE lessons ADD COLUMN user_id INTEGER"),
            ("video_url", "ALTER TABLE lessons ADD COLUMN video_url VARCHAR(500) NOT NULL DEFAULT ''"),
        ]
        for column_name, statement in lesson_statements:
            if column_name not in lesson_columns:
                db.session.execute(text(statement))

        artwork_columns = {column["name"] for column in inspect(db.engine).get_columns("artworks")}
        artwork_statements = [
            ("video_url", "ALTER TABLE artworks ADD COLUMN video_url VARCHAR(500) NOT NULL DEFAULT ''"),
        ]
        for column_name, statement in artwork_statements:
            if column_name not in artwork_columns:
                db.session.execute(text(statement))
        db.session.commit()

    def _seed_lessons() -> None:
        """Create or extend the starter course without touching user lessons."""

        admin = User.query.filter_by(role="admin").order_by(User.created_at.asc()).first()
        author_id = admin.id if admin else None
        starter_lessons = [
            (
                "Civic Awareness Basics",
                "Understand what civic education means, why it matters, and how citizens shape public life.",
                "Civic education helps people understand their rights, duties, and the institutions that serve the public.\n"
                "In Kenya, civic knowledge supports informed participation, peaceful dialogue, and accountable leadership. Citizens need to understand the Constitution, county government, Parliament, courts, independent commissions, and the public offices that make decisions on their behalf.\n"
                "A strong civic culture begins with ordinary habits: asking for evidence, showing up for public forums, listening respectfully, and choosing leaders based on public interest rather than pressure or misinformation.",
                1,
                15,
            ),
            (
                "Your Voice at the Ballot Box",
                "Learn how to prepare for an election, verify details, and vote with confidence.",
                "Good voting decisions start long before election day. Compare manifestos, verify candidate information, and understand where and when to vote.\n"
                "A voter should confirm registration details, carry the correct identification, follow polling-station instructions, and keep the ballot secret. Responsible participation also means helping first-time voters understand the process without pressuring them.\n"
                "Voting is not only a personal choice. It is a public responsibility that affects schools, roads, health services, security, jobs, and the way public money is managed.",
                2,
                20,
            ),
            (
                "Leadership and Accountability",
                "See how citizens hold leaders accountable after elections through civic action and public oversight.",
                "Democracy does not end once ballots are counted. Citizens can attend public forums, follow budgets, raise issues through representatives, and monitor service delivery.\n"
                "Accountability requires records. Track campaign promises, budget allocations, procurement notices, and county project timelines. When information is unclear, citizens can ask questions through lawful channels and public participation spaces.\n"
                "Civic power is strongest when people stay informed after elections, not only during campaign season.",
                3,
                18,
            ),
            (
                "Community Participation Toolkit",
                "Turn knowledge into action with practical habits for public engagement and civic advocacy.",
                "Strong communities build civic culture through discussions, volunteerism, voter education, and respectful debate.\n"
                "Use school clubs, youth groups, faith communities, local forums, and digital platforms to share accurate information. A good civic message should be clear, respectful, non-violent, and rooted in facts.\n"
                "Community participation is most useful when it turns concern into organized action: documenting issues, proposing solutions, and following up with public offices.",
                4,
                16,
            ),
            (
                "The Constitution and National Values",
                "Understand the values that guide public life, leadership, rights, and national unity.",
                "The Constitution is the foundation of Kenya's public life. It protects rights, assigns public responsibilities, and explains how power should be exercised.\n"
                "National values include patriotism, human dignity, equity, social justice, inclusiveness, equality, human rights, non-discrimination, good governance, integrity, transparency, and accountability.\n"
                "Citizens can use these values to evaluate public decisions, campaign messages, civic artwork, and the conduct of leaders.",
                5,
                22,
            ),
            (
                "County Government and Devolution",
                "Learn how counties work and how residents can influence local services.",
                "Devolution brings government closer to citizens by giving counties responsibility for local services such as health facilities, agriculture support, early childhood education, local roads, markets, and county planning.\n"
                "Residents can influence county priorities through public participation, budget hearings, petitions, ward meetings, and direct engagement with elected and appointed county officials.\n"
                "A citizen who understands devolution can connect everyday problems to the right public office instead of treating every issue as a national matter.",
                6,
                24,
            ),
            (
                "Public Participation and Budget Tracking",
                "Use public forums, budget documents, and community evidence to influence decisions.",
                "Public participation is a constitutional principle. It gives citizens a chance to review plans, raise concerns, and propose priorities before decisions are finalized.\n"
                "Budget tracking starts with simple questions: What was promised? How much was allocated? Who is responsible? What timeline was given? What evidence shows progress?\n"
                "When citizens organize evidence and attend forums consistently, public participation becomes more than attendance. It becomes oversight.",
                7,
                26,
            ),
            (
                "Fighting Corruption Through Civic Action",
                "Identify red flags, protect public resources, and report concerns responsibly.",
                "Corruption weakens public services and reduces trust. Civic education helps citizens recognize red flags such as unexplained costs, ghost projects, favoritism, missing records, and repeated delays without clear reasons.\n"
                "Responsible reporting requires evidence and lawful channels. Citizens should avoid spreading unsupported claims, but they should also avoid silence when public resources are being misused.\n"
                "Integrity grows when communities normalize questions about budgets, procurement, delivery, and leadership conduct.",
                8,
                21,
            ),
            (
                "Digital Citizenship and Misinformation",
                "Build safer online habits for civic discussion, campaign content, and public debate.",
                "Digital platforms can educate voters, but they can also spread false information quickly. A responsible digital citizen checks the source, date, evidence, and motive behind a civic claim before sharing it.\n"
                "Look for signs of manipulation: emotional headlines, anonymous sources, fake screenshots, edited videos, and messages that pressure people to react immediately.\n"
                "Good civic communication should reduce confusion, not increase fear. Share verified information, correct mistakes openly, and report harmful content when necessary.",
                9,
                19,
            ),
            (
                "Peaceful Elections and Social Cohesion",
                "Promote respectful participation before, during, and after elections.",
                "Peaceful elections require citizens, leaders, institutions, and communities to reject intimidation, hate speech, and violence.\n"
                "Social cohesion starts with how people speak about each other. Avoid messages that target communities, spread fear, or frame politics as a threat to coexistence.\n"
                "After results are announced, citizens should use lawful dispute channels, respect due process, and continue working together on shared public needs.",
                10,
                17,
            ),
        ]
        for title, summary, content, order, minutes in starter_lessons:
            slug = "-".join(title.lower().strip().split())
            existing = Lesson.query.filter_by(slug=f"{slug}-{order}").first()
            if existing is None:
                db.session.add(
                    Lesson(
                        title=title,
                        slug=f"{slug}-{order}",
                        summary=summary,
                        content=content,
                        order=order,
                        estimated_minutes=minutes,
                        user_id=author_id,
                    )
                )
            else:
                existing.title = title
                existing.summary = summary
                existing.content = content
                existing.order = order
                existing.estimated_minutes = minutes
                existing.user_id = existing.user_id or author_id
        db.session.commit()

    with app.app_context():
        db.create_all()
        _ensure_lesson_columns()
        if not Category.query.first():
            for name in [
                "Peace",
                "Democracy",
                "Voting Process",
                "Youth Participation",
                "Constitution",
                "Leadership",
                "Anti-Corruption",
                "Women's Participation",
                "Disability Inclusion",
                "Election Integrity",
                "Public Participation",
                "County Governance",
                "Budget Accountability",
                "Digital Literacy",
                "Human Rights",
                "National Values",
            ]:
                Category.get_or_create(name=name, description=f"Artwork about {name.lower()}.")
        for name in [
            "Public Participation",
            "County Governance",
            "Budget Accountability",
            "Digital Literacy",
            "Human Rights",
            "National Values",
        ]:
            Category.get_or_create(name=name, description=f"Artwork about {name.lower()}.")

        admin_email = app.config.get("SEED_ADMIN_EMAIL", "admin@civicart.local")
        admin_username = app.config.get("SEED_ADMIN_USERNAME", "admin")
        admin_password = app.config.get("SEED_ADMIN_PASSWORD", "Admin@12345")
        if not User.query.filter_by(email=admin_email).first():
            db.session.add(
                User(
                    username=admin_username,
                    email=admin_email,
                    role="admin",
                    password_hash=generate_password_hash(admin_password),
                )
            )
        db.session.commit()
        _seed_lessons()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
        use_reloader=False,
    )
