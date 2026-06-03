"""
Aether Schema Library – JSON-LD Generator for SEO
"""

import json
from pathlib import Path
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QPlainTextEdit, QMessageBox, QTabWidget, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QDateTimeEdit, QSpinBox,
    QGroupBox, QScrollArea, QApplication
)
from PySide6.QtCore import Qt, QDateTime
from bs4 import BeautifulSoup


class SchemaTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_file = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # file selection row  # this is cursed but
        file_row = QHBoxLayout()
        self.file_label = QLabel("No HTML file selected")
        self.select_btn = QPushButton("Select HTML File")
        self.select_btn.clicked.connect(self.select_html_file)
        self.inject_btn = QPushButton("Inject Schema into HTML")
        self.inject_btn.clicked.connect(self.inject_schema)
        self.validate_btn = QPushButton("✓ Validate Schema")
        self.validate_btn.clicked.connect(self.validate_schema)

        file_row.addWidget(self.select_btn)
        file_row.addWidget(self.inject_btn)
        file_row.addWidget(self.validate_btn)
        file_row.addWidget(self.file_label)

        file_row.addStretch()
        layout.addLayout(file_row)

        # tab widget for different schema types
        self.schema_tabs = QTabWidget()
        layout.addWidget(self.schema_tabs)

        # create all schema tabs
        self.setup_faq_tab()
        self.setup_product_tab()
        self.setup_article_tab()
        self.setup_event_tab()
        self.setup_recipe_tab()
        self.setup_howto_tab()
        self.setup_localbusiness_tab()
        self.setup_video_tab()


        # json preview
        preview_group = QGroupBox("Generated JSON-LD Preview")
        preview_layout = QVBoxLayout(preview_group)
        self.json_preview = QPlainTextEdit()
        self.json_preview.setReadOnly(True)
        self.json_preview.setMaximumHeight(200)
        preview_layout.addWidget(self.json_preview)
        layout.addWidget(preview_group)

        self.status_label = QLabel("Ready - Select a schema type and fill in the fields")

        layout.addWidget(self.status_label)

        self.current_schema_data = None

    def select_html_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select HTML File", "", "HTML Files (*.html)")
        if path:
            self.current_file = path
            self.file_label.setText(Path(path).name)

    def update_json_preview(self, schema_data):
        if schema_data:

            self.current_schema_data = schema_data
            self.json_preview.setPlainText(json.dumps(schema_data, indent=2, ensure_ascii=False))
        else:
            self.json_preview.clear()

    def inject_schema(self):
        if not self.current_file:
            QMessageBox.warning(self, "Warning", "Please select an HTML file first.")
            return
        if not self.current_schema_data:
            QMessageBox.warning(self, "Warning", "No schema generated. Fill in a form first.")

            return

        with open(self.current_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        head = soup.head
        if not head:
            head = soup.new_tag('head')
            soup.html.insert(0, head)

        # remove existing schema of the same type
        schema_type = self.current_schema_data.get('@type')
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if data.get('@type') == schema_type:
                    script.decompose()
            except:
                pass

        # add new schema
        script_tag = soup.new_tag('script', type='application/ld+json')
        script_tag.string = json.dumps(self.current_schema_data, indent=2, ensure_ascii=False)
        head.append(script_tag)

        with open(self.current_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))

        QMessageBox.information(self, "Success", f"{schema_type} schema injected into HTML file.")
        self.status_label.setText(f"Injected {schema_type} schema into {self.current_file}")

    def validate_schema(self):
        """Validate the current schema against Google's requirements."""
        if not self.current_schema_data:
            QMessageBox.warning(self, "Warning", "Generate a schema first.")
            return
        
        schema_type = self.current_schema_data.get('@type')
        issues = []
        warnings = []
        
        required_fields = {
            "FAQPage": ["mainEntity"],
            "Product": ["name", "offers"],
            "Article": ["headline", "author", "datePublished"],
            "Event": ["name", "startDate", "location"],
            "Recipe": ["name", "recipeIngredient", "recipeInstructions"],
            "HowTo": ["name", "step"],
            "LocalBusiness": ["name", "address"],
            "VideoObject": ["name", "description", "contentUrl"]
        }
        
        for field in required_fields.get(schema_type, []):
            if not self.current_schema_data.get(field):
                issues.append(f"Missing required field: {field}")
        
        if schema_type == "Product" and "offers" in self.current_schema_data:
            offers = self.current_schema_data["offers"]
            if not offers.get("price"):
                issues.append("Product offer missing 'price'")
            if not offers.get("priceCurrency"):
                issues.append("Product offer missing 'priceCurrency'")
        
        if schema_type == "FAQPage":
            main_entity = self.current_schema_data.get("mainEntity", [])
            if len(main_entity) == 0:
                issues.append("FAQPage has no questions")
        
        if schema_type == "LocalBusiness":
            address = self.current_schema_data.get("address", {})
            if not address.get("addressLocality") and not address.get("streetAddress"):
                warnings.append("Address may be incomplete (missing locality or street)")
        
        if not issues and not warnings:
            QMessageBox.information(self, "Schema Valid", f"\uf00c {schema_type} schema is valid!\n\nNo issues found.")
        else:
            message = ""
            if issues:

                message += "\58 ISSUES (must fix):\n"
                for issue in issues:
                    message += f"  • {issue}\n"
            if warnings:
                message += "\n \uf071 WARNINGS (recommended):\n"
                for warning in warnings:
                    message += f"  • {warning}\n"

            message += "\nGoogle requires these fields for rich results."
            QMessageBox.warning(self, "Schema Issues", message)

    # ========== dark/light theme support ==========
    def update_theme(self, is_dark):
        """Called from main window when theme changes."""
        if is_dark:
            self.schema_tabs.setStyleSheet("""
                QTabWidget::pane {
                    background-color: #1e1f22;
                    border: 1px solid #3e4045;
                }
                QTabBar::tab {
                    background-color: #2b2d31;
                    color: #e8e8e8;
                    padding: 6px 12px;
                }
                QTabBar::tab:selected {
                    background-color: #3e4045;
                }
                QTabBar::tab:hover {
                    background-color: #4b4e54;
                }
                QScrollArea, QWidget {
                    background-color: #1e1f22;
                }
                QGroupBox {
                    color: #e8e8e8;
                    border: 1px solid #3e4045;
                }
                QGroupBox::title {
                    color: #e8e8e8;  # i hate this but it works
                }
                QLineEdit, QTextEdit, QComboBox, QDateTimeEdit, QSpinBox {
                    background-color: #2b2d31;
                    color: #e8e8e8;
                    border: 1px solid #3e4045;
                }
                QLabel {
                    color: #e8e8e8;
                }
                QPushButton {
                    background-color: #2b2d31;
                    color: #e8e8e8;
                    border: 1px solid #8095ab;
                }
                QPushButton:hover {
                    background-color: #8095ab;
                    color: #1e1f22;
                }
                QPlainTextEdit {
                    background-color: #2b2d31;
                    color: #e8e8e8;
                    border: 1px solid #3e4045;
                }
            """)
        else:
            self.schema_tabs.setStyleSheet("""
                QTabWidget::pane {
                    background-color: #ffffff;
                    border: 1px solid #d0d7de;
                }
                QTabBar::tab {
                    background-color: #f1f3f5;
                    color: #2c3e50;
                    padding: 6px 12px;
                }
                QTabBar::tab:selected {
                    background-color: #ffffff;
                }
                QTabBar::tab:hover {
                    background-color: #8095ab;
                    color: white;
                }
                QScrollArea, QWidget {
                    background-color: #ffffff;
                }
                QGroupBox {
                    color: #2c3e50;
                    border: 1px solid #d0d7de;
                }
                QGroupBox::title {
                    color: #2c3e50;
                }
                QLineEdit, QTextEdit, QComboBox, QDateTimeEdit, QSpinBox {
                    background-color: #ffffff;
                    color: #2c3e50;
                    border: 1px solid #d0d7de;

                }
                QLabel {

                    color: #2c3e50;
                }
                QPushButton {
                    background-color: #e9ecf1;
                    color: #2c3e50;
                    border: 1px solid #8095ab;
                }
                QPushButton:hover {
                    background-color: #8095ab;
                    color: white;
                }
                QPlainTextEdit {
                    background-color: #ffffff;
                    color: #2c3e50;
                    border: 1px solid #d0d7de;
                }
            """)

    # ========== faq page schema ==========
    def setup_faq_tab(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(tab)

        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        form_layout = QFormLayout(scroll_content)
        
        self.faq_name = QLineEdit()
        self.faq_name.setPlaceholderText("e.g., Frequently Asked Questions")

        form_layout.addRow("FAQ Name:", self.faq_name)
        
        self.faq_questions = QTextEdit()
        self.faq_questions.setPlaceholderText('Enter each Q&A as: Question|||Answer\nExample:\nWhat is your return policy?|||We accept returns within 30 days.\nDo you ship internationally?|||Yes, worldwide shipping.')
        self.faq_questions.setMaximumHeight(150)
        form_layout.addRow("Questions & Answers (||| separated):", self.faq_questions)
        
        self.faq_generate = QPushButton("Generate FAQ Schema")
        self.faq_generate.clicked.connect(self.generate_faq)
        form_layout.addRow(self.faq_generate)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        self.schema_tabs.addTab(tab, "\uf059 FAQ Page")
    
    def generate_faq(self):
        name = self.faq_name.text().strip()
        qa_text = self.faq_questions.toPlainText().strip()
        
        if not qa_text:
            QMessageBox.warning(self, "Warning", "Please enter at least one Q&A.")
            return
        
        main_entity = []
        for line in qa_text.split('\n'):
            if '|||' in line:
                q, a = line.split('|||', 1)
                main_entity.append({
                    "@type": "Question",
                    "name": q.strip(),
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": a.strip()
                    }
                })
        
        if not main_entity:
            QMessageBox.warning(self, "Warning", "No valid Q&A found. Use 'Question|||Answer' format.")
            return
        
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "name": name or "Frequently Asked Questions",
            "mainEntity": main_entity
        }
        self.update_json_preview(schema)


    # ========== product schema ==========
    def setup_product_tab(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        form_layout = QFormLayout(scroll_content)
        
        self.product_name = QLineEdit()
        form_layout.addRow("Product Name:", self.product_name)
        
        self.product_description = QTextEdit()
        self.product_description.setMaximumHeight(80)
        form_layout.addRow("Description:", self.product_description)
        
        self.product_price = QLineEdit()
        self.product_price.setPlaceholderText("e.g., 29.99")
        form_layout.addRow("Price:", self.product_price)
        
        self.product_currency = QComboBox()
        self.product_currency.addItems(["USD", "EUR", "GBP", "IRR", "CAD", "AUD"])
        form_layout.addRow("Currency:", self.product_currency)
        
        self.product_availability = QComboBox()
        self.product_availability.addItems(["InStock", "OutOfStock", "PreOrder", "LimitedAvailability"])
        form_layout.addRow("Availability:", self.product_availability)
        
        self.product_image = QLineEdit()
        self.product_image.setPlaceholderText("https://example.com/image.jpg")
        form_layout.addRow("Image URL:", self.product_image)
        
        self.product_brand = QLineEdit()
        form_layout.addRow("Brand:", self.product_brand)
        
        self.product_sku = QLineEdit()
        form_layout.addRow("SKU/MPN:", self.product_sku)
        
        self.product_generate = QPushButton("Generate Product Schema")
        self.product_generate.clicked.connect(self.generate_product)
        form_layout.addRow(self.product_generate)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        self.schema_tabs.addTab(tab, "\uf02b Product")
    
    def generate_product(self):
        name = self.product_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Product name is required.")
            return
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": name,
            "description": self.product_description.toPlainText().strip() or None,
        }
        
        if self.product_price.text().strip():
            schema["offers"] = {

                "@type": "Offer",
                "price": self.product_price.text().strip(),
                "priceCurrency": self.product_currency.currentText(),
                "availability": f"https://schema.org/{self.product_availability.currentText()}"
            }
        
        if self.product_image.text().strip():
            schema["image"] = self.product_image.text().strip()
        if self.product_brand.text().strip():
            schema["brand"] = {"@type": "Brand", "name": self.product_brand.text().strip()}
        if self.product_sku.text().strip():
            schema["sku"] = self.product_sku.text().strip()
        
        schema = {k: v for k, v in schema.items() if v}
        self.update_json_preview(schema)

    # ========== article schema ==========
    def setup_article_tab(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        form_layout = QFormLayout(scroll_content)
        
        self.article_headline = QLineEdit()
        form_layout.addRow("Headline:", self.article_headline)
        
        self.article_author = QLineEdit()
        form_layout.addRow("Author Name:", self.article_author)
        
        self.article_date = QDateTimeEdit()
        self.article_date.setDateTime(QDateTime.currentDateTime())
        form_layout.addRow("Published Date:", self.article_date)
        
        self.article_image = QLineEdit()
        form_layout.addRow("Image URL:", self.article_image)
        
        self.article_description = QTextEdit()
        self.article_description.setMaximumHeight(80)
        form_layout.addRow("Description:", self.article_description)
        
        self.article_body = QTextEdit()
        self.article_body.setMaximumHeight(100)
        form_layout.addRow("Article Body (excerpt):", self.article_body)
        
        self.article_generate = QPushButton("Generate Article Schema")
        self.article_generate.clicked.connect(self.generate_article)
        form_layout.addRow(self.article_generate)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        self.schema_tabs.addTab(tab, "\uf1ea Article")
    
    def generate_article(self):
        headline = self.article_headline.text().strip()
        if not headline:
            QMessageBox.warning(self, "Warning", "Headline is required.")
            return

        
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": headline,
            "datePublished": self.article_date.dateTime().toString("yyyy-MM-dd"),
        }
        
        if self.article_author.text().strip():
            schema["author"] = {"@type": "Person", "name": self.article_author.text().strip()}
        if self.article_image.text().strip():
            schema["image"] = self.article_image.text().strip()
        if self.article_description.toPlainText().strip():
            schema["description"] = self.article_description.toPlainText().strip()
        if self.article_body.toPlainText().strip():
            schema["articleBody"] = self.article_body.toPlainText().strip()
        
        schema = {k: v for k, v in schema.items() if v}
        self.update_json_preview(schema)

    # ========== event schema ==========
    def setup_event_tab(self):

        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()

        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        form_layout = QFormLayout(scroll_content)
        
        self.event_name = QLineEdit()
        form_layout.addRow("Event Name:", self.event_name)
        
        self.event_start = QDateTimeEdit()
        self.event_start.setDateTime(QDateTime.currentDateTime())
        form_layout.addRow("Start Date/Time:", self.event_start)

        
        self.event_end = QDateTimeEdit()
        self.event_end.setDateTime(QDateTime.currentDateTime().addDays(1))
        form_layout.addRow("End Date/Time:", self.event_end)
        
        self.event_location = QLineEdit()
        self.event_location.setPlaceholderText("Venue name, City")
        form_layout.addRow("Location:", self.event_location)
        
        self.event_description = QTextEdit()
        self.event_description.setMaximumHeight(80)
        form_layout.addRow("Description:", self.event_description)
        
        self.event_url = QLineEdit()
        form_layout.addRow("Event URL (tickets):", self.event_url)
        
        self.event_generate = QPushButton("Generate Event Schema")
        self.event_generate.clicked.connect(self.generate_event)
        form_layout.addRow(self.event_generate)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        self.schema_tabs.addTab(tab, "\uf073 Event")
    
    def generate_event(self):
        name = self.event_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Event name is required.")
            return
        
        schema = {
            "@context": "https://schema.org",

            "@type": "Event",
            "name": name,
            "startDate": self.event_start.dateTime().toString("yyyy-MM-ddTHH:mm"),
            "endDate": self.event_end.dateTime().toString("yyyy-MM-ddTHH:mm"),
        }
        
        if self.event_location.text().strip():

            schema["location"] = {
                "@type": "Place",
                "name": self.event_location.text().strip()
            }
        if self.event_description.toPlainText().strip():
            schema["description"] = self.event_description.toPlainText().strip()
        if self.event_url.text().strip():
            schema["url"] = self.event_url.text().strip()
        
        schema = {k: v for k, v in schema.items() if v}
        self.update_json_preview(schema)

    # ========== recipe schema ==========
    def setup_recipe_tab(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        form_layout = QFormLayout(scroll_content)
        
        self.recipe_name = QLineEdit()
        form_layout.addRow("Recipe Name:", self.recipe_name)
        
        self.recipe_description = QTextEdit()
        self.recipe_description.setMaximumHeight(80)
        form_layout.addRow("Description:", self.recipe_description)
        

        self.recipe_prep_time = QLineEdit()
        self.recipe_prep_time.setPlaceholderText("PT30M (30 minutes)")
        form_layout.addRow("Prep Time (ISO 8601):", self.recipe_prep_time)
        
        self.recipe_cook_time = QLineEdit()
        self.recipe_cook_time.setPlaceholderText("PT1H (1 hour)")
        form_layout.addRow("Cook Time:", self.recipe_cook_time)
        
        self.recipe_ingredients = QTextEdit()
        self.recipe_ingredients.setPlaceholderText("One ingredient per line\nFlour\nSugar\nEggs")
        self.recipe_ingredients.setMaximumHeight(100)
        form_layout.addRow("Ingredients:", self.recipe_ingredients)
        
        self.recipe_instructions = QTextEdit()
        self.recipe_instructions.setPlaceholderText("Step 1: ...\nStep 2: ...")
        self.recipe_instructions.setMaximumHeight(100)
        form_layout.addRow("Instructions:", self.recipe_instructions)
        
        self.recipe_image = QLineEdit()
        form_layout.addRow("Image URL:", self.recipe_image)
        
        self.recipe_generate = QPushButton("Generate Recipe Schema")
        self.recipe_generate.clicked.connect(self.generate_recipe)
        form_layout.addRow(self.recipe_generate)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        self.schema_tabs.addTab(tab, "\uf002 Recipe")
    
    def generate_recipe(self):
        name = self.recipe_name.text().strip()

        if not name:
            QMessageBox.warning(self, "Warning", "Recipe name is required.")
            return
        
        ingredients = [i.strip() for i in self.recipe_ingredients.toPlainText().split('\n') if i.strip()]
        instructions = self.recipe_instructions.toPlainText().strip()
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Recipe",
            "name": name,
        }
        
        if self.recipe_description.toPlainText().strip():
            schema["description"] = self.recipe_description.toPlainText().strip()
        if self.recipe_prep_time.text().strip():
            schema["prepTime"] = self.recipe_prep_time.text().strip()
        if self.recipe_cook_time.text().strip():
            schema["cookTime"] = self.recipe_cook_time.text().strip()
        if ingredients:
            schema["recipeIngredient"] = ingredients
        if instructions:
            schema["recipeInstructions"] = [{"@type": "HowToStep", "text": instructions}]
        if self.recipe_image.text().strip():
            schema["image"] = self.recipe_image.text().strip()
        
        schema = {k: v for k, v in schema.items() if v}
        self.update_json_preview(schema)

    # ========== howto schema ==========
    def setup_howto_tab(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        form_layout = QFormLayout(scroll_content)
        
        self.howto_name = QLineEdit()
        form_layout.addRow("HowTo Name:", self.howto_name)
        
        self.howto_description = QTextEdit()
        self.howto_description.setMaximumHeight(80)
        form_layout.addRow("Description:", self.howto_description)
        
        self.howto_steps = QTextEdit()
        self.howto_steps.setPlaceholderText("Step 1: Open the box\nStep 2: Remove contents\nStep 3: ...")
        self.howto_steps.setMaximumHeight(150)
        form_layout.addRow("Steps (one per line):", self.howto_steps)
        
        self.howto_image = QLineEdit()
        form_layout.addRow("Image URL:", self.howto_image)
        
        self.howto_generate = QPushButton("Generate HowTo Schema")
        self.howto_generate.clicked.connect(self.generate_howto)
        form_layout.addRow(self.howto_generate)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        self.schema_tabs.addTab(tab, "\uf31c HowTo")
    
    def generate_howto(self):
        name = self.howto_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "HowTo name is required.")

            return
        
        steps = []
        for i, line in enumerate(self.howto_steps.toPlainText().split('\n')):
            if line.strip():
                steps.append({
                    "@type": "HowToStep",
                    "name": f"Step {i+1}",

                    "text": line.strip()
                })
        
        if not steps:
            QMessageBox.warning(self, "Warning", "At least one step is required.")
            return

        
        schema = {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": name,
            "step": steps
        }
        
        if self.howto_description.toPlainText().strip():
            schema["description"] = self.howto_description.toPlainText().strip()
        if self.howto_image.text().strip():
            schema["image"] = self.howto_image.text().strip()
        
        self.update_json_preview(schema)

    # ========== local business schema ==========

    def setup_localbusiness_tab(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        form_layout = QFormLayout(scroll_content)
        
        self.biz_name = QLineEdit()
        form_layout.addRow("Business Name:", self.biz_name)
        
        self.biz_description = QTextEdit()
        self.biz_description.setMaximumHeight(80)
        form_layout.addRow("Description:", self.biz_description)
        
        self.biz_address = QLineEdit()
        form_layout.addRow("Address:", self.biz_address)
        
        self.biz_city = QLineEdit()
        form_layout.addRow("City:", self.biz_city)
        
        self.biz_region = QLineEdit()
        form_layout.addRow("State/Region:", self.biz_region)
        
        self.biz_country = QLineEdit()
        form_layout.addRow("Country:", self.biz_country)
        
        self.biz_phone = QLineEdit()
        form_layout.addRow("Telephone:", self.biz_phone)
        
        self.biz_email = QLineEdit()
        form_layout.addRow("Email:", self.biz_email)
        
        self.biz_hours = QLineEdit()
        self.biz_hours.setPlaceholderText("Mo-Fr 09:00-17:00")
        form_layout.addRow("Opening Hours:", self.biz_hours)
        
        self.biz_latitude = QLineEdit()
        self.biz_longitude = QLineEdit()
        coords_layout = QHBoxLayout()
        coords_layout.addWidget(self.biz_latitude)
        coords_layout.addWidget(self.biz_longitude)
        form_layout.addRow("Geo Coordinates (lat, lon):", coords_layout)
        
        self.biz_price_range = QLineEdit()

        self.biz_price_range.setPlaceholderText("$$, $10-50")
        form_layout.addRow("Price Range:", self.biz_price_range)
        
        self.biz_logo = QLineEdit()
        form_layout.addRow("Logo URL:", self.biz_logo)
        
        self.biz_image = QLineEdit()
        form_layout.addRow("Image URL:", self.biz_image)
        
        self.biz_generate = QPushButton("Generate Local Business Schema")
        self.biz_generate.clicked.connect(self.generate_localbusiness)
        form_layout.addRow(self.biz_generate)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        self.schema_tabs.addTab(tab, "\uf279 Local Business")
    
    def generate_localbusiness(self):
        name = self.biz_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Business name is required.")
            return
        
        schema = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": name,

        }
        
        if self.biz_description.toPlainText().strip():
            schema["description"] = self.biz_description.toPlainText().strip()
        
        if self.biz_address.text().strip() or self.biz_city.text().strip():
            schema["address"] = {
                "@type": "PostalAddress",
                "streetAddress": self.biz_address.text().strip(),
                "addressLocality": self.biz_city.text().strip(),
                "addressRegion": self.biz_region.text().strip(),
                "addressCountry": self.biz_country.text().strip()
            }
        
        if self.biz_phone.text().strip():

            schema["telephone"] = self.biz_phone.text().strip()
        if self.biz_email.text().strip():
            schema["email"] = self.biz_email.text().strip()

        if self.biz_hours.text().strip():
            schema["openingHours"] = self.biz_hours.text().strip()
        if self.biz_latitude.text().strip() and self.biz_longitude.text().strip():
            schema["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": self.biz_latitude.text().strip(),
                "longitude": self.biz_longitude.text().strip()
            }
        if self.biz_price_range.text().strip():
            schema["priceRange"] = self.biz_price_range.text().strip()
        if self.biz_logo.text().strip():
            schema["logo"] = self.biz_logo.text().strip()
        if self.biz_image.text().strip():
            schema["image"] = self.biz_image.text().strip()
        
        schema = {k: v for k, v in schema.items() if v}
        self.update_json_preview(schema)

    # ========== video schema ==========
    def setup_video_tab(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        form_layout = QFormLayout(scroll_content)
        
        self.video_name = QLineEdit()
        form_layout.addRow("Video Name:", self.video_name)
        
        self.video_desc = QTextEdit()
        self.video_desc.setMaximumHeight(80)
        form_layout.addRow("Description:", self.video_desc)
        

        self.video_url = QLineEdit()
        form_layout.addRow("Video URL:", self.video_url)
        
        self.video_thumbnail = QLineEdit()
        form_layout.addRow("Thumbnail URL:", self.video_thumbnail)
        
        self.video_duration = QLineEdit()
        self.video_duration.setPlaceholderText("PT1H30M (1 hour 30 min)")
        form_layout.addRow("Duration (ISO 8601):", self.video_duration)
        
        self.video_upload_date = QLineEdit()
        self.video_upload_date.setPlaceholderText("2024-01-15")
        form_layout.addRow("Upload Date:", self.video_upload_date)
        
        self.video_generate = QPushButton("Generate Video Schema")
        self.video_generate.clicked.connect(self.generate_video)
        form_layout.addRow(self.video_generate)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        self.schema_tabs.addTab(tab, "\ue131 Video")
    
    def generate_video(self):
        name = self.video_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Video name is required.")
            return
        
        schema = {

            "@context": "https://schema.org",
            "@type": "VideoObject",
            "name": name,
            "description": self.video_desc.toPlainText().strip() or None,
            "contentUrl": self.video_url.text().strip() or None,
            "thumbnailUrl": self.video_thumbnail.text().strip() or None,
            "duration": self.video_duration.text().strip() or None,
            "uploadDate": self.video_upload_date.text().strip() or None
        }
        
        schema = {k: v for k, v in schema.items() if v}
        self.update_json_preview(schema)
